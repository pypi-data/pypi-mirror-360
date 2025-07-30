# -*- coding: utf-8 -*-
# @Time   : 2025/08/28 10:24
# @Author : zip
# @Moto   : Knowledge comes from decomposition
from __future__ import absolute_import, division, print_function

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import torch

from scarabs.nova.utils import tensor_pad


class DataCollatorMixin:
    def __call__(self, features, return_tensors=None):
        if return_tensors is None:
            return_tensors = self.return_tensors  # type: ignore
        if return_tensors == "pt":
            return self.torch_call(features)  # type: ignore
        elif return_tensors == "np":
            return self.numpy_call(features)  # type: ignore
        else:
            raise ValueError(f"Framework '{return_tensors}' not recognized!")


@dataclass
class CollatorFactoryWithTabular(DataCollatorMixin):
    label_names: List[str]
    feature2meta: Dict[str, Any]
    return_tensors: str = "pt"

    def torch_call(self, batch_examples):
        X = {}
        for example in batch_examples:
            for name, value in example.items():
                if name not in X:
                    X[name] = []
                X[name].append(value)

        label_names = [] if self.label_names is None else self.label_names
        for name in X:
            if name in self.feature2meta.keys():
                _feature_meta = self.feature2meta[name]
                if _feature_meta.target == "RawFeature":
                    X[name] = torch.tensor(X[name], dtype=torch.float64)
                else:
                    X[name] = torch.tensor(X[name], dtype=torch.long)

            if name in label_names:
                X[name] = torch.tensor(X[name], dtype=torch.float64)

        return X


@dataclass
class CollatorFactoryWithLLMPretrain(DataCollatorMixin):
    pad_id: int
    completion_only_loss: bool = True
    padding_free: bool = False
    return_position_ids: bool = True
    pad_to_multiple_of: Optional[int] = None
    return_tensors: str = "pt"

    def torch_call(self, batch_examples):
        input_ids = [torch.tensor(example["input_ids"]) for example in batch_examples]
        attention_mask = [torch.ones_like(input_ids) for input_ids in input_ids]

        if self.return_position_ids:
            if "position_ids" in batch_examples[0]:
                position_ids = [
                    torch.tensor(example["position_ids"]) for example in batch_examples
                ]
            else:
                position_ids = [torch.arange(len(ids)) for ids in input_ids]
        if "labels" in batch_examples[0]:
            labels = [torch.tensor(example["labels"]) for example in batch_examples]
        else:
            labels = [torch.tensor(example["input_ids"]) for example in batch_examples]

        # Pad
        output = {}
        if self.padding_free:
            output["input_ids"] = torch.cat(input_ids, dim=0).unsqueeze(0)
            output["attention_mask"] = torch.cat(attention_mask, dim=0).unsqueeze(0)
            if self.return_position_ids:
                output["position_ids"] = torch.cat(position_ids, dim=0).unsqueeze(0)
            output["labels"] = torch.cat(labels, dim=0).unsqueeze(0)

        else:
            output["input_ids"] = tensor_pad(
                input_ids,
                padding_value=self.pad_id,
                padding_side="right",
                pad_to_multiple_of=self.pad_to_multiple_of,
            )
            output["attention_mask"] = tensor_pad(
                attention_mask,
                padding_value=0,
                padding_side="right",
                pad_to_multiple_of=self.pad_to_multiple_of,
            )
            if self.return_position_ids:
                output["position_ids"] = tensor_pad(
                    position_ids,
                    padding_value=0,
                    padding_side="right",
                    pad_to_multiple_of=self.pad_to_multiple_of,
                )
            output["labels"] = tensor_pad(
                labels,
                padding_value=-100,
                padding_side="right",
                pad_to_multiple_of=self.pad_to_multiple_of,
            )

        return output


@dataclass
class CollatorFactoryWithLLMSFT(DataCollatorMixin):
    max_seq_length: int
    pad_id: int
    completion_only_loss: bool = True
    padding_free: bool = False
    return_position_ids: bool = True
    pad_to_multiple_of: Optional[int] = None
    return_tensors: str = "pt"

    def torch_call(self, batch_examples):
        input_ids = [torch.tensor(example["input_ids"]) for example in batch_examples]
        attention_mask = [torch.ones_like(input_ids) for input_ids in input_ids]

        if self.return_position_ids:
            if "position_ids" in batch_examples[0]:
                position_ids = [
                    torch.tensor(example["position_ids"]) for example in batch_examples
                ]
            else:
                position_ids = [torch.arange(len(ids)) for ids in input_ids]
        if "labels" in batch_examples[0]:
            labels = [torch.tensor(example["labels"]) for example in batch_examples]
        else:
            labels = [torch.tensor(example["input_ids"]) for example in batch_examples]
        if self.completion_only_loss and "completion_mask" in batch_examples[0]:
            completion_mask = [
                torch.tensor(example["completion_mask"]) for example in batch_examples
            ]
        if "assistant_masks" in batch_examples[0]:
            assistant_masks = [
                torch.tensor(example["assistant_masks"]) for example in batch_examples
            ]

        # Pad
        output = {}
        if self.padding_free:
            output["input_ids"] = torch.cat(input_ids, dim=0).unsqueeze(0)
            output["attention_mask"] = torch.cat(attention_mask, dim=0).unsqueeze(0)
            if self.return_position_ids:
                output["position_ids"] = torch.cat(position_ids, dim=0).unsqueeze(0)
            output["labels"] = torch.cat(labels, dim=0).unsqueeze(0)
            if self.completion_only_loss and "completion_mask" in batch_examples[0]:
                completion_mask = torch.cat(completion_mask, dim=0).unsqueeze(0)
                output["labels"][completion_mask == 0] = -100
            if "assistant_masks" in batch_examples[0]:
                assistant_masks = torch.cat(assistant_masks, dim=0).unsqueeze(0)
                output["labels"][assistant_masks == 0] = -100

        else:
            output["input_ids"] = tensor_pad(
                input_ids,
                padding_value=self.pad_id,
                padding_side="right",
                pad_to_multiple_of=self.pad_to_multiple_of,
            )
            output["attention_mask"] = tensor_pad(
                attention_mask,
                padding_value=0,
                padding_side="right",
                pad_to_multiple_of=self.pad_to_multiple_of,
            )
            if self.return_position_ids:
                output["position_ids"] = tensor_pad(
                    position_ids,
                    padding_value=0,
                    padding_side="right",
                    pad_to_multiple_of=self.pad_to_multiple_of,
                )
            output["labels"] = tensor_pad(
                labels,
                padding_value=-100,
                padding_side="right",
                pad_to_multiple_of=self.pad_to_multiple_of,
            )
            if self.completion_only_loss and "completion_mask" in batch_examples[0]:
                completion_mask = tensor_pad(
                    completion_mask,
                    padding_value=0,
                    padding_side="right",
                    pad_to_multiple_of=self.pad_to_multiple_of,
                )
                output["labels"][
                    completion_mask == 0
                ] = -100  # mask everything that is not in the completion
            if "assistant_masks" in batch_examples[0]:
                assistant_masks = tensor_pad(
                    assistant_masks,
                    padding_value=0,
                    padding_side="right",
                    pad_to_multiple_of=self.pad_to_multiple_of,
                )
                output["labels"][assistant_masks == 0] = -100
        return output
