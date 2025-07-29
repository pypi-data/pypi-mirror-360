"""ESPN player model."""

# pylint: disable=duplicate-code,too-many-locals,too-many-branches,line-too-long
import datetime
import logging
from typing import Any

import pytest_is_running
import requests_cache
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from ...cache import MEMORY
from ..google.google_address_model import create_google_address_model
from ..player_model import VERSION, PlayerModel
from ..sex import Sex
from ..species import Species

_BAD_URLS = {
    "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024/athletes/4689686?lang=en&region=us",
    "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024/athletes/2333612?lang=en&region=us",
}


def _create_espn_player_model(
    session: requests_cache.CachedSession,
    player: dict[str, Any],
    positions_validator: dict[str, str],
    dt: datetime.datetime,
    version: str,
) -> PlayerModel:
    identifier = str(player["playerId"])
    jersey = player.get("jersey")
    fumbles = None
    fumbles_lost = None
    if "statistics" in player:
        statistics_response = session.get(player["statistics"]["$ref"])
        if statistics_response.ok:
            statistics_dict = statistics_response.json()
            fumbles = None
            for category in statistics_dict["splits"]["categories"]:
                for stat in category["stats"]:
                    if stat["name"] == "fumbles":
                        fumbles = stat["value"]
                    if stat["name"] == "fumblesLost":
                        fumbles_lost = stat["value"]
    athlete_dict = {}
    athelete_url = player["athlete"]["$ref"]
    if athelete_url not in _BAD_URLS:
        athlete_response = session.get(athelete_url)
        athlete_response.raise_for_status()
        athelete_url = athlete_response.url
        athlete_dict = athlete_response.json()
    position_response = session.get(player["position"]["$ref"])
    position_response.raise_for_status()
    position_dict = position_response.json()
    name = athlete_dict.get("fullName", identifier)

    birth_date = None
    try:
        birth_date = parse(athlete_dict["dateOfBirth"]).date()
    except KeyError:
        logging.debug("Failed to get birth date for %s", athelete_url)

    birth_place = athlete_dict.get("birthPlace", {})
    birth_address_components = []
    city = birth_place.get("city")
    if city is not None:
        birth_address_components.append(city)
    state = birth_place.get("state")
    if state is not None:
        birth_address_components.append(state)
    country = birth_place.get("country")
    if country is not None:
        birth_address_components.append(country)

    birth_address = None
    if not birth_address_components:
        query = ", ".join(birth_address_components).strip()
        if query:
            try:
                birth_address = create_google_address_model(
                    query=query,
                    session=session,
                    dt=None,
                )
            except ValueError:
                logging.warning("Failed to get birth address for: %s", query)

    position_abbreviation = position_dict["abbreviation"]

    return PlayerModel(
        identifier=identifier,
        jersey=jersey,
        kicks=None,
        fumbles=fumbles,
        fumbles_lost=fumbles_lost,
        field_goals=None,
        field_goals_attempted=None,
        offensive_rebounds=None,
        assists=None,
        turnovers=None,
        name=name,
        marks=None,
        handballs=None,
        disposals=None,
        goals=None,
        behinds=None,
        hit_outs=None,
        tackles=None,
        rebounds=None,
        insides=None,
        clearances=None,
        clangers=None,
        free_kicks_for=None,
        free_kicks_against=None,
        brownlow_votes=None,
        contested_possessions=None,
        uncontested_possessions=None,
        contested_marks=None,
        marks_inside=None,
        one_percenters=None,
        bounces=None,
        goal_assists=None,
        percentage_played=None,
        birth_date=birth_date,
        species=str(Species.HUMAN),
        handicap_weight=None,
        father=None,
        sex=str(Sex.MALE),
        age=None if birth_date is None else relativedelta(birth_date, dt.date()).years,
        starting_position=positions_validator[position_abbreviation]
        if position_abbreviation != "-"
        else None,
        weight=athlete_dict["weight"] * 0.453592 if "weight" in athlete_dict else None,
        birth_address=birth_address,
        owner=None,
        seconds_played=None,
        three_point_field_goals=None,
        three_point_field_goals_attempted=None,
        free_throws=None,
        free_throws_attempted=None,
        defensive_rebounds=None,
        steals=None,
        blocks=None,
        personal_fouls=None,
        points=None,
        game_score=None,
        point_differential=None,
        version=version,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_espn_player_model(
    session: requests_cache.CachedSession,
    player: dict[str, Any],
    positions_validator: dict[str, str],
    dt: datetime.datetime,
    version: str,
) -> PlayerModel:
    return _create_espn_player_model(
        session=session,
        player=player,
        positions_validator=positions_validator,
        dt=dt,
        version=version,
    )


def create_espn_player_model(
    session: requests_cache.CachedSession,
    player: dict[str, Any],
    dt: datetime.datetime,
    positions_validator: dict[str, str],
) -> PlayerModel:
    """Create a player model based off ESPN."""
    if (
        not pytest_is_running.is_running()
        and dt.date() < datetime.datetime.today().date() - datetime.timedelta(days=7)
    ):
        return _cached_create_espn_player_model(
            session=session,
            player=player,
            positions_validator=positions_validator,
            dt=dt,
            version=VERSION,
        )
    with session.cache_disabled():
        return _create_espn_player_model(
            session=session,
            player=player,
            positions_validator=positions_validator,
            dt=dt,
            version=VERSION,
        )
