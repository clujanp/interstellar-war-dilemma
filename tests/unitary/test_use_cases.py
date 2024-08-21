import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch, call
from app.core.interfaces.use_cases import (
    PlanetUseCases, CivilizationUseCases, SkirmishUseCases, RoundUseCases,
    MemoriesUseCases
)


class TestPlanetUseCases(TestCase):
    def test_init_success(self):
        service = MagicMock()
        use_case = PlanetUseCases(service)
        assert use_case.service == service

    def test_generate_success(self):
        service = MagicMock()
        use_case = PlanetUseCases(service)
        planets = [MagicMock(), MagicMock()]
        service.create.side_effect = planets
        response = use_case.generate(2)
        service.create.assert_has_calls([call() for _ in range(2)])
        assert planets == response


class TestCivilizationUseCases(TestCase):
    def test_init_success(self):
        service = MagicMock()
        use_case = CivilizationUseCases(service)
        assert use_case.service == service

    def test_register_success(self):
        service = MagicMock()
        use_case = CivilizationUseCases(service)
        civilization = MagicMock()
        service.create.return_value = civilization
        response = use_case.register('name', 'strategy', 10)
        service.create.assert_called_once_with('name', 'strategy', 10)
        assert civilization == response


class TestSkirmishUseCases(TestCase):
    def setUp(self):
        self.civ1 = MagicMock(name='civ1')
        self.civ2 = MagicMock(name='civ2')
        self.civ3 = MagicMock(name='civ3')
        self.planet1 = MagicMock(name='planet1')
        self.planet2 = MagicMock(name='planet2')
        self.planet3 = MagicMock(name='planet3')
        self.planets = [self.planet1, self.planet2, self.planet3]
        self.civ1.memory = MagicMock(
            civilizations=lambda: [self.civ2, self.civ3],
            length=3,
            skirmishes_count=lambda _:
                {self.civ2: 2, self.civ3: 1}[_],
        )
        self.civ2.memory = MagicMock(
            civilizations=lambda: [self.civ1],
            length=2,
            skirmishes_count=lambda _:
                {self.civ1: 2, self.civ3: 0}[_],
        )
        self.civ3.memory = MagicMock(
            civilizations=lambda: [self.civ1, self.civ2],
            length=3,
            skirmishes_count=lambda _:
                {self.civ1: 1, self.civ2: 1}[_],
        )

    def test_init_success(self):
        service = MagicMock()
        use_case = SkirmishUseCases(service)
        assert use_case.service == service

    def test_create_success(self):
        service = MagicMock()
        use_case = SkirmishUseCases(service)
        skirmishes = [MagicMock(), MagicMock(), MagicMock()]
        service.create.side_effect = skirmishes
        response = use_case.create(
            [
                (self.civ1, self.civ2),
                (self.civ2, self.civ3),
                (self.civ3, self.civ1)
            ],
            self.planets
        )
        service.create.assert_has_calls([
            call(self.planet1, self.civ1, self.civ2),
            call(self.planet2, self.civ2, self.civ3),
            call(self.planet3, self.civ3, self.civ1),
        ])
        assert skirmishes == response

    def test_create_number_fail(self):
        service = MagicMock()
        use_case = SkirmishUseCases(service)
        with self.assertRaises(AssertionError) as context:
            use_case.create(
                [  # FAIL: 2 skirmishes for 3 planets
                    (self.civ1, self.civ2),
                    (self.civ2, self.civ3),
                ],
                self.planets
            )
        assert "Invalid number of skirmishes" in str(context.exception)

    def test_resolve_success(self):
        service = MagicMock()
        use_case = SkirmishUseCases(service)
        skirmishes = [MagicMock(), MagicMock(), MagicMock()]
        use_case.resolve(skirmishes)
        service.resolve.assert_has_calls([call(_) for _ in skirmishes])


