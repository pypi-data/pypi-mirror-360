# -*- coding: utf-8 -*-
# @Time   : 2024/08/26 10:24
# @Author : zip
# @Moto   : Knowledge comes from decomposition
from __future__ import absolute_import, division, print_function

import logging
import os
import shutil
import time
from functools import wraps
from typing import Optional

import numpy as np
import torch
from packaging import version

logger = logging.getLogger(__name__)


parsed_torch_version_base = version.parse(version.parse(torch.__version__).base_version)
is_torch_greater_or_equal_than_1_13 = parsed_torch_version_base >= version.parse("1.13")


# 定义计时装饰器
def time_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # 使用高精度计时
        result = func(*args, **kwargs)  # 执行函数
        end_time = time.perf_counter()
        logger.info(f"函数 {func.__name__} 耗时: {end_time - start_time:.4f} 秒")
        return result

    return wrapper


# 定义缓存文件装饰器
def cache_folder_decorator(cache_folder_attr):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cache_folder = getattr(self, cache_folder_attr)
            os.makedirs(cache_folder, exist_ok=True)
            result = func(self, *args, **kwargs)  # 执行函数
            shutil.rmtree(cache_folder, ignore_errors=True)
            return result

        return wrapper

    return decorator


# 获得文件夹下，指定后缀的文件路径
def get_filenames(directory, suffix=None):
    filenames = []
    files = os.listdir(directory)
    for _file in files:
        tmp_file = os.path.join(directory, _file)
        if os.path.isfile(tmp_file):
            if tmp_file.endswith(suffix):
                filenames.append(tmp_file)
    return filenames


# 获得文件夹下, 所有文件的绝对路径
def get_files_abs_path(path):
    if isinstance(path, list):
        return [os.path.abspath(p) for p in path]
    elif os.path.isdir(path):
        return [
            os.path.abspath(os.path.join(root, fi))
            for root, dirs, files in os.walk(path)
            for fi in files
        ]
    elif os.path.isfile(path):
        return [os.path.abspath(path)]
    else:
        raise ValueError("Invalid path or unsupported type")


# 获得文件夹下，最大的checkpoint的文件
def get_checkpoint_path(directory):
    filenames = []
    files = os.listdir(directory)
    for _file in files:
        if _file.startswith("checkpoint"):
            filenames.append(_file)

    return os.path.join(directory, max(filenames))


# 计算模型参数量的方法
def count_parameters(model):
    for name, param in model.named_parameters():
        if param.requires_grad:
            print(f"层: {name} | 参数大小: {param.size()} | 参数量: {param.numel()}")

    count = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"模型总参数量: {count}")


# 设置日志颜色
def set_color(log, color, highlight=True):
    color_set = ["black", "red", "green", "yellow", "blue", "pink", "cyan", "white"]
    try:
        index = color_set.index(color)
    except Exception:
        index = len(color_set) - 1
    prev_log = "\033["
    if highlight:
        prev_log += "1;3"
    else:
        prev_log += "0;3"
    prev_log += str(index) + "m"
    return prev_log + log + "\033[0m"


# tensor的填充方式
def tensor_pad(
    tensors: list[torch.Tensor],
    padding_value: int = 0,
    padding_side: str = "right",
    pad_to_multiple_of: Optional[int] = None,
) -> torch.Tensor:
    """
    Pads a list of tensors to the same shape along the first dimension.

    Args:
        tensors (`list[torch.Tensor]`):
            List of input tensors to pad.
        padding_value (`int`):
            Value to use for padding. Default is 0.
        padding_side (`str`):
            Side on which to add padding. Must be 'left' or 'right'. Default is 'right'.

    Returns:
        `torch.Tensor`:
            A single tensor containing the padded tensors.

    Examples:
        >>> import torch
        >>> pad([torch.tensor([1, 2, 3]), torch.tensor([4, 5])])
        tensor([[1, 2, 3],
                [4, 5, 0]])
        >>> pad([torch.tensor([[1, 2], [3, 4]]), torch.tensor([[5, 6]])])
        tensor([[[1, 2],
                [3, 4]],

                [[5, 6],
                [0, 0]]])
    """
    # Determine the maximum shape for each dimension
    output_shape = np.max([t.shape for t in tensors], 0).tolist()

    # Apply pad_to_multiple_of to the first (sequence) dimension
    if pad_to_multiple_of is not None:
        remainder = output_shape[0] % pad_to_multiple_of
        if remainder != 0:
            output_shape[0] += pad_to_multiple_of - remainder

    # Create an output tensor filled with the padding value
    output = torch.full(
        (len(tensors), *output_shape),
        padding_value,
        dtype=tensors[0].dtype,
        device=tensors[0].device,
    )

    for i, t in enumerate(tensors):
        # Determine the slice for the sequence dimension
        if padding_side == "left":
            seq_slice = slice(output_shape[0] - t.shape[0], output_shape[0])
        elif padding_side == "right":
            seq_slice = slice(0, t.shape[0])
        else:
            raise ValueError("padding_side must be 'left' or 'right'")

        slices = (seq_slice,) + tuple(slice(0, s) for s in t.shape[1:])
        output[i][slices] = t

    return output
