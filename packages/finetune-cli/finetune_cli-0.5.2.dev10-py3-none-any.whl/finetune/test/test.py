import re

from finetune.parquet import ParquetReader

with ParquetReader('finetune/statics/seed_prompts_20250219225920.parquet') as pr:
    data = pr.get_raw_line(0)
    print(data)
    questions_str = data['questions']
    print(questions_str)
    questions = re.findall(r"question='(.*?)'", questions_str)
    print(f"knowledge:{data['KnowledgeBase']}")