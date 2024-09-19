from .controller import GameplayController as Controller
from app.utils.functions import snake_to_pascal
from app.core.domain.models import Score
from app.application.logging import logger


# controller(prompt) -> process(context) -> rasterize(template, context)


@Controller.scenario('welcome', 'welcome.txt')
def welcome(context: dict, *_) -> None:
    ...


@Controller.scenario('start', 'civilizations_start.txt', alias=['s'])
def start(context: dict, *_) -> None:
    logger.start_stopwatch('start')
    civilization_use_cases = context['use_cases']['civilizations']
    strategies_use_cases = context['use_cases']['strategies']
    initial_resources = context['config']['initial_resources']
    plus_civ_name = context['config']['complementary_civilization_name']

    strategies = strategies_use_cases.load_strategies()
    context['civilizations'] = []
    for name, strategy in strategies.items():
        name = snake_to_pascal(name)
        civ = civilization_use_cases.register(
            name, strategy, initial_resources)
        context['civilizations'].append(civ)

    if len(context['civilizations']) % 2 > 0:
        aditional_civ = civilization_use_cases.register(
            plus_civ_name,
            strategies_use_cases.select_random_builtin(),
            initial_resources,
        )
        context['civilizations'].append(aditional_civ)
    context['rounds'] = []
    logger.stop_stopwatch('start', "Start gameplay ⏱️  {ms}ms")


@Controller.scenario('round', 'rounds.txt', alias=['r', 'rnd'])
def rounds(context: dict, iterations: str = None, *_) -> None:
    logger.start_stopwatch('rounds')
    assert iterations is None or iterations.isdigit(), (
        "Invalid number of rounds")
    iterations: int = int(iterations or 1)

    civilizations = context.get('civilizations')
    use_cases_round = context['use_cases']['round']
    use_cases_planet = context['use_cases']['planet']
    use_cases_skirmish = context['use_cases']['skirmish']
    memories = context['memories']

    assert civilizations, "Civilizations not registered"
    logger.checkpoint_stopwatch('rounds', "Rounds prepare ⏱️  {ms}ms")

    for _ in range(iterations):
        logger.start_stopwatch('iter')
        logger.set_checkpoint_stopwatch('rounds')

        opponents = use_cases_round.decide_opponents(civilizations)
        logger.checkpoint_stopwatch('iter', "decide opponents ⏱️  {ms}ms")
        planets = use_cases_planet.generate(len(opponents))
        logger.checkpoint_stopwatch('iter', "generate planets ⏱️  {ms}ms")

        skirmishes = use_cases_skirmish.create(opponents, planets)
        logger.checkpoint_stopwatch('iter', "create skirmishes ⏱️  {ms}ms")
        use_cases_skirmish.resolve(skirmishes)
        logger.checkpoint_stopwatch('iter', "resolve skirmishes ⏱️  {ms}ms")

        memories.record_round_in_memories(skirmishes)
        number = len(context['rounds']) + 1
        context['rounds'].append(
            use_cases_round.create_round(number, skirmishes))
        context['n_last_rounds'] = iterations
        logger.checkpoint_stopwatch('iter', "save round ⏱️  {ms}ms")
        logger.checkpoint_stopwatch(
            'rounds', f"Round {number} ⏱️  {{ms}}ms")

    logger.stop_stopwatch(
        'rounds', f"Process {iterations} rounds ⏱️  {{ms}}ms")


@Controller.scenario('summary', 'summary.txt', alias=['t', 'sum'])
def summary(context: dict, *_) -> None:
    context['summary'] = context['memories'].summary()


@Controller.scenario('end', 'end.txt', alias=['x'])
def end(context: dict, *_) -> None:
    memories = context['memories']

    context['max_score'] = Score.MAX_SCORE
    context['report'] = memories.report()
    context['report']['rounds_len'] = len(context['rounds'])
    # context['finished'] = True
    context['memories'].save()
    context['summary'] = context['memories'].summary()
