from . import (  # noqa: F401
    Civilization, Planet, Memories, Position, Statistic, Cost, Score,
    BuiltInStrategies
)


def test02(memories, planet, opponent, resources):
    # Si el planeta tiene un costo alto y los recursos son bajos, coopero.
    if planet.cost == Cost.HIGH and resources < 3:
        return Position.COOPERATION

    # Si el oponente ha sido agresivo más del 60% del tiempo, atacaré.
    if memories.aggressions(opponent).percent > 60:
        return Position.AGGRESSION

    # Si he ganado las últimas 3 escaramuzas, puedo permitirme cooperar.
    if memories.last_scores(opponent, 3) == [Score.WIN, Score.WIN, Score.WIN]:
        return Position.COOPERATION

    # Si el oponente ha cooperado en el pasado, replicaré su comportamiento.
    last_opponent_positions = memories.last_positions(opponent, 1)
    if (
        last_opponent_positions
        and last_opponent_positions[0] == Position.COOPERATION
    ):
        return Position.COOPERATION

    # Si ninguna condición se cumple, atacaré por defecto.
    return Position.AGGRESSION
