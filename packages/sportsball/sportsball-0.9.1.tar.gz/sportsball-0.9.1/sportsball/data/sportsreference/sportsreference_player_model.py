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
from .sportsreference_venue_model import create_sportsreference_venue_model

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
    height = None
    headshot = None
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
        height_ft_inches = jsonld["height"]["value"].split()[0].split("-")
        height = (float(height_ft_inches[0]) * 30.48) + (
            float(height_ft_inches[1]) * 2.54
        )
        if "image" in jsonld:
            headshot = jsonld["image"]["contentUrl"]
    position = positions.get(name)
    seconds_played = None
    if name in minutes_played:
        seconds_played = int(minutes_played[name].total_seconds())
    colleges = {}
    for a in soup.find_all("a"):
        url = a.get("href")
        if url is None:
            continue
        if not url.startswith("/friv/colleges.cgi?college="):
            continue
        title = a.get("title")
        if title in colleges:
            continue
        college = create_sportsreference_venue_model(
            venue_name=title, session=session, dt=dt
        )
        if college is None:
            continue
        colleges[title] = college
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
        height=height,
        colleges=list(colleges.values()),
        headshot=headshot,
        forced_fumbles=None,
        fumbles_recovered=None,
        fumbles_recovered_yards=None,
        fumbles_touchdowns=None,
        offensive_two_point_returns=None,
        offensive_fumbles_touchdowns=None,
        defensive_fumbles_touchdowns=None,
        average_gain=None,
        completion_percentage=None,
        completions=None,
        espn_quarterback_rating=None,
        interception_percentage=None,
        interceptions=None,
        long_passing=None,
        misc_yards=None,
        net_passing_yards=None,
        net_total_yards=None,
        passing_attempts=None,
        passing_big_plays=None,
        passing_first_downs=None,
        passing_fumbles=None,
        passing_fumbles_lost=None,
        passing_touchdown_percentage=None,
        passing_touchdowns=None,
        passing_yards=None,
        passing_yards_after_catch=None,
        quarterback_rating=None,
        sacks=None,
        passing_yards_at_catch=None,
        sacks_yards_lost=None,
        net_passing_attempts=None,
        total_offensive_plays=None,
        total_points=None,
        total_touchdowns=None,
        total_yards=None,
        total_yards_from_scrimmage=None,
        two_point_pass=None,
        two_point_pass_attempt=None,
        yards_per_completion=None,
        yards_per_pass_attempt=None,
        net_yards_per_pass_attempt=None,
        long_rushing=None,
        rushing_attempts=None,
        rushing_big_plays=None,
        rushing_first_downs=None,
        rushing_fumbles=None,
        rushing_fumbles_lost=None,
        rushing_touchdowns=None,
        rushing_yards=None,
        stuffs=None,
        stuff_yards_lost=None,
        two_point_rush=None,
        two_point_rush_attempts=None,
        yards_per_rush_attempt=None,
        espn_widereceiver=None,
        long_reception=None,
        receiving_big_plays=None,
        receiving_first_downs=None,
        receiving_fumbles=None,
        receiving_fumbles_lost=None,
        receiving_targets=None,
        receiving_touchdowns=None,
        receiving_yards=None,
        receiving_yards_after_catch=None,
        receiving_yards_at_catch=None,
        receptions=None,
        two_point_receptions=None,
        two_point_reception_attempts=None,
        yards_per_reception=None,
        assist_tackles=None,
        average_interception_yards=None,
        average_sack_yards=None,
        average_stuff_yards=None,
        blocked_field_goal_touchdowns=None,
        blocked_punt_touchdowns=None,
        defensive_touchdowns=None,
        hurries=None,
        kicks_blocked=None,
        long_interception=None,
        misc_touchdowns=None,
        passes_batted_down=None,
        passes_defended=None,
        quarterback_hits=None,
        sacks_assisted=None,
        sacks_unassisted=None,
        sacks_yards=None,
        safeties=None,
        solo_tackles=None,
        stuff_yards=None,
        tackles_for_loss=None,
        tackles_yards_lost=None,
        yards_allowed=None,
        points_allowed=None,
        one_point_safeties_made=None,
        missed_field_goal_return_td=None,
        blocked_punt_ez_rec_td=None,
        interception_touchdowns=None,
        interception_yards=None,
        average_kickoff_return_yards=None,
        average_kickoff_yards=None,
        extra_point_attempts=None,
        extra_point_percentage=None,
        extra_point_blocked=None,
        extra_points_blocked_percentage=None,
        extra_points_made=None,
        fair_catches=None,
        fair_catch_percentage=None,
        field_goal_attempts_max_19_yards=None,
        field_goal_attempts_max_29_yards=None,
        field_goal_attempts_max_39_yards=None,
        field_goal_attempts_max_49_yards=None,
        field_goal_attempts_max_59_yards=None,
        field_goal_attempts_max_99_yards=None,
        field_goal_attempts_above_50_yards=None,
        field_goal_attempt_yards=None,
        field_goals_blocked=None,
        field_goals_blocked_percentage=None,
        field_goals_made=None,
        field_goals_made_max_19_yards=None,
        field_goals_made_max_29_yards=None,
        field_goals_made_max_39_yards=None,
        field_goals_made_max_49_yards=None,
        field_goals_made_max_59_yards=None,
        field_goals_made_max_99_yards=None,
        field_goals_made_above_50_yards=None,
        field_goals_made_yards=None,
        field_goals_missed_yards=None,
        kickoff_out_of_bounds=None,
        kickoff_returns=None,
        kickoff_returns_touchdowns=None,
        kickoff_return_yards=None,
        kickoffs=None,
        kickoff_yards=None,
        long_field_goal_attempt=None,
        long_field_goal_made=None,
        long_kickoff=None,
        total_kicking_points=None,
        touchback_percentage=None,
        touchbacks=None,
        defensive_fumble_returns=None,
        defensive_fumble_return_yards=None,
        fumble_recoveries=None,
        fumble_recovery_yards=None,
        kick_return_fair_catches=None,
        kick_return_fair_catch_percentage=None,
        kick_return_fumbles=None,
        kick_return_fumbles_lost=None,
        kick_returns=None,
        kick_return_touchdowns=None,
        kick_return_yards=None,
        long_kick_return=None,
        long_punt_return=None,
        misc_fumble_returns=None,
        misc_fumble_return_yards=None,
        opposition_fumble_recoveries=None,
        opposition_fumble_recovery_yards=None,
        opposition_special_team_fumble_returns=None,
        opposition_special_team_fumble_return_yards=None,
        punt_return_fair_catches=None,
        punt_return_fair_catch_percentage=None,
        punt_return_fumbles=None,
        punt_return_fumbles_lost=None,
        punt_returns=None,
        punt_returns_started_inside_the_10=None,
        punt_returns_started_inside_the_20=None,
        punt_return_touchdowns=None,
        special_team_fumble_returns=None,
        yards_per_kick_return=None,
        yards_per_punt_return=None,
        yards_per_return=None,
        average_punt_return_yards=None,
        gross_average_punt_yards=None,
        long_punt=None,
        net_average_punt_yards=None,
        punts=None,
        punts_blocked=None,
        punts_blocked_percentage=None,
        punts_inside_10=None,
        punts_inside_10_percentage=None,
        punts_inside_20=None,
        punts_inside_20_percentage=None,
        punts_over_50=None,
        punt_yards=None,
        defensive_points=None,
        misc_points=None,
        return_touchdowns=None,
        total_two_point_conversions=None,
        passing_touchdowns_9_yards=None,
        passing_touchdowns_19_yards=None,
        passing_touchdowns_29_yards=None,
        passing_touchdowns_39_yards=None,
        passing_touchdowns_49_yards=None,
        passing_touchdowns_above_50_yards=None,
        receiving_touchdowns_9_yards=None,
        receiving_touchdowns_19_yards=None,
        receiving_touchdowns_29_yards=None,
        receiving_touchdowns_39_yards=None,
        punt_return_yards=None,
        receiving_touchdowns_49_yards=None,
        receiving_touchdowns_above_50_yards=None,
        rushing_touchdowns_9_yards=None,
        rushing_touchdowns_19_yards=None,
        rushing_touchdowns_29_yards=None,
        rushing_touchdowns_39_yards=None,
        rushing_touchdowns_49_yards=None,
        rushing_touchdowns_above_50_yards=None,
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
