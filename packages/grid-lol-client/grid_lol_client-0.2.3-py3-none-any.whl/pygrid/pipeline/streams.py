import orjson
from httpx import Response
from io import BufferedReader


def get_line_iterator(input_obj):
    if isinstance(input_obj, Response):
        return input_obj.iter_lines()
    else:
        return input_obj


def process_live_stats(live_stats_input: BufferedReader | Response):
    """Function to process a binary read or httpx stream of a Riot LiveStats JSONL file

    Args:
        live_stats_input (BufferedReader | httpx.stream): Input file or httpx Reponse object to download series

    Returns:
        game_participant_info (dict): game_info event
        game_end_event (dict): game_end event
        final_stats_update (dict): The final stats_update event
        final_champ_select (dict): The final champ_select event which contains the completed draft
        saved_events (list): All events except for champ_select events
    """
    saved_events = []
    game_participant_info = None
    game_end_event = None
    final_stats_update = None
    final_champ_select = None

    with live_stats_input as input_stream:
        for line in get_line_iterator(input_stream):
            if line:
                event = orjson.loads(line)
                schema = event["rfc461Schema"]
                if schema == "game_info":
                    game_participant_info = event
                    # The game_info event is missing a gameTime which causes future processing to fail.
                    event["gameTime"] = -1
                if schema == "game_end":
                    game_end_event = event
                if schema == "stats_update":
                    final_stats_update = event
                # We want the final champ select event before trading is enabled. We determine this by the gameState.
                # POST_CHAMP_SELECT have information on the trading sequence
                if schema == "champ_select" and event["gameState"] == "CHAMP_SELECT":
                    final_champ_select = event
                else:
                    saved_events.append(event)

    return (
        game_participant_info,
        game_end_event,
        final_stats_update,
        final_champ_select,
        saved_events,
    )
