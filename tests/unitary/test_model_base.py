import init  # noqa: F401
from unittest import TestCase
from uuid import UUID
from app.core.domain.models.base import BaseModel


class TestBaseModel(TestCase):
    def setUp(self):
        self.instance = BaseModel()

    def test_uid_is_uuid_success(self):
        assert isinstance(self.instance.uid, UUID)

    def test_uid_is_unique_success(self):
        instance2 = BaseModel()
        assert self.instance.uid != instance2.uid

    def test_hash_function_success(self):
        assert hash(self.instance) == hash(self.instance.uid)

    def test_repr_function_success(self):
        expected_repr = (
            f"{self.instance.__class__.__name__}: "
            f"{str(self.instance.uid)[-3:]}"
        )
        assert repr(self.instance) == expected_repr

    def test_model_config_success(self):
        assert isinstance(BaseModel.model_config, dict)
