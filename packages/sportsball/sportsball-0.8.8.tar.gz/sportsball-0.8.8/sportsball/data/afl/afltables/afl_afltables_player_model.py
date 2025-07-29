"""AFL AFLTables player model."""

# pylint: disable=line-too-long,duplicate-code,too-many-arguments,too-many-locals
import datetime
import logging
import os
from urllib.parse import urlparse

import pytest_is_running
import requests_cache
from bs4 import BeautifulSoup
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from ....cache import MEMORY
from ...player_model import VERSION, PlayerModel
from ...sex import Sex
from ...species import Species


def _create_afl_afltables_player_model(
    player_url: str,
    jersey: str,
    kicks: int | None,
    name: str,
    marks: int | None,
    handballs: int | None,
    disposals: int | None,
    goals: int | None,
    behinds: int | None,
    hit_outs: int | None,
    tackles: int | None,
    rebounds: int | None,
    insides: int | None,
    clearances: int | None,
    clangers: int | None,
    free_kicks_for: int | None,
    free_kicks_against: int | None,
    brownlow_votes: int | None,
    contested_possessions: int | None,
    uncontested_possessions: int | None,
    contested_marks: int | None,
    marks_inside: int | None,
    one_percenters: int | None,
    bounces: int | None,
    goal_assists: int | None,
    percentage_played: float | None,
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    version: str,
) -> PlayerModel:
    o = urlparse(player_url)
    last_component = o.path.split("/")[-1]
    identifier, _ = os.path.splitext(last_component)
    jersey = "".join(filter(str.isdigit, jersey))
    response = session.get(player_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    player_page_text = soup.get_text()

    birth_date = None
    try:
        birth_date = parse(
            player_page_text.split("Born:")[1].strip().split()[0].strip()
        )
    except IndexError:
        logging.debug("Couldn't find birth date from %s", response.url)

    weight = None
    try:
        weight = float(player_page_text.split("Weight:")[1].strip().split()[0].strip())
    except IndexError:
        logging.debug("Couldn't find weight from %s", response.url)

    return PlayerModel(
        identifier=identifier,
        jersey=jersey,
        kicks=kicks,
        fumbles=None,
        fumbles_lost=None,
        field_goals=None,
        field_goals_attempted=None,
        offensive_rebounds=None,
        assists=None,
        turnovers=None,
        name=name,
        marks=marks,
        handballs=handballs,
        disposals=disposals,
        goals=goals,
        behinds=behinds,
        hit_outs=hit_outs,
        tackles=tackles,
        rebounds=rebounds,
        insides=insides,
        clearances=clearances,
        clangers=clangers,
        free_kicks_for=free_kicks_for,
        free_kicks_against=free_kicks_against,
        brownlow_votes=brownlow_votes,
        contested_possessions=contested_possessions,
        uncontested_possessions=uncontested_possessions,
        contested_marks=contested_marks,
        marks_inside=marks_inside,
        one_percenters=one_percenters,
        bounces=bounces,
        goal_assists=goal_assists,
        percentage_played=percentage_played,
        birth_date=birth_date,
        species=str(Species.HUMAN),
        handicap_weight=None,
        father=None,
        sex=str(Sex.MALE),
        age=None if birth_date is None else relativedelta(birth_date, dt).years,
        starting_position=None,
        weight=weight,
        birth_address=None,
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
def _cached_create_afl_afltables_player_model(
    player_url: str,
    jersey: str,
    kicks: int | None,
    name: str,
    marks: int | None,
    handballs: int | None,
    disposals: int | None,
    goals: int | None,
    behinds: int | None,
    hit_outs: int | None,
    tackles: int | None,
    rebounds: int | None,
    insides: int | None,
    clearances: int | None,
    clangers: int | None,
    free_kicks_for: int | None,
    free_kicks_against: int | None,
    brownlow_votes: int | None,
    contested_possessions: int | None,
    uncontested_possessions: int | None,
    contested_marks: int | None,
    marks_inside: int | None,
    one_percenters: int | None,
    bounces: int | None,
    goal_assists: int | None,
    percentage_played: float | None,
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    version: str,
) -> PlayerModel:
    return _create_afl_afltables_player_model(
        player_url=player_url,
        jersey=jersey,
        kicks=kicks,
        name=name,
        marks=marks,
        handballs=handballs,
        disposals=disposals,
        goals=goals,
        behinds=behinds,
        hit_outs=hit_outs,
        tackles=tackles,
        rebounds=rebounds,
        insides=insides,
        clearances=clearances,
        clangers=clangers,
        free_kicks_for=free_kicks_for,
        free_kicks_against=free_kicks_against,
        brownlow_votes=brownlow_votes,
        contested_possessions=contested_possessions,
        uncontested_possessions=uncontested_possessions,
        contested_marks=contested_marks,
        marks_inside=marks_inside,
        one_percenters=one_percenters,
        bounces=bounces,
        goal_assists=goal_assists,
        percentage_played=percentage_played,
        session=session,
        dt=dt,
        version=version,
    )


def create_afl_afltables_player_model(
    player_url: str,
    jersey: str,
    kicks: int | None,
    session: requests_cache.CachedSession,
    name: str,
    marks: int | None,
    handballs: int | None,
    disposals: int | None,
    goals: int | None,
    behinds: int | None,
    hit_outs: int | None,
    tackles: int | None,
    rebounds: int | None,
    insides: int | None,
    clearances: int | None,
    clangers: int | None,
    free_kicks_for: int | None,
    free_kicks_against: int | None,
    brownlow_votes: int | None,
    contested_possessions: int | None,
    uncontested_possessions: int | None,
    contested_marks: int | None,
    marks_inside: int | None,
    one_percenters: int | None,
    bounces: int | None,
    goal_assists: int | None,
    percentage_played: float | None,
    dt: datetime.datetime,
) -> PlayerModel:
    """Create a player model from AFL Tables."""
    if not pytest_is_running.is_running():
        return _cached_create_afl_afltables_player_model(
            player_url=player_url,
            jersey=jersey,
            kicks=kicks,
            name=name,
            marks=marks,
            handballs=handballs,  # pyright: ignore
            disposals=disposals,
            goals=goals,
            behinds=behinds,
            hit_outs=hit_outs,
            tackles=tackles,
            rebounds=rebounds,
            insides=insides,
            clearances=clearances,
            clangers=clangers,
            free_kicks_for=free_kicks_for,
            free_kicks_against=free_kicks_against,
            brownlow_votes=brownlow_votes,
            contested_possessions=contested_possessions,
            uncontested_possessions=uncontested_possessions,
            contested_marks=contested_marks,
            marks_inside=marks_inside,
            one_percenters=one_percenters,
            bounces=bounces,
            goal_assists=goal_assists,
            percentage_played=percentage_played,
            session=session,
            dt=dt,
            version=VERSION,
        )
    with session.cache_disabled():
        return _create_afl_afltables_player_model(
            player_url=player_url,
            jersey=jersey,
            kicks=kicks,
            name=name,
            marks=marks,
            handballs=handballs,
            disposals=disposals,
            goals=goals,
            behinds=behinds,
            hit_outs=hit_outs,
            tackles=tackles,
            rebounds=rebounds,
            insides=insides,
            clearances=clearances,
            clangers=clangers,
            free_kicks_for=free_kicks_for,
            free_kicks_against=free_kicks_against,
            brownlow_votes=brownlow_votes,
            contested_possessions=contested_possessions,
            uncontested_possessions=uncontested_possessions,
            contested_marks=contested_marks,
            marks_inside=marks_inside,
            one_percenters=one_percenters,
            bounces=bounces,
            goal_assists=goal_assists,
            percentage_played=percentage_played,
            session=session,
            dt=dt,
            version=VERSION,
        )
