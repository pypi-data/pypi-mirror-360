# Copyright (c) 2025, DeepLink.
# modify from sglang
from typing import List, Optional

import torch
import triton
import triton.language as tl

from dlblas.utils.device_utils import get_device_props


@triton.jit
def compute_m_range(
    pid,
    batch_size,
    seg_indptr,
    weight_indices,
    m_num_tiles_indptr,
    BLOCK_SIZE_M: tl.constexpr,
):
    idx = 0
    for bs in range(batch_size):
        tiles = tl.load(m_num_tiles_indptr + bs)
        if pid >= tiles:
            idx = bs

    idx_start = tl.load(m_num_tiles_indptr + idx)

    m_range_start = tl.load(seg_indptr + idx) + (pid - idx_start) * BLOCK_SIZE_M
    m_range_end = min(tl.load(seg_indptr + idx + 1), m_range_start + BLOCK_SIZE_M)
    expert_id = tl.load(weight_indices + idx)
    return m_range_start, m_range_end, expert_id


@triton.jit
def grouped_gemm_triton_kernel(
    a,
    b,
    c,
    batch_size,
    N,
    K,
    seg_indptr,
    weight_indices,
    m_num_tiles_indptr,
    scale_a,
    scale_b,
    use_fp8_w8a8: tl.constexpr,
    group_n: tl.constexpr,
    group_k: tl.constexpr,
    a_stride_0: tl.constexpr,
    b_stride_0: tl.constexpr,
    b_stride_1: tl.constexpr,
    as_stride_0: tl.constexpr,
    as_stride_1: tl.constexpr,
    bs_stride_0: tl.constexpr,
    bs_stride_2: tl.constexpr,
    bs_stride_1: tl.constexpr,
    BLOCK_SIZE_M: tl.constexpr,
    BLOCK_SIZE_N: tl.constexpr,
    BLOCK_SIZE_K: tl.constexpr,
):
    c_dtype = c.dtype.element_ty

    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)
    total_m_block = tl.load(m_num_tiles_indptr + batch_size)
    if pid_m >= total_m_block:
        return

    m_range_start, m_range_end, expert_id = compute_m_range(pid_m, batch_size, seg_indptr, weight_indices,
                                                            m_num_tiles_indptr, BLOCK_SIZE_M)
    if m_range_end - m_range_start == 0:
        return

    n_range_start = pid_n * BLOCK_SIZE_N
    n_range_end = min(n_range_start + BLOCK_SIZE_N, N)

    offs_am = tl.arange(0, BLOCK_SIZE_M)
    offs_bn = tl.arange(0, BLOCK_SIZE_N)

    offs_am = tl.where(offs_am < m_range_end - m_range_start, offs_am, 0)
    offs_bn = tl.where(offs_bn < n_range_end - n_range_start, offs_bn, 0)
    offs_am = tl.max_contiguous(tl.multiple_of(offs_am, BLOCK_SIZE_M), BLOCK_SIZE_M)
    offs_bn = tl.max_contiguous(tl.multiple_of(offs_bn, BLOCK_SIZE_N), BLOCK_SIZE_N)
    offs_k = tl.arange(0, BLOCK_SIZE_K)

    a_ptr = a + (m_range_start + offs_am[:, None]) * a_stride_0 + offs_k[None, :]
    b_ptr = b + ((expert_id * b_stride_0) + (n_range_start + offs_bn[:, None]) * b_stride_1 + offs_k[None, :])

    if group_k > 0 and group_n > 0:
        a_scale_ptrs = scale_a + (m_range_start + offs_am[:, None]) * as_stride_0
        offs_bsn = (n_range_start + offs_bn) // group_n
        b_scale_ptrs = scale_b + (expert_id * bs_stride_0) + offs_bsn * bs_stride_1

    accumulator = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)
    for k in range(0, tl.cdiv(K, BLOCK_SIZE_K)):
        a_tile = tl.load(a_ptr, mask=offs_k[None, :] < (K - k * BLOCK_SIZE_K), other=0.0)
        b_tile = tl.load(b_ptr, mask=offs_k[None, :] < (K - k * BLOCK_SIZE_K), other=0.0)

        if group_k > 0 and group_n > 0:
            k_start = k * BLOCK_SIZE_K
            offs_ks = k_start // group_k
            a_scale = tl.load(a_scale_ptrs + offs_ks * as_stride_1)
            b_scale = tl.load(b_scale_ptrs + offs_ks * bs_stride_2)
            accumulator += tl.dot(a_tile, b_tile.T) * a_scale * b_scale[None, :]
        else:
            accumulator = tl.dot(a_tile, b_tile.T, accumulator)
        a_ptr += BLOCK_SIZE_K
        b_ptr += BLOCK_SIZE_K

    if use_fp8_w8a8 and not (group_k > 0 and group_n > 0):
        scale_a_value = tl.load(scale_a + expert_id)
        scale_b_value = tl.load(scale_b + expert_id)
        accumulator *= scale_a_value * scale_b_value

    c_tile = accumulator.to(c_dtype)

    offs_cm = m_range_start + tl.arange(0, BLOCK_SIZE_M)
    offs_cn = n_range_start + tl.arange(0, BLOCK_SIZE_N)
    c_ptr = c + offs_cm[:, None] * N + offs_cn[None, :]
    c_mask = (offs_cm[:, None] < m_range_end) & (offs_cn[None, :] < n_range_end)
    tl.store(c_ptr, c_tile, mask=c_mask)


