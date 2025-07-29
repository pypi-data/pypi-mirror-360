from pydantic import BaseModel


class Alpaca(BaseModel):
    input: str = ''
    output: str = ''
    instruction: str = ''
