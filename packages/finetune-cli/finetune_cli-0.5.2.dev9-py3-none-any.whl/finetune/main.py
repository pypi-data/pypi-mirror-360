import json
import os

import typer

from finetune.GRPO.export import ModelSaver
from finetune.alpaca_shuffler import AlpacaShuffler

app = typer.Typer(
    name="fine-tuning tools.",
    no_args_is_help=True,
)


@app.command()
def hive_reward_train(
        hive_reward_folder_path: str = typer.Argument(..., help="Path to the hive-reward dataset folder."),
        model_name: str = typer.Argument('Qwen2.5-0.5B-Instruct', help="Model name for training."),
        SYSTEM_PROMPT: str = typer.Option(
            '你是一名专家，请不要直接给出答案，而是经过严谨而深思熟虑的思考后再给出答案，其中要把每一步的思考过程不可省略的详细说出来，并把思考过程放在<think></think>中显示。',
            help="System prompt for the training faster."),
        SYSTEM_PROMPT_FREQ: float = typer.Option(0.1, help="Frequency of the system prompt in the training."),
        max_prompt_length: int = typer.Option(25565, help="Maximum prompt length for the training."),
        max_seq_length: int = typer.Option(1024, help="Maximum sequence length for the training."),
        alpaca_dataset_path: str = typer.Argument("", help="Path to the alpaca dataset for training."),
        logging_steps: int = typer.Option(1, help="Logging steps for the training."),
        save_steps: int = typer.Option(100, help="Save steps for the training."),
        use_vllm: bool = typer.Option(True, help="Whether to use vllm for training."),
        report_to: str = typer.Option("tensorboard",
                                      help="Reporting tool for the training, e.g., 'wandb' or 'tensorboard'."),
        fp16: bool = typer.Option(True, help="Whether to use fp16 for training."),
        learning_rate: float = typer.Option(5e-4, help="Learning rate for the training."),
        num_train_epochs: int = typer.Option(3, help="Number of training epochs."),
        max_steps: int = typer.Option(10000, help="Maximum number of training steps."),
        train_model: list[str] = typer.Option(
            ['q_proj', 'gate_proj', 'up_proj', 'v_proj', 'k_proj', 'down_proj', 'o_proj'],
            help="List of model components to train."),
        LoRA_r: int = typer.Option(8, help="LoRA rank for the training."),
        LoRA_alpha: int = typer.Option(16, help="LoRA alpha for the training."),
        per_device_train_batch_size: int = typer.Option(4, help="Batch size per device for training."),
        gradient_checkpointing: bool = typer.Option(True, help="Whether to use gradient checkpointing for training."),
        load_in_8bit: bool = typer.Option(False, help="Whether to load the model in 8-bit for training."),
        vllm_gpu_memory_utilization: float = typer.Option(0.95, help="GPU memory utilization for vllm."),
        vllm_server_host: str = typer.Option('localhost', help="Host for the vllm server."),
        vllm_server_port: int = typer.Option(8000, help="Port for the vllm server."),
        gradient_accumulation_steps: int = typer.Option(1, help="Number of gradient accumulation steps for training."),
        vllm_tensor_parallel_size: int = typer.Option(2, help="Tensor parallel size for vllm."),
        vllm_mode: str = typer.Option("server", help="Mode for vllm, either 'server' or 'colocate'."),
):
    from finetune.GRPO.hivetrainer import HiveTrainer
    T = HiveTrainer(
        **locals()  # unpack all local variables as arguments
    )
    T.train()


@app.command()
def export(
        load_in_4bit: bool = typer.Option(False, help="Whether to load the model in 4-bit precision."),
        base_model_name: str = typer.Option(..., help="Base model name for export."),
        checkpoint_path: str = typer.Option(..., help="Path to the model checkpoint."),
        output_dir: str = typer.Option("exported_model", help="Directory to save the exported model."),
        to_vllm_format: bool = typer.Option(False, help="Whether to convert the model to vLLM format."),
):
    try:
        saver = ModelSaver(
            **locals()  # unpack all local variables as arguments
        )
        saved_path = saver.merge_and_save()
        print(f"\n✅ 模型保存成功！路径：{saved_path}")
        print("下一步建议：")
        print(f"1. 使用 transformers 加载: AutoModel.from_pretrained('{saved_path}')")
        print(f"或使用 vllm 加载: vllm serve {saved_path} --dtype=half")
        if to_vllm_format:
            print(f"2. 使用 vLLM 加载: LLM('{saved_path}_vllm')")
        print(f"3. 查看文件: ls -lh {saved_path}")

    except Exception as e:
        print(f"\n❌ 保存失败: {str(e)}")
        print("建议检查：")
        print("1. 确认checkpoint路径是否正确")
        print("2. 检查显存是否足够（尝试使用--load_in_4bit）")
        print("3. 确认模型与LoRA权重是否兼容")


@app.command()
def merge_alpaca(
        alpaca_file_list: list[str] = typer.Option(['1.alpaca.json'], 'List of Alpaca JSON files to merge.'),
        output_file: str = typer.Option("merged.alpaca.json", help="Output file path for the merged Alpaca JSON.")
):
    """
    Merge multiple Alpaca JSON files into a single file.
    :param alpaca_file_list: List of Alpaca JSON files to merge.
    :param output_file: Output file path for the merged Alpaca JSON.
    """
    assert len(alpaca_file_list) > 0, "请提供至少一个Alpaca JSON文件路径"
    for file_path in alpaca_file_list:
        assert os.path.exists(file_path), f"文件 {file_path} 不存在"

    data_list = []

    for it in alpaca_file_list:
        data_list.append(json.loads(open(it, 'r', encoding='utf-8').read()))

    AS = AlpacaShuffler()
    shuffled_data = AS.merge_shuffler(data_list)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(shuffled_data, f, ensure_ascii=False, indent=4)


def main():
    """
    entrypoint
    """
    app()
