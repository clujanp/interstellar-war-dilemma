from pydantic import BaseModel, Field
from ulid import ULID


class CustomBaseModel(BaseModel):
    """Custom base that provides a centralized template for all models."""
    id: ULID = Field(default_factory=ULID)

    def __hash__(self):
        return id(self)
