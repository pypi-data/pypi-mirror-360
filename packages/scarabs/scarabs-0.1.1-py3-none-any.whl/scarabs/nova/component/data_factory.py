# -*- coding: utf-8 -*-
# @Time   : 2025/06/17 20:10
# @Author : zip
# @Moto   : Knowledge comes from decomposition
from __future__ import absolute_import, division, print_function

import logging
import os
from itertools import chain

from accelerate import PartialState
from datasets import (
    Dataset,
    load_dataset,
    load_from_disk,
)

from scarabs.nova.component.args_factory import TaskArguments
from scarabs.nova.utils import (
    Feature2Transformer,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
    cache_folder_decorator,
    get_files_abs_path,
    set_color,
)

logger = logging.getLogger(__name__)


class DataFactory:
    """
    1 读取数据
    2 处理数据
    """

    def __init__(self, args: TaskArguments):
        _DATA = "data"
        self.args = args

        if args is None:
            self.task_name_or_path = "encode"
        else:
            self.task_name_or_path = args.task_name_or_path

        if self.task_name_or_path is not None:
            self.ds_dir = os.path.join(self.task_name_or_path, _DATA)
            os.makedirs(self.ds_dir, exist_ok=True)
            self.ds_cache = os.path.join(self.ds_dir, "cache")

    def _read_data_files(self, files, data_format):
        if data_format not in ["text", "csv", "json", "parquet"]:
            raise ValueError(
                "❌ no data_format is provided, data_format must be (text, csv, json, parquet)"
            )
        if files is None:
            raise ValueError("❌ files should not be None")

        _files = get_files_abs_path(files)
        logger.info(set_color("ℹ️  >>>>>>>>>>>>> Data from Files", "blue"))
        for i, m in enumerate(_files):
            logger.info(set_color("📘 %d -> %s" % (i, m), "blue"))
        logger.info(set_color("ℹ️  <<<<<<<<<<<<< Data from Files", "blue"))

        # 读取数据
        _ds = load_dataset(
            data_format,
            data_files=_files,
            split="train",
            cache_dir=self.ds_cache,
        )

        if not isinstance(_ds, Dataset):
            raise ValueError(f"🔥 dataset is not a Dataset, but {type(_ds)}")
        return _ds

    def _load_from_disk(self, cache_dir):
        if cache_dir is None:
            raise ValueError("❌ cache_dir should not be None")

        _ds = load_from_disk(cache_dir, keep_in_memory=False)
        logger.warning(f"🔔 Finished loading from cache, disk: {cache_dir}")
        return _ds

    def _prepare_dataset(self, files, _process_fn, _NAME):
        _ds_cache_dir = os.path.join(self.ds_dir, _NAME)
        _data_format = self.args.data_format
        try:
            # 从 cache 中直接加载数据
            _ds = self._load_from_disk(_ds_cache_dir)
        except Exception:
            # 读取数据
            _ds = self._read_data_files(files, _data_format)

            # 处理数据
            logger.info(
                set_color(
                    f"ℹ️  before {_NAME} process dataset[0] info: {_ds[0]} \n", "pink"
                )
            )
            _ds = _process_fn(_ds)
            logger.info(
                set_color(
                    f"ℹ️  after {_NAME} process dataset[0] info: {_ds[0]} \n", "pink"
                )
            )
            _ds.save_to_disk(_ds_cache_dir)
            _ds = self._load_from_disk(_ds_cache_dir)
        return _ds

    def _sanity_check(self, ds, tokenizer):
        if ds is None or ds[0].get("input_ids") is None and tokenizer is None:
            raise ValueError(
                "❌ no dataset is no provided, tokenizer is provided, or no input_ids is provided"
            )
        tokens = ds[0]["input_ids"][:10][:-1]
        target = ds[0]["input_ids"][:10][1:]

        logger.info(set_color("🔍 >>>>>>>>>>>>> Sanity Check", "pink"))
        for t, m in zip(tokens, target):
            decoded = tokenizer.decode([t])
            logger.info(set_color("%10s: %6d -> %6d" % (repr(decoded), t, m), "pink"))
        logger.info(set_color("🔍 <<<<<<<<<<<<< Sanity Check", "pink"))

        if len(tokens) != len(target):
            raise ValueError(f"🔥 length mismatch: {len(tokens)} vs {len(target)}")

    def _ds_process_map(
        self,
        ds: Dataset,
        handle_fn,
        batched,
        batch_size,
        desc,
        num_proc,
        cache_path="cache.arrow",
    ):
        with PartialState().local_main_process_first():
            ds = ds.map(
                handle_fn,
                batched=batched,
                batch_size=batch_size,
                num_proc=num_proc,
                desc=desc,
                cache_file_name=f"{self.ds_cache}/{cache_path}",
            )
        return ds


