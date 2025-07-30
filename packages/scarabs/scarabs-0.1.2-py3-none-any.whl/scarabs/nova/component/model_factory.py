# -*- coding: utf-8 -*-
# @Time   : 2024/07/30 10:24
# @Author : zip
# @Moto   : Knowledge comes from decomposition
from __future__ import absolute_import, division, print_function

import logging
import os
from collections import OrderedDict
from typing import List, Optional

import torch
from safetensors.torch import load_file
from tqdm import tqdm

from scarabs.nova.utils import PreTrainedModel, is_torch_greater_or_equal_than_1_13
from scarabs.nova.utils.tool_utils import set_color

logger = logging.getLogger(__name__)
SAFE_WEIGHTS_NAME = "model.safetensors"
WEIGHTS_NAME = "pytorch_model.bin"


class ModelFactory:
    def __init__(
        self,
        model: Optional[PreTrainedModel] = None,
    ):
        self.model = model

    def _get_nested_attr(self, obj, attr_path, default=None):
        """
        安全获取对象的嵌套属性
        :param obj: 目标对象
        :param attr_path: 属性路径字符串，如 'embedding_layer.feature_embedding.weight'
        :param default: 属性不存在时的默认返回值
        :return: 属性值或default
        """
        current = obj
        for attr in attr_path.split("."):
            try:
                current = getattr(current, attr)
            except AttributeError:
                return default
        return current

    def _load_state_dict(
        self, model: PreTrainedModel, resume_from_checkpoint: Optional[str] = None
    ):
        if resume_from_checkpoint is not None:
            # load safetensors weight
            model_files = self._get_filenames(resume_from_checkpoint, "safetensors")
            state_dict = {}
            for _file in tqdm(model_files):
                state_dict.update(self._get_safetensors_model_state_dict(_file))

            self._load_state_dict_into_model(model, state_dict)

            for k in state_dict.keys():
                if "emb" in k:
                    before = state_dict[k]
                    after = self._get_nested_attr(model, k)
                    if after is None:
                        continue
                    self._sanity_check(before[:5], after[:5])
                    break
            del state_dict
            logger.warning(f"🔔 Load state dict model from {resume_from_checkpoint}")
        return model

    def _load_state_dict_into_model(self, model_to_load, state_dict, strict=True):
        # Convert old format to new format if needed from a PyTorch state_dict
        # 1. 参数名转换（保留原有逻辑）
        old_keys = []
        new_keys = []
        renamed_keys = {}
        renamed_gamma = {}
        renamed_beta = {}
        warning_msg = (
            f"A pretrained model of type `{model_to_load.__class__.__name__}` "
        )

        for key in state_dict.keys():
            new_key = None
            if "gamma" in key:
                # We add only the first key as an example
                new_key = key.replace("gamma", "weight")
                renamed_gamma[key] = new_key if not renamed_gamma else renamed_gamma
            if "beta" in key:
                # We add only the first key as an example
                new_key = key.replace("beta", "bias")
                renamed_beta[key] = new_key if not renamed_beta else renamed_beta
            if new_key:
                old_keys.append(key)
                new_keys.append(new_key)
        renamed_keys = {**renamed_gamma, **renamed_beta}
        if renamed_keys:
            warning_msg += "contains parameters that have been renamed internally (a few are listed below but more are present in the model):\n"
            for old_key, new_key in renamed_keys.items():
                warning_msg += f"* `{old_key}` -> `{new_key}`\n"
            warning_msg += "If you are using a model from the Hub, consider submitting a PR to adjust these weights and help future users."
            logger.warning(warning_msg)
        for old_key, new_key in zip(old_keys, new_keys):
            state_dict[new_key] = state_dict.pop(old_key)

        # 2. 处理多GPU训练导致的"module."前缀
        if any(key.startswith("module.") for key in state_dict.keys()):
            new_state_dict = OrderedDict()
            for k, v in state_dict.items():
                name = k[7:] if k.startswith("module.") else k
                new_state_dict[name] = v
            state_dict = new_state_dict

        load_result = model_to_load.load_state_dict(state_dict, strict=strict)

        def _issue_warnings_after_load(model, load_result):
            if len(load_result.missing_keys) != 0:
                if model._keys_to_ignore_on_save is not None and set(
                    load_result.missing_keys
                ) == set(model._keys_to_ignore_on_save):
                    model.tie_weights()
                else:
                    logger.warning(
                        f"There were missing keys in the checkpoint model loaded: {load_result.missing_keys}."
                    )
            if len(load_result.unexpected_keys) != 0:
                logger.warning(
                    f"There were unexpected keys in the checkpoint model loaded: {load_result.unexpected_keys}."
                )

        _issue_warnings_after_load(model_to_load, load_result)
        # # copy state_dict so _load_from_state_dict can modify it
        # metadata = getattr(state_dict, "_metadata", None)
        # state_dict = state_dict.copy()
        # if metadata is not None:
        #     state_dict._metadata = metadata # type:ignore

        # # PyTorch's `_load_from_state_dict` does not copy parameters in a module's descendants
        # # so we need to apply the function recursively.
        # def load(module, prefix=""):
        #     local_metadata = {} if metadata is None else metadata.get(prefix[:-1], {})
        #     module._load_from_state_dict(
        #         state_dict,
        #         prefix,
        #         local_metadata,
        #         strict,  # 支持严格模式参数
        #         error_msgs,
        #         [],
        #         [],
        #         assign_to_params_buffers=True,  # PyTorch 1.12+支持
        #     )
        #     for name, child in module.named_children():
        #         if child is not None:
        #             load(child, prefix + name + ".")

        # load(model_to_load)
        # Delete `state_dict` so it could be collected by GC earlier. Note that `state_dict` is a copy of the argument, so
        # it's safe to delete it.
        # del state_dict

        # # 5. 严格模式检查
        # if strict and error_msgs:
        #     missing_keys, unexpected_keys = [], []
        #     for msg in error_msgs:
        #         if "missing" in msg:
        #             missing_keys.append(msg.split("'")[1])
        #         elif "unexpected" in msg:
        #             unexpected_keys.append(msg.split("'")[1])

        #     if missing_keys or unexpected_keys:
        #         err_msg = f"Error(s) in loading state_dict for {type(model_to_load).__name__}:"
        #         if missing_keys:
        #             err_msg += f"\n\tMissing keys: {', '.join(missing_keys)}"
        #         if unexpected_keys:
        #             err_msg += f"\n\tUnexpected keys: {', '.join(unexpected_keys)}"
        #         raise RuntimeError(err_msg)  # 严格模式抛异常

        # return error_msgs

    def _get_filenames(self, directory, suffix=""):
        filenames = []
        files = os.listdir(directory)
        for fi in files:
            tmp_file = os.path.join(directory, fi)
            if os.path.isfile(tmp_file):
                if tmp_file.endswith(suffix):
                    filenames.append(tmp_file)
        return filenames

    def _get_safetensors_model_state_dict(self, model_path):
        """返回 safetensors 模型的 state_dict"""
        state_dict = load_file(model_path)
        return state_dict

    def _sanity_check(self, before: List, after: List):
        logger.info(">>>>>>>>>>>>> Sanity Check ")
        logger.info(f"\nbefore: {before}")
        logger.info(f"\nafter: {after}")
        logger.info("<<<<<<<<<<<<< Sanity Check")

        assert len(before) == len(after), (
            f"length mismatch: {len(before)} vs {len(after)}"
        )

    def _calulate_parameters(self, model):
        """
        Calculate the number of parameters in the model.
        """
        trainable_params = 0
        non_trainable_params = 0

        for name, param in model.named_parameters():
            if param.requires_grad:
                trainable_params += param.numel()
            else:
                non_trainable_params += param.numel()

        total_params = trainable_params + non_trainable_params
        total = round(total_params / 1e6, 2)
        logger.info(set_color(f"📊 Trainable parameters: {trainable_params}", "pink"))
        logger.info(
            set_color(f"📊 Non-trainable parameters: {non_trainable_params}", "pink")
        )
        logger.info(set_color(f"📊 Total parameters: {total_params}({total}M)", "pink"))


