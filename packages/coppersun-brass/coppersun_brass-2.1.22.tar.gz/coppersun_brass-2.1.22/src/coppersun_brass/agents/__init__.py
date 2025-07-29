"""Copper Alloy Brass Agents Module"""

# Import specific agents only when needed to avoid circular imports
__all__ = ['WatchAgent', 'ScoutAgent', 'StrategistAgent']

def __getattr__(name):
    if name == 'WatchAgent':
        from .watch.watch_agent import WatchAgent
        return WatchAgent
    elif name == 'ScoutAgent':
        from .scout.scout_agent import ScoutAgent
        return ScoutAgent
    elif name == 'StrategistAgent':
        from .strategist.strategist_agent import StrategistAgent
        return StrategistAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")