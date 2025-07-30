# -*- coding: utf-8 -*-
# @Time   : 2024/07/30 10:24
# @Author : zip
# @Moto   : Knowledge comes from decomposition

from __future__ import absolute_import, division, print_function

import logging
import os
import random
import warnings
from typing import List, Optional

import datasets
import evaluate
import numpy as np
import torch
import transformers
from torchinfo import summary
from tqdm import tqdm

from scarabs.nova import (
    CollatorFactoryWithTabular,
    DataFactoryWithTabular,
    EarlyStoppingByEvalDataCallback,
    ModelFactoryWithTabular,
    PretrainedConfig,
    PrettyTablePrinterCallback,
    TaskArguments,
    TrainerFactoryWithTabular,
    set_color,
    set_log,
    set_seed,
)

logger = logging.getLogger(__name__)
tqdm.pandas()
warnings.filterwarnings("ignore")


# Tabular ctr
class TaskFactoryWithTabularCtr:
    TASK = "TaskFactory Tabular Ctr"

    def __init__(
        self,
        args: Optional[TaskArguments] = None,
        config: Optional[PretrainedConfig] = None,
        metrics: List = ["metrics/roc_auc"],
    ):
        self.args = args
        self.config = config

        if self.args is not None:  # Setup runtimes
            self._seed(self.args)
            self._metric = evaluate.combine(
                [
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), "nova", _)
                    for _ in metrics
                ]
            )

        if self.args is not None:
            self.task_name_or_path = self.args.task_name_or_path
            os.makedirs(self.task_name_or_path, exist_ok=True)
            set_log(self.task_name_or_path)

    def _seed(self, training_args: TaskArguments):
        # Set seed before initializing model.
        set_seed(training_args.seed)
        random.seed(training_args.seed)
        os.environ["PYTHONHASHSEED"] = str(training_args.seed)
        np.random.seed(training_args.seed)
        torch.manual_seed(training_args.seed)
        torch.cuda.manual_seed(training_args.seed)
        torch.backends.cudnn.deterministic = True

        cpu_count = os.cpu_count()
        if cpu_count is not None:
            torch.set_num_threads(cpu_count // 2)

    def _logging_summary(self, training_args: TaskArguments):
        if training_args.should_log:
            # The default of training_args.log_level is passive, so we set log level at info here to have that default.
            transformers.utils.logging.set_verbosity_info()

        log_level = training_args.get_process_log_level()
        datasets.utils.logging.set_verbosity(log_level)
        transformers.utils.logging.set_verbosity(log_level)
        transformers.utils.logging.enable_default_handler()
        transformers.utils.logging.enable_explicit_format()

        # Log on each process the small summary:
        logger.warning(
            f"Process rank: {training_args.local_rank}, device: {training_args.device}, n_gpu: {training_args.n_gpu}, "
            + f"distributed training: {training_args.parallel_mode.value == 'distributed'}, 16-bits training: {training_args.fp16}"
        )

        # Set the verbosity to info of the Transformers logger (on main process only):
        logger.info(f"Training/evaluation parameters {training_args}")

    def create_feature2meta_in_config(self):
        if self.args is None:
            raise ValueError("task_args must be not None")
        if self.config is None:
            raise ValueError("config must be not None")

        # data factory
        DataFactory = DataFactoryWithTabular(args=self.args, config=self.config)
        DataFactory.create_feature2meta()
        DataFactory.save_feature2meta()

    def train(self, model=None, ds_train=None, ds_eval=None):
        # runtimes
        if self.config is None:
            raise ValueError("config must be not None")
        if self.args is None:
            raise ValueError("args must be not None")

        if model is None:
            raise ValueError("model must be not None")

        if self.args.logging_dir is not None:
            self.args.logging_dir = os.path.join(
                self.args.task_name_or_path, self.args.logging_dir
            )
        if self.args.output_dir is not None:
            self.args.output_dir = os.path.join(
                self.args.task_name_or_path, self.args.output_dir
            )

        # data factory
        DataFactory = DataFactoryWithTabular(args=self.args, config=self.config)
        DataFactory.load_feature2meta()
        if ds_train is None and self.args.train_file:
            ds_train = DataFactory.prepare_train_dataset()
            logger.info(
                set_color("✅  <<<<<<<<<<<<< ds_train prepare success ", "pink")
            )
        if ds_train is None:
            raise ValueError("ds_train or data_args.train_file should ")

        if ds_eval is None and self.args.valid_file:
            ds_eval = DataFactory.prepare_valid_dataset()
            logger.info(set_color("✅  <<<<<<<<<<<<< ds_eval prepare success ", "pink"))
        if self.args.do_eval:
            if ds_eval is None:
                raise ValueError("ds_eval or data_args.valid_file should ")

        # model factory
        ModelFactory = ModelFactoryWithTabular(model=model)
        model = ModelFactory.handle_with_train(
            self.args.load_resume_from_checkpoint,
            self.args.incremental_resume_from_checkpoint,
        )
        if model is None:
            raise ValueError("model must be not None")
        logger.info(set_color("✅  <<<<<<<<<<<<< model prepare success ", "pink"))

        # collator factory
        CollatorFactory = CollatorFactoryWithTabular(
            label_names=self.args.label_names,  # type: ignore
            feature2meta=DataFactory.FT.feature2meta,
        )

        # compute metrics
        def compute_metrics_fn(eval_pred):
            logits, labels = eval_pred
            res = self._metric.compute(prediction_scores=logits, references=labels)
            return res

        # train
        self._logging_summary(self.args)
        trainer = TrainerFactoryWithTabular(
            model=model,
            args=self.args,
            train_dataset=ds_train,  # type: ignore
            eval_dataset=ds_eval,  # type: ignore
            data_collator=CollatorFactory,  # data collator
            compute_metrics=compute_metrics_fn,  # type: ignore
            callbacks=[
                PrettyTablePrinterCallback,  # type: ignore
                EarlyStoppingByEvalDataCallback(
                    self.args.early_stopping_patience,
                    self.args.early_stopping_threshold,
                ),
            ],
        )

        # model show and data show
        if trainer.train_dataset is not None and trainer.data_collator is not None:
            input_data = trainer.train_dataset[0]
            input_data = dict(trainer.data_collator([input_data]))  # type: ignore
            logger.info(set_color("🔍 >>>>>>>>>>>>> Data Check", "pink"))
            logger.info(set_color(f"{input_data}", "pink"))
            logger.info(set_color("🔍 <<<<<<<<<<<<< Data Check", "pink"))
            device = next(trainer.model.parameters()).device  # type: ignore
            input_data = {key: value.to(device) for key, value in input_data.items()}
            summary(
                trainer.model,  # type: ignore
                depth=20,
                input_data=input_data,  # type: ignore
            )

        # Training
        if self.args.do_train:
            logger.info(set_color("🚀 *** Training 🟢 🟢 🟢 ***", "pink"))

            train_result = trainer.train()

            trainer.save_model()  # Saves the tokenizer too for easy upload
            metrics = train_result.metrics
            metrics["train_samples"] = len(ds_train)  # type: ignore
            trainer.log_metrics("train", metrics)
            trainer.save_metrics("train", metrics)
            trainer.save_state()

        # Evaluation
        if self.args.do_eval:
            logger.info(set_color("🚀 *** Evaluate 🟢 🟢 🟢 ***", "pink"))
            metrics = trainer.evaluate(ds_eval)  # type: ignore
            metrics["eval_samples"] = len(ds_eval)  # type: ignore
            trainer.log_metrics("eval", metrics)
            trainer.save_metrics("eval", metrics)

    def eval(self, model=None, ds_eval=None):
        # runtimes
        if self.config is None:
            raise ValueError("config must be not None")
        if self.args is None:
            raise ValueError("args must be not None")

        if model is None:
            raise ValueError("model must be not None")

        if self.args.logging_dir is not None:
            self.args.logging_dir = os.path.join(
                self.args.task_name_or_path, self.args.logging_dir
            )
        if self.args.output_dir is not None:
            self.args.output_dir = os.path.join(
                self.args.task_name_or_path, self.args.output_dir
            )

        # data factory
        DataFactory = DataFactoryWithTabular(args=self.args, config=self.config)
        DataFactory.load_feature2meta()

        if ds_eval is None and self.args.valid_file:
            ds_eval = DataFactory.prepare_valid_dataset()
        if ds_eval is None:
            raise ValueError("ds_eval or data_args.valid_file should ")
        logger.info(set_color("✅  <<<<<<<<<<<<< eval data prepare success ", "pink"))

        # model factory
        if self.args.load_resume_from_checkpoint is None:
            raise ValueError("load_resume_from_checkpoint should ")

        ModelFactory = ModelFactoryWithTabular(model=model)
        model = ModelFactory.handle_with_inference(
            self.args.load_resume_from_checkpoint
        )
        if model is None:
            raise ValueError("model must be not None")
        logger.info(set_color("✅  <<<<<<<<<<<<< model prepare success ", "pink"))

        # collator factory
        CollatorFactory = CollatorFactoryWithTabular(
            label_names=self.args.label_names,  # type: ignore
            feature2meta=DataFactory.FT.feature2meta,
        )
        logger.info(set_color("✅  <<<<<<<<<<<<< collator prepare success ", "pink"))

        # compute metrics
        def compute_metrics_fn(eval_pred):
            logits, labels = eval_pred
            res = self._metric.compute(prediction_scores=logits, references=labels)
            return res

        # Traner
        trainer = TrainerFactoryWithTabular(
            model=model,
            args=self.args,
            data_collator=CollatorFactory,  # data collator
            compute_metrics=compute_metrics_fn,  # type: ignore
        )

        # model show and data show
        if trainer.train_dataset is not None and trainer.data_collator is not None:
            _data_show = trainer.train_dataset[0]
            logger.info(set_color("🔍 >>>>>>>>>>>>> Data Check", "pink"))
            logger.info(set_color(f"{_data_show}", "pink"))
            logger.info(set_color("🔍 <<<<<<<<<<<<< Data Check", "pink"))
            summary(
                model,
                depth=20,
                input_data=trainer.data_collator([_data_show]),  # type: ignore
            )

        # Evaluation
        logger.info(set_color("🚀 *** Evaluate 🟢 🟢 🟢 ***", "pink"))
        metrics = trainer.evaluate(ds_eval)  # type: ignore
        metrics["eval_samples"] = len(ds_eval)  # type: ignore
        trainer.log_metrics("eval", metrics)
        trainer.save_metrics("eval", metrics)

    def inference_with_load_model(self, from_checkpoint, modelFunc):
        # load data processing
        config = PretrainedConfig.from_pretrained(from_checkpoint)
        DataFactory = DataFactoryWithTabular(args=None, config=config)
        DataFactory.load_feature2meta()

        ModelFactory = ModelFactoryWithTabular(model=modelFunc(config))
        self.model = ModelFactory.handle_with_inference(from_checkpoint)

        # set
        def get_best_device():
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                if device_count > 1:  # 在多个GPU的情况下，选择空闲显存最大的GPU
                    max_memory = 0
                    best_device_id = 0
                    for i in range(device_count):
                        memory = torch.cuda.get_device_properties(
                            i
                        ).total_memory - torch.cuda.memory_allocated(i)
                        if memory > max_memory:
                            max_memory = memory
                            best_device_id = i
                    return torch.device(f"cuda:{best_device_id}")
                else:
                    return torch.device("cuda:0")
            else:
                return torch.device("cpu")

        self.device = get_best_device()

        self.model.to(self.device)  # type: ignore
        self.model.eval()
        self.FeatureMeta = DataFactory.FT

        logger.info(
            set_color(f"model load success, model in device: {self.device}", "pink")
        )

    def inference(self, X):
        with torch.no_grad():
            X = self.FeatureMeta.handle(X)
            for name in X:
                X[name] = torch.tensor([X[name]], dtype=torch.long).to(self.device)  # type: ignore
            return self.model(**X)

    def batch_inference(self, batch_X):
        for _ in range(len(batch_X)):
            batch_X[_] = self.FeatureMeta.handle(batch_X[_])

        X = {}
        for _ in range(len(batch_X)):
            for name in batch_X[_]:
                if name not in X:
                    X[name] = []
                X[name].append(batch_X[_][name])

        with torch.no_grad():
            for name in X:
                X[name] = torch.tensor(X[name], dtype=torch.long).to(self.device)  # type: ignore
            return self.model(**X)


class TaskFactoryWithLLM:
    TASK = "TaskFactory LLM"

    def __init__(
        self,
        args: Optional[TaskArguments] = None,
    ):
        self.args = args

        if self.args is not None:  # Setup runtimes
            self._seed(self.args)

        if self.args is not None:
            self.task_name_or_path = self.args.task_name_or_path
            os.makedirs(self.task_name_or_path, exist_ok=True)
            set_log(self.task_name_or_path)

    def _seed(self, training_args: TaskArguments):
        # Set seed before initializing model.
        set_seed(training_args.seed)
        random.seed(training_args.seed)
        os.environ["PYTHONHASHSEED"] = str(training_args.seed)
        np.random.seed(training_args.seed)
        torch.manual_seed(training_args.seed)
        torch.cuda.manual_seed(training_args.seed)
        torch.backends.cudnn.deterministic = True

        cpu_count = os.cpu_count()
        if cpu_count is not None:
            torch.set_num_threads(cpu_count // 2)

    def _logging_summary(self, training_args: TaskArguments):
        if training_args.should_log:
            # The default of training_args.log_level is passive, so we set log level at info here to have that default.
            transformers.utils.logging.set_verbosity_info()

        log_level = training_args.get_process_log_level()
        datasets.utils.logging.set_verbosity(log_level)
        transformers.utils.logging.set_verbosity(log_level)
        transformers.utils.logging.enable_default_handler()
        transformers.utils.logging.enable_explicit_format()

        # Log on each process the small summary:
        logger.warning(
            f"Process rank: {training_args.local_rank}, device: {training_args.device}, n_gpu: {training_args.n_gpu}, "
            + f"distributed training: {training_args.parallel_mode.value == 'distributed'}, 16-bits training: {training_args.fp16}"
        )

        # Set the verbosity to info of the Transformers logger (on main process only):
        logger.info(f"Training/evaluation parameters {training_args}")

    def train(
        self,
        TrainFunc,
        model=None,
        tokenizer=None,
        ds_train=None,
        ds_eval=None,
        data_collator=None,
        **kwargs,
    ):
        # runtimes
        if self.args is None:
            raise ValueError("args must be not None")

        if self.args.logging_dir is not None:
            self.args.logging_dir = os.path.join(
                self.args.task_name_or_path, self.args.logging_dir
            )
        if self.args.output_dir is not None:
            self.args.output_dir = os.path.join(
                self.args.task_name_or_path, self.args.output_dir
            )

        # train
        self._logging_summary(self.args)
        trainer = TrainFunc(
            args=self.args,
            model=model,
            processing_class=tokenizer,
            train_dataset=ds_train,
            eval_dataset=ds_eval,
            data_collator=data_collator,
            callbacks=[
                PrettyTablePrinterCallback,
                EarlyStoppingByEvalDataCallback(
                    self.args.early_stopping_patience,
                    self.args.early_stopping_threshold,
                ),
            ],
            **kwargs,
        )
        # model show and data show
        if trainer.train_dataset is not None and trainer.data_collator is not None:
            # ds = trainer.get_train_dataloader()
            # input_data = None
            # for line in ds:
            #     input_data = line
            #     break

            input_data = {"input_ids": trainer.train_dataset[0]["input_ids"]}

            input_data = dict(trainer.data_collator([input_data]))
            logger.info(set_color("🔍 >>>>>>>>>>>>> Data Check", "pink"))
            logger.info(set_color(f"{input_data}", "pink"))
            logger.info(set_color("🔍 <<<<<<<<<<<<< Data Check", "pink"))

            device = next(trainer.model.parameters()).device
            input_data = {key: value.to(device) for key, value in input_data.items()}
            summary(
                trainer.model,
                depth=20,
                input_data=input_data,  # type: ignore
            )

        # Training
        if self.args.do_train:
            logger.info(set_color("🚀 *** Training 🟢 🟢 🟢 ***", "pink"))

            train_result = trainer.train()

            trainer.save_model()  # Saves the tokenizer too for easy upload
            metrics = train_result.metrics
            metrics["train_samples"] = len(trainer.train_dataset)  # type: ignore
            trainer.log_metrics("train", metrics)
            trainer.save_metrics("train", metrics)
            trainer.save_state()

        # Evaluation
        if self.args.do_eval:
            logger.info(set_color("🚀 *** Evaluate 🟢 🟢 🟢 ***", "pink"))
            metrics = trainer.evaluate(ds_eval)  # type: ignore
            metrics["eval_samples"] = len(ds_eval)  # type: ignore
            trainer.log_metrics("eval", metrics)
            trainer.save_metrics("eval", metrics)

    def inference_with_load_model(
        self,
        model_tokenizer_config_name_or_path,
        model_func,
        peft_name_or_path=None,
    ):
        from peft.peft_model import PeftModel
        from transformers import AutoTokenizer

        # load model
        self.model = model_func.from_pretrained(model_tokenizer_config_name_or_path)

        if peft_name_or_path is not None:
            self.model = PeftModel.from_pretrained(
                model=self.model, model_id=peft_name_or_path
            )

        # load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_tokenizer_config_name_or_path
        )

        # set
        def get_best_device():
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                if device_count > 1:  # 在多个GPU的情况下，选择空闲显存最大的GPU
                    max_memory = 0
                    best_device_id = 0
                    for i in range(device_count):
                        memory = torch.cuda.get_device_properties(
                            i
                        ).total_memory - torch.cuda.memory_allocated(i)
                        if memory > max_memory:
                            max_memory = memory
                            best_device_id = i
                    return torch.device(f"cuda:{best_device_id}")
                else:
                    return torch.device("cuda:0")
            else:
                return torch.device("cpu")

        self.device = get_best_device()
        self.model.to(self.device)  # type: ignore
        self.model.eval()

    def inference(self, X, max_tokens=128):
        with torch.no_grad():
            i = 0
            res = []
            tokens = [-1]
            X = self.tokenizer(X)
            if X.get("input_ids") is None or X.get("attention_mask") is None:
                return "input X is err"

            while i < max_tokens and tokens[0] != self.tokenizer.pad_token_id:
                inputs = {}
                for name in X:
                    if name not in ["input_ids", "attention_mask"]:
                        continue
                    inputs[name] = torch.tensor([X[name]], dtype=torch.long).to(
                        self.device
                    )

                output = self.model(**inputs)
                logits = output.logits
                tokens = torch.argmax(logits, dim=-1)
                tokens = tokens[0].tolist()[:-2:-1]
                X["input_ids"] = X["input_ids"] + tokens  # type: ignore
                X["attention_mask"] = X["attention_mask"] + [1]  # type: ignore
                res += tokens
                i += 1

            answer = self.tokenizer.decode(res)
            return answer