class DataFactoryWithTabular(DataFactory):
    def __init__(self, args, config):
        super().__init__(args)
        self.config = config

    @cache_folder_decorator(cache_folder_attr="ds_cache")
    def prepare_train_dataset(self):
        _NAME = "train"
        _file = self.args.train_file
        _ds = self._prepare_dataset(_file, self._process_fn, _NAME)
        return _ds

    @cache_folder_decorator(cache_folder_attr="ds_cache")
    def prepare_valid_dataset(self):
        _NAME = "valid"
        _file = self.args.valid_file
        _ds = self._prepare_dataset(_file, self._process_fn, _NAME)
        return _ds

    @cache_folder_decorator(cache_folder_attr="ds_cache")
    def prepare_test_dataset(self):
        _NAME = "test"
        _file = self.args.test_file
        _ds = self._prepare_dataset(_file, self._process_fn, _NAME)
        return _ds

    @cache_folder_decorator(cache_folder_attr="ds_cache")
    def create_feature2meta(self):
        _files = self.args.train_file
        _data_format = self.args.data_format

        self.FT = Feature2Transformer()
        self.FT.create_and_load_meta(config=self.config)

        # 读取数据
        ds = self._read_data_files(_files, _data_format)

        valid_columns = list(self.FT.feature2meta.keys())
        ds = ds.remove_columns(
            [col for col in ds.column_names if col not in valid_columns]
        )

        # 建立元特征
        self._ds_process_map(
            ds,
            self.FT.build_meta_batch,
            True,
            10000,
            "Running FT build_meta_batch on dataset",
            1,
        )

        for item in self.FT.feature2meta.items():
            logger.info(
                set_color(f"🔍 【{item[0]}】 vocab size: {len(item[1].vocab)}", "pink")
            )

    def load_feature2meta(self):
        self.FT = Feature2Transformer()
        self.FT.create_and_load_meta(config=self.config)
        for item in self.FT.feature2meta.items():
            logger.info(
                set_color(f"🔍 【{item[0]}】 vocab size: {len(item[1].vocab)}", "pink")
            )

    def save_feature2meta(self):
        obj_dict = {}
        for name, fea in self.FT.feature2meta.items():
            obj_dict[name] = fea.__dict__
        self.config.features = obj_dict
        path = os.path.join(self.ds_dir, "meta")
        self.config.save_pretrained(os.path.join(self.ds_dir, "meta"))
        logger.info(set_color(f"👔 save feature meta in {path}", "pink"))

    def get_feature2meta(self):
        return self.FT.feature2meta

    def _process_fn(self, ds: Dataset):
        workers = self.args.preprocessing_num_workers
        label_names = [] if self.config.label_names is None else self.config.label_names

        valid_columns = list(self.FT.feature2meta.keys()) + label_names
        ds = ds.remove_columns(
            [col for col in ds.column_names if col not in valid_columns]
        )

        # 处理数据
        ds = self._ds_process_map(
            ds,
            self.FT.handle,
            False,
            None,
            "Running FT handle on dataset",
            workers,
        )

        return ds


class DataFactoryWithLLM(DataFactory):
    def __init__(
        self,
        args,
        tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast,
    ):
        super().__init__(args)

        self.tokenizer = tokenizer
        if self.tokenizer is None:
            raise ValueError("tokenizer is not initialized")

        self.pad_id = self.init_pad_id()
        self.max_seq_length = self.init_max_seq_length()

    def init_pad_id(self):
        try:
            pad_id = self.tokenizer.pad_token_id
            if pad_id is None:
                raise
        except Exception:
            logger.warning(
                f"The pad_token_id is not set. We set it to {self.tokenizer.eos_token_id}."
            )
            pad_id = self.tokenizer.eos_token_id
        pad_id = int(pad_id)  # type: ignore
        return pad_id

    def init_max_seq_length(self):
        if self.pad_id is None:
            raise ValueError("pad_token_id is not set")

        if (
            self.args.max_seq_length is None
            or self.args.max_seq_length > self.tokenizer.model_max_length
        ):
            logger.warning(
                f"The max_seq_length passed ({self.args.max_seq_length}) is larger than the maximum length for the "
                f"model ({self.tokenizer.model_max_length}). Using max_seq_length={self.tokenizer.model_max_length}."
            )
            self.args.max_seq_length = self.tokenizer.model_max_length

        max_seq_length = min(
            self.args.max_seq_length,  # type: ignore
            self.tokenizer.model_max_length,
        )
        return max_seq_length

    @cache_folder_decorator(cache_folder_attr="ds_cache")
    def prepare_train_dataset(self):
        _NAME = "train"
        _file = self.args.train_file
        _ds = self._prepare_dataset(_file, self._process_fn, _NAME)

        self._sanity_check(_ds, self.tokenizer)
        return _ds

    @cache_folder_decorator(cache_folder_attr="ds_cache")
    def prepare_valid_dataset(self):
        _NAME = "valid"
        _file = self.args.valid_file
        _ds = self._prepare_dataset(_file, self._process_fn, _NAME)

        self._sanity_check(_ds, self.tokenizer)
        return _ds

    @cache_folder_decorator(cache_folder_attr="ds_cache")
    def prepare_test_dataset(self):
        _NAME = "test"
        _file = self.args.test_file
        _ds = self._prepare_dataset(_file, self._process_fn, _NAME)

        self._sanity_check(_ds, self.tokenizer)
        return _ds

    def _process_fn(self):
        raise NotImplementedError()


