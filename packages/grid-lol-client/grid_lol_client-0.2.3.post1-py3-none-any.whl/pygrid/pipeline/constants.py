from .champions import get_champion_mappings

ID_NAME_MAP, NAME_ID_MAP = get_champion_mappings()

# These are the dictionary keys that all live stats events share. We need to remove them.
SHARED_LIVE_STATS_EVENT_KEYS = [
    "gameID",
    "gameName",
    "gameTime",
    "generationID",
    "parentGameID",
    "path",
    "platformID",
    "playbackID",
    "repeater_timestamp",
    "rfc001Scope",
    "rfc190Scope",
    "rfc460Hostname",
    "rfc460Timestamp",
    "rfc461Schema",
    "rootGameID",
    "sequenceIndex",
    "source_type",
    "stageID",
]

# Draft pick turns (i.e. the numerical order in which champs are picked by side)
DRAFT_TURNS_BLUE = [1, 4, 5, 8, 9]
DRAFT_TURNS_RED = [2, 3, 6, 7, 10]

OBJECTIVE_NAME_MAP = {
    "slayBaron": "baron",
    "slayRiftHerald": "riftHerald",
    "slayVoidGrub": "horde",
    "slayDragon": "dragon",
    "destroyTower": "tower",
    "destroyFortifier": "inhibitor",
}