@triton.jit
def compute_m_num_tiles_indptr(m_num_tiles_indptr, seg_indptr, batch_size: tl.constexpr, BLOCK_SIZE_M: tl.constexpr):
    for bs in range(batch_size):
        m = tl.load(seg_indptr + bs + 1) - tl.load(seg_indptr + bs)
        cur_num_tiles = tl.cdiv(m, BLOCK_SIZE_M)
        pre_num_tiles = tl.load(m_num_tiles_indptr + bs)
        tl.store(m_num_tiles_indptr + bs + 1, pre_num_tiles + cur_num_tiles)


def grouped_gemm_triton(
    a: torch.Tensor,
    b: torch.Tensor,
    c: torch.Tensor,
    batch_size: int,
    weight_column_major: bool,
    seg_indptr: Optional[torch.Tensor] = None,
    weight_indices: Optional[torch.Tensor] = None,
    use_fp8_w8a8: bool = False,
    scale_a: torch.Tensor = None,
    scale_b: torch.Tensor = None,
    block_shape: Optional[List[int]] = None,
):
    assert weight_column_major
    if use_fp8_w8a8 and block_shape is None:
        assert scale_a is not None and scale_b is not None

    if block_shape is not None:
        assert len(block_shape) == 2
        block_n, block_k = block_shape[0], block_shape[1]
        assert triton.cdiv(a.shape[-1], block_k) == scale_a.shape[-1]
        assert triton.cdiv(b.shape[-2], block_n) == scale_b.shape[-2]
        assert triton.cdiv(b.shape[-1], block_k) == scale_b.shape[-1]

    # TODO: adjust config or tune kernel
    # Reduce block size to prevent L40 shared memory overflow.
    config = {
        'BLOCK_SIZE_M': 64,
        'BLOCK_SIZE_N': 32,
        'BLOCK_SIZE_K': 128,
    }

    m_num_tiles_indptr = torch.zeros(batch_size + 1, device=a.device, dtype=torch.int64)
    compute_m_num_tiles_indptr[(1, )](m_num_tiles_indptr, seg_indptr, batch_size, config['BLOCK_SIZE_M'])

    def grid(META):
        return (
            triton.cdiv(a.size(0), META['BLOCK_SIZE_M']) + batch_size,
            triton.cdiv(b.size(1), META['BLOCK_SIZE_N']),
        )

    grouped_gemm_triton_kernel[grid](
        a,
        b,
        c,
        batch_size,
        b.size(1),
        b.size(2),
        seg_indptr,
        weight_indices,
        m_num_tiles_indptr,
        scale_a,
        scale_b,
        use_fp8_w8a8,
        0 if block_shape is None else block_shape[0],
        0 if block_shape is None else block_shape[1],
        a.stride(0),
        b.stride(0),
        b.stride(1),
        scale_a.stride(0) if scale_a is not None and scale_a.ndim == 2 else 0,
        scale_a.stride(1) if scale_a is not None and scale_a.ndim == 2 else 0,
        scale_b.stride(0) if scale_b is not None and scale_b.ndim >= 2 else 0,
        scale_b.stride(2) if scale_b is not None and scale_b.ndim == 3 else 0,
        scale_b.stride(1) if scale_b is not None and scale_b.ndim >= 2 else 0,
        **config,
    )
    return c


