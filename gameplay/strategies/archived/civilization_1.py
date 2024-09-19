from . import BuiltInStrategies, Position, Planet, Civilization, Score


# def grunts(
#     self: Civilization, planet: Planet, opponent: Civilization
# ) -> bool:
#     return True


# def sangheili(
#     self: Civilization, planet: Planet, opponent: Civilization
# ) -> bool:
#     return BuiltInStrategies.always_aggression()


def el_charlie(
    self: Civilization, planet: Planet, opponent: Civilization
) -> bool:
    aggre_sta = self.memory.aggressions(opponent)
    percent = aggre_sta.percent
    if percent > 0.91:
        return False
    return True


# def the_covenant(
#     self: Civilization, planet: Planet, opponent: Civilization
# ) -> bool:
#     return BuiltInStrategies.reply_last(self=self, opponent=opponent)


def el_juan(
    self: Civilization, planet: Planet, opponent: Civilization
) -> bool:
    # Comprobar si el oponente está en la memoria de civilizaciones conocidas
    if opponent in self.memory.civilizations():
        return True
    return True


def the_king(
    self: Civilization, planet: Planet, opponent: Civilization
) -> bool:
    if self.memory.last_positions(opponent) == Position.COOPERATION:
        return True
    if self.memory.last_positions(opponent) == Position.AGGRESSION:
        return False
    return False


def el_juan_2(
        self: Civilization, planet: Planet, opponent: Civilization
) -> bool:
    # Si el oponente es conocido y hemos ganado en el pasado, atacamos
    if opponent in self.memory.civilizations():
        last_scores = self.memory.last_scores(opponent)
        if (
            last_scores == Score.WIN or last_scores
            == Score.LOSE
        ):
            return False
    return True

    # # Si el oponente es desconocido o hemos perdido antes, evaluar condiciones del planeta y la fuerza del oponente
    # if self.strength > opponent.strength * 1.2:
    #     # Si somos significativamente más fuertes, atacar
    #     logger.info(f"Attacking {opponent.name} due to superior strength.")
    #     return True
    # elif planet.resources > opponent.resources * 1.5:
    #     # Si el planeta tiene más recursos, atacar para controlarlos
    #     logger.info(f"Attacking {opponent.name} to gain control of superior resources.")
    #     return True
    # else:
    #     # Si no estamos seguros de ganar, fortificarse y esperar una mejor oportunidad
    #     logger.info(f"Defensive stance against {opponent.name}, awaiting better conditions.")
    #     return False


# def the_charlie(
#     self: Civilization, planet: Planet, opponent: Civilization
# ) -> bool:
#     memory = self.memory
#     result = memory.cooperations(opponent)
#     percent = result.percent * 100
#     if percent > 75:
#         return True
#     else:
#         return False
