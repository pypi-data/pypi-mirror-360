from pydantic import BaseModel


class SeedPrompt(BaseModel):
    question: str


class SeedPropmts(BaseModel):
    seed_prompts: list[SeedPrompt]


class Answer(BaseModel):
    raw_topic: str
    answer: str


class Translation(BaseModel):
    raw_sentence: str
    zh_cn_result: str
