import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch, call
from app.core.domain.services import RoundService


class TestRoundService(TestCase):
    def setUp(self):
        self.civ1 = MagicMock(name='civ1')
        self.civ2 = MagicMock(name='civ2')
        self.civ3 = MagicMock(name='civ3')
        self.civ4 = MagicMock(name='civ4')

        self.civ1.memory = MagicMock(
            civilizations=lambda: [self.civ2, self.civ3],
            length=3,
            skirmishes_count=lambda _:
                {self.civ2: 2, self.civ3: 1, self.civ4: 0}[_],
        )
        self.civ2.memory = MagicMock(
            civilizations=lambda: [self.civ1],
            length=2,
            skirmishes_count=lambda _:
                {self.civ1: 2, self.civ3: 0, self.civ4: 0}[_],
        )
        self.civ3.memory = MagicMock(
            # mocked memories with all civilizations
            civilizations=lambda: [self.civ1, self.civ2, self.civ4],
            length=5,
            skirmishes_count=lambda _:
                {self.civ1: 2, self.civ2: 2, self.civ4: 1}[_],
        )
        self.civ4.memory = MagicMock(
            civilizations=lambda: [],
            length=0,
            skirmishes_count=lambda _: 0,
        )
        self.civilizations = [self.civ1, self.civ2, self.civ3, self.civ4]

    @patch('app.core.domain.services.round.Round')
    def test_create_round_with_default_values(self, mock_round: MagicMock):
        mock_skirmish = MagicMock()
        response = RoundService.create(1, [mock_skirmish])
        mock_round.assert_called_once_with(
            number=1, skirmishes=[mock_skirmish])
        assert mock_round.return_value == response

    @patch("app.core.domain.services.round.choices")
    def test_decide_opponents_success(self, mock_choices: MagicMock):
        mock_choices.side_effect = [
            [self.civ4], [self.civ3], [self.civ4], [self.civ1]
        ]
        response = RoundService.decide_opponents(self.civilizations)
        mock_choices.assert_has_calls([
            call((self.civ2, self.civ3, self.civ4,), weights=(2, 3, 4), k=1),
            call((self.civ3,), weights=(3,), k=1),
        ])
        assert [
            (self.civ1, self.civ4),
            (self.civ2, self.civ3),
        ] == response

    def test_decide_opponents_number_fail(self):
        with self.assertRaises(AssertionError) as context:
            RoundService.decide_opponents(self.civilizations[:-1])
        assert "Invalid number of civilizations" in str(context.exception)