class DataFactoryWithLLMPretrain(DataFactoryWithLLM):
    """your data ,data name is suffix .jsonl or .json
    {"text": "your text"}
    {"text": "your text"}
    """

    def __init__(
        self,
        args,
        tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast,
    ):
        super().__init__(args, tokenizer)

    def _tokenize_function(self, examples, template):
        # Remove empty lines
        examples["text"] = [
            line for line in examples["text"] if len(line) > 0 and not line.isspace()
        ]
        if template is not None:
            examples["text"] = [template.format(line) for line in examples["text"]]
        if self.tokenizer is None:
            raise ValueError("tokenizer is initialized")

        return self.tokenizer(examples["text"])

    def _process_fn(self, ds: Dataset, template=None):
        workers = self.args.preprocessing_num_workers
        _ds = self._ds_process_map(
            ds,
            lambda _: self._tokenize_function(_, template),
            True,
            1000,
            "Running tokenizer on dataset",
            num_proc=workers,
        )
        _ds = _ds.remove_columns(["text", "attention_mask"])

        if self.args.pretrain_concat_text:
            # Otherwise, we tokenize every text, then concatenate them together before splitting them in smaller parts.
            # Main data processing function that will concatenate all texts from our dataset and generate chunks of max_seq_length.
            def group_texts(lines):
                # Concatenate all texts.
                concatenated_examples = {
                    k: list(chain(*lines[k])) for k in lines.keys()
                }
                total_length = len(concatenated_examples[list(lines.keys())[0]])

                # We drop the small remainder, and if the total_length < max_seq_length  we exclude this batch and return an empty dict.
                # We could add padding if the model supported it instead of this drop, you can customize this part to your needs.
                total_length = (
                    total_length // self.max_seq_length
                ) * self.max_seq_length + 1

                # Split by chunks of max_len.
                result = {
                    k: [
                        t[i : i + self.max_seq_length]
                        for i in range(0, total_length, self.max_seq_length)
                    ]
                    for k, t in concatenated_examples.items()
                }

                return result

            # Note that with `batched=True`, this map processes 1,000 texts together, so group_texts throws away a
            # remainder for each of those groups of 1,000 texts. You can adjust that batch_size here but a higher value
            # might be slower to preprocess.
            #
            # To speed up this part, we use multiprocessing. See the documentation of the map method for more information:
            # https://huggingface.co/docs/datasets/process#map
            _ds = self._ds_process_map(
                _ds,
                group_texts,
                True,
                10000,
                f"Grouping texts in chunks of {self.max_seq_length}",
                workers,
                "groups.arrow",
            )
        return _ds


class DataFactoryWithLLMSFT(DataFactory):
    """your data ,data name is suffix .jsonl or .json
    example = {
        "prompt": [{"role": "user", "content": "What color is the sky?"}],
        "completion": [{"role": "assistant", "content": "It is blue."}],
    }
    """

    def __init__(self, args):
        super().__init__(args)

    @cache_folder_decorator(cache_folder_attr="ds_cache")
    def prepare_train_dataset(self):
        _NAME = "train"
        _file = self.args.train_file
        _ds = self._prepare_dataset(_file, self._process_fn, _NAME)

        return _ds

    @cache_folder_decorator(cache_folder_attr="ds_cache")
    def prepare_valid_dataset(self):
        _NAME = "valid"
        _file = self.args.valid_file
        _ds = self._prepare_dataset(_file, self._process_fn, _NAME)

        return _ds

    @cache_folder_decorator(cache_folder_attr="ds_cache")
    def prepare_test_dataset(self):
        _NAME = "test"
        _file = self.args.test_file
        _ds = self._prepare_dataset(_file, self._process_fn, _NAME)

        return _ds

    def _process_fn(self, df):
        return df
