import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch
from app.config.messages import ERR_SECURE_PROXY as ERR_MSG
from app.adapters.repositories.strategy.proxies import SecureProxyFactory
from app.adapters.repositories.strategy.proxies.proxy import SecureProxy
from app.adapters.repositories.strategy.proxies.proxy_read import ReadableProxy
from app.adapters.repositories.strategy.proxies.proxy_write import (
    WritableProxy)
from app.adapters.repositories.strategy.proxies.proxy_method import (
    MethodAccessibleProxy)
from app.adapters.repositories.strategy.proxies.executer import SafeExecuter
from app.application.exceptions.proxy import (
    RestrictedAccessError, OverrideError)


class TestSecureProxyFactoryTestCase(TestCase):
    def setUp(self):
        class MockedClass:
            ...
        self.mocked_class = MockedClass
        self.mock_safe_executer = MagicMock(SafeExecuter)
        self.proxy_definitions = {
            MockedClass: {
                'readable_attrs': ['readable_attr'],
                'writable_attrs': ['writeable_attr'],
                'accessible_methods': ['accessible_method'],
            }
        }
        self.factory = SecureProxyFactory(self.proxy_definitions)
        self.factory._safe_executer = self.mock_safe_executer

    @patch('app.adapters.repositories.strategy.proxies.factory.SecureProxy')
    def test_call_secure_proxy_success(self, mock_secure_proxy: MagicMock):
        mock_secure_proxy.return_value = MagicMock()
        obj = self.mocked_class()
        result = self.factory(obj)

        mock_secure_proxy.assert_called_once_with(
            obj,
            self.proxy_definitions[self.mocked_class]['readable_attrs'],
            self.proxy_definitions[self.mocked_class]['writable_attrs'],
            self.proxy_definitions[self.mocked_class]['accessible_methods'],
            method_wrapper=self.mock_safe_executer,
        )
        assert mock_secure_proxy.return_value == result

    def test_call_pass_through_success(self):
        obj = 42
        result = self.factory(obj, pass_=True)
        assert result == obj

    def test_call_not_secure_proxy_fail(self):
        obj = 42
        with self.assertRaises(AttributeError) as context:
            self.factory(obj)
        expected_message = ERR_MSG['not_secure_proxy'].format(
            obj.__class__.__name__)
        assert str(context.exception) == expected_message


class TestSecureProxy(TestCase):
    @patch(
        'app.adapters.repositories.strategy.proxies.proxy'
        '.MethodAccessibleProxy'
    )
    @patch('app.adapters.repositories.strategy.proxies.proxy.WritableProxy')
    @patch('app.adapters.repositories.strategy.proxies.proxy.ReadableProxy')
    def setUp(
        self,
        mock_readable_proxy: MagicMock,
        mock_writable_proxy: MagicMock,
        mock_method_accessible_proxy: MagicMock
    ):
        self.mock_method = MagicMock()
        self.mock_obj = MagicMock(
            readable_attr='value1',
            writable_attr='value2',
            accessible_method=self.mock_method,
        )
        self.readable_attrs = ['readable_attr']
        self.writable_attrs = ['writable_attr']
        self.accessible_methods = ['accessible_method']
        self.proxy = SecureProxy(
            self.mock_obj,
            self.readable_attrs,
            self.writable_attrs,
            self.accessible_methods,
            method_wrapper='mocked_method_wrapper'
        )
        mock_readable_proxy.return_value.readable_attr = 'value1'
        mock_writable_proxy.return_value.writable_attr = 'value2'
        mock_method_accessible_proxy.return_value.accessible_method = (
            self.mock_method)
        self.mock_readable_proxy = mock_readable_proxy
        self.mock_writable_proxy = mock_writable_proxy
        self.mock_method_accessible_proxy = mock_method_accessible_proxy
        self.mock_readable_proxy.assert_called_once_with(
            self.mock_obj, self.readable_attrs)
        self.mock_writable_proxy.assert_called_once_with(
            self.mock_obj, self.writable_attrs)
        self.mock_method_accessible_proxy.assert_called_once_with(
            self.mock_obj, self.accessible_methods, 'mocked_method_wrapper'
        )

    def test_instance_success(self):
        assert (
            self.proxy._readable_proxy
            == self.mock_readable_proxy.return_value
        )
        assert (
            self.proxy._writable_proxy
            == self.mock_writable_proxy.return_value
        )
        assert (
            self.proxy._method_accessible_proxy
            == self.mock_method_accessible_proxy.return_value
        )

    def test_getattr_readable_attr_success(self):
        response = self.proxy.readable_attr
        assert self.mock_readable_proxy.return_value.readable_attr == response

    def test_getattr_callable_success(self):
        response = self.proxy.accessible_method
        assert (
            self.mock_method_accessible_proxy.return_value.accessible_method
            == response
        )

    def test_getattr_obj_success(self):
        response = self.proxy._obj
        assert self.mock_obj == response

    def test_setattr_writable_attr_success(self):
        self.proxy.writable_attr = 'new_value'
        assert (
            self.mock_writable_proxy.return_value.writable_attr == 'new_value')

    def test_setattr_own_proxy_success(self):
        self.proxy._own_proxy = 'new_value'
        assert self.proxy._own_proxy == 'new_value'


