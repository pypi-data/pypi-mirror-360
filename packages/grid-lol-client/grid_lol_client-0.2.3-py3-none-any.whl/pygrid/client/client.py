from typing import List, Any, Callable
import httpx
from tqdm import tqdm

from ..central_data.enums import OrderDirection
from .extended_clients import (
    ExtendedCentralDataClient as CentralDataClient,
    ExtendedSeriesStateClient as SeriesStateClient,
)


class GridClient:
    """Wrapper for GRID API clients with rate limiting."""

    def __init__(self, api_key: str):
        """
        Initialize GRID API clients.

        Args:
            api_key: GRID API key
        """
        self.api_key = api_key
        self.http_client = httpx.Client(headers={"x-api-key": api_key}, follow_redirects=True)
        self.central_data_client = CentralDataClient(
            http_client=self.http_client,
            url="https://api.grid.gg/central-data/graphql",
        )
        self.series_state_client = SeriesStateClient(
            http_client=self.http_client,
            url="https://api.grid.gg/live-data-feed/series-state/graphql",
        )

    def _paginate_all(
        self,
        fetch_func: Callable,
        extract_path: str,
        page_size: int | None = 50,
        **kwargs,
    ) -> List[Any]:
        all_items = []
        after = None
        has_next_page = True
        pbar = None

        while has_next_page:
            if page_size is None:
                result = fetch_func(after=after, **kwargs)
            else:
                result = fetch_func(after, page_size, **kwargs)
            result = getattr(result, extract_path)
            all_items.extend(result.edges)
            if pbar is None:
                pbar = tqdm(total = result.total_count)
            pbar.update(len(result.edges))
            has_next_page = result.page_info.has_next_page
            after = result.page_info.end_cursor
        if pbar is not None:
            pbar.close()
        return all_items

    def get_all_teams(self) -> List[Any]:
        """
        Get all available teams.

        Returns:
            List of team edges
        """
        return self._paginate_all(self.central_data_client.get_available_teams, "teams")

    def get_all_players(self) -> List[Any]:
        """
        Get all available players.

        Returns:
            List of player edges
        """
        return self._paginate_all(
            self.central_data_client.get_available_players, "players"
        )

    def get_all_tournaments(self) -> List[Any]:
        """
        Get all available tournaments.

        Returns:
            List of tournament edges
        """
        return self._paginate_all(
            self.central_data_client.get_available_tournaments, "tournaments"
        )

    def get_all_series(
        self,
        order: OrderDirection = OrderDirection.DESC,
        **kwargs,
    ) -> List[Any]:
        """
        Look up played all played series.

        Args:
            **kwargs: Additional parameters for get_series

        Returns:
            List of series edges
        """
        return self._paginate_all(
            self.central_data_client.get_series,
            "all_series",
            None,
            order=order,
            **kwargs,
        )

    def get_series_state(self, series_id: str, game_finished: bool | None = None, game_started: bool | None = None) -> Any:
        """
        Fetch the indepth stats of all games played a series including
            - Stats for all players stats
            - Objective stats
            - Game drafts determined by GRID

        Args:
            series_id: Series ID
            game_finished: Optional boolean to filter by games that have a winner
            game_started: Optional boolean to filter by games that have been started

        Returns:
            Series draft summary
        """
        result = self.series_state_client.series_state(series_id, game_finished=game_finished, game_started=game_started)
        return result

    def get_series_games(self, series_id: str) -> Any:
        """
        Fetch the game IDs of all available games in a series

        Args:
            series_id: Series ID

        Returns:
            Series games details
        """
        result = self.series_state_client.series_games(series_id)
        return result

    def get_team_by_team_code(self, team_code: str) -> str | None:
        """
        Look up team ID by team code.

        Args:
            team_code: Team code

        Returns:
            Team ID if found and unique, otherwise None
        """
        available_teams = self.central_data_client.get_lol_teams_by_team_code(team_code)

        if available_teams.teams.total_count == 1:
            return available_teams.teams.edges[0].node.id
        return None

    def get_available_files(self, series_id: str) -> httpx.Response:
        """
        Get list of available files for a specific series.

        Args:
            series_id: Series ID

        Returns:
            Response object with list of available files
        """
        return self.http_client.get(
            f"https://api.grid.gg/file-download/list/{series_id}"
        )

    def get_riot_summary(self, series_id: str, game_number: int) -> httpx.Response:
        """
        Get the Riot summary for a specific game in a series. The format very similar to the Match-v5 summary API.

        Args:
            series_id: Series ID
            game_number: Game number within the series

        Returns:
            Response object with Riot "summary" data
        """
        return self.http_client.get(
            f"https://api.grid.gg/file-download/end-state/riot/series/{series_id}/games/{game_number}/summary"
        )

    def get_riot_details(self, series_id: str, game_number: int) -> httpx.Response:
        """
        Get the Riot detail for a specific game in a series. The format is somewhat close to the Match-v5 timeline.

        Args:
            series_id: Series ID
            game_number: Game number within the series

        Returns:
            Response object with Riot "details" data
        """
        return self.http_client.get(
            f"https://api.grid.gg/file-download/end-state/riot/series/{series_id}/games/{game_number}/details"
        )

    def get_riot_replay(self, series_id: str, game_number: int) -> httpx.Response:
        """
        Get a raw replay (.rofl) file for a game

        Args:
            series_id: Series ID
            game_number: Game number within the series

        Returns:
            Response object with the raw replay data.
        """
        return self.http_client.get(
            f"https://api.grid.gg/file-download/replay/riot/series/{series_id}/games/{game_number}"
        )

    def get_riot_live_stats(self, series_id: str, game_number: int) -> httpx.stream:
        """
        Get the Riot LiveStats (.jsonl) file for a game. Since this file is very large, an httpx.stream is returned.

        Args:
            series_id: Series ID
            game_number: Game number within the series

        Returns:
            Response object with the raw replay data.
        """
        return self.http_client.stream(
            "GET",
            f"https://api.grid.gg/file-download/events/riot/series/{series_id}/games/{game_number}",
        )

    def get_grid_events(self, series_id: str) -> httpx.Response:
        """
        Get the GRID game-agnostic formated events for all games in a series

        Args:
            series_id: Series ID

        Returns:
            Response object with the GRID events
        """
        return self.http_client.get(
            f"https://api.grid.gg/file-download/events/grid/series/{series_id}"
        )

    def get_grid_end_state(self, series_id: str) -> httpx.Response:
        """
        Get the GRID game-agnostic end-state summary for all games in a series

        Args:
            series_id: Series ID

        Returns:
            Response object with the GRID end-state
        """
        return self.http_client.get(
            f"https://api.grid.gg/file-download/end-state/grid/series/{series_id}"
        )

    def get_tencent_summary(self, series_id: str, game_number: int) -> httpx.Response:
        """
        Get the Tencent summary for a specific game in a series.

        Args:
            series_id: Series ID
            game_number: Game number within the series

        Returns:
            Response object with Tencent summary data
        """
        return self.http_client.get(
            f"https://api.grid.gg/file-download/end-state/tencent/series/{series_id}/games/{game_number}"
        )
