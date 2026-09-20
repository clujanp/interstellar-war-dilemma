# pylint: disable=unused-argument
# pylint: disable=protected-access
from itertools import product
from unittest import TestCase
from app.core.domain.value_objects import Decision
from app.core.game.dto import AstroBodyDTO
from app.core.game.repositories.strategies import StrategiesRepo
from app.core.game.repositories.wrappers import StrategyLocal


class TestStrategiesRepo(TestCase):
    """Unit tests for the strategies repository."""

    def setUp(self):
        """Set up the repository and values shared by the test cases."""

        @StrategyLocal.register
        def all_out_attack(
            opponent: str, astro: AstroBodyDTO, resources: float
        ) -> Decision:
            return Decision.ATTACK

        @StrategyLocal.register
        def all_out_cooperate(
            opponent: str, astro: AstroBodyDTO, resources: float
        ) -> Decision:
            return Decision.COOPERATE

        @StrategyLocal.register
        def all_out_neutral(
            opponent: str, astro: AstroBodyDTO, resources: float
        ) -> Decision:
            return Decision.NONE

        self.repo = StrategiesRepo()
        self.remote_strategies = (
            "http://michi.com/war",
            "http://michi.com/peace",
            "http://michi.com/neutral",
        )
        self.local_strategies = (
            "app://all_out_attack",
            "app://all_out_cooperate",
            "app://all_out_neutral",
        )
        self.players = ("Player1", "Player2", "Player3")

    def test_register_remote_strategy(self):
        """Test registering a remote strategy."""
        for strategy, player in zip(self.remote_strategies, self.players):
            self.repo.register_strategy(strategy, player)

        assert len(self.repo._StrategiesRepo__strategies) == 3
        for uri_and_name, strategy in self.repo._StrategiesRepo__strategies.items():
            uri, _name = uri_and_name
            assert uri == strategy.callback_uri
        assert list(self.repo._StrategiesRepo__strategies.keys()) == [
            ("http://michi.com/war", "Player1"),
            ("http://michi.com/peace", "Player2"),
            ("http://michi.com/neutral", "Player3"),
        ]

    def test_register_local_strategy(self):
        """Test registering a local strategy."""
        for strategy, player in product(self.local_strategies, self.players):
            self.repo.register_strategy(strategy, player)
        assert len(self.repo._StrategiesRepo__strategies) == 9
        for uri_and_name, strategy in self.repo._StrategiesRepo__strategies.items():
            uri, _name = uri_and_name
            assert uri.split("://")[1] == strategy.local_strategy.__name__
        assert list(self.repo._StrategiesRepo__strategies.keys()) == [
            ("app://all_out_attack", "Player1"),
            ("app://all_out_attack", "Player2"),
            ("app://all_out_attack", "Player3"),
            ("app://all_out_cooperate", "Player1"),
            ("app://all_out_cooperate", "Player2"),
            ("app://all_out_cooperate", "Player3"),
            ("app://all_out_neutral", "Player1"),
            ("app://all_out_neutral", "Player2"),
            ("app://all_out_neutral", "Player3"),
        ]

    def test_register_idempotent_remote_strategy(self):
        """Test registering an remote strategy again."""
        uri = self.remote_strategies[0]
        player = self.players[0]
        self.repo.register_strategy(uri, player)
        self.repo.register_strategy(uri, player)

        assert len(self.repo._StrategiesRepo__strategies.keys()) == 1

    def test_register_existing_remote_strategy(self):
        """Test registering an existing remote strategy."""
        uri = self.remote_strategies[0]
        player = self.players[0]
        self.repo.register_strategy(uri, player)

        with self.assertRaises(ValueError) as error:
            self.repo.register_strategy(uri, "other")

        assert str(error.exception) == (
            f"A strategy with callback URI '{uri}' "
            "is already registered under a different name."
        )

    def test_register_local_strategy_with_different_name(self):
        """Test rejecting a remote URI registered with another name."""
        strategy = self.local_strategies[0]
        self.repo.register_strategy(strategy, "Player1")
        self.repo.register_strategy(strategy, "Player2")
        self.repo.register_strategy(strategy, "Player3")

        assert len(self.repo._StrategiesRepo__strategies.keys()) == 3

    def test_register_invalid_uri(self):
        """Test rejecting a strategy URI with an unsupported scheme."""
        strategy = "invalid://strategy"
        with self.assertRaises(Exception) as error:
            self.repo.register_strategy(strategy, self.players[0])

        assert strategy in str(error.exception)
        assert self.repo.list_strategies() == {}

    def test_unregister_registered_strategy(self):
        """Test unregistering a registered strategy."""
        strategy = self.local_strategies[0]
        player = self.players[0]
        self.repo.register_strategy(strategy, player)

        self.repo.unregister_strategy(strategy, player)

        assert self.repo.get_strategy(strategy, player) is None

    def test_unregister_missing_strategy(self):
        """Test that unregistering a missing strategy does nothing."""
        self.repo.unregister_strategy(self.local_strategies[0], self.players[0])
        assert self.repo.list_strategies() == {}

    def test_get_registered_strategy(self):
        """Test retrieving a registered strategy."""
        strategy = self.remote_strategies[0]
        player = self.players[0]
        self.repo.register_strategy(strategy, player)

        registered = self.repo.get_strategy(strategy, player)

        assert registered is not None
        assert registered.callback_uri == strategy

    def test_get_missing_strategy(self):
        """Test returning none when retrieving a missing strategy."""
        strategy = self.repo.get_strategy(self.local_strategies[0], self.players[0])
        assert strategy is None

    def test_list_strategies(self):
        """Test listing all registered strategies."""
        for strategy, player in zip(self.remote_strategies, self.players):
            self.repo.register_strategy(strategy, player)

        strategies = self.repo.list_strategies()

        assert list(strategies) == [
            ("http://michi.com/war", "Player1"),
            ("http://michi.com/peace", "Player2"),
            ("http://michi.com/neutral", "Player3"),
        ]

    def test_list_strategies_returns_a_copy(self):
        """Test returning a copy of the registered strategies mapping."""
        strategy = self.local_strategies[0]
        player = self.players[0]
        self.repo.register_strategy(strategy, player)

        strategies = self.repo.list_strategies()
        strategies.clear()

        assert self.repo.get_strategy(strategy, player) is not None
