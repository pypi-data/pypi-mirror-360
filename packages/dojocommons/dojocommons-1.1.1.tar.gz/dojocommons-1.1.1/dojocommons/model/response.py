from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class Response(BaseModel):
    status_code: int = Field(alias="statusCode")
    body: Optional[str]

    model_config = ConfigDict(
        populate_by_name=True,
    )
