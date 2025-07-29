import json
import os

import loguru


class HiveRewardDataset:
    def __init__(self, folder_path: str, **kwargs):
        """
        HiveRewardDataset is a class to load datasets from a specified folder containing.
        :param folder_path: The path to the folder containing the datasets.
        :param kwargs: Additional keyword arguments, such as SYSTEM_PROMPT.
        """
        self.folder_path = folder_path
        self.datasets = []
        self.SYSTEM_PROMPT = kwargs.get('SYSTEM_PROMPT', '')

    def _load_dataset_from_hive_reward(self):
        """
        Load QA datasets(Alpaca format.)
        and convert to chat format with system prompt.
        Add progress visualization and sampling logging.
        """
        from tqdm import tqdm
        import random
        from loguru import logger

        processed_data = []

        hive_reward_files = []
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith('.hive-reward.json'):
                    hive_reward_files.append(os.path.join(root, file))
        loguru.logger.info(f"Found {len(hive_reward_files)} files.")
        for file in tqdm(hive_reward_files, desc="Loading hive-reward files"):
            self.datasets.append(json.loads(open(file, 'r').read()))
        with tqdm(total=len(self.datasets),
                  desc="Converting samples",
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{rate_fmt}]") as pbar:
            for idx, item in enumerate(self.datasets):
                # 合并指令和输入
                user_content = ""
                if item.get("topic", "").strip():
                    user_content += "\n" + item["topic"]

                # 构建对话格式
                formatted_item = {
                    "prompt": [
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": user_content}
                    ],
                    "answer": "",
                    "metadata": {
                        "hive-reward": json.dumps(item, ensure_ascii=False)  # 疑似Dataset中不会保持json结构，故而strify后传输
                    }
                }

                if random.random() < 0.001 or idx in (0, len(self.datasets) - 1):
                    logger.debug("\nSampled QA[{}]:\nSYSTEM: {}\nUSER: {}\nANSWER: {}",
                                 idx,
                                 self.SYSTEM_PROMPT[:50] + "..." if len(
                                     self.SYSTEM_PROMPT) > 50 else self.SYSTEM_PROMPT,
                                 user_content[:100] + "..." if len(user_content) > 100 else user_content,
                                 "")

                processed_data.append(formatted_item)
                pbar.update(1)
                pbar.set_postfix_str(f"Last sampled: {idx}" if idx in (0, len(self.datasets) - 1) else "")

        # 数据集最终转换
        from datasets import Dataset
        return Dataset.from_list(processed_data)

    def load_datasets(self):
        return self._load_dataset_from_hive_reward()
