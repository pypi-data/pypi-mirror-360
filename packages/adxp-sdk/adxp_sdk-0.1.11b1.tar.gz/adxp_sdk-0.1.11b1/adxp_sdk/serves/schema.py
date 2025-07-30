from typing import Optional
from pydantic import BaseModel, ConfigDict
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, ConfigDict, Field


class GraphPath(BaseModel):
    name: str = Field(default="", description="graph name. it will be prefix of api")
    object_path: str = Field(
        description="graph path. format supposed to be /path/to/module.py:object_name"
    )


class RemoteRunnableRequest(BaseModel):
    input: dict
    config: Optional[RunnableConfig]
    kwargs: Optional[dict]

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "examples": [
                {
                    "input": {"messages": []},
                    "config": {},
                    "kwargs": {},
                }
            ]
        },
    )
