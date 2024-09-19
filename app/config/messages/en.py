ERR_SECURE_PROXY = {
    'not_acc_methd': "Cannot access method: {0}",
    'acc_restric': "Access to '{0}' is restricted",
    'not_modify': "Cannot modify attribute: {0}",
    'methd_not_modify': "Cannot modify method: {0}",
    'not_secure_proxy': "Object '{0}' is not configurable as secure proxy",
    'debug_secure_proxy': "Secure proxy created for {0}",
    'debug_metd_warps': "Method {0} of {1} wrapped",
    'debug_unproxy': "Unproxying args:{0} | kwargs:{1}",
    'debug_proxy': "Trying proxying {0}",
}


ERR_STRATEGY_SERVICE = {
    'must_return': "Strategy '{0}' must return a boolean value, got {1}",
    'signature': "Invalid strategy signature of '{0}'",
}


ERR_MODELS_VALIDATIONS = {
    'civilizations_diff': "Civilizations must be different",
    'not_enough_resources': "Not enough resources to colonize the planet",
    'planet_colonized': "Planet already colonized",
    'owner_data_dict': "Owner data must be a dictionary",
    'owner_data_max_size': "Owner data must have less than 10 items",
    'owner_data_keys': "Owner data keys must be strings",
    'owner_data_values':
        "Owner data values must be int, float, str, bool, Civilization, "
        "Planet or None",
}

ERR_LOCAL_REPOSITORY_STRATEGY = {
    'warning_more_than_one': "More than one strategy found in {0}",
    'debug_loaded': "Loaded strategies: {0}",
}


ERR_SKIRMISH_SERVICE = {
    'already_resolved': "Skirmish already resolved",
}
