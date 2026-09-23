# pylint: disable=unused-argument
# pylint: disable=protected-access
import json
from inspect import signature
from unittest import TestCase
import requests
import responses
from app.core.domain.value_objects import Decision
from app.core.game.dto import AstroBodyDTO
from app.core.game.repositories.wrappers import StrategyRemote, StrategyLocal
from app.core.game.repositories.interfaces import IStrategy


class TestStrategyRemote(TestCase):
    """Unit tests for the StrategyRemote wrapper."""

    def setUp(self):
        """Set up test fixtures."""
        self.callback_uri = "http://michi.com/war"
        self.scenario = dict(
            opponent="Player2",
            astro=AstroBodyDTO(name="Earth", kind="planet", cost=10, production=5),
            resources=100.0,
        )

    def test_interface(self):
        """Test that StrategyRemote inherits from the correct base class."""
        assert issubclass(StrategyRemote, IStrategy)

    def test_initialization(self):
        """Test that StrategyRemote can be initialized."""
        remote_strategy = StrategyRemote(callback_uri=self.callback_uri)
        assert remote_strategy.callback_uri == self.callback_uri
        assert callable(remote_strategy) is True

    @responses.activate
    def test_request(self):
        """Test that StrategyRemote can make a request."""
        remote_strategy = StrategyRemote(callback_uri=self.callback_uri)
        responses.post(self.callback_uri, status=200, json={"decision": "ATTACK"})

        decision = remote_strategy(**self.scenario)

        assert decision == Decision.ATTACK
        assert responses.calls[0].request.url == self.callback_uri
        assert responses.calls[0].request.method == "POST"
        assert responses.calls[0].request.body.decode("utf-8") == json.dumps(
            {
                "opponent": "Player2",
                "astro": {
                    "name": "Earth",
                    "kind": "planet",
                    "cost": 10.0,
                    "production": 5.0,
                },
                "resources": 100.0,
            }
        )

    @responses.activate
    def test_request_timeout(self):
        """Test that StrategyRemote handles request timeouts."""
        remote_strategy = StrategyRemote(callback_uri=self.callback_uri)
        remote_strategy.TIMEOUT = 0.001
        responses.post(
            self.callback_uri,
            body=requests.exceptions.ConnectTimeout(),
        )
        decision = remote_strategy(**self.scenario)
        assert decision is Decision.NONE


class TestStrategyLocal(TestCase):
    """Unit tests for the StrategyLocal wrapper."""

    def setUp(self):
        """Set up test fixtures."""
        self.scenario = dict(
            opponent="Player2",
            astro=AstroBodyDTO(name="Earth", kind="planet", cost=10, production=5),
            resources=100.0,
        )

        def all_out_attack(
            opponent: str, astro: AstroBodyDTO, resources: float
        ) -> Decision:
            return Decision.ATTACK

        self.strategy_all_out_attack = all_out_attack

        def all_out_cooperate(
            opponent: str, astro: AstroBodyDTO, resources: float
        ) -> Decision:
            return Decision.COOPERATE

        self.strategy_all_out_cooperate = all_out_cooperate

    def test_interface(self):
        """Test that StrategyLocal inherits from the correct base class."""
        assert issubclass(StrategyLocal, IStrategy)

    def test_register(self):
        """Test that a local strategy can be registered."""

        @StrategyLocal.register
        def all_out_attack(
            opponent: str, astro: AstroBodyDTO, resources: float
        ) -> Decision:
            return Decision.ATTACK

        assert (
            "app://all_out_attack"
            in StrategyLocal._StrategyLocal__registered_strategies
        )

    def test_register_not_standarize_local_strategy(self):
        """Test that registering a bad local strategy raises an error."""
        with self.subTest("must be callable"):
            with self.assertRaises(ValueError) as error:
                StrategyLocal.register("not callable")
            assert str(error.exception) == ("Function 'not callable' must be callable")

        with self.subTest("must have correct arguments"):

            def bad_arguments(opponent: str) -> Decision:
                return Decision.ATTACK

            with self.assertRaises(ValueError) as error:
                StrategyLocal.register(bad_arguments)
            assert "Function bad_arguments must have parameters" in str(error.exception)

        with self.subTest("must have correct return annotation"):

            def bad_return(opponent: str, astro: AstroBodyDTO, resources: float) -> str:
                return "not a Decision"

            with self.assertRaises(ValueError) as error:
                StrategyLocal.register(bad_return)
            assert ("Function bad_return must have return annotation like") in str(
                error.exception
            )

    def test_unregister(self):
        """Test when already register function is unregister"""

        @StrategyLocal.register
        def test_strategy(
            opponent: str, astro: AstroBodyDTO, resources: float
        ) -> Decision:
            return Decision.ATTACK

        assert (
            "app://test_strategy" in StrategyLocal._StrategyLocal__registered_strategies
        )
        StrategyLocal.unregister(test_strategy)
        assert (
            "app://test_strategy"
            not in StrategyLocal._StrategyLocal__registered_strategies
        )

    def test_unregister_non_register(self):
        """Test when not register function try to unregister"""

        def not_regitered(
            opponent: str, astro: AstroBodyDTO, resources: float
        ) -> Decision:
            return Decision.ATTACK

        with self.assertRaises(ValueError) as error:
            StrategyLocal.unregister(not_regitered)
        assert str(error.exception) == ("Function 'not_regitered' not is registered.")

    def test_unregister_non_strategy(self):
        """Test when not strategy function try to unregister"""
        with self.assertRaises(ValueError) as error:
            StrategyLocal.unregister("not_regitered")
        assert str(error.exception) == ("Function 'not_regitered' must be callable")

    def test_initialization(self):
        """Test that StrategyLocal can be initialized."""
        StrategyLocal.register(self.strategy_all_out_attack)
        StrategyLocal.register(self.strategy_all_out_cooperate)

        choice_strategy = StrategyLocal(callback_uri="app://all_out_attack")

        assert signature(choice_strategy) == signature(self.strategy_all_out_attack)
        assert choice_strategy(**self.scenario) == self.strategy_all_out_attack(
            **self.scenario
        )
        assert choice_strategy(**self.scenario) == Decision.ATTACK

    def test_call_local_strategy(self):
        """Test calling a registered local strategy."""
        StrategyLocal.register(self.strategy_all_out_attack)

        choice_strategy = StrategyLocal(callback_uri="app://all_out_attack")
        result = choice_strategy(**self.scenario)

        assert result == Decision.ATTACK

    def test_call_unregistered_local_strategy(self):
        """Test calling an unregistered local strategy."""
        with self.assertRaises(KeyError) as error:
            StrategyLocal(callback_uri="app://non_existent_strategy")

        assert str(error.exception) == "'app://non_existent_strategy'"

    def test_call_bad_strategy_return_none_decision(self):
        """Test calling a strategy with bad return results in Decision.NONE."""

        def bad_strategy(
            opponent: str, astro: AstroBodyDTO, resources: float
        ) -> Decision: ...

        StrategyLocal.register(bad_strategy)
        choice_strategy = StrategyLocal(callback_uri="app://bad_strategy")
        result = choice_strategy(**self.scenario)

        assert result == Decision.NONE
