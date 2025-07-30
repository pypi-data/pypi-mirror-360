# -*- coding: utf-8 -*-
# @Time   : 2024/08/30 10:24
# @Author : zip
# @Moto   : Knowledge comes from decomposition

from __future__ import absolute_import, division, print_function

import logging
import os
from collections import defaultdict
from typing import Any, Dict, List, Literal, Optional, Union

import numpy as np
import torch
from prettytable import PrettyTable
from transformers.trainer import (
    EvalPrediction,  # type: ignore
    OptimizerNames,  # type: ignore
    Trainer,
    TrainerCallback,  # type: ignore
    nested_concat,  # type: ignore
    nested_detach,  # type: ignore
)
from trl import SFTTrainer

from scarabs.nova.component.args_factory import TaskArguments
from scarabs.nova.component.collator_factory import CollatorFactoryWithLLMPretrain
from scarabs.nova.component.data_factory import (
    DataFactoryWithLLMPretrain,
    DataFactoryWithLLMSFT,
)
from scarabs.nova.utils import AutoModelForCausalLM, AutoTokenizer, set_color

logger = logging.getLogger(__name__)
PREFIX_CHECKPOINT_DIR = "checkpoint"


class PrettyTablePrinterCallback(TrainerCallback):
    """
    A bare [`TrainerCallback`] that just PrettyTable the logs.
    """

    def on_log(self, args, state, control, logs, **kwargs):
        _ = logs.pop("total_flos", None)
        _res = PrettyTable()
        _res.field_names = list(logs.keys())
        _res.add_row(logs.values())
        if state.is_local_process_zero:
            logger.info(set_color(f"\n{_res}", "pink"))


# EvalData Early stop callback function
class EarlyStoppingByEvalDataCallback(TrainerCallback):
    """Determine whether to stop early based on evaluation data
    early_stopping_patience: Judgment frequency，
    early_stopping_threshold: Difference, stop if the condition is not met once within the number of judgments
    """

    def __init__(
        self,
        early_stopping_patience: int = 10,
        early_stopping_threshold: Optional[float] = 1e-7,
    ):
        self.early_stopping_patience = early_stopping_patience
        self.early_stopping_threshold = early_stopping_threshold
        # early_stopping_patience_counter denotes the number of times validation metrics failed to improve.
        self.early_stopping_patience_counter = 0

    def check_metric_value(self, args, state, control, metric_value):
        # best_metric is set by code for load_best_model
        operator = np.greater if args.greater_is_better else np.less
        if state.best_metric is None or (
            operator(metric_value, state.best_metric)
            and abs(metric_value - state.best_metric) > self.early_stopping_threshold
        ):
            self.early_stopping_patience_counter = 0
        else:
            self.early_stopping_patience_counter += 1

    def on_train_begin(self, args, state, control, **kwargs):
        # assert (
        #     args.load_best_model_at_end
        # ), "EarlyStoppingCallback requires load_best_model_at_end = True"
        # assert (
        #     args.metric_for_best_model is not None
        # ), "EarlyStoppingCallback requires metric_for_best_model is defined"
        # assert (
        #     args.evaluation_strategy != IntervalStrategy.NO
        # ), "EarlyStoppingCallback requires IntervalStrategy of steps or epoch"
        pass

    def on_evaluate(self, args, state, control, metrics, **kwargs):
        metric_to_check = args.metric_for_best_model
        # if not metric_to_check.startswith("eval_"):
        #     metric_to_check = f"eval_{metric_to_check}"
        metric_value = metrics.get(metric_to_check)

        if metric_value is None:
            logger.warning(
                f"early stopping required metric_for_best_model, but did not find {metric_to_check} so early stopping"
                " is disabled"
            )
            return

        self.check_metric_value(args, state, control, metric_value)
        if self.early_stopping_patience_counter >= self.early_stopping_patience:
            control.should_training_stop = True


