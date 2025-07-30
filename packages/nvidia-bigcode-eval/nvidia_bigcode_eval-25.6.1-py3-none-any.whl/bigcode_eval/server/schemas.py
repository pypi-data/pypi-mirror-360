"""Pydantic BaseModels schemas for server payload messages. 
Implements some names mapping between bigcode and openAI API schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from collections.abc import Iterable
from typing import TypedDict, List, Any
import random


class OpenAiRequestsParams(BaseModel):
    model: str = Field(alias="model", default=None)
    max_gen_toks: Optional[int] = Field(alias="max_tokens", default=None)
    until: Optional[list[str] | str] = Field(alias="stop", default=None)
    temperature: Optional[float | int] = None
    top_p: Optional[float] = None
    n: Optional[int] = None
    stream: Optional[bool] = None
    use_random_seed_in_requests: bool = Field(exclude=True, default=True)
    seed: Optional[int] = None

    class Config:
        populate_by_name = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.use_random_seed_in_requests and self.seed is None:
            self.seed = random.randint(0, 2**32 - 1)


class OpenAiCompletionParams(OpenAiRequestsParams):
    prompt: Optional[str | list[str] | Iterable[int] | Iterable[Iterable[int]]]
    
    class Config:
        populate_by_name = True


class OpenAiChatCompletionParams(OpenAiRequestsParams):
    messages: Optional[list[dict[str, str]]]
    tools: list[dict] = None
    
    class Config:
        populate_by_name = True


class OpenAiOutputWithTools(TypedDict):
    text: Optional[str]
    tools: Optional[List[dict]]