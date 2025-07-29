import atexit
import concurrent
import json
from datetime import datetime

import loguru
from kink import di
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tqdm import tqdm

from finetune.tools.dataset_convert.llm_init import global_llm
from finetune.tools.dataset_convert.schemas.schemas import Translation
from finetune.tools.dataset_convert.schemas.works.PydanticSafetyParser import ChatWithSafetyPydanticOutputParser


def translation(raw_str: str):
    with global_llm():
        parser = PydanticOutputParser(pydantic_object=Translation)
        promptTemplate = ChatPromptTemplate.from_messages([
            ("system", "{format_instructions};"
                       "{system_prompt}"),
            ("user", raw_str)
        ])
        input_args = {
            "format_instructions": parser.get_format_instructions(),
            "system_prompt": "请准确翻译以下用户提供给你的文字资料成中文，如果用户没有提供，不返回即可"
        }
        res = ChatWithSafetyPydanticOutputParser(model=di['llm'], input_args=input_args,
                                                 promptTemplate=promptTemplate,
                                                 schemas_model=Translation)
        return res.zh_cn_result


def dataset_convert():
    loguru.logger.remove()
    loguru.logger.add(lambda msg: tqdm.write(msg, end=""))

    with open('statics/linux_command_raw.json', 'r') as file:
        r = json.loads(file.read())
    with open('statics/alpaca_dataset.json', 'r') as file:
        r1 = json.loads(file.read())
    loguru.logger.info("Read done.")
    new_r = []
    file_name = f'fine_tune_datafile_{datetime.now().strftime("%Y%m%d%H%M%S")}_tmp.json'
    with tqdm(total=len(r) + len(r1)) as pbar:
        pbar.set_description("Converting")

        def process_item(it, pbar):
            n1 = {
                "instruction": "请根据提示给出linux命令",
                "input": translation(it['nl_command'] if 'nl_command' in it else ''),
                "response": it['bash_code']
            }
            new_r.append(n1)
            with open(file_name, 'a') as file:
                json.dump(n1, file, ensure_ascii=False)
                file.write('\n')
            loguru.logger.debug(f"{n1}")
            pbar.update(1)

        with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
            futures = [executor.submit(process_item, it, pbar) for it in r]
            # 等待所有任务完成
            concurrent.futures.wait(futures)

        # def process_item_n2(it, pbar):
        #     n2 = {
        #         "instruction": translation(it['instruction'] if 'instruction' in it else ''),
        #         "input": translation(it['input'] if 'input' in it else ''),
        #         "response": it['response']
        #     }
        #     new_r.append(n2)
        #     loguru.logger.debug(f"{n2}")
        #     pbar.update(1)

        # with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
        #     futures = [executor.submit(process_item_n2, it, pbar) for it in r1]
        #     # 等待所有任务完成
        #     concurrent.futures.wait(futures)
    @atexit.register
    def save():
        loguru.logger.warning("Saving...")
        json.dump(new_r, open(f'fine_tune_datafile_{datetime.now().strftime("%Y%m%d%H%M%S")}.json', 'w'),
                  ensure_ascii=False, indent=4)
        loguru.logger.success("Saved.")