# TrainData Early stop callback function
class EarlyStoppingByTrainDataCallback(TrainerCallback):
    """Determine whether to stop early based on train data
    early_stopping_patience: Judgment frequency，
    early_stopping_threshold: Difference, stop if the condition is not met once within the number of judgments
    """

    def __init__(
        self,
        early_stopping_patience: int = 10,
        early_stopping_threshold: Optional[float] = 1e-7,
    ):
        self.early_stopping_patience = early_stopping_patience
        self.early_stopping_threshold = early_stopping_threshold
        # early_stopping_patience_counter denotes the number of times validation metrics failed to improve.
        self.early_stopping_patience_counter = 0

    def check_metric_value(self, args, state, control, metric_value):
        # best_metric is set by code for load_best_model
        operator = np.greater if args.greater_is_better else np.less
        if state.best_metric is None or (
            operator(metric_value, state.best_metric)
            and abs(metric_value - state.best_metric) > self.early_stopping_threshold
        ):
            self.early_stopping_patience_counter = 0
        else:
            self.early_stopping_patience_counter += 1

    def on_train_begin(self, args, state, control, **kwargs):
        # assert args.load_best_model_at_end, "EarlyStoppingCallback requires load_best_model_at_end = True"
        # assert (
        #     args.metric_for_best_model is not None
        # ), "EarlyStoppingCallback requires metric_for_best_model is defined"
        # assert (
        #     args.evaluation_strategy != IntervalStrategy.NO
        # ), "EarlyStoppingCallback requires IntervalStrategy of steps or epoch"
        pass

    def on_evaluate(self, args, state, control, metrics, **kwargs):
        metric_to_check = args.metric_for_best_model
        # if not metric_to_check.startswith("eval_"):
        #     metric_to_check = f"eval_{metric_to_check}"
        metric_value = metrics.get(metric_to_check)

        if metric_value is None:
            logger.warning(
                f"early stopping required metric_for_best_model, but did not find {metric_to_check} so early stopping"
                " is disabled"
            )
            return

        self.check_metric_value(args, state, control, metric_value)
        if self.early_stopping_patience_counter >= self.early_stopping_patience:
            control.should_training_stop = True


