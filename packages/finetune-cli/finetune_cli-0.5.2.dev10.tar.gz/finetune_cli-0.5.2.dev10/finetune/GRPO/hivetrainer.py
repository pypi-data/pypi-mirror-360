import json
import os
from datetime import datetime

import loguru
from transformers import AutoModelForCausalLM
from transformers.trainer_utils import get_last_checkpoint
from trl import GRPOConfig, GRPOTrainer
from peft import LoraConfig

from finetune.GRPO.ModGRPOTrainer import MODGRPOTrainer
from finetune.GRPO.rewards.format_rewards import think_format_reward_func
from finetune.GRPO.rewards.hive_rewards.hive_reward_datasets import HiveRewardDataset
from finetune.GRPO.rewards.hive_rewards.hive_rewards import hive_reward


class HiveTrainer:
    def __init__(self,
                 model_name="Qwen2.5-0.5B-Instruct",
                 alpaca_dataset_path="",
                 hive_reward_folder_path="",
                 max_prompt_length=25565,
                 max_seq_length=128000,
                 logging_steps=1,
                 save_steps=50,
                 use_vllm=True,
                 report_to="tensorboard",
                 fp16=True,
                 learning_rate=5e-5,
                 num_train_epochs=9,
                 max_steps=10000,
                 train_model=['q_proj', 'k_proj', 'v_proj'],
                 LoRA_r=8,
                 LoRA_alpha=16,
                 per_device_train_batch_size=1,
                 gradient_checkpointing=True,
                 load_in_8bit=False,
                 vllm_gpu_memory_utilization=0.95,
                 vllm_server_host='localhost',
                 vllm_server_port=8000,
                 gradient_accumulation_steps=1,
                 vllm_mode="server",  # or colocate
                 vllm_tensor_parallel_size=2,
                 **kwargs):

        assert os.path.exists(model_name), f"Model {model_name} does not exist. Please check the path."
        assert os.path.exists(alpaca_dataset_path) or os.path.exists(
            hive_reward_folder_path), f"Dataset path {alpaca_dataset_path} or {hive_reward_folder_path} does not exist. Please check the path."

        self.hive_reward_dataset = None
        self.output_dir = model_name + "_trained"
        self.trainer = None
        self.model_name = model_name
        self.SYSTEM_PROMPT = kwargs.get('SYSTEM_PROMPT', '')  # 为了加速拟合的系统提示词
        self.SYSTEM_PROMPT_FREQ = kwargs.get('SYSTEM_PROMPT_FREQ', 0.1)  # 系统提示此出现的概率（为了防止过拟合，模型把所有策略都依托到提示词上）
        self.alpaca_dataset_path = alpaca_dataset_path
        self.hive_reward_folder_path = hive_reward_folder_path
        self.max_prompt_length = max_prompt_length
        self.max_seq_length = max_seq_length

        self.logging_steps = logging_steps
        self.save_steps = save_steps
        self.use_vllm = use_vllm
        self.report_to = report_to
        self.fp16 = fp16
        self.learning_rate = learning_rate
        self.num_train_epochs = num_train_epochs
        self.max_steps = max_steps
        self.train_model = train_model
        self.LoRA_r = LoRA_r
        self.LoRA_alpha = LoRA_alpha
        self.per_device_train_batch_size = per_device_train_batch_size
        self.gradient_checkpointing = gradient_checkpointing
        self.load_in_8bit = load_in_8bit
        self.vllm_gpu_memory_utilization = vllm_gpu_memory_utilization
        self.vllm_server_host = vllm_server_host
        self.vllm_server_port = vllm_server_port
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.vllm_mode = vllm_mode
        self.vllm_tensor_parallel_size = vllm_tensor_parallel_size

        loguru.logger.info(f"Initializing HiveTrainer with the following parameters:{locals()}")

    def load_datasets(self):
        if self.hive_reward_folder_path:
            loguru.logger.info(f"Loading datasets from {self.hive_reward_folder_path}")
            self.hive_reward_dataset = HiveRewardDataset(self.hive_reward_folder_path)
            datasets = self.hive_reward_dataset.load_datasets()
            loguru.logger.info(f"Loaded {len(datasets)} datasets.")
            return datasets
        elif self.alpaca_dataset_path:
            loguru.logger.info(f"Loading datasets from {self.alpaca_dataset_path}")
            datasets = self._load_QA_dataset()
            loguru.logger.info(f"Loaded {len(datasets)} datasets.")
            return datasets
        else:
            raise ValueError("Please provide either hive_reward_folder_path or alpaca_dataset_path.")

    def config_trainer(self):
        training_args = GRPOConfig(
            output_dir=self.output_dir,
            logging_steps=self.logging_steps,
            save_steps=self.save_steps,
            use_vllm=self.use_vllm,
            report_to=self.report_to,
            fp16=self.fp16,
            learning_rate=self.learning_rate,
            num_train_epochs=self.num_train_epochs,
            max_steps=self.max_steps,
            per_device_train_batch_size=self.per_device_train_batch_size,
            gradient_checkpointing=self.gradient_checkpointing,
            vllm_gpu_memory_utilization=self.vllm_gpu_memory_utilization,
            vllm_server_host=self.vllm_server_host,
            vllm_server_port=self.vllm_server_port,
            gradient_accumulation_steps=self.gradient_accumulation_steps,
            vllm_mode=self.vllm_mode,
            vllm_tensor_parallel_size=self.vllm_tensor_parallel_size,
            max_completion_length=self.max_seq_length
        )

        peft_config = LoraConfig(
            r=self.LoRA_r,
            lora_alpha=self.LoRA_alpha,
            target_modules=self.train_model,
            task_type="CAUSAL_LM",
            lora_dropout=0.05,
        )
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            load_in_8bit=self.load_in_8bit,
        )
        loguru.logger.debug(f"Load model done.")
        self.trainer = MODGRPOTrainer(
            model=model,
            reward_funcs=[
                hive_reward,  # general_reward
                # think_format_reward_func
            ],
            args=training_args,
            train_dataset=self.load_datasets(),
            peft_config=peft_config,
        )
        loguru.logger.debug(f"Load trainer done.")

    def _output_dir_check(self):
        """
        Check the output_dir is existed?
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            return False
        if len(os.listdir(self.output_dir)) == 0:
            return False
        return True

    def train(self):
        tmp_kwargs = {}
        if self._output_dir_check():
            last_checkpoint = get_last_checkpoint(self.output_dir)
            if last_checkpoint is not None:
                tmp_kwargs["resume_from_checkpoint"] = last_checkpoint
        self.config_trainer()
        self.trainer.train(**tmp_kwargs)
        save_name = f'lora_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        # self.model.save_lora(save_name)
        # self.model.save_pretrained_merged("model", self.tokenizer, save_method="merged_16bit")

    def _load_QA_dataset(self):
        """
        Load QA datasets(Alpaca format.)
        and convert to chat format with system prompt.
        Add progress visualization and sampling logging.
        """
        from tqdm import tqdm
        import random
        from loguru import logger

        with tqdm(total=1, desc="Loading dataset", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
            with open(self.alpaca_dataset_path) as file:
                alpaca_data = json.load(file)
            pbar.update(1)

        processed_data = []

        with tqdm(total=len(alpaca_data),
                  desc="Converting samples",
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{rate_fmt}]") as pbar:
            for idx, item in enumerate(alpaca_data):
                # 合并指令和输入
                user_content = item["instruction"]
                if item.get("input", "").strip():
                    user_content += "\n" + item["input"]

                # 构建对话格式
                formatted_item = {
                    "prompt": [
                        {"role": "system",
                         "content": self.SYSTEM_PROMPT if self.SYSTEM_PROMPT_FREQ > random.random() else ""},
                        {"role": "user", "content": user_content}
                    ],
                    "answer": item["output"]
                }

                # 采样记录（0.1%概率 + 首尾样本）
                if random.random() < 0.001 or idx in (0, len(alpaca_data) - 1):
                    logger.debug("\nSampled QA[{}]:\nSYSTEM: {}\nUSER: {}\nANSWER: {}",
                                 idx,
                                 self.SYSTEM_PROMPT[:50] + "..." if len(
                                     self.SYSTEM_PROMPT) > 50 else self.SYSTEM_PROMPT,
                                 user_content[:100] + "..." if len(user_content) > 100 else user_content,
                                 item["output"][:100] + "..." if len(item["output"]) > 100 else item["output"])

                processed_data.append(formatted_item)
                pbar.update(1)
                pbar.set_postfix_str(f"Last sampled: {idx}" if idx in (0, len(alpaca_data) - 1) else "")

        # 数据集最终转换
        from datasets import Dataset
        return Dataset.from_list(processed_data)

    def extract_think(self, text: str):
        """
        Extract <think>(.*?)</think> content.
        """
        think = text.split("<think>")[-1]
        think = think.split("</think>")[0]
        return think.strip()

    def extract_answer(self, text: str):
        """
        Extract answer(eliminate think)
        """
        if "<think>" in text and "</think>" in text:
            return text.replace(f"<think>{self.extract_think(text)}</think>", "").strip()
        return text.strip()

    def reward_func(self, prompts, completions, answer, **kwargs) -> list[float]:
        """
        GRPO中的奖励函数
        """
        responses = [completion[0]["content"] for completion in completions]
        thinks = [self.extract_think(t) for t in responses]
        answers = [self.extract_answer(t) for t in responses]
