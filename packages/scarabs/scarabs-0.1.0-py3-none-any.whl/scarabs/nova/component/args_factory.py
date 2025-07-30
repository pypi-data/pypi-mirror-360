# -*- coding: utf-8 -*-
# @Time   : 2024/08/13 10:24
# @Author : zip
# @Moto   : Knowledge comes from decomposition
from dataclasses import dataclass, field
from typing import Dict, Optional

from scarabs.nova.utils import TrainingArguments, set_log


def flatten_dict(nested: Dict, sep: str = "/") -> Dict:
    """Flatten dictionary and concatenate nested keys with separator."""

    def recurse(nest: Dict, prefix: str, into: Dict) -> None:
        for k, v in nest.items():
            if sep in k:
                raise ValueError(f"separator '{sep}' not allowed to be in key '{k}'")
            if isinstance(v, Dict):
                recurse(v, prefix + k + sep, into)
            else:
                into[prefix + k] = v

    flat = {}
    recurse(nested, "", flat)
    return flat


@dataclass
class ModelArguments:
    """
    Arguments pertaining to which model/config/tokenizer we are going to fine-tune, or train from scratch.
    """

    incremental_resume_from_checkpoint: Optional[str] = field(
        default=None,
        metadata={"help": "incremental resume from checkpoint"},
    )

    model_name_or_path: Optional[str] = field(
        default=None,
        metadata={
            "help": (
                "The model checkpoint for weights initialization. Don't set if you want to train a model from scratch."
            )
        },
    )
    config_name_or_path: Optional[str] = field(
        default=None,
        metadata={
            "help": "Pretrained config name or path if not the same as model_name"
        },
    )
    tokenizer_name: Optional[str] = field(
        default=None,
        metadata={
            "help": "Pretrained tokenizer name or path if not the same as model_name"
        },
    )
    cache_dir: Optional[str] = field(
        default=None,
        metadata={
            "help": "Where do you want to store the pretrained models downloaded from huggingface.co"
        },
    )
    use_fast_tokenizer: bool = field(
        default=True,
        metadata={
            "help": "Whether to use one of the fast tokenizer (backed by the tokenizers library) or not."
        },
    )
    token: Optional[str] = field(
        default=None,
        metadata={
            "help": (
                "The token to use as HTTP bearer authorization for remote files. If not specified, will use the token "
                "generated when running `huggingface-cli login` (stored in `~/.huggingface`)."
            )
        },
    )
    model_revision: str = field(
        default="main",
        metadata={
            "help": "The specific model version to use (can be a branch name, tag name or commit id)."
        },
    )
    torch_dtype: str = field(
        default="auto",
        metadata={
            "help": (
                "Override the default `torch.dtype` and load the model under this dtype. If `auto` is passed, the "
                "dtype will be automatically derived from the model's weights."
            ),
            "choices": ["auto", "bfloat16", "float16", "float32"],
        },
    )
    trust_remote_code: bool = field(
        default=False, metadata={"help": "Trust remote code when loading a model."}
    )
    low_cpu_mem_usage: bool = field(
        default=False,
        metadata={
            "help": (
                "It is an option to create the model as an empty shell, then only materialize its parameters when the pretrained weights are loaded. "
                "set True will benefit LLM loading time and RAM consumption."
            )
        },
    )
    attn_implementation: Optional[str] = field(
        default=None,
        metadata={
            "help": (
                "Which attention implementation to use; you can run --attn_implementation=flash_attention_2, in which case you must install this manually by running `pip install flash-attn --no-build-isolation`"
            )
        },
    )
    sft_task_type: Optional[str] = field(
        default="CAUSAL_LM",
        metadata={
            "help": ("Enum class for the different types of tasks supported by PEFT.")
        },
    )
    peft_config: Optional[Dict] = field(
        default=None,
        metadata={
            "help": ("PEFT config for the different types of tasks supported by PEFT.")
        },
    )
    num_virtual_tokens: int = field(
        default=4,
        metadata={"help": ("num_virtual_tokens (`int`): Number of virtual tokens.")},
    )
    load_in_8bit: bool = field(
        default=False,
        metadata={
            "help": "use 8 bit precision for the base model - works only with LoRA"
        },
    )
    load_in_4bit: bool = field(
        default=False,
        metadata={
            "help": "use 4 bit precision for the base model - works only with LoRA"
        },
    )
    model_gradient_checkpointing: bool = field(
        default=False,
        metadata={
            "help": "use gradient checkpointing to save memory at the expense of slower backward pass"
        },
    )
    model_gradient_checkpointing_kwargs: Dict = field(
        default_factory=dict,
        metadata={"help": "kwargs for gradient checkpointing"},
    )
    model_bf16: bool = field(
        default=False,
        metadata={
            "help": "use bfloat16 precision for the base model - works only with LoRA"
        },
    )

    def to_dict(self):
        output_dict = {}
        for key, value in self.__dict__.items():
            output_dict[key] = value
        return flatten_dict(output_dict)

    def __post_init__(self):
        if self.load_in_8bit and self.load_in_4bit:
            raise ValueError("You can't use 8 bit and 4 bit precision at the same time")

        if self.tokenizer_name is None and self.model_name_or_path is not None:
            self.tokenizer_name = self.model_name_or_path