# Tabular
class TrainerFactoryWithTabular(Trainer):
    def __init__(
        self,
        model=None,
        args=None,
        data_collator=None,
        train_dataset=None,
        eval_dataset=None,
        processing_class=None,
        model_init=None,
        compute_loss_func=None,
        compute_metrics=None,
        callbacks=None,
        optimizers=(None, None),
        optimizer_cls_and_kwargs=None,
        preprocess_logits_for_metrics=None,
    ):
        super().__init__(
            model,
            args,
            data_collator,
            train_dataset,
            eval_dataset,
            processing_class,
            model_init,
            compute_loss_func,
            compute_metrics,
            callbacks,
            optimizers,
            optimizer_cls_and_kwargs,
            preprocess_logits_for_metrics,
        )
        self._stored_metrics = defaultdict(lambda: defaultdict(list))

    def store_y_and_preds(
        self, labels, preds, train_eval: Literal["train", "eval"] = "train"
    ) -> None:
        """收集模型预测结果和真实标签，用于评估"""
        self._stored_metrics[train_eval]["labels"].extend(labels)
        self._stored_metrics[train_eval]["preds"].extend(preds)

        if train_eval == "train":
            if len(self._stored_metrics[train_eval]["labels"]) > 100000:
                self._stored_metrics[train_eval]["labels"] = self._stored_metrics[
                    train_eval
                ]["labels"][-100000:]
                self._stored_metrics[train_eval]["preds"] = self._stored_metrics[
                    train_eval
                ]["preds"][-100000:]

    def _compute_metrics(self, logits, labels):
        if logits is not None:
            self.all_preds = (
                logits
                if self.all_preds is None
                else nested_concat(self.all_preds, logits, padding_index=-100)
            )
            if self.all_preds is not None and len(self.all_preds) > 100000:
                self.all_preds = self.all_preds[-100000:]
        if labels is not None:
            self.all_labels = (
                labels
                if self.all_labels is None
                else nested_concat(self.all_labels, labels, padding_index=-100)
            )
            if self.all_labels is not None and len(self.all_labels) > 100000:
                self.all_labels = self.all_labels[-100000:]

    def training_step(
        self,
        model: torch.nn.Module,
        inputs: Dict[str, Union[torch.Tensor, Any]],
        num_items_in_batch=None,
    ) -> torch.Tensor:
        """Module can be modified, and different training modules need to be designed according to different requirements"""
        has_labels = (
            False
            if len(self.label_names) == 0
            else all(inputs.get(k) is not None for k in self.label_names)
        )

        model.train()
        inputs = self._prepare_inputs(inputs)

        # labels may be popped when computing the loss (label smoothing for instance) so we grab them first.
        if has_labels:
            labels = nested_detach(tuple(inputs.get(name) for name in self.label_names))
            if len(labels) == 1:
                labels = labels[0]
        else:
            labels = None

        with self.compute_loss_context_manager():
            out = self.compute_loss(
                model,
                inputs,
                return_outputs=True,
                num_items_in_batch=num_items_in_batch,
            )

            if isinstance(out, tuple):
                loss, outputs = out
            else:
                loss, outputs = out, None

        del inputs

        if isinstance(outputs, dict):
            outputs = tuple(
                v
                for k, v in outputs.items()
                if k not in ["loss"]  # type: ignore
            )
        elif isinstance(outputs, tuple):
            outputs = outputs[1:]

        if outputs is not None:
            logits = nested_detach(outputs)
            if len(logits) == 1:
                logits = logits[0]

        kwargs = {}

        # For LOMO optimizers you need to explicitly use the learnign rate
        if self.args.optim in [OptimizerNames.LOMO, OptimizerNames.ADALOMO]:
            kwargs["learning_rate"] = self._get_learning_rate()

        if self.args.n_gpu > 1:
            loss = loss.mean()  # type: ignore

        self.accelerator.backward(loss, **kwargs)

        # 加入预测值和真实值， 用于后续评估
        if labels is not None and logits is not None:
            self.store_y_and_preds(labels, logits, train_eval="train")

        return loss.detach() / self.args.gradient_accumulation_steps

    def prediction_step(
        self,
        model: torch.nn.Module,
        inputs: Dict[str, Union[torch.Tensor, Any]],
        prediction_loss_only: bool,
        ignore_keys: Optional[List[str]] = None,
    ):
        """The module can be modified, and different prediction modules need to be designed according to different requirements"""
        has_labels = (
            False
            if len(self.label_names) == 0
            else all(inputs.get(k) is not None for k in self.label_names)
        )

        inputs = self._prepare_inputs(inputs)
        if ignore_keys is None:
            if hasattr(self.model, "config"):
                ignore_keys = getattr(
                    self.model.config,  # type: ignore
                    "keys_to_ignore_at_inference",
                    [],
                )
            else:
                ignore_keys = []

        # labels may be popped when computing the loss (label smoothing for instance) so we grab them first.
        if has_labels:
            labels = nested_detach(tuple(inputs.get(name) for name in self.label_names))
            if len(labels) == 1:
                labels = labels[0]
        else:
            labels = None

        with torch.no_grad():
            if has_labels:
                with self.compute_loss_context_manager():
                    loss, outputs = self.compute_loss(
                        model, inputs, return_outputs=True
                    )

                del inputs

                loss = loss.mean().detach()

                if isinstance(outputs, dict):
                    logits = tuple(
                        v  # type: ignore
                        for k, v in outputs.items()
                        if k not in ignore_keys + ["loss"]  # type: ignore
                    )
                else:
                    logits = outputs[1:]

            else:
                loss = None
                with self.compute_loss_context_manager():
                    outputs = model(**inputs)

                del inputs

                if isinstance(outputs, dict):
                    logits = tuple(
                        v for k, v in outputs.items() if k not in ignore_keys
                    )
                else:
                    logits = outputs
                # TODO: this needs to be fixed and made cleaner later.
                if self.args.past_index >= 0:
                    self._past = outputs[self.args.past_index - 1]

        if prediction_loss_only:
            return (loss, None, None)

        logits = nested_detach(logits)
        if len(logits) == 1:
            logits = logits[0]

        # 加入预测值和真实值， 用于后续评估
        if labels is not None and logits is not None:
            self.store_y_and_preds(labels, logits, train_eval="eval")

        return (loss, logits, labels)

    def compute_loss(
        self, model, inputs, return_outputs=False, num_items_in_batch=None
    ):
        """
        How the loss is computed by Trainer. By default, all models return the loss in the first element.

        Subclass and override for custom behavior.
        """
        if self.model_accepts_loss_kwargs:
            loss_kwargs = {}
            if num_items_in_batch is not None:
                loss_kwargs["num_items_in_batch"] = num_items_in_batch
            inputs = {**inputs, **loss_kwargs}
        outputs = model(**inputs)

        # Save past state if it exists
        # TODO: this needs to be fixed and made cleaner later.
        if self.args.past_index >= 0:
            self._past = outputs[self.args.past_index]

        if isinstance(outputs, dict) and "loss" not in outputs:
            raise ValueError(
                "The model did not return a loss from the inputs, only the following keys: "
                f"{','.join(outputs.keys())}. For reference, the inputs it received are {','.join(inputs.keys())}."
            )
        # We don't use .loss here since the model may return tuples instead of ModelOutput.
        loss = outputs["loss"] if isinstance(outputs, dict) else outputs[0]

        if self.args.average_tokens_across_devices and self.model_accepts_loss_kwargs:
            loss *= self.accelerator.num_processes

        return (loss, outputs) if return_outputs else loss

    def log(self, logs: dict[str, float], start_time: Optional[float] = None) -> None:
        """
        Log `logs` on the various objects watching training, including stored metrics.

        Args:
            logs (`dict[str, float]`):
                The values to log.
            start_time (`float` or `None`, *optional*, defaults to `None`):
                Start time of the training.
        """
        # logs either has 'loss' or 'eval_loss'
        train_eval = "train" if "loss" in logs else "eval"
        # 基于收集的预测值和真实值，计算指标
        labels = self._stored_metrics[train_eval]["labels"]
        preds = self._stored_metrics[train_eval]["preds"]
        if len(labels) > 0 and len(preds) > 0 and len(labels) == len(preds):
            logs["labels_mean"] = torch.tensor(labels).mean().item()
            logs["preds_mean"] = torch.tensor(preds).mean().item()
            logs["sample_count"] = len(labels)
            if train_eval == "train":
                metrics = self.compute_metrics(
                    EvalPrediction(predictions=preds, label_ids=labels)  # type: ignore
                )
                metrics = {k: float(v) for k, v in metrics.items()}
                logs.update(metrics)
            del self._stored_metrics[train_eval]

        return super().log(logs, start_time)

    def _train_determine_best_metric(self, metrics, trial):
        """
        Determine if the model should be saved based on the evaluation metrics.
        If args.metric_for_best_model is not set, the loss is used.

        Returns:
            bool: True if a new best metric was found, else False
        """
        is_new_best_metric = False

        if self.args.metric_for_best_model is not None:
            metric_to_check = self.args.metric_for_best_model

            if metric_to_check in metrics:
                metric_value = metrics[metric_to_check]
            else:
                return is_new_best_metric

            operator = np.greater if self.args.greater_is_better else np.less

            if self.state.best_metric is None:
                self.state.best_metric = (
                    float("-inf") if self.args.greater_is_better else float("inf")
                )

            if operator(metric_value, self.state.best_metric):
                run_dir = self._get_output_dir(trial=trial)
                checkpoint_folder = f"{PREFIX_CHECKPOINT_DIR}-{self.state.global_step}"
                output_dir = os.path.join(run_dir, checkpoint_folder)  # type: ignore

                self.state.best_metric = metric_value
                self.state.best_model_checkpoint = output_dir

                is_new_best_metric = True

        return is_new_best_metric