@triton.jit
def _silu_and_mul_post_quant_kernel(
    input_ptr,
    stride_input_0,
    stride_input_1,
    stride_input_2,
    output_ptr,
    stride_output_0,
    stride_output_1,
    stride_output_2,
    output_scale_ptr,
    stride_output_scale_0,
    stride_output_scale_1,
    stride_output_scale_2,
    masked_m_ptr,
    size_n,
    fp8_max,
    fp8_min,
    BLOCK_N: tl.constexpr,
    NUM_STAGE: tl.constexpr,
):
    expert_id = tl.program_id(2)
    token_id = tl.program_id(1)
    hidden_dim_block_index = tl.program_id(0)

    block_num_per_expert = tl.num_programs(1)

    token_num_cur_expert = tl.load(masked_m_ptr + expert_id)

    stride_input_0 = tl.cast(stride_input_0, dtype=tl.int64)
    stride_output_0 = tl.cast(stride_output_0, dtype=tl.int64)
    stride_input_1 = tl.cast(stride_input_1, dtype=tl.int64)
    stride_output_1 = tl.cast(stride_output_1, dtype=tl.int64)

    offs_in_d = hidden_dim_block_index * BLOCK_N + tl.arange(0, BLOCK_N)
    input_ptr_offs = input_ptr + expert_id * stride_input_0 + offs_in_d
    output_ptr_offs = output_ptr + expert_id * stride_output_0 + offs_in_d
    output_scale_offs = (output_scale_ptr + expert_id * stride_output_scale_0 +
                         hidden_dim_block_index * stride_output_scale_2)

    for token_index in tl.range(token_id, token_num_cur_expert, block_num_per_expert, num_stages=NUM_STAGE):
        gate = tl.load(
            input_ptr_offs + token_index * stride_input_1,
            mask=offs_in_d < size_n,
            other=0.0,
        ).to(tl.float32)
        up = tl.load(
            input_ptr_offs + token_index * stride_input_1 + size_n,
            mask=offs_in_d < size_n,
            other=0.0,
        )
        gate = gate / (1 + tl.exp(-gate))
        gate = gate.to(input_ptr.dtype.element_ty)
        gate_up = up * gate
        _absmax = tl.maximum(tl.max(tl.abs(gate_up)), 1e-10)
        output_s = _absmax / fp8_max
        output_q = tl.clamp(gate_up / output_s, fp8_min, fp8_max).to(output_ptr.dtype.element_ty)
        tl.store(
            output_ptr_offs + token_index * stride_output_1,
            output_q,
            mask=offs_in_d < size_n,
        )
        tl.store(
            output_scale_offs + token_index * stride_output_scale_1,
            output_s,
        )


