import os

from tqdm import tqdm

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    pipeline
)
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

# 配置参数
MODEL_NAME = "hfl/chinese-bert-wwm-ext"
MAX_LENGTH = 128
BATCH_SIZE = 16
NUM_EPOCHS = 12
MODEL_SAVE_PATH = "./bert_topic_classifier"
TRAIN_PARQUET = '../datasets/topic_raw_data.parquet'


def read_dataset(path=TRAIN_PARQUET):
    df = pd.read_parquet(path)
    return df


class TopicDataset(Dataset):
    """自定义数据集处理类"""

    def __init__(self, texts, labels, tokenizer):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            max_length=MAX_LENGTH,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": torch.tensor(label, dtype=torch.long)
        }


def compute_metrics(p):
    """自定义评估指标"""
    preds = np.argmax(p.predictions, axis=1)
    return {
        "accuracy": accuracy_score(p.label_ids, preds),
        "f1": f1_score(p.label_ids, preds)
    }


def train_model():
    """训练函数"""
    # 加载数据
    df = read_dataset()
    texts = df["topic"].tolist()
    labels = df["is_topic_meet_instructions"].tolist()

    # 划分训练集和验证集
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )

    # 初始化分词器
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # 创建数据集
    train_dataset = TopicDataset(train_texts, train_labels, tokenizer)
    val_dataset = TopicDataset(val_texts, val_labels, tokenizer)

    # 加载预训练模型
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=2
    )

    # 训练参数设置
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        eval_strategy="epoch",  # 新版本参数名
        save_strategy="epoch",  # 与评估策略一致
        logging_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        seed=42,
        fp16=torch.cuda.is_available(),
    )

    # 创建Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics
    )

    # 开始训练
    trainer.train()

    # 保存模型
    model.save_pretrained(MODEL_SAVE_PATH)
    tokenizer.save_pretrained(MODEL_SAVE_PATH)
    print(f"模型已保存至 {MODEL_SAVE_PATH}")


def predict(texts, model_path=MODEL_SAVE_PATH, predict_batch_size=BATCH_SIZE):
    # 加载模型和分词器
    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)

    # 设备配置
    main_device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = model.to(main_device)

    # 多GPU处理 (兼容属性传递)
    if torch.cuda.device_count() > 1:
        print(f"使用 {torch.cuda.device_count()} 块GPU")
        original_model = model  # 保存原始模型引用
        model = torch.nn.DataParallel(model)
        # 动态属性转发（关键修复）
        model.config = original_model.config
        model.device = main_device
        model.can_generate = getattr(original_model, "can_generate", False)

    # 创建pipeline
    classifier = pipeline(
        "text-classification",
        model=model,
        tokenizer=tokenizer,
        device=0 if torch.cuda.is_available() else -1,
        batch_size=predict_batch_size
    )

    # 转换数据为生成器以支持流式处理
    def text_generator():
        for text in texts:
            yield text

    # 实时进度显示
    results = []
    with tqdm(total=len(texts), desc="预测进度", unit="样本", dynamic_ncols=True) as pbar:
        for text in texts:
            try:
                out = classifier(text, padding=True, truncation=True, max_length=MAX_LENGTH)
                results.append(out[0])
            except Exception as e:
                print(f"预测错误: 文本 {text[:50]}... 发生异常: {str(e)}")
            finally:
                pbar.update(1)
    return [{
        "label": int(res["label"].split("_")[-1]),
        "confidence": res["score"]
    } for res in results]


def predict_parquet(
        input_path: str,
        output_path: str,
        text_column: str = "topic",
        label_column: str = "is_topic_meet_instructions",
        model_path: str = MODEL_SAVE_PATH
) -> pd.DataFrame:
    """
    批量预测parquet文件并覆盖标签列

    Args:
        input_path (str): 输入parquet文件路径
        output_path (str): 输出parquet文件路径
        text_column (str): 文本列名，默认'topic'
        label_column (str): 待覆盖的标签列名，默认'is_topic_meet_instructions'
        model_path (str): 模型路径，默认MODEL_SAVE_PATH

    Returns:
        pd.DataFrame: 包含预测结果的DataFrame
    """
    df = pd.read_parquet(input_path)
    texts = df[text_column].tolist()
    predictions = predict(texts, model_path)
    df[label_column] = [pred["label"] for pred in predictions]
    df["pred_confidence"] = [pred["confidence"] for pred in predictions]  # 新增置信度列

    # 保存结果
    df.to_parquet(output_path, index=False)
    print(f"预测结果已保存至 {output_path}")

    return df


def predict_parquet_with_knowledgebase_questions(
        input_path: str,
        output_path: str,
        text_column: str = "questions",
        label_column: str = "is_topic_meet_instructions",
        model_path: str = MODEL_SAVE_PATH,
        batch_size: int = 256
) -> pd.DataFrame:
    # 读取数据
    df = pd.read_parquet(input_path)
    texts = df[text_column].tolist()

    # 多GPU预测
    predictions = predict(texts, model_path, batch_size)

    # 处理结果
    df[label_column] = [pred["label"] for pred in predictions]
    df["pred_confidence"] = [pred["confidence"] for pred in predictions]
    df = df[df[label_column] != 0]

    # 保存结果
    df.to_parquet(output_path, index=False)
    print(f"预测结果已保存至 {output_path}")
    return df


if __name__ == "__main__":
    # 训练模型
    # train_model()

    # 测试预测
    test_texts = [
        "如何配置SSL证书来提高网站安全性？",
        "请说明网络钓鱼攻击的基本原理",
        "Python编程基础教学"
    ]

    predictions = predict(test_texts)
    for text, pred in zip(test_texts, predictions):
        print(f"文本：{text}")
        print(f"预测结果：{pred}\n")

    # predict_parquet('../datasets/input.parquet', '../datasets/output.parquet')
    predict_parquet_with_knowledgebase_questions('../datasets/seed_prompts_20250416120441.parquet',
                                                 '../datasets/output.parquet')