class TestReadableProxy(TestCase):
    def setUp(self):
        self.mock_obj = MagicMock()
        self.property_fget = MagicMock()
        self.mock_obj.property = property(self.property_fget)
        self.readable_attrs = ['readable_attr', 'property']
        self.proxy = ReadableProxy(self.mock_obj, self.readable_attrs)

    def test_getattr_readable_attr_success(self):
        self.mock_obj.readable_attr = 'value'
        result = self.proxy.readable_attr
        assert result == 'value'

    def test_getattr_property_success(self):
        self.property_fget.return_value = 'prop_value'
        result = self.proxy.property
        self.property_fget.assert_called_once_with(self.mock_obj)
        assert result == 'prop_value'

    def test_getattr_non_readable_attr_fail(self):
        with self.assertRaises(RestrictedAccessError) as context:
            _ = self.proxy.non_readable_attr
        expected_message = ERR_MSG['acc_restric'].format('non_readable_attr')
        assert str(context.exception) == expected_message

    def test_getattr_callable_attr_fail(self):
        self.mock_obj.readable_attr = MagicMock()
        with self.assertRaises(RestrictedAccessError) as context:
            _ = self.proxy.readable_attr
        expected_message = ERR_MSG['not_acc_methd'].format('readable_attr')
        assert str(context.exception) == expected_message


class TestWritableProxy(TestCase):
    def setUp(self):
        self.mock_obj = MagicMock(writable_attr='value')
        self.writable_attrs = ['writable_attr']
        self.proxy = WritableProxy(self.mock_obj, self.writable_attrs)

    def test_setattr_writable_attr_success(self):
        self.proxy.writable_attr = 'new_value'
        assert self.mock_obj.writable_attr == 'new_value'

    def test_setattr_non_writable_attr_fail(self):
        with self.assertRaises(OverrideError) as context:
            self.proxy.non_writable_attr = 'value'
        expected_message = ERR_MSG['not_modify'].format('non_writable_attr')
        assert str(context.exception) == expected_message

    def test_setattr_private_attr_success(self):
        self.proxy._private_attr = 'value'
        assert self.proxy._private_attr == 'value'

    def test_setattr_property_success(self):
        class MockObj:
            def __init__(self): self._writable_attr = 'value'
            @property
            def writable_attr(self): return self._writable_attr
            @writable_attr.setter
            def writable_attr(self, value): self._writable_attr = value

        self.mock_obj = MockObj()
        self.writable_attrs = ['writable_attr']
        self.proxy = WritableProxy(self.mock_obj, self.writable_attrs)

        self.proxy.writable_attr = 'new_value'
        assert self.mock_obj.writable_attr == 'new_value'

    def test_setattr_property_without_fset_fail(self):
        prop = property(fget=lambda x: 'value')
        type(self.mock_obj).writable_attr = prop
        with self.assertRaises(OverrideError) as context:
            self.proxy.writable_attr = 'new_value'
        expected_message = ERR_MSG['not_modify'].format('writable_attr')
        assert str(context.exception) == expected_message

    def test_setattr_callable_attr_fail(self):
        self.mock_obj.writable_attr = MagicMock()
        with self.assertRaises(OverrideError) as context:
            self.proxy.writable_attr = 'new_value'
        expected_message = ERR_MSG['methd_not_modify'].format('writable_attr')
        assert str(context.exception) == expected_message


