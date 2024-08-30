from gameplay.strategy import BuiltInStrategies


REPO_CONFIG = {
    'strategy_path': 'gameplay/strategies',
    'search_pattern': "*.py",
    'built_in_strategies': {
        'always_cooperation': BuiltInStrategies.always_cooperation,
        'always_aggression': BuiltInStrategies.always_aggression,
        'random': BuiltInStrategies.random,
        'reply_last': BuiltInStrategies.reply_last,
    }
}
