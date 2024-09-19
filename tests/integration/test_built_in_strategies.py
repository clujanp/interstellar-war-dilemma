import init  # noqa: F401
from pytest import fixture
from pytest_mock import MockerFixture
from unittest.mock import call
from typing import List
from gameplay.strategy import BuiltInStrategies as BIS
from gameplay.classes import Civilization, Memories, Position


COO = Position.COOPERATION
AGR = Position.AGGRESSION


@fixture
def mock_memories(mocker: MockerFixture):
    memories = mocker.create_autospec(Memories, instance=True)
    return memories


@fixture
def mock_civilization(mocker: MockerFixture):
    civilization = mocker.create_autospec(Civilization, instance=True)
    return civilization


def simulate_rounds(strategy, opponent, memories) -> List[bool]:
    return [strategy(opponent=opponent, memories=memories) for _ in range(10)]


def test_always_cooperation_success(
    mock_civilization: Civilization, mock_memories: Memories
):
    mock_memories.last_positions.return_value = COO
    assert [
        COO for _ in range(10)
    ] == simulate_rounds(
        BIS.always_cooperation, mock_civilization, mock_memories)
    mock_memories.last_positions.assert_not_called()


def test_always_aggression_success(
    mock_civilization: Civilization, mock_memories: Memories
):
    mock_memories.last_positions.return_value = AGR
    assert [
        AGR for _ in range(10)
    ] == simulate_rounds(
        BIS.always_aggression, mock_civilization, mock_memories)
    mock_memories.last_positions.assert_not_called()


def test_random_strategy_success(
    mock_civilization: Civilization,
    mock_memories: Memories,
    mocker: MockerFixture,
):
    mock_random = mocker.patch('gameplay.strategy.choice')
    random_choices = [x for _ in range(5) for x in (COO, AGR,)]
    mock_random.side_effect = random_choices
    assert random_choices == simulate_rounds(
        BIS.random, mock_civilization, mock_memories)
    mock_memories.last_positions.assert_not_called()


def test_tic_for_tac_success(
    mock_civilization: Civilization, mock_memories: Memories
):
    mock_memories.last_positions.side_effect = [
        [], [AGR], [COO], [AGR], [COO], [AGR], [AGR], [AGR], [COO], [COO],
        [COO]
    ]
    expected = [COO, AGR, COO, AGR, COO, AGR, AGR, AGR, COO, COO]
    assert expected == simulate_rounds(
        BIS.tic_for_tac, mock_civilization, mock_memories)
    assert [
        call(mock_civilization) for _ in range(10)
    ] == mock_memories.last_positions.call_args_list


def test_friedman_success(
    mock_civilization: Civilization,
    mock_memories: Memories,
):
    percents = [0, 0, 0, 0.333, 0.25, 0.4, 0.5, 0.57, 0.5, 0.444]
    expected = [COO, COO, COO, AGR, AGR, AGR, AGR, AGR, AGR, AGR]
    responses = []
    for percent in percents:
        mock_memories.aggressions.return_value.percent = percent
        responses.append(
            BIS.friedman(opponent=mock_civilization, memories=mock_memories))
    assert expected == responses
    assert [
        call(mock_civilization) for _ in range(10)
    ] == mock_memories.aggressions.call_args_list


def test_joss_strategy_success(
    mock_civilization: Civilization,
    mock_memories: Memories,
    mocker: MockerFixture,
):
    mock_random = mocker.patch('gameplay.strategy.random')
    random_choices = [0.0 if i == 7 else 1.0 for i in range(1, 11)]
    mock_random.side_effect = random_choices

    mock_memories.last_positions.side_effect = [
        [], [COO], [COO], [AGR], [COO], [COO], [COO], [COO], [COO], [COO],
        [COO]
    ]
    expected = [COO, COO, COO, AGR, COO, COO, AGR, COO, COO, COO]
    assert expected == simulate_rounds(
        BIS.joss, mock_civilization, mock_memories)
    mock_memories.last_positions.assert_called()


def test_sample_strategy_success(
    mock_civilization: Civilization, mock_memories: Memories
):
    mock_memories.skirmishes_count.side_effect = [i for i in range(10)]
    mock_memories.last_positions.side_effect = [
        [COO, AGR], [AGR, AGR], [AGR, COO], [COO, COO],
        [COO, AGR], [AGR, COO], [COO, AGR], [AGR, AGR], [AGR, COO],
    ]
    expected = [COO, COO, COO, AGR, COO, COO, COO, COO, COO, AGR]
    assert expected == simulate_rounds(
        BIS.sample, mock_civilization, mock_memories)
    assert [
        call(mock_civilization, 2) for _ in range(8)
    ] == mock_memories.last_positions.call_args_list
    assert [
        call(mock_civilization) for _ in range(10)
    ] == mock_memories.skirmishes_count.call_args_list


def test_tester_strategy_success(
    mock_civilization: Civilization, mock_memories: Memories
):
    mock_memories.skirmishes_count.side_effect = [i for i in range(10)]
    mock_memories.first_positions.side_effect = [[COO, AGR] for _ in range(8)]
    mock_memories.last_positions.side_effect = [
        [AGR], [AGR], [COO], [COO], [AGR], [COO], [COO], [COO], [COO]]
    expected = [COO, AGR, AGR, AGR, COO, COO, AGR, COO, COO, COO]
    assert expected == simulate_rounds(
        BIS.tester, mock_civilization, mock_memories)
    assert [
        call(mock_civilization) for _ in range(10)
    ] == mock_memories.skirmishes_count.call_args_list
    assert [
        call(mock_civilization, 2) for _ in range(8)
    ] == mock_memories.first_positions.call_args_list
    assert [
        call(mock_civilization) for _ in range(8)
    ] == mock_memories.last_positions.call_args_list