class TestMethodAccessibleProxy(TestCase):
    def setUp(self):
        class DummyClass:
            def __init__(self): self.value = 42
            def method(self): return "method called"
            def restricted_method(self): return "restricted method called"

        self.obj = DummyClass()
        self.accessible_methods = ['method']
        self.method_wrapper = MagicMock()

    def test_getattr_accessible_method_success(self):
        proxy = MethodAccessibleProxy(self.obj, self.accessible_methods, None)
        result = proxy.method()
        assert result == "method called"

    def test_getattr_not_accessible_method_fail(self):
        proxy = MethodAccessibleProxy(self.obj, self.accessible_methods, None)
        with self.assertRaises(RestrictedAccessError) as context:
            proxy.restricted_method()
        expected_message = ERR_MSG['acc_restric'].format('restricted_method')
        assert str(context.exception) == expected_message

    def test_getattr_with_method_wrapper_success(self):
        wrapper = lambda func: lambda: f"wrapped {func()}"  # noqa: E731
        proxy = MethodAccessibleProxy(
            self.obj, self.accessible_methods, wrapper)
        result = proxy.method()
        assert result == "wrapped method called"

    def test_getattr_with_method_wrapper_called(self):
        self.method_wrapper.side_effect = (
            lambda func: lambda: f"wrapped {func()}")
        proxy = MethodAccessibleProxy(
            self.obj, self.accessible_methods, self.method_wrapper)
        result = proxy.method()
        self.method_wrapper.assert_called_once_with(
            getattr(self.obj, 'method'))
        assert result == "wrapped method called"


class TestSafeExecuter(TestCase):
    def setUp(self):
        self.mock_proxy_factory = MagicMock()
        self.safe_executer = SafeExecuter(self.mock_proxy_factory)
        self.mock_method = MagicMock()

    def test_call_success(self):
        wrapped_method = self.safe_executer(self.mock_method)
        result = wrapped_method(1, 2, key='value')

        self.mock_method.assert_called_once_with(1, 2, key='value')
        self.mock_proxy_factory.assert_called_once_with(
            self.mock_method.return_value, pass_=True)
        assert result == self.mock_proxy_factory.return_value

    def test_unproxy_args_success(self):
        proxy_instance = MagicMock(spec=SecureProxy)
        proxy_instance._obj = 'unproxied_value'
        args = (proxy_instance, 2)
        kwargs = {'key': proxy_instance}
        unproxied_args, unproxied_kwargs = self.safe_executer._unproxy_args(
            args, kwargs)

        assert unproxied_args == ('unproxied_value', 2)
        assert unproxied_kwargs == {'key': 'unproxied_value'}

    def test_proxy_return_dict_success(self):
        return_value = {'key': 'value'}
        self.mock_proxy_factory.side_effect = lambda x, pass_: x
        result = self.safe_executer._proxy_return(return_value)
        assert result == {'key': 'value'}

    def test_proxy_return_list_success(self):
        return_value = ['value1', 'value2']
        self.mock_proxy_factory.side_effect = lambda x, pass_: x
        result = self.safe_executer._proxy_return(return_value)
        assert result == ['value1', 'value2']

    def test_proxy_return_tuple_success(self):
        return_value = ('value1', 'value2')
        self.mock_proxy_factory.side_effect = lambda x, pass_: x
        result = self.safe_executer._proxy_return(return_value)
        assert result == ('value1', 'value2')

    def test_proxy_return_single_value_success(self):
        return_value = 'value'
        result = self.safe_executer._proxy_return(return_value)
        self.mock_proxy_factory.assert_called_once_with('value', pass_=True)
        assert result == self.mock_proxy_factory.return_value