def silu_and_mul_masked_post_quant_fwd(
    input: torch.Tensor,
    output: torch.Tensor,
    output_scale: torch.Tensor,
    quant_group_size: int,
    masked_m: torch.Tensor,
):
    assert input.is_contiguous()
    assert output.dtype == torch.float8_e4m3fn
    assert output.is_contiguous()
    assert len(input.shape) == 3
    assert input.shape[0] == masked_m.shape[0]
    assert input.shape[-1] % 2 == 0
    size_n = input.shape[-1] // 2
    assert size_n % quant_group_size == 0
    expert_num = len(masked_m)
    if expert_num < 4:
        BLOCK_NUM_PER_EXPERT = 64
    else:
        BLOCK_NUM_PER_EXPERT = 32
    BLOCK_N = quant_group_size
    num_warps = 1
    NUM_STAGES = 6
    hidden_dim_split_block_num = triton.cdiv(size_n, BLOCK_N)
    assert BLOCK_N % quant_group_size == 0
    grid = (
        hidden_dim_split_block_num,
        BLOCK_NUM_PER_EXPERT,
        expert_num,
    )
    finfo = torch.finfo(torch.float8_e4m3fn)
    fp8_max = finfo.max
    fp8_min = -fp8_max
    _silu_and_mul_post_quant_kernel[grid](
        input,
        *input.stride(),
        output,
        *output.stride(),
        output_scale,
        *output_scale.stride(),
        masked_m,
        size_n,
        fp8_max,
        fp8_min,
        BLOCK_N=BLOCK_N,
        NUM_STAGE=NUM_STAGES,
        num_warps=num_warps,
    )


@triton.jit
def silu_and_mul_triton_kernel(
    gateup_output,
    down_input,
    hidden_size,
    reorder_topk_ids,
    scales,
    start_expert_id,
    end_expert_id,
    BLOCK_SIZE: tl.constexpr,
):
    InDtype = gateup_output.dtype.element_ty
    OutDtype = down_input.dtype.element_ty

    half_hidden_size = hidden_size // 2

    pid = tl.program_id(0)
    expert_id = tl.load(reorder_topk_ids + pid)
    if expert_id >= start_expert_id and expert_id <= end_expert_id:
        gateup_output_ptr = gateup_output + pid * hidden_size
        gate_output_ptr = gateup_output_ptr
        up_output_ptr = gateup_output_ptr + half_hidden_size
        down_input_ptr = down_input + pid * half_hidden_size

        if scales is not None:
            scale = tl.load(scales + expert_id - start_expert_id)
            scale = (1 / scale).to(InDtype)
        else:
            scale = 1

        for start_offset in tl.range(0, half_hidden_size, BLOCK_SIZE):
            offset = start_offset + tl.arange(0, BLOCK_SIZE)
            mask = offset < half_hidden_size

            gate_output = tl.load(gate_output_ptr + offset, mask=mask).to(tl.float32)
            up_output = tl.load(up_output_ptr + offset, mask=mask)

            # silu & mul & quantize
            gate_output = gate_output * tl.sigmoid(gate_output)
            gate_output = gate_output.to(InDtype)

            silu_mul_output = gate_output * up_output * scale
            silu_mul_output = silu_mul_output.to(OutDtype)
            tl.store(down_input_ptr + offset, silu_mul_output, mask=mask)


def renormalize(topk_weights: torch.Tensor, renormalize: bool):
    if renormalize:
        topk_weights = topk_weights / topk_weights.sum(dim=-1, keepdim=True)
    if not topk_weights.is_contiguous():
        topk_weights = topk_weights.contiguous()
    return topk_weights


