import re
from .constants import OBJECTIVE_NAME_MAP
from ..series_state.series_state import SeriesStateSeriesStateGamesTeams


def parse_tournament_name(
    tournament_name: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    """Parse tournament names with formats:
        league year split
        league year
        league - split year (event_type: details)

    Args:
        tournament_name (str): Full tournament name string

    Returns:
        tuple[str | None, str| None, str | None, str | None]: league year split event_type. None if parsing failed
    """
    league = None
    year = None
    split = None
    event_type = None

    # Handle bracketed event type
    if "(" in tournament_name:
        main_part = tournament_name.split("(")[0].strip()
        event_part = re.search(r"\((.*?):", tournament_name)
        if event_part:
            event_type = event_part.group(1).strip()
    else:
        main_part = tournament_name

    # Extract year
    year_match = re.search(r"20\d{2}", main_part)
    if year_match:
        year = year_match.group(0)

        # Handle dash format
        if " - " in main_part:
            parts = main_part.split(" - ", 1)
            if len(parts) > 0:
                league = parts[0].strip() or None

            if len(parts) > 1:
                rest = parts[1]
                split_match = re.search(r"(\w+)\s+" + year, rest)
                if split_match:
                    split = split_match.group(1)
        else:
            parts = main_part.split(year)
            if len(parts) > 0:
                league = parts[0].strip() or None
            if len(parts) > 1:
                split = parts[1].strip() or None

    return league, year, split, event_type


def parse_series_format(series_format: str) -> int | None:
    """Parse the "best-of-n" series format.

    Args:
        series_format (str): A string containing best-of-

    Returns:
        int | None: n, repreenting n games in a best-of-n series. None if best-of- is not found
    """
    name_split = series_format.split("best-of-")
    if len(name_split) != 2:
        return None
    return int(name_split[1])


def parse_duration(duration: str) -> int:
    """Parses the ISO 8601 formatted duration string into seconds

    Args:
        duration (str): ISO 8601 formatted string (supporting the PTHMS duration designators)

    Returns:
        int: The equivalent number of seconds
    """
    m = re.match(
        r"^PT(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S?)?$",
        duration,
    )

    if not m:
        return 0

    hours, minutes, seconds = m.groups()

    total_seconds = 0
    if hours:
        total_seconds += float(hours) * 3600
    if minutes:
        total_seconds += float(minutes) * 60
    if seconds:
        total_seconds += float(seconds)

    return int(total_seconds)


def parse_team_objectives(series_state_team: SeriesStateSeriesStateGamesTeams) -> dict:
    """Parses the objectives taken from a team object in a series_state returned from the API

    Args:
        series_state_team (SeriesStateSeriesStateGamesTeams): Team state object from a Series State

    Returns:
        dict: A dictionary of objectives taken (kills / first) matching the format found in the match-v5 API
    """
    objectives = {
        "champion": {
            "first": series_state_team.first_kill,
            "kills": series_state_team.kills,
        },
    }

    for grid_name, match_v5_name in OBJECTIVE_NAME_MAP.items():
        objective = next(
            (obj for obj in series_state_team.objectives if obj.id == grid_name), None
        )
        if objective is None:
            objectives[match_v5_name] = {"first": False, "kills": 0}
        else:
            objectives[match_v5_name] = {
                "first": objective.completed_first,
                "kills": objective.completion_count,
            }

    return objectives