class ModelFactoryWithTabular(ModelFactory):
    def __init__(self, model: Optional[PreTrainedModel]):
        super().__init__(model)

    def _incremental_load_from_checkpoint(
        self, model: PreTrainedModel, incremental_resume_from_checkpoint
    ):
        if incremental_resume_from_checkpoint is None:
            return model

        safe_weights_file = os.path.join(
            incremental_resume_from_checkpoint, SAFE_WEIGHTS_NAME
        )
        weights_file = os.path.join(incremental_resume_from_checkpoint, WEIGHTS_NAME)
        weights_only_kwarg = (
            {"weights_only": True} if is_torch_greater_or_equal_than_1_13 else {}
        )
        # We load the model state dict on the CPU to avoid an OOM error.
        if os.path.isfile(safe_weights_file):
            state_dict = load_file(safe_weights_file, device="cpu")
        else:
            state_dict = torch.load(
                weights_file,
                map_location="cpu",
                **weights_only_kwarg,
            )

        # load 之前需要对state_dict（历史部分+增量部分）即改变size不一样部分的权重
        model_dict = model.state_dict()
        mismatched_key = []
        for v in model_dict.keys():
            for k in state_dict.keys():
                if v == k and model_dict[v].shape != state_dict[k].shape:
                    logger.warning(
                        f"🔔 {v} shape mismatched, current: {model_dict[v].shape} != history:{state_dict[k].shape}"
                    )
                    mismatched_key.append(k)

        # 修改历史部分- size不一样部分,注：这里的不一致只针对第一维度
        for key in mismatched_key:
            current_size = model_dict[key].size()
            history_size = state_dict[key].size()
            if current_size[0] > history_size[0]:
                model_dict[key][: history_size[0], :] = state_dict[key]
                state_dict[key] = model_dict[key]

            if current_size[0] < history_size[0]:
                model_dict[key] = state_dict[key][: current_size[0], :]
                state_dict[key] = model_dict[key]
            logger.warning(
                f"🔔 {key} is updated from history:{history_size} to current:{current_size}"
            )

        # workaround for FSDP bug https://github.com/pytorch/pytorch/issues/82963
        # which takes *args instead of **kwargs
        load_result = model.load_state_dict(state_dict, True)
        # release memory
        del state_dict

        def _issue_warnings_after_load(model, load_result):
            if len(load_result.missing_keys) != 0:
                if model._keys_to_ignore_on_save is not None and set(
                    load_result.missing_keys
                ) == set(model._keys_to_ignore_on_save):
                    model.tie_weights()
                else:
                    logger.warning(
                        f"There were missing keys in the checkpoint model loaded: {load_result.missing_keys}."
                    )
            if len(load_result.unexpected_keys) != 0:
                logger.warning(
                    f"There were unexpected keys in the checkpoint model loaded: {load_result.unexpected_keys}."
                )

        _issue_warnings_after_load(model, load_result)

        logger.warning(
            f"🔔 Incremental load state dict model from {incremental_resume_from_checkpoint}"
        )
        return model

    def handle_with_train(
        self, resume_from_checkpoint=None, incremental_resume_from_checkpoint=None
    ):
        if self.model is None:
            raise ValueError("model is required.")

        self.model = self._load_state_dict(self.model, resume_from_checkpoint)

        self.model = self._incremental_load_from_checkpoint(
            self.model, incremental_resume_from_checkpoint
        )
        for _, param in self.model.named_parameters():
            param.requires_grad = True

        self._calulate_parameters(self.model)
        return self.model

    def handle_with_inference(self, resume_from_checkpoint):
        if self.model is None:
            raise ValueError("model is required.")

        self.model = self._load_state_dict(self.model, resume_from_checkpoint)
        for _, param in self.model.named_parameters():
            param.requires_grad = False
        self._calulate_parameters(self.model)
        return self.model
