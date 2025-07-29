# save_model.py
import argparse
import torch
import logging
from datetime import datetime
from peft import PeftModel
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelSaver:
    def __init__(self,
                 load_in_4bit,
                 base_model_name,
                 checkpoint_path,
                 output_dir,
                 to_vllm_format
                 ):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self.load_in_4bit = load_in_4bit
        self.base_model_name = base_model_name
        self.checkpoint_path = checkpoint_path
        self.output_dir = output_dir
        self.to_vllm_format = to_vllm_format

    def _load_base_model(self):
        """加载基础模型"""
        logger.info(f"Loading base model from {self.base_model_name}")

        # 量化配置（如果指定）
        bnb_config = None
        if self.load_in_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )

        return AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            trust_remote_code=True
        )

    def _load_lora_weights(self, model):
        """加载LoRA权重"""
        logger.info(f"Loading LoRA weights from {self.checkpoint_path}")
        return PeftModel.from_pretrained(
            model,
            self.checkpoint_path,
            is_trainable=False
        )

    def merge_and_save(self):
        """合并权重并保存模型"""
        try:
            # 1. 加载基础模型
            base_model = self._load_base_model()

            # 2. 加载LoRA权重
            lora_model = self._load_lora_weights(base_model)

            # 3. 合并权重
            logger.info("Merging LoRA weights with base model")
            merged_model = lora_model.merge_and_unload()

            # 4. 加载tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.base_model_name,
                trust_remote_code=True
            )

            # 5. 保存配置
            save_path = f"{self.output_dir}/merged_model_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # 6. 保存完整模型
            merged_model.save_pretrained(save_path)
            self.tokenizer.save_pretrained(save_path)
            logger.info(f"Model saved to {save_path}")

            # 7. 可选：转换为vLLM格式
            if self.to_vllm_format:
                self._convert_to_vllm_format(merged_model, save_path)

            return save_path

        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise

    def _convert_to_vllm_format(self, model, path):
        """转换为vLLM兼容格式"""
        logger.info("Converting to vLLM format")
        # 这里添加具体的格式转换逻辑
        # 示例：可能需要重新保存为特定的张量布局
        model.save_pretrained(
            f"{path}_vllm",
            safe_serialization=False  # 关闭安全序列化以使用pytorch格式
        )
        logger.info(f"vLLM format saved to {path}_vllm")


def parse_args():
    parser = argparse.ArgumentParser(description="保存合并后的模型")

    parser.add_argument(
        "--base_model_name",
        type=str,
        required=True,
        help="基础模型名称或路径"
    )
    parser.add_argument(
        "--checkpoint_path",
        type=str,
        required=True,
        help="包含LoRA权重的checkpoint路径"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./saved_models",
        help="输出目录"
    )
    parser.add_argument(
        "--load_in_4bit",
        action="store_true",
        help="使用4位量化加载模型"
    )
    parser.add_argument(
        "--to_vllm_format",
        action="store_true",
        help="转换为vLLM兼容格式"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    saver = ModelSaver(args)

    try:
        saved_path = saver.merge_and_save()
        print(f"\n✅ 模型保存成功！路径：{saved_path}")
        print("下一步建议：")
        print(f"1. 使用 transformers 加载: AutoModel.from_pretrained('{saved_path}')")
        print(f"或使用 vllm 加载: vllm serve {saved_path} --dtype=half")
        if args.to_vllm_format:
            print(f"2. 使用 vLLM 加载: LLM('{saved_path}_vllm')")
        print(f"3. 查看文件: ls -lh {saved_path}")

    except Exception as e:
        print(f"\n❌ 保存失败: {str(e)}")
        print("建议检查：")
        print("1. 确认checkpoint路径是否正确")
        print("2. 检查显存是否足够（尝试使用--load_in_4bit）")
        print("3. 确认模型与LoRA权重是否兼容")