@triton.jit
def _quant_fp8_kernel(
    a_ptr,
    out_ptr,
    scale_ptr,
    M,
    M_out,
    fp8_min: tl.constexpr,
    fp8_max: tl.constexpr,
    stride_am,
    stride_ak: tl.constexpr,
    stride_om,
    stride_ok: tl.constexpr,
    stride_sm,
    stride_sg,
    GROUP_SIZE: tl.constexpr,
):
    """quant fp8 kernel."""
    group_id = tl.program_id(0)
    m_id_start = tl.program_id(1)
    m_id_stride = tl.num_programs(1)

    g_offs = group_id * GROUP_SIZE + tl.arange(0, GROUP_SIZE)
    g_offs = tl.max_contiguous(tl.multiple_of(g_offs, GROUP_SIZE), GROUP_SIZE)
    rfp8_max = 1 / fp8_max

    m_id = m_id_start
    a_ptrs = a_ptr + m_id * stride_am + g_offs * stride_ak
    o_ptrs = out_ptr + m_id * stride_om + g_offs * stride_ok
    s_ptr = scale_ptr + m_id * stride_sm + group_id * stride_sg

    for m_id in tl.range(m_id_start, M_out, m_id_stride):

        a = tl.load(a_ptrs, mask=m_id < M, other=0).to(tl.float32)
        scale = tl.max(tl.abs(a)) * rfp8_max
        out = a / scale

        out = tl.clamp(out, fp8_min, fp8_max)
        out = out.to(out_ptr.dtype.element_ty)

        tl.store(o_ptrs, out)
        tl.store(s_ptr, scale)

        a_ptrs += m_id_stride * stride_am
        o_ptrs += m_id_stride * stride_om
        s_ptr += m_id_stride * stride_sm