@dataclass
class TaskArguments(TrainingArguments):
    # ======= 任务 =======
    task_name_or_path: str = field(
        default="encode",
        metadata={"help": ("The task_name_or_path")},
    )
    output_dir: str = field(
        default="model",
        metadata={
            "help": "The output directory where the model predictions and checkpoints will be written."
        },
    )
    # ======= 数据 =======
    data_format: Optional[str] = field(
        default=None,
        metadata={"help": "The datasets path (text, csv, json, jsonl, parquet)"},
    )
    train_file: Optional[str] = field(
        default=None, metadata={"help": "The input training data file (a text file)."}
    )
    valid_file: Optional[str] = field(
        default=None,
        metadata={
            "help": "An optional input evaluation data file to evaluate the perplexity on (a text file)."
        },
    )
    test_file: Optional[str] = field(
        default=None,
        metadata={
            "help": "An optional input test data file to evaluate the perplexity on (a text file)."
        },
    )
    preprocessing_num_workers: Optional[int] = field(
        default=2,
        metadata={"help": "The number of processes to use for the preprocessing."},
    )
    pretrain_concat_text: bool = field(
        default=False,
        metadata={
            "help": "Whether distinct lines of text in the dataset are to be handled as distinct sequences."
        },
    )
    max_seq_length: Optional[int] = field(
        default=None,
        metadata={"help": "The seq of token to use for max."},
    )
    # ======= 模型参数 =======
    load_resume_from_checkpoint: Optional[str] = field(
        default=None,
        metadata={"help": "load resume from checkpoint"},
    )
    incremental_resume_from_checkpoint: Optional[str] = field(
        default=None,
        metadata={"help": "incremental resume from checkpoint"},
    )
    model_tokenizer_config_name_or_path: Optional[str] = field(
        default=None,
        metadata={
            "help": (
                "The model checkpoint for weights initialization. Don't set if you want to train a model from scratch."
            )
        },
    )
    # ======= 训练时参数 =======
    early_stopping_patience: int = field(
        default=20,
        metadata={
            "help": "Execute N steps, stop if all indicators are below the optimal solution"
        },
    )
    early_stopping_threshold: float = field(
        default=1e-7,
        metadata={
            "help": "Execute N steps, Difference, stop if the condition is not met once within the number of judgments"
        },
    )

    def __post_init__(self):
        set_log(self.task_name_or_path)

        if self.data_format is None:
            raise ValueError("Need an data_format.")

        if self.data_format == "jsonl":
            self.data_format = "json"

        super().__post_init__()
