# Copyright (c) 2025, DeepLink.
import functools

import torch
import triton

WARPS_PER_SM = {
    (8, 0): 64,
    (8, 6): 48,
    (8, 7): 48,
    (8, 9): 48,
    (9, 0): 64,
    (10, 0): 64,
    (10, 1): 48,
    (12, 0): 48,
}


@functools.lru_cache
def get_device_props(device=None):
    if device is None:
        device = torch.cuda.current_device()

    props = torch.cuda.get_device_properties(device)

    warps_per_sm = WARPS_PER_SM.get((props.major, props.minor), 32)
    out = dict(
        multi_processor_count=props.multi_processor_count,
        warps_per_sm=warps_per_sm,
    )
    return out


def is_mlu_592():
    target = triton.runtime.driver.active.get_current_target()
    return target.backend == 'mlu' and target.arch == 592


def is_muxi():
    target = triton.runtime.driver.active.get_current_target()
    return target.backend == 'maca'


def is_cuda():
    try:
        torch.cuda.is_available()
        return True
    except Exception:
        return False


def is_npu():
    try:
        import torch_npu  # noqa: F401
        torch.npu.is_available()
        return True
    except Exception:
        return False


def infer_device():
    """
    Get current device name based on available devices
    """
    if is_cuda():
        return 'cuda'
    elif is_npu():
        return 'npu'
    elif is_mlu_592():
        return 'mlu'
    elif is_muxi():
        return 'cuda'
    else:
        return 'cpu'
