import json

import loguru
from tqdm import tqdm

from finetune.structure.alpaca import Alpaca


class Converter:
    def __init__(self, data: dict):
        """
        负责将Parquet的数据格式读取并返回标准的Alpaca格式要素
        """
        self.data = Alpaca()
        self.data.instruction = data.pop('input')
        self.data.input = ''
        self.data.output = ''

    def invoke(self):
        return self.data


class Qa2Alpaca:
    def __init__(self, file: str, *args, **kwargs):
        loguru.logger.remove()
        loguru.logger.add(lambda msg: tqdm.write(msg, end=""))
        self.input_file(file, *args, **kwargs)

    def filiter(self, data_it: dict):
        """
        数据过滤器
        :param data_it:
        :return:
        """
        if len(data_it['output']) > 128:
            return None
        else:
            return data_it

    def input_file(self, input_file: str, *args, **kwargs):
        """
        read input_file and convert to alpaca formatting file.
        :param input_file:
        :return:
        """
        converted_file_name = input_file.replace(".json", "_converted.json")
        big_dict = []
        with open(input_file, "r", encoding=kwargs['encoding'], errors='ignore') as f:
            f_ptr = f.readlines()
            with tqdm(total=len(f_ptr)) as pbar:
                pbar.set_description("Converting")
                for it in f_ptr:
                    try:
                        data: dict = json.loads(it)
                        converter = Converter(data)
                        data = converter.invoke().__dict__
                        data = self.filiter(data)
                        if data:
                            big_dict.append(data)
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        loguru.logger.error(f"Error processing line: {it.strip()}. Error: {e}")
                        continue
                    finally:
                        pbar.update(1)
        with open(converted_file_name, "w", encoding="utf-8") as f_out:
            f_out.write(json.dumps(big_dict, ensure_ascii=False) + '\n')
        loguru.logger.success(f"Converted file: {converted_file_name};")
        loguru.logger.info(f"Data count: {len(big_dict)};")


if __name__ == '__main__':
    qa2alpaca = Qa2Alpaca("../../statics/chinese_law.json", encoding='utf-8')