class TestRoundUseCases(TestCase):
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

    @patch('app.core.domain.services.round.RoundService.decide_opponents')
    def test_decide_opponents_success(self, mock_decide_opponents: MagicMock):
        response = RoundUseCases.decide_opponents(self.civilizations)
        mock_decide_opponents.assert_called_once_with(self.civilizations)
        assert mock_decide_opponents.return_value == response

    def test_create_round_success(self):
        service = MagicMock()
        use_case = RoundUseCases(service)
        skirmishes = [MagicMock(), MagicMock()]
        response = use_case.create_round(1, skirmishes)
        service.create.assert_called_once_with(1, skirmishes)
        assert service.create.return_value == response


class TestMemoriesUseCases(TestCase):
    def setUp(self):
        self.civ1 = MagicMock(name='civ1')
        self.civ2 = MagicMock(name='civ2')
        self.civ3 = MagicMock(name='civ3')
        self.civ4 = MagicMock(name='civ4')
        self.civ1.memory = MagicMock(remember=MagicMock())
        self.civ2.memory = MagicMock(remember=MagicMock())
        self.civ3.memory = MagicMock(remember=MagicMock())
        self.civ4.memory = MagicMock(remember=MagicMock())
        self.skirmish1 = MagicMock(name='skirmish1', civilizations=[self.civ1])
        self.skirmish2 = MagicMock(name='skirmish2', civilizations=[self.civ2])
        self.skirmish3 = MagicMock(name='skirmish3', civilizations=[self.civ3])
        self.skirmish4 = MagicMock(name='skirmish4', civilizations=[self.civ4])

    @patch("app.core.interfaces.use_cases.MemoriesServiceWrapper")
    def test_init_success(self, mock_service: MagicMock):
        mock_service.return_value = MagicMock()
        use_case = MemoriesUseCases()
        assert mock_service.return_value == use_case.service

    @patch("app.core.interfaces.use_cases.MemoriesServiceWrapper")
    def test_record_round_in_memories_success(self, mock_service: MagicMock):
        mock_service.return_value = MagicMock()
        use_case = MemoriesUseCases()
        skirmishes = [self.skirmish1, self.skirmish2, self.skirmish3]
        use_case.record_round_in_memories(skirmishes)

        self.civ1.memory.remember.assert_called_once_with(self.skirmish1)
        self.civ2.memory.remember.assert_called_once_with(self.skirmish2)
        self.civ3.memory.remember.assert_called_once_with(self.skirmish3)
        mock_service.return_value.remember.assert_has_calls(
            [call(skirmish) for skirmish in skirmishes]
        )

    @patch("app.core.interfaces.use_cases.MemoriesServiceWrapper")
    def test_summary_success(self, mock_service: MagicMock):
        mock_service.return_value = MagicMock()
        use_case = MemoriesUseCases()
        response = use_case.summary()
        assert mock_service.return_value.summary.return_value == response
        mock_service.return_value.summary.assert_called_once_with()

    @patch("app.core.interfaces.use_cases.MemoriesServiceWrapper")
    def test_summary_sucess(self, mock_service: MagicMock):
        mock_service.return_value = MagicMock()
        use_case = MemoriesUseCases()
        response = use_case.summary()
        mock_service.return_value.summary.assert_called_once_with()
        assert mock_service.return_value.summary.return_value == response

    @patch("app.core.interfaces.use_cases.MemoriesServiceWrapper")
    def test_report_success(self, mock_service: MagicMock):
        mock_service.return_value = MagicMock()
        use_case = MemoriesUseCases()
        response = use_case.report()
        assert mock_service.return_value.report.return_value == response
        mock_service.return_value.report.assert_called_once_with()

    @patch("app.core.interfaces.use_cases.MemoriesServiceWrapper")
    def test_report_save(self, mock_service: MagicMock):
        mock_service.return_value = MagicMock()
        use_case = MemoriesUseCases()
        use_case.save()
        mock_service.return_value.save.assert_called_once_with()
