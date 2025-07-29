import pendulum
from .parsers import parse_team_objectives, parse_series_format, parse_tournament_name
from .constants import (
    SHARED_LIVE_STATS_EVENT_KEYS,
    DRAFT_TURNS_BLUE,
    DRAFT_TURNS_RED,
    NAME_ID_MAP,
)
from ..series_state.series_state import SeriesStateSeriesStateGamesTeams
from ..central_data.get_series import GetSeriesAllSeriesEdges


def game_event_from_grid(event: dict) -> dict:
    """
    Removes the shared keys from a Riot LiveStats event and formats the remaining data

    Args:
        event: Event data dictionary
        game_id: Game ID

    Returns:
        ATG Game event formatted dictionary
    """
    # Extract schema information
    schema = event["rfc461Schema"]
    sequence_index = event["sequenceIndex"]
    game_time = event["gameTime"]

    # Extract event-specific details
    event_details = {
        key: value
        for key, value in event.items()
        if key not in SHARED_LIVE_STATS_EVENT_KEYS
    }

    return {
        "schema": schema,
        "sequence_index": sequence_index,
        "game_time": game_time,
        "source_data": event_details,
    }


def draft_event_from_grid(
    blue_draft: list[dict],
    red_draft: list[dict],
    bans: list[dict],
    game_participant_info: dict,
) -> list[dict]:

    pick_bans = []

    P_MAP = {
        NAME_ID_MAP.get(participant["championName"].lower()): participant[
            "participantID"
        ]
        for participant in game_participant_info["participants"]
    }

    for i, (blue, red) in enumerate(zip(blue_draft, red_draft)):
        is_phase_one = i < 3

        pick_bans.append(
            {
                "champion_id": blue,
                "participant_id": P_MAP[blue],
                "is_pick": True,
                "is_phase_one": is_phase_one,
                "is_blue": True,
                "pick_turn": DRAFT_TURNS_BLUE[i],
            }
        )
        pick_bans.append(
            {
                "champion_id": red,
                "participant_id": P_MAP[red],
                "is_pick": True,
                "is_phase_one": is_phase_one,
                "is_blue": True,
                "pick_turn": DRAFT_TURNS_RED[i],
            }
        )

    for idx, ban in enumerate(bans):
        pick_bans.append(
            {
                "champion_id": ban["championID"],
                "participant_id": None,
                "is_pick": False,
                "is_phase_one": idx < 6,
                "is_blue": ban["teamID"] == 100,
                "pick_turn": ban["pickTurn"],
            }
        )

    return pick_bans


def team_dto_from_grid(series_state_team: SeriesStateSeriesStateGamesTeams) -> dict:
    return {
        "bans": {},
        "objectives": parse_team_objectives(series_state_team),
        "team_id": 100 if series_state_team.side == "blue" else 200,
        "win": series_state_team.won,
        "fk_team_id": series_state_team.id,
    }


def series_from_grid(series_data: GetSeriesAllSeriesEdges) -> dict:
    return {
        "id": series_data.node.id,
        "type": series_data.node.type.name,
        "scheduled_start_time": pendulum.parse(
            series_data.node.start_time_scheduled
        ),
        "tournament_id": series_data.node.tournament.id,
        "format": parse_series_format(series_data.node.format.name),
        "external_links": {
            _.data_provider.name: _.external_entity.id
            for _ in series_data.node.external_links
        },
    }


def team_from_grid(team_data) -> dict:
    logo_url = (
        None
        if team_data.logo_url == "https://cdn.grid.gg/assets/team-logos/generic"
        else team_data.logo_url
    )
    associated_ids = {
        _.data_provider.name: _.external_entity.id for _ in team_data.external_links
    }
    associated_ids["GRID"] = team_data.id
    team_details = {
        "id": team_data.id,
        "name": team_data.name,
        "team_code": team_data.name_shortened,
        "source_data": {
            "external_ids": associated_ids,
            "logo_url": logo_url,
            "color_primary": team_data.color_primary,
            "color_secondary": team_data.color_secondary,
        },
    }
    return team_details


def tournament_from_grid(tournament_data) -> dict:
    logo_url = (
        None
        if tournament_data.logo_url
        == "https://cdn.grid.gg/assets/tournament-logos/generic"
        else tournament_data.logo_url
    )
    league, year, split, event_type = parse_tournament_name(tournament_data.name)

    external_ids = {
        _.data_provider.name: _.external_entity.id
        for _ in tournament_data.external_links
    }

    tournament_details = {
        "id": tournament_data.id,
        "name": tournament_data.name,
        "league": league,
        "year": year,
        "split": split,
        "event_type": event_type,
        "start_date": tournament_data.start_date,
        "end_date": tournament_data.end_date,
        "source_data": {
            "external_ids": external_ids,
            "name_shortened": tournament_data.name_shortened,
            "logo_url": logo_url,
        },
    }

    return tournament_details
