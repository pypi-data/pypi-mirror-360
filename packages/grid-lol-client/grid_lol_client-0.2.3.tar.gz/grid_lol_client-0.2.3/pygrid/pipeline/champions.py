import httpx


def fetch_champion_data() -> dict:
    """
    Fetch the latest champion data from the LoL Data Dragon.

    Returns:
        Dictionary with champion data
    """
    versions_response = httpx.get(
        "https://ddragon.leagueoflegends.com/api/versions.json"
    )
    versions_response.raise_for_status()
    latest_version = versions_response.json()[0]

    champion_response = httpx.get(
        f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
    )
    champion_response.raise_for_status()

    return champion_response.json()


def get_champion_mappings() -> tuple[dict[int, str], dict[str, int]]:
    """
    Create mappings between champion IDs and names.

    Returns:
        Tuple containing (id_to_name_map, name_to_id_map)
    """
    champion_data = fetch_champion_data()

    id_to_name_map = {
        int(champion_data["data"][champ_key]["key"]): champion_data["data"][champ_key][
            "name"
        ]
        for champ_key in champion_data["data"].keys()
    }

    name_to_id_map = {
        champion_data["data"][champ_key]["id"].lower(): int(
            champion_data["data"][champ_key]["key"]
        )
        for champ_key in champion_data["data"].keys()
    }

    return id_to_name_map, name_to_id_map
