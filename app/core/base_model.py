from pydantic import BaseModel


class CustomBaseModel(BaseModel):
    """Custom base that provides a centralized template for all models."""
    def __hash__(self):
        return id(self)
