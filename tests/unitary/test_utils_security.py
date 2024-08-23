import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock
from app.utils.security import SecureProxy
from app.config.messages import ERR_SECURE_PROXY as ERR_MSG


class TestSecureProxy(TestCase):
    def setUp(self):
        self.mock_obj = MagicMock()
        self.readable_attrs = ['readable_attr', 'prop_attr']
        self.writable_attrs = ['writable_attr', 'prop_attr']
        self.accessible_methods = ['accessible_method']
        self.proxy = SecureProxy(
            self.mock_obj,
            self.readable_attrs,
            self.writable_attrs,
            self.accessible_methods
        )

    def test_getattr_readable_attr_success(self):
        self.mock_obj.readable_attr = 'value'
        result = self.proxy.readable_attr
        assert result == 'value'

    def test_getattr_not_readable_fail(self):
        with self.assertRaises(AttributeError) as context:
            _ = self.proxy.not_readable
        assert (
            ERR_MSG['acc_restric'].format('not_readable')
            == str(context.exception)
        )

    def test_getattr_readable_attr_is_callable_fail(self):
        self.mock_obj.readable_attr = MagicMock()
        with self.assertRaises(AttributeError) as context:
            _ = self.proxy.readable_attr
        assert (
            ERR_MSG['not_acc_methd'].format('readable_attr')
            == str(context.exception)
        )

    def test_setattr_writable_attr_success(self):
        self.mock_obj.writable_attr = 'value'
        self.proxy.writable_attr = 'new_value'
        assert 'new_value' == self.mock_obj.writable_attr

    def test_setattr_not_writable_fail(self):
        with self.assertRaises(AttributeError) as context:
            self.proxy.not_writable = 'new_value'
        assert (
            ERR_MSG['not_modify'].format('not_writable')
            == str(context.exception)
        )

    def test_setattr_writable_attr_is_callable_fail(self):
        self.mock_obj.writable_attr = MagicMock()
        with self.assertRaises(AttributeError) as context:
            self.proxy.writable_attr = 'new_value'
        assert (
            ERR_MSG['methd_not_modify'].format('writable_attr')
            == str(context.exception)
        )

    def test_getattr_accessible_method_success(self):
        self.mock_obj.accessible_method = MagicMock(return_value='result')
        result = self.proxy.accessible_method()
        assert 'result' == result

    def test_getattr_property_success(self):
        type(self.mock_obj).prop_attr = property(
            fget=MagicMock(return_value='prop_value'))
        result = self.proxy.prop_attr
        assert result == 'prop_value'

    def test_setattr_property_success(self):
        fset_mock = MagicMock()
        type(self.mock_obj).prop_attr = property(
            fget=MagicMock(return_value='prop_value'),
            fset=fset_mock
        )
        self.proxy.prop_attr = 'new_value'
        fset_mock.assert_called_once_with(self.mock_obj, 'new_value')

    def test_setattr_property_no_fset_fail(self):
        type(self.mock_obj).prop_attr = property(
            fget=MagicMock(return_value='prop_value'))
        with self.assertRaises(AttributeError) as context:
            self.proxy.prop_attr = 'new_value'
        assert (
            ERR_MSG['not_modify'].format('prop_attr')
            == str(context.exception)
        )
