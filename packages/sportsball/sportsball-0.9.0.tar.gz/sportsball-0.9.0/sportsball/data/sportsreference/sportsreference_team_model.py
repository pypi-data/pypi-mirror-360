"""Sports Reference team model."""

# pylint: disable=too-many-arguments,too-many-locals,duplicate-code,too-many-branches,too-many-statements
import datetime
import http
import json
import logging
import urllib.parse
from urllib.parse import urlparse

import extruct  # type: ignore
import pytest_is_running
import requests
from bs4 import BeautifulSoup, Tag
from scrapesession.scrapesession import ScrapeSession  # type: ignore
from w3lib.html import get_base_url

from ...cache import MEMORY
from ..google.google_news_model import create_google_news_models
from ..league import League
from ..sex import Sex
from ..team_model import VERSION, TeamModel
from ..x.x_social_model import create_x_social_model
from .sportsreference_coach_model import create_sportsreference_coach_model
from .sportsreference_player_model import create_sportsreference_player_model

_BAD_URLS = {
    "https://www.sports-reference.com/cbb/players/jahmiah-simmons-2.html",
    "https://www.sports-reference.com/cbb/players/mohamed-sherif-12.html",
    "https://www.sports-reference.com/cbb/players/ana-beatriz-passos-alves-da-silva-1.html",
    "https://www.sports-reference.com/cbb/players/cia-eklof-1.html",
    "https://www.sports-reference.com/cbb/players/aj-caldwell-2.html",
    "https://www.sports-reference.com/cbb/players/akuwovo-ogheneyole-1.html",
    "https://www.sports-reference.com/cbb/players/jevon-lyle-1.html",
    "https://www.sports-reference.com/cbb/players/mike-aaman-1.html",
}
_NON_WAYBACK_URLS: set[str] = {
    "https://www.sports-reference.com/cbb/schools/stony-brook/women/2021.html",
    "https://www.sports-reference.com/cbb/schools/minnesota/women/2019.html",
    "https://www.sports-reference.com/cbb/schools/rice/women/2019.html",
    "https://www.sports-reference.com/cbb/schools/north-carolina/women/2018.html",
    "https://www.sports-reference.com/cbb/schools/minnesota/women/2009.html",
    "https://www.basketball-reference.com/teams/GSW/2016.html",
    "https://www.sports-reference.com/cbb/schools/cal-state-fullerton/men/2007.html",
}
_BAD_TEAM_URLS = {
    "https://www.sports-reference.com/cbb/schools/mid-atlantic-christian/2016.html",
    "https://www.sports-reference.com/cbb/schools/claflin/2013.html",
    "https://www.sports-reference.com/cbb/schools/chaminade/2011.html",
    "https://www.sports-reference.com/cbb/schools/alaska-anchorage/2016.html",
}


def _find_name(response: requests.Response, soup: BeautifulSoup, url: str) -> str:
    base_url = get_base_url(response.text, url)
    try:
        data = extruct.extract(response.text, base_url=base_url)
        return data["json-ld"][0]["name"]
    except (json.decoder.JSONDecodeError, IndexError) as exc:
        h1 = soup.find("h1")
        if not isinstance(h1, Tag):
            logging.error(response.text)
            raise ValueError(f"h1 is null for {url}.") from exc
        span = h1.find_all("span")
        try:
            return span[1].get_text().strip()
        except IndexError:
            for span in soup.find_all("span", itemprop="title"):
                if not isinstance(span, Tag):
                    continue
                span_text = span.get_text().strip()
                if span_text == "BBR Home":
                    continue
                if span_text == "Teams":
                    continue
                return span_text
            test_url = "/".join(url.split("/")[:-1]) + "/"
            for a in soup.find_all("a", href=True):
                a_url = urllib.parse.urljoin(url, a.get("href"))
                if a_url == test_url:
                    return a.get_text().strip()
            name_tag = soup.find("meta", itemprop="name")
            if not isinstance(name_tag, Tag):
                name_tag = soup.find("meta", itemprop="og:title")
                if not isinstance(name_tag, Tag):
                    logging.error(type(name_tag))
                    logging.error(response.text)
                    raise ValueError("name_tag not a tag.") from exc
            content = name_tag.get("content")
            if not isinstance(content, str):
                raise ValueError("content not a tag.") from exc
            return " ".join(content.strip().split()[1:])


