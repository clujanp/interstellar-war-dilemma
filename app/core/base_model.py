from pydantic import BaseModel, Field, ConfigDict
from ulid import ULID


class CustomBaseModel(BaseModel):
    """Custom base that provides a centralized template for all models."""
    id: ULID = Field(default_factory=ULID)

    model_config = ConfigDict(
        from_attributes=True,
        revalidate_instances="never"
    )

    def __hash__(self):
        return id(self)
