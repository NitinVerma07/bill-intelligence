from pydantic import BaseModel, Field


class Person(BaseModel):
    id: str
    name: str
    assigned_item_indices: list[int] = Field(default_factory=list)
