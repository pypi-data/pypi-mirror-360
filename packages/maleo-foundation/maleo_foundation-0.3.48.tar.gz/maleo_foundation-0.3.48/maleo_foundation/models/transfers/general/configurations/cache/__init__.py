from __future__ import annotations
from pydantic import BaseModel, Field
from .redis import RedisCacheConfigurations


class CacheConfigurations(BaseModel):
    redis: RedisCacheConfigurations = Field(
        ..., description="Redis cache's configurations"
    )
