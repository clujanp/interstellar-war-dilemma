from app.core.domain.models import Civilization, Planet
from app.core.domain.services.memories import MemoriesServiceWrapper

SECURITY_PROXY = {
    Civilization: {
        'readable_attrs': ['name'],
        'writable_attrs': [],
        'accessible_methods': []
    },
    Planet: {
        'readable_attrs': ['name', 'cost'],
        'writable_attrs': [],
        'accessible_methods': []
    },
    MemoriesServiceWrapper: {
        'readable_attrs': ['length'],
        'writable_attrs': [],
        'accessible_methods': [
            'civilizations',
            'opponents',
            'skirmishes_count',
            'last_positions',
            'last_scores',
            'cooperations',
            'aggressions',
            'conquests',
            'hits',
            'loss',
            'mistakes',
        ]
    },
}
