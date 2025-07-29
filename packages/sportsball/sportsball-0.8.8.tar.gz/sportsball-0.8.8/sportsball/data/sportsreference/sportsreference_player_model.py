"""Sports reference player model."""

# pylint: disable=too-many-arguments,unused-argument,line-too-long,duplicate-code,too-many-locals
import datetime
import http
import logging
from urllib.parse import unquote

import extruct  # type: ignore
import pytest_is_running
import requests_cache
from bs4 import BeautifulSoup
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from scrapesession.session import DEFAULT_TIMEOUT  # type: ignore

from ...cache import MEMORY
from ..google.google_address_model import create_google_address_model
from ..player_model import VERSION, PlayerModel
from ..sex import Sex
from ..species import Species

_FIX_URLS = {
    "https://www.sports-reference.com/cbb/players/leyla-öztürk-1.html": "https://www.sports-reference.com/cbb/players/leyla-ozturk-1.html",
    "https://www.sports-reference.com/cbb/players/vianè-cumber-1.html": "https://www.sports-reference.com/cbb/players/viane-cumber-1.html",
    "https://www.sports-reference.com/cbb/players/cia-eklof-1.html": "https://www.sports-reference.com/cbb/players/cia-eklöf-1.html",
    "https://www.sports-reference.com/cbb/players/chae-harris-1.html": "https://www.sports-reference.com/cbb/players/cha%C3%A9-harris-1.html",
    "https://www.sports-reference.com/cbb/players/tilda-sjokvist-1.html": "https://www.sports-reference.com/cbb/players/tilda-sjökvist-1.html",
    "https://www.sports-reference.com/cbb/players/hana-muhl-1.html": "https://www.sports-reference.com/cbb/players/hana-mühl-1.html",
    "https://www.sports-reference.com/cbb/players/noa-comesaña-1.html": "https://www.sports-reference.com/cbb/players/noa-comesana-1.html",
    "https://www.sports-reference.com/cbb/players/nadège-jean-1.html": "https://www.sports-reference.com/cbb/players/nadege-jean-1.html",
}


def _fix_url(url: str) -> str:
    url = unquote(url)
    url = url.replace("é", "e")
    url = url.replace("ć", "c")
    url = url.replace("ã", "a")
    url = url.replace("á", "a")
    url = url.replace("á", "a")
    url = url.replace("ö", "o")
    url = url.replace("ü", "u")

    url = url.replace("Ã©", "é")
    url = url.replace("Ã¶", "ö")
    url = url.replace("Ã¼", "ü")

    return _FIX_URLS.get(url, url)


