# 简述
## install
```bash
pip install finetune-cli
```
## help
```bash
> finetune -h
usage: finetune [-h] [--index_file INDEX_FILE] [--index_folder INDEX_FOLDER] [--input_parquet_file INPUT_PARQUET_FILE]
                [--encoding ENCODING] [--instruction INSTRUCTION] [--system_prompt SYSTEM_PROMPT] [--response_prefix RESPONSE_PREFIX]       
                [--response_suffix RESPONSE_SUFFIX] [--exams] [--gen_questions]
                [--convert_json_tmp_to_alpaca_file_path CONVERT_JSON_TMP_TO_ALPACA_FILE_PATH]

fine-tuning tools by stupidfish.

optional arguments:
  -h, --help            show this help message and exit
  --index_file INDEX_FILE
                        Input a index txt,read line by line.
  --index_folder INDEX_FOLDER
                        Input a folder,i'll read all the .md files.
  --input_parquet_file INPUT_PARQUET_FILE
                        Path to the input parquet file.
  --encoding ENCODING   file encoding with markdowns.
  --instruction INSTRUCTION
                        Alpaca's instruction for the fine-tuning process.
  --system_prompt SYSTEM_PROMPT
                        System prompt for the fine-tuning process.
  --response_prefix RESPONSE_PREFIX
                        Prefix to be added before the response.
  --response_suffix RESPONSE_SUFFIX
                        Suffix to be added after the response.
  --exams               Execute the exam method.
  --gen_questions       Generate questions for exam.
  --convert_json_tmp_to_alpaca_file_path CONVERT_JSON_TMP_TO_ALPACA_FILE_PATH
                        Convert json.tmp's file to alpaca json dataset.

```
## 举例
```bash
# 此例子为从wiki目录中的所有markdown自动生成问题（试卷）
> finetune --index_folder D:\work\diamond-shovel\wiki --encoding utf-8
2025-04-08 00:30:07.043 | INFO     | finetune.parquet.fine_tuning.tools:gen_questions_by_index_folder:176 - Get 8 markdown files.
  0%|                                                                                                                | 0/8 [00:00<?, ?it/s]
...
```
