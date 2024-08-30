import init  # noqa: F401
import logging
from pytest import fixture
from pytest_mock import MockerFixture
from app.config.injection_dependency import (
    get_gameplay_controller, GameplayController)
from app.config.local_strategies_repository import REPO_CONFIG


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
    logging.info(f"{strategies = }")

    # validate all errors are logged
    expected_errors = [
        (ValueError,
         "Strategy 'test_fail1' must return a boolean value, got None",),
        (TypeError,
         "test_fail2() got an unexpected keyword argument 'opponent'",),
    ]
    for error_args, expected in zip(
        mock_logger_error.call_args_list,
        expected_errors
    ):
        assert isinstance(error_args[0][0], expected[0])
        assert str(error_args[0][0]) == expected[1]

    assert all(
        name in expected_stratgies.keys()
        and callable(strategy)
        for name, strategy in strategies.items()
    )