def _create_sportsreference_player_model(
    session: requests_cache.CachedSession,
    player_url: str,
    fg: dict[str, int],
    fga: dict[str, int],
    offensive_rebounds: dict[str, int],
    assists: dict[str, int],
    turnovers: dict[str, int],
    positions: dict[str, str],
    positions_validator: dict[str, str],
    sex: Sex,
    dt: datetime.datetime,
    minutes_played: dict[str, datetime.timedelta],
    three_point_field_goals: dict[str, int],
    three_point_field_goals_attempted: dict[str, int],
    free_throws: dict[str, int],
    free_throws_attempted: dict[str, int],
    defensive_rebounds: dict[str, int],
    steals: dict[str, int],
    blocks: dict[str, int],
    personal_fouls: dict[str, int],
    points: dict[str, int],
    game_scores: dict[str, float],
    point_differentials: dict[str, int],
    version: str,
) -> PlayerModel | None:
    """Create a player model from sports reference."""
    player_url = _fix_url(player_url)
    response = session.get(player_url, timeout=DEFAULT_TIMEOUT)
    # Some players can't be accessed on sports reference
    if response.status_code == http.HTTPStatus.FORBIDDEN:
        logging.warning("Cannot access player at URL %s", player_url)
        return None
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    h1 = soup.find("h1")
    if h1 is None:
        logging.warning("h1 is null for %s", player_url)
        return None
    name = h1.get_text().strip()
    data = extruct.extract(response.text, base_url=response.url)
    birth_date = None
    weight = None
    birth_address = None
    for jsonld in data["json-ld"]:
        if jsonld["@type"] != "Person":
            continue
        birth_date = parse(jsonld["birthDate"])
        weight = float(jsonld["weight"]["value"].split()[0]) * 0.453592
        birth_address = create_google_address_model(
            query=jsonld["birthPlace"],
            session=session,
            dt=None,
        )
    position = positions.get(name)
    seconds_played = None
    if name in minutes_played:
        seconds_played = int(minutes_played[name].total_seconds())
    return PlayerModel(
        identifier=name,
        jersey=None,
        kicks=None,
        fumbles=None,
        fumbles_lost=None,
        field_goals=fg.get(name),
        field_goals_attempted=fga.get(name),
        offensive_rebounds=offensive_rebounds.get(name),
        assists=assists.get(name),
        turnovers=turnovers.get(name),
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
        sex=str(sex),
        age=None if birth_date is None else relativedelta(birth_date, dt).years,
        starting_position=positions_validator[position]
        if position is not None
        else None,
        weight=weight,
        birth_address=birth_address,
        owner=None,
        seconds_played=seconds_played,
        three_point_field_goals=three_point_field_goals.get(name),
        three_point_field_goals_attempted=three_point_field_goals_attempted.get(name),
        free_throws=free_throws.get(name),
        free_throws_attempted=free_throws_attempted.get(name),
        defensive_rebounds=defensive_rebounds.get(name),
        steals=steals.get(name),
        blocks=blocks.get(name),
        personal_fouls=personal_fouls.get(name),
        points=points.get(name),
        game_score=game_scores.get(name),
        point_differential=point_differentials.get(name),
        version=version,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_sportsreference_player_model(
    session: requests_cache.CachedSession,
    player_url: str,
    fg: dict[str, int],
    fga: dict[str, int],
    offensive_rebounds: dict[str, int],
    assists: dict[str, int],
    turnovers: dict[str, int],
    positions: dict[str, str],
    positions_validator: dict[str, str],
    sex: Sex,
    dt: datetime.datetime,
    minutes_played: dict[str, datetime.timedelta],
    three_point_field_goals: dict[str, int],
    three_point_field_goals_attempted: dict[str, int],
    free_throws: dict[str, int],
    free_throws_attempted: dict[str, int],
    defensive_rebounds: dict[str, int],
    steals: dict[str, int],
    blocks: dict[str, int],
    personal_fouls: dict[str, int],
    points: dict[str, int],
    game_scores: dict[str, float],
    point_differentials: dict[str, int],
    version: str,
) -> PlayerModel | None:
    return _create_sportsreference_player_model(
        session=session,
        player_url=player_url,
        fg=fg,
        fga=fga,
        offensive_rebounds=offensive_rebounds,
        assists=assists,
        turnovers=turnovers,
        positions=positions,
        positions_validator=positions_validator,
        sex=sex,
        dt=dt,
        minutes_played=minutes_played,
        three_point_field_goals=three_point_field_goals,
        three_point_field_goals_attempted=three_point_field_goals_attempted,
        free_throws=free_throws,
        free_throws_attempted=free_throws_attempted,
        defensive_rebounds=defensive_rebounds,
        steals=steals,
        blocks=blocks,
        personal_fouls=personal_fouls,
        points=points,
        game_scores=game_scores,
        point_differentials=point_differentials,
        version=version,
    )


def create_sportsreference_player_model(
    session: requests_cache.CachedSession,
    player_url: str,
    fg: dict[str, int],
    fga: dict[str, int],
    offensive_rebounds: dict[str, int],
    assists: dict[str, int],
    turnovers: dict[str, int],
    positions: dict[str, str],
    positions_validator: dict[str, str],
    sex: Sex,
    dt: datetime.datetime,
    minutes_played: dict[str, datetime.timedelta],
    three_point_field_goals: dict[str, int],
    three_point_field_goals_attempted: dict[str, int],
    free_throws: dict[str, int],
    free_throws_attempted: dict[str, int],
    defensive_rebounds: dict[str, int],
    steals: dict[str, int],
    blocks: dict[str, int],
    personal_fouls: dict[str, int],
    points: dict[str, int],
    game_scores: dict[str, float],
    point_differentials: dict[str, int],
) -> PlayerModel | None:
    """Create a player model from sports reference."""
    if not pytest_is_running.is_running():
        return _cached_create_sportsreference_player_model(
            session=session,
            player_url=player_url,
            fg=fg,
            fga=fga,
            offensive_rebounds=offensive_rebounds,
            assists=assists,
            turnovers=turnovers,
            positions=positions,
            positions_validator=positions_validator,
            sex=sex,
            dt=dt,
            minutes_played=minutes_played,
            three_point_field_goals=three_point_field_goals,
            three_point_field_goals_attempted=three_point_field_goals_attempted,
            free_throws=free_throws,
            free_throws_attempted=free_throws_attempted,
            defensive_rebounds=defensive_rebounds,
            steals=steals,
            blocks=blocks,
            personal_fouls=personal_fouls,
            points=points,
            game_scores=game_scores,
            point_differentials=point_differentials,
            version=VERSION,
        )
    with session.cache_disabled():
        return _create_sportsreference_player_model(
            session=session,
            player_url=player_url,
            fg=fg,
            fga=fga,
            offensive_rebounds=offensive_rebounds,
            assists=assists,
            turnovers=turnovers,
            positions=positions,
            positions_validator=positions_validator,
            sex=sex,
            dt=dt,
            minutes_played=minutes_played,
            three_point_field_goals=three_point_field_goals,
            three_point_field_goals_attempted=three_point_field_goals_attempted,
            free_throws=free_throws,
            free_throws_attempted=free_throws_attempted,
            defensive_rebounds=defensive_rebounds,
            steals=steals,
            blocks=blocks,
            personal_fouls=personal_fouls,
            points=points,
            game_scores=game_scores,
            point_differentials=point_differentials,
            version=VERSION,
        )