def _quant_fp8_launcher(A: torch.Tensor, group_size: int, out: torch.Tensor, scales: torch.Tensor):
    """quant online."""
    M, K = A.shape
    num_groups = K // group_size
    M_out = out.size(0)

    dtype = out.dtype
    finfo = torch.finfo(dtype)
    fmin = finfo.min
    fmax = finfo.max

    num_warps = 1
    num_stages = 1

    props = get_device_props(A.device.index)
    num_sm = props['multi_processor_count']
    warps_per_sm = props['warps_per_sm']
    max_ctas = num_sm * warps_per_sm // num_warps
    grid_size1 = min(M_out, max_ctas // num_groups)
    assert grid_size1 < 65536
    grid = (num_groups, grid_size1)
    _quant_fp8_kernel[grid](
        A,
        out,
        scales,
        M,
        M_out,
        fp8_min=fmin,
        fp8_max=fmax,
        stride_am=A.stride(0),
        stride_ak=A.stride(1),
        stride_om=out.stride(0),
        stride_ok=out.stride(1),
        stride_sm=scales.stride(0),
        stride_sg=scales.stride(1),
        GROUP_SIZE=group_size,
        num_warps=num_warps,
        num_stages=num_stages,
    )
    return out, scales


def quant_fp8(A: torch.Tensor, group_size: int, dtype: torch.dtype = torch.float8_e4m3fn):
    """quant fp8."""
    assert A.dim() == 2
    M, K = A.shape
    assert K % group_size == 0
    num_groups = K // group_size
    out = torch.empty_like(A, dtype=dtype)
    scales = A.new_empty(M, num_groups, dtype=torch.float32)
    return _quant_fp8_launcher(A, group_size, out, scales)


def biased_grouped_topk(
    hidden_states: torch.Tensor,
    gating_output: torch.Tensor,
    correction_bias: torch.Tensor,
    topk: int,
    renormalize: bool,
    num_expert_group: int = 0,
    topk_group: int = 0,
    n_share_experts_fusion: int = 0,
    routed_scaling_factor: Optional[float] = None,
):
    assert hidden_states.shape[0] == gating_output.shape[0], 'Number of tokens mismatch'

    scores = gating_output.sigmoid()
    num_token = scores.shape[0]
    num_experts = scores.shape[1]
    scores_for_choice = scores.view(num_token, -1) + correction_bias.unsqueeze(0)
    group_scores = (scores_for_choice.view(num_token, num_expert_group, -1).topk(2,
                                                                                 dim=-1)[0].sum(dim=-1))  # [n, n_group]
    group_idx = torch.topk(group_scores, k=topk_group, dim=-1, sorted=False)[1]  # [n, top_k_group]
    group_mask = torch.zeros_like(group_scores)  # [n, n_group]
    group_mask.scatter_(1, group_idx, 1)  # [n, n_group]
    score_mask = (group_mask.unsqueeze(-1).expand(num_token, num_expert_group,
                                                  scores.shape[-1] // num_expert_group).reshape(num_token,
                                                                                                -1))  # [n, e]
    tmp_scores = scores_for_choice.masked_fill(~score_mask.bool(), float('-inf'))  # [n, e]
    _, topk_ids = torch.topk(tmp_scores, k=topk, dim=-1, sorted=False)
    topk_weights = scores.gather(1, topk_ids)

    if n_share_experts_fusion:
        topk_ids[:, -1] = torch.randint(
            low=num_experts,
            high=num_experts + n_share_experts_fusion,
            size=(topk_ids.size(0), ),
            dtype=topk_ids.dtype,
            device=topk_ids.device,
        )
        topk_weights[:, -1] = topk_weights[:, :-1].sum(dim=-1) / routed_scaling_factor

    if renormalize:
        topk_weights_sum = (topk_weights.sum(dim=-1, keepdim=True)
                            if n_share_experts_fusion == 0 else topk_weights[:, :-1].sum(dim=-1, keepdim=True))
        topk_weights = topk_weights / topk_weights_sum

    return topk_weights.to(torch.float32), topk_ids.to(torch.int32)


@triton.jit
def kernel_map_logic_to_physical_hash(topk_idx_ptr, physical_idx_ptr, log2phy_ptr, logcnt_ptr, seed, num_tokens,
                                      num_topk, num_logical_experts, max_replica, BLOCK: tl.constexpr):
    pid = tl.program_id(0)
    start_t = pid * BLOCK
    end_t = tl.minimum(start_t + BLOCK, num_tokens)

    for t in range(start_t, end_t):
        row_off = t * num_topk
        for k in range(num_topk):
            logic_exp = tl.load(topk_idx_ptr + row_off + k)

            # 条件判断不能用 continue，只能嵌套写
            if logic_exp >= 0:
                cnt = tl.load(logcnt_ptr + logic_exp)
                if cnt > 0:
                    # 构造 hash 值
                    combined = ((t << 16) ^ (k << 8) ^ seed) & 0xFFFFFFFF
                    x = combined
                    x = ((x >> 16) ^ x) * 0x45d9f3b
                    x = ((x >> 16) ^ x) * 0x45d9f3b
                    x = (x >> 16) ^ x
                    rand_val = x & 0x7fffffff

                    replica_id = rand_val % cnt.to(tl.uint32)
                    phy_id_addr = log2phy_ptr + logic_exp * max_replica + replica_id
                    phy_id = tl.load(phy_id_addr)
                    tl.store(physical_idx_ptr + row_off + k, phy_id)
                else:
                    tl.store(physical_idx_ptr + row_off + k, -1)
            else:
                tl.store(physical_idx_ptr + row_off + k, -1)


def map_logic_to_physical_idx_hash_random(topk_idx: torch.Tensor,
                                          log2phy: torch.Tensor,
                                          logcnt: torch.Tensor,
                                          seed: int = 12345,
                                          block_size: int = 128) -> torch.Tensor:
    num_tokens, num_topk = topk_idx.shape
    physical_idx = torch.empty_like(topk_idx, dtype=torch.int32, device=topk_idx.device)

    grid = ((num_tokens + block_size - 1) // block_size, )

    kernel_map_logic_to_physical_hash[grid](topk_idx,
                                            physical_idx,
                                            log2phy,
                                            logcnt,
                                            seed,
                                            num_tokens,
                                            num_topk,
                                            log2phy.shape[0],
                                            log2phy.shape[1],
                                            BLOCK=block_size)

    return physical_idx