class TrainerFactoryWithLLMPretrain(Trainer):
    def __init__(
        self,
        args: TaskArguments,
        model=None,
        data_collator=None,
        train_dataset=None,
        eval_dataset=None,
        processing_class=None,
        model_init=None,
        compute_loss_func=None,
        compute_metrics=None,
        callbacks=None,
        optimizers=(None, None),
        optimizer_cls_and_kwargs=None,
        preprocess_logits_for_metrics=None,
    ):
        if model is None and args.model_tokenizer_config_name_or_path is None:
            raise ValueError(
                "model cannot be None or model_tokenizer_config_name_or_path not be set"
            )
        if model is None:
            model = args.model_tokenizer_config_name_or_path
        model_id = model if isinstance(model, str) else model.config._name_or_path  # type: ignore

        # tokenizer
        if processing_class is None:
            processing_class = AutoTokenizer.from_pretrained(model_id)

        # data
        DataFactory = DataFactoryWithLLMPretrain(args, processing_class)  # type: ignore

        if train_dataset is None and args.train_file:
            train_dataset = DataFactory.prepare_train_dataset()
        if eval_dataset is None and args.valid_file:
            eval_dataset = DataFactory.prepare_valid_dataset()

        # model
        if isinstance(model, str):
            model = AutoModelForCausalLM.from_pretrained(model)

        # data collator
        data_collator = CollatorFactoryWithLLMPretrain(pad_id=DataFactory.pad_id)

        super().__init__(
            model=model,
            args=args,
            data_collator=data_collator,
            train_dataset=train_dataset,  # type: ignore
            eval_dataset=eval_dataset,
            processing_class=processing_class,
            model_init=model_init,
            compute_loss_func=compute_loss_func,
            compute_metrics=compute_metrics,
            callbacks=callbacks,
            optimizers=optimizers,
            optimizer_cls_and_kwargs=optimizer_cls_and_kwargs,
            preprocess_logits_for_metrics=preprocess_logits_for_metrics,
        )