def _create_sportsreference_team_model(
    session: ScrapeSession,
    url: str,
    dt: datetime.datetime,
    league: League,
    player_urls: set[str],
    points: float,
    fg: dict[str, int],
    fga: dict[str, int],
    offensive_rebounds: dict[str, int],
    assists: dict[str, int],
    turnovers: dict[str, int],
    team_name: str,
    positions_validator: dict[str, str],
    minutes_played: dict[str, datetime.timedelta],
    three_point_field_goals: dict[str, int],
    three_point_field_goals_attempted: dict[str, int],
    free_throws: dict[str, int],
    free_throws_attempted: dict[str, int],
    defensive_rebounds: dict[str, int],
    steals: dict[str, int],
    blocks: dict[str, int],
    personal_fouls: dict[str, int],
    player_points: dict[str, int],
    game_scores: dict[str, float],
    point_differentials: dict[str, int],
    version: str,
) -> TeamModel:
    if url in _BAD_TEAM_URLS:
        return TeamModel(
            identifier=team_name,
            name=team_name,
            location=None,
            players=[],
            odds=[],
            points=points,
            ladder_rank=None,
            news=create_google_news_models(team_name, session, dt, league),
            social=create_x_social_model(team_name, session, dt),
            coaches=[],
            lbw=None,
            end_dt=None,
            version=version,
        )

    if url in _NON_WAYBACK_URLS:
        with session.wayback_disabled():
            response = session.get(url)
    else:
        response = session.get(url)

    if response.status_code == http.HTTPStatus.NOT_FOUND:
        logging.warning("Could not find team %s at url %s", team_name, url)
        return TeamModel(
            identifier=team_name,
            name=team_name,
            location=None,
            players=[],
            odds=[],
            points=points,
            ladder_rank=None,
            news=create_google_news_models(team_name, session, dt, league),
            social=create_x_social_model(team_name, session, dt),
            coaches=[],
            lbw=None,
            end_dt=None,
            version=version,
        )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    title = soup.find("title")
    if not isinstance(title, Tag):
        raise ValueError(f"title not a tag for {url}.")
    title_str = title.get_text().strip().lower()
    if "file not found" in title_str:
        session.cache.delete(urls=[url])
        response = session.get(url)
        response.raise_for_status()

    name = _find_name(response, soup, url)

    valid_player_urls = set()
    for a in soup.find_all("a"):
        player_url = urllib.parse.urljoin(url, a.get("href"))
        if player_url in player_urls and player_url not in _BAD_URLS:
            valid_player_urls.add(player_url)

    coach_url = None
    for a in soup.find_all("a", href=True):
        a_url = urllib.parse.urljoin(url, a.get("href"))
        a_o = urlparse(a_url)
        path_split = a_o.path.split("/")
        if len(path_split) <= 2:
            continue
        if not path_split[-1]:
            continue
        entity_identifier = path_split[-2]
        if entity_identifier == "coaches":
            coach_url = a_url
            break

    o = urlparse(url)
    sex_id = o.path.split("/")[-2]
    sex = Sex.MALE
    if sex_id == "women":
        sex = Sex.FEMALE

    positions = {}
    for tr in soup.find_all("tr"):
        player_name = None
        position = None
        for td in tr.find_all("td"):
            data_stat = td.get("pos")
            if data_stat == "player":
                player_name = td.get_text().strip()
            elif data_stat == "pos":
                position = td.get_text().strip()
        if player_name is not None and position is not None:
            positions[player_name] = position

    return TeamModel(
        identifier=name,
        name=name,
        players=[
            y
            for y in [  # pyright: ignore
                create_sportsreference_player_model(
                    session=session,
                    player_url=x,
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
                    points=player_points,
                    game_scores=game_scores,
                    point_differentials=point_differentials,
                )
                for x in valid_player_urls
            ]
            if y is not None
        ],
        odds=[],
        points=points,
        ladder_rank=None,
        location=None,
        news=create_google_news_models(name, session, dt, league),
        social=create_x_social_model(name, session, dt),
        coaches=[create_sportsreference_coach_model(session, coach_url, dt)]
        if coach_url is not None
        else [],
        lbw=None,
        end_dt=None,
        version=version,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_sportsreference_team_model(
    session: ScrapeSession,
    url: str,
    dt: datetime.datetime,
    league: League,
    player_urls: set[str],
    points: float,
    fg: dict[str, int],
    fga: dict[str, int],
    offensive_rebounds: dict[str, int],
    assists: dict[str, int],
    turnovers: dict[str, int],
    team_name: str,
    positions_validator: dict[str, str],
    minutes_played: dict[str, datetime.timedelta],
    three_point_field_goals: dict[str, int],
    three_point_field_goals_attempted: dict[str, int],
    free_throws: dict[str, int],
    free_throws_attempted: dict[str, int],
    defensive_rebounds: dict[str, int],
    steals: dict[str, int],
    blocks: dict[str, int],
    personal_fouls: dict[str, int],
    player_points: dict[str, int],
    game_scores: dict[str, float],
    point_differentials: dict[str, int],
    version: str,
) -> TeamModel:
    return _create_sportsreference_team_model(
        session=session,
        url=url,
        dt=dt,
        league=league,
        player_urls=player_urls,
        points=points,
        fg=fg,
        fga=fga,
        offensive_rebounds=offensive_rebounds,
        assists=assists,
        turnovers=turnovers,
        team_name=team_name,
        positions_validator=positions_validator,
        minutes_played=minutes_played,
        three_point_field_goals=three_point_field_goals,
        three_point_field_goals_attempted=three_point_field_goals_attempted,
        free_throws=free_throws,
        free_throws_attempted=free_throws_attempted,
        defensive_rebounds=defensive_rebounds,
        steals=steals,
        blocks=blocks,
        personal_fouls=personal_fouls,
        player_points=player_points,
        game_scores=game_scores,
        point_differentials=point_differentials,
        version=version,
    )


def create_sportsreference_team_model(
    session: ScrapeSession,
    url: str,
    dt: datetime.datetime,
    league: League,
    player_urls: set[str],
    points: float,
    fg: dict[str, int],
    fga: dict[str, int],
    offensive_rebounds: dict[str, int],
    assists: dict[str, int],
    turnovers: dict[str, int],
    team_name: str,
    positions_validator: dict[str, str],
    minutes_played: dict[str, datetime.timedelta],
    three_point_field_goals: dict[str, int],
    three_point_field_goals_attempted: dict[str, int],
    free_throws: dict[str, int],
    free_throws_attempted: dict[str, int],
    defensive_rebounds: dict[str, int],
    steals: dict[str, int],
    blocks: dict[str, int],
    personal_fouls: dict[str, int],
    player_points: dict[str, int],
    game_scores: dict[str, float],
    point_differentials: dict[str, int],
) -> TeamModel:
    """Create a team model from Sports Reference."""
    if not pytest_is_running.is_running():
        return _cached_create_sportsreference_team_model(
            session=session,
            url=url,
            dt=dt,
            league=league,
            player_urls=player_urls,
            points=points,
            fg=fg,
            fga=fga,
            offensive_rebounds=offensive_rebounds,
            assists=assists,
            turnovers=turnovers,
            team_name=team_name,
            positions_validator=positions_validator,
            minutes_played=minutes_played,
            three_point_field_goals=three_point_field_goals,
            three_point_field_goals_attempted=three_point_field_goals_attempted,
            free_throws=free_throws,
            free_throws_attempted=free_throws_attempted,
            defensive_rebounds=defensive_rebounds,
            steals=steals,
            blocks=blocks,
            personal_fouls=personal_fouls,
            player_points=player_points,
            game_scores=game_scores,
            point_differentials=point_differentials,
            version=VERSION,
        )
    with session.cache_disabled():
        return _create_sportsreference_team_model(
            session=session,
            url=url,
            dt=dt,
            league=league,
            player_urls=player_urls,
            points=points,
            fg=fg,
            fga=fga,
            offensive_rebounds=offensive_rebounds,
            assists=assists,
            turnovers=turnovers,
            team_name=team_name,
            positions_validator=positions_validator,
            minutes_played=minutes_played,
            three_point_field_goals=three_point_field_goals,
            three_point_field_goals_attempted=three_point_field_goals_attempted,
            free_throws=free_throws,
            free_throws_attempted=free_throws_attempted,
            defensive_rebounds=defensive_rebounds,
            steals=steals,
            blocks=blocks,
            personal_fouls=personal_fouls,
            player_points=player_points,
            game_scores=game_scores,
            point_differentials=point_differentials,
            version=VERSION,
        )
