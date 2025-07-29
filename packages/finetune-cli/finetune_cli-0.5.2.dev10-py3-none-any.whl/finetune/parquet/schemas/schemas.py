from pydantic import BaseModel


class SeedPrompt(BaseModel):
    question: str


class SeedPropmts(BaseModel):
    seed_prompts: list[SeedPrompt]


class FilterResult(BaseModel):
    is_topic_meet_instructions: bool


class Answer(BaseModel):
    raw_topic: str
    answer: str


class TopicRawData(BaseModel):
    topic: str
    is_topic_meet_instructions: int


def pydantic_encoder(obj):
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