class TrainerFactoryWithLLMSFT(SFTTrainer):
    def __init__(
        self,
        args: TaskArguments,
        model=None,
        data_collator=None,
        train_dataset=None,
        eval_dataset=None,
        processing_class=None,
        compute_loss_func=None,
        compute_metrics=None,
        callbacks=None,
        optimizers=(None, None),
        optimizer_cls_and_kwargs=None,
        preprocess_logits_for_metrics=None,
        peft_config=None,
        formatting_func=None,
    ):
        if model is None:
            model = args.model_tokenizer_config_name_or_path
        if model is None:
            raise ValueError("model cannot be None not be set")

        # Data
        DataFactory = DataFactoryWithLLMSFT(args)  # type: ignore

        if train_dataset is None and args.train_file:
            train_dataset = DataFactory.prepare_train_dataset()
        if eval_dataset is None and args.valid_file:
            eval_dataset = DataFactory.prepare_valid_dataset()

        # Args
        from trl import SFTConfig

        if not isinstance(args, SFTConfig):
            dict_args = args.to_dict()
            dict_args["hub_token"] = args.hub_token  # to_dict hides the hub_token
            dict_args.pop("push_to_hub_token")

            dict_args.pop("task_name_or_path")
            dict_args.pop("data_format")
            dict_args.pop("train_file")
            dict_args.pop("valid_file")
            dict_args.pop("test_file")
            dict_args.pop("preprocessing_num_workers")
            dict_args.pop("pretrain_concat_text")
            dict_args.pop("load_resume_from_checkpoint")
            dict_args.pop("incremental_resume_from_checkpoint")
            dict_args.pop("model_tokenizer_config_name_or_path")
            dict_args.pop("early_stopping_patience")
            dict_args.pop("early_stopping_threshold")

            args = SFTConfig(**dict_args)  # type:ignore

        super().__init__(
            model=model,
            args=args,
            data_collator=data_collator,
            train_dataset=train_dataset,  # type: ignore
            eval_dataset=eval_dataset,
            processing_class=processing_class,
            compute_loss_func=compute_loss_func,
            compute_metrics=compute_metrics,
            callbacks=callbacks,  # type: ignore
            optimizers=optimizers,
            optimizer_cls_and_kwargs=optimizer_cls_and_kwargs,
            preprocess_logits_for_metrics=preprocess_logits_for_metrics,
            peft_config=peft_config,
            formatting_func=formatting_func,
        )
