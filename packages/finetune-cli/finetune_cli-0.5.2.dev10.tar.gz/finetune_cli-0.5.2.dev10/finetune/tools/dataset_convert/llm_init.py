import loguru
from kink import di
from langchain_openai import ChatOpenAI

from finetune.tools.dataset_convert.config import Master


class global_llm:
    def __enter__(self):
        loguru.logger.debug("Entering global_llm context manager.")
        loguru.logger.info(f"default_model: {Master.get('default_model')}")
        loguru.logger.info(f"openai_api_endpoint: {Master.get('openai_api_endpoint')}")
        loguru.logger.info(f"openai_api_key: {Master.get('openai_api_key')}")

        di['llm'] = ChatOpenAI(
            model=Master.get("default_model"),
            base_url=Master.get("openai_api_endpoint"),
            api_key=Master.get("openai_api_key"),
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        di['llm'] = None