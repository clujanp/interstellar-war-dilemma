from pydantic import BaseModel as BM, Field, ConfigDict
from uuid import uuid4, UUID


class BaseModel(BM):
    uid: UUID = Field(default_factory=lambda: uuid4())

    model_config = ConfigDict(
        arbitrary_types_allowed=True, from_attributes=True)

    def __hash__(self):
        return hash(self.uid)

    def __repr__(self):
        return f"{self.__class__.__name__}: {str(self.uid)[-3:]}"
