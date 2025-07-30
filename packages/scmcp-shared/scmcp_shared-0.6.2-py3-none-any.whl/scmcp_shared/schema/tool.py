from pydantic import BaseModel, Field
from typing import List


class Tool(BaseModel):
    name: str = Field(description="The name of the tool")
    description: str = Field(description="The description of the tool")


class ToolList(BaseModel):
    tools: List[Tool]