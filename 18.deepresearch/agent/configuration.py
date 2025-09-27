import os
from pydantic import BaseModel, Field
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig


class Configuration(BaseModel):
    """The configuration for the agent."""

    query_generator_model: str = Field(
        default="deepseek-chat",
        metadata={
            "description": "用于生成搜索查询的LLM"
        },
    )

    reflection_model: str = Field(
        default="deepseek-chat",
        metadata={
            "description": "用于反思的LLM"
        },
    )

    answer_model: str = Field(
        default="deepseek-chat",
        metadata={
            "description": "用于回答的LLM"
        },
    )

    number_of_initial_queries: int = Field(
        default=3,
        metadata={"description": "初始搜索查询的数量"},
    )

    max_research_loops: int = Field(
        default=2,
        metadata={"description": "最大研究循环次数"},
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
