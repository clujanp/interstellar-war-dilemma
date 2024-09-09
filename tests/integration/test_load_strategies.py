import init  # noqa: F401
from pytest import fixture
from pytest_mock import MockerFixture
from app.config.injection_dependency import (
    get_gameplay_controller, GameplayController)
from app.config.local_strategies_repository import REPO_CONFIG
from app.adapters.repositories.strategy.proxies.exceptions import (
    OverrideError, RestrictedAccessError)


@fixture
def setup_gameplay(mocker: MockerFixture) -> GameplayController:
    mocker.patch.dict(
        'app.config.local_strategies_repository.REPO_CONFIG',
        {**REPO_CONFIG, 'strategy_path': 'tests/integration/mocks/strategies'}
    )
    yield get_gameplay_controller()


def test_load_strategies(
    setup_gameplay: GameplayController, mocker: MockerFixture
):
    from tests.integration.mocks.strategies.mock_strategy_1 import test01

    gameplay = setup_gameplay
    mock_logger_error = mocker.patch('logging.Logger.error')

    strategies_use_cases = gameplay.context['use_cases']['strategies']
    expected_stratgies = {
        'test01': test01,
    }
    strategies = strategies_use_cases.load_strategies()

    # validate all errors are logged
    expected_errors = {
        ValueError:
            "Strategy 'test_fail1' must return a boolean value, got None",
        TypeError:
            "test_fail2() got an unexpected keyword argument 'opponent'",
        RestrictedAccessError:
            "Access to 'memory' is restricted",
        OverrideError:
            "Cannot modify attribute: memory",
    }
    for args, kwargs in mock_logger_error.call_args_list:
        assert str(args[0]) == expected_errors[type(args[0])]

    assert all(
        name in expected_stratgies.keys()
        and callable(strategy)
        for name, strategy in strategies.items()
    )
