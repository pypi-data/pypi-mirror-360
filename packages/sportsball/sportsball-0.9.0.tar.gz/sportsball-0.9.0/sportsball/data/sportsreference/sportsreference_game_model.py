"""Sports Reference game model."""

# pylint: disable=too-many-locals,too-many-statements,unused-argument,protected-access,too-many-arguments,use-maxsplit-arg,too-many-branches,duplicate-code,broad-exception-caught
import datetime
import io
import logging
import re
import urllib.parse

import dateutil
import pandas as pd
import pytest_is_running
import requests
from bs4 import BeautifulSoup, Tag
from dateutil.parser import parse
from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ...cache import MEMORY
from ..game_model import VERSION, GameModel
from ..league import League
from ..season_type import SeasonType
from ..team_model import TeamModel
from .sportsreference_team_model import create_sportsreference_team_model
from .sportsreference_venue_model import create_sportsreference_venue_model

_MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
_NUMBER_PARENTHESIS_PATTERN = r"\(\d+\)"


def _find_old_dt(
    dfs: list[pd.DataFrame],
    session: ScrapeSession,
    soup: BeautifulSoup,
    url: str,
    league: League,
    player_urls: set[str],
    fg: dict[str, int],
    fga: dict[str, int],
    offensive_rebounds: dict[str, int],
    assists: dict[str, int],
    turnovers: dict[str, int],
    response: requests.Response,
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
) -> tuple[datetime.datetime, list[TeamModel], str | None]:
    teams: list[TeamModel] = []

    def _process_team_row(df: pd.DataFrame):
        team_rows = [str(df.iat[0, x]) for x in range(len(df.columns.values))]
        team_rows = [x for x in team_rows if x != "nan"]
        if len(team_rows) == 1:
            team_row = team_rows[0]
            for sentinel in ["Next Game", "Prev Game"]:
                if sentinel in team_row:
                    team_rows = [
                        team_row[: team_row.find(sentinel) + len(sentinel)].strip(),
                        team_row[team_row.find(sentinel) + len(sentinel) :]
                        .strip()
                        .replace("/ Next Game ⇒", "")
                        .replace("⇒", "")
                        .strip(),
                    ]
                    last_splits = team_rows[1].split()
                    if last_splits:
                        if last_splits[0] in _MONTHS:
                            continue
                    break
            if not team_rows[1]:
                sentinel = "Next Game"
                team_rows = [
                    team_row[: team_row.find(sentinel) + len(sentinel)].strip(),
                    team_row[team_row.find(sentinel) + len(sentinel) :]
                    .strip()
                    .replace("⇒", "")
                    .strip(),
                ]
            if not team_rows[1]:
                sentinel = "Prev Game"
                team_rows = [
                    team_row[: team_row.find(sentinel) + len(sentinel)].strip(),
                    team_row[team_row.find(sentinel) + len(sentinel) :]
                    .strip()
                    .replace("⇒", "")
                    .strip(),
                ]
        for team_row in team_rows:
            if team_row.startswith("⇒"):
                team_row = team_row[1:]
            team_row = team_row.strip()
            if "Prev Game" in team_row:
                team_name_points = (
                    team_row.split("⇐")[0]
                    .strip()
                    .replace("Prev Game", "")
                    # .replace("/", "")
                    .strip()
                )
            else:
                team_name_points = (
                    team_row.split("⇒")[0].replace("Next Game", "").strip()
                )
            # Handle team name points like "Indiana Pacers 97 45-37 (Won 3)"
            if "-" in team_name_points:
                dash_splits = team_name_points.split("-")
                # Handle team name points like "Kansas City-Omaha Kings 89"
                # and cases like "Kansas City-Omaha Kings 95 44-38 (Won 1) ⇐ Prev Game"
                for i in range(len(dash_splits) - 1):
                    if (
                        dash_splits[i].split()[-1].isdigit()
                        and dash_splits[i + 1].split()[0].isdigit()
                    ):
                        team_name_points = " ".join(
                            "-".join(dash_splits[: i + 1]).strip().split()[:-1]
                        )
                        break
            for marker in ["Lost", "Won"]:
                team_name_points = team_name_points.split(marker)[0].strip()
            points = int(team_name_points.split()[-1].strip())
            team_name = " ".join(team_name_points.split()[:-1]).strip()
            if " at " in team_name:
                team_name = team_name.split(" at ")[0].strip()
            if " vs " in team_name:
                team_name = team_name.split(" vs ")[0].strip()
            for month in _MONTHS:
                month_split = " " + month + " "
                if month_split in team_name:
                    team_name = team_name.split(month_split)[0].strip()
                    points = int(team_name.split()[-1].strip())
                    team_name = " ".join(team_name.split()[:-1]).strip()
                    break
            team_name = " ".join(
                re.sub(_NUMBER_PARENTHESIS_PATTERN, "", team_name).split()
            ).strip()
            team_a = soup.find("a", text=team_name, href=True)
            if not isinstance(team_a, Tag):
                logging.error(team_name)
                logging.error(response.url)
                logging.error(response.text)
                raise ValueError("team_a is not a tag.")
            team_url = urllib.parse.urljoin(url, str(team_a.get("href")))
            if dt is None:
                raise ValueError("dt is null.")
            teams.append(
                create_sportsreference_team_model(
                    session=session,
                    url=team_url,
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
                )
            )

    dt = None
    venue_name = None
    for df in dfs:
        if len(df) == 2:
            test_row = df.iat[0, 0]
            test_row_2 = df.iat[1, 0]
            if isinstance(test_row, float):
                continue

            try:
                if (
                    "Prev Game" in test_row
                    or "Next Game" in test_row
                    or "Lost" in test_row
                    or "PM," in test_row_2
                ):
                    date_venue_split = df.iat[1, 0].split()
                    current_idx = 5
                    try:
                        dt = parse(" ".join(date_venue_split[:current_idx]))
                    except dateutil.parser._parser.ParserError:  # type: ignore
                        try:
                            current_idx = 3
                            dt = parse(" ".join(date_venue_split[:current_idx]))
                        except dateutil.parser._parser.ParserError:  # type: ignore
                            dt = parse(
                                " ".join(",".join(test_row.split(",")[1:]).split()[:3])
                            )
                    venue_name = " ".join(date_venue_split[current_idx:])
                    _process_team_row(df)
                    break
            except TypeError as exc:
                logging.error(test_row)
                logging.error(response.url)
                logging.error(response.text)
                raise exc

    if dt is None:
        title_tag = soup.find("title")
        if not isinstance(title_tag, Tag):
            raise ValueError("title_tag is not a tag.")
        title = title_tag.get_text().strip().split("|")[0].strip()
        date = title[title.find(",") :].strip()
        dt = parse(date)
        for df in dfs:
            test_row = df.iat[0, 0]
            if isinstance(test_row, float):
                continue
            try:
                if "Prev Game" in test_row:
                    _process_team_row(df)
                    break
            except TypeError as exc:
                logging.error(test_row)
                logging.error(response.url)
                logging.error(response.text)
                raise exc

    if venue_name is not None and not venue_name.replace(",", "").strip():
        venue_name = None

    if dt is None:
        raise ValueError("dt is null.")
    if venue_name is None:
        logging.warning("venue_name is null for %s.", url)

    return (dt, teams, venue_name)


def _find_new_dt(
    soup: BeautifulSoup,
    scorebox_meta_div: Tag,
    url: str,
    session: ScrapeSession,
    league: League,
    player_urls: set[str],
    scores: list[float],
    fg: dict[str, int],
    fga: dict[str, int],
    offensive_rebounds: dict[str, int],
    assists: dict[str, int],
    turnovers: dict[str, int],
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
) -> tuple[datetime.datetime, list[TeamModel], str]:
    in_divs = scorebox_meta_div.find_all("div")
    current_in_div_idx = 0
    in_div = in_divs[current_in_div_idx]
    in_div_text = in_div.get_text().strip()
    current_in_div_idx += 1
    if "Tournament" in in_div_text:
        in_div_text = in_divs[1].get_text().strip()
        current_in_div_idx += 1
    try:
        dt = parse(in_div_text)
    except dateutil.parser._parser.ParserError as exc:  # type: ignore
        logging.error("Failed to parse date for URL: %s", url)
        raise exc
    venue_div = in_divs[current_in_div_idx]
    venue_name = venue_div.get_text().strip()
    scorebox_div = soup.find("div", class_="scorebox")
    if not isinstance(scorebox_div, Tag):
        raise ValueError("scorebox_div is not a Tag.")

    teams: list[TeamModel] = []
    for a in scorebox_div.find_all("a"):
        team_url = urllib.parse.urljoin(url, a.get("href"))
        if "/schools/" in team_url:
            teams.append(
                create_sportsreference_team_model(
                    session=session,
                    url=team_url,
                    dt=dt,
                    league=league,
                    player_urls=player_urls,
                    points=scores[len(teams)],
                    fg=fg,
                    fga=fga,
                    offensive_rebounds=offensive_rebounds,
                    assists=assists,
                    turnovers=turnovers,
                    team_name=a.get_text().strip(),
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
                )
            )

    return (dt, teams, venue_name)


def _create_sportsreference_game_model(
    session: ScrapeSession,
    url: str,
    league: League,
    positions_validator: dict[str, str],
    version: str,
) -> GameModel | None:
    # pylint: disable=too-many-branches
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    page_title = soup.find("h1", class_="page_title")

    # If the page_title is bad, try fetching from a non wayback source
    if page_title is not None:
        if "file not found" in page_title.get_text().strip().lower():
            session.cache.delete(urls=[url, response.url])
            with session.wayback_disabled():
                response = session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

    player_urls = set()
    for a in soup.find_all("a"):
        player_url = urllib.parse.urljoin(url, a.get("href"))
        if "/players/" in player_url and not player_url.endswith("/players/"):
            player_urls.add(player_url)

    scores = []
    for score_div in soup.find_all("div", class_="score"):
        try:
            scores.append(float(score_div.get_text().strip()))
        except ValueError as exc:
            logging.error(response.text)
            raise exc

    handle = io.StringIO()
    handle.write(response.text)
    handle.seek(0)
    fg = {}
    fga = {}
    offensive_rebounds = {}
    assists = {}
    turnovers = {}
    minutes_played = {}
    three_point_field_goals = {}
    three_point_field_goals_attempted = {}
    free_throws = {}
    free_throws_attempted = {}
    defensive_rebounds = {}
    steals = {}
    blocks = {}
    personal_fouls = {}
    player_points = {}
    game_scores = {}
    point_differentials = {}
    try:
        dfs = pd.read_html(handle)
        for df in dfs:
            if df.index.nlevels > 1:
                df.columns = df.columns.get_level_values(1)
            if "Starters" in df.columns.values:
                players = df["Starters"].tolist()
                if "FG" in df.columns.values:
                    fgs = df["FG"].tolist()
                    for idx, player in enumerate(players):
                        fg[player] = fgs[idx]
                if "FGA" in df.columns.values:
                    fgas = df["FGA"].tolist()
                    for idx, player in enumerate(players):
                        fga[player] = fgas[idx]
                if "OREB" in df.columns.values:
                    orebs = df["OREB"].tolist()
                    for idx, player in enumerate(players):
                        offensive_rebounds[player] = orebs[idx]
                if "AST" in df.columns.values:
                    asts = df["AST"].tolist()
                    for idx, player in enumerate(players):
                        assists[player] = asts[idx]
                if "TOV" in df.columns.values:
                    tovs = df["TOV"].tolist()
                    for idx, player in enumerate(players):
                        turnovers[player] = tovs[idx]
                if "MP" in df.columns.values.tolist():
                    mps = df["MP"].tolist()
                    for idx, player in enumerate(players):
                        mp = mps[idx]
                        mp_minutes, mp_seconds = mp.split(":")
                        minutes_played[player] = datetime.timedelta(
                            minutes=int(mp_minutes), seconds=int(mp_seconds)
                        )
                if "3P" in df.columns.values.tolist():
                    threeps = df["3P"].tolist()
                    for idx, player in enumerate(players):
                        three_point_field_goals[player] = threeps[idx]
                if "3PA" in df.columns.values.tolist():
                    threepsattempted = df["3PA"].tolist()
                    for idx, player in enumerate(players):
                        three_point_field_goals_attempted[player] = threepsattempted[
                            idx
                        ]
                if "FT" in df.columns.values.tolist():
                    fts = df["FT"].tolist()
                    for idx, player in enumerate(players):
                        free_throws[player] = fts[idx]
                if "FTA" in df.columns.values.tolist():
                    ftas = df["FTA"].tolist()
                    for idx, player in enumerate(players):
                        free_throws_attempted[player] = ftas[idx]
                if "DRB" in df.columns.values.tolist():
                    drbs = df["DRB"].tolist()
                    for idx, player in enumerate(players):
                        defensive_rebounds[player] = drbs[idx]
                if "STL" in df.columns.values.tolist():
                    stls = df["STL"].tolist()
                    for idx, player in enumerate(players):
                        steals[player] = stls[idx]
                if "BLK" in df.columns.values.tolist():
                    blks = df["BLK"].tolist()
                    for idx, player in enumerate(players):
                        blocks[player] = blks[idx]
                if "PF" in df.columns.values.tolist():
                    pfs = df["PF"].tolist()
                    for idx, player in enumerate(players):
                        personal_fouls[player] = pfs[idx]
                if "PTS" in df.columns.values.tolist():
                    ptss = df["PTS"].tolist()
                    for idx, player in enumerate(players):
                        player_points[player] = ptss[idx]
                if "GmSc" in df.columns.values.tolist():
                    gmscs = df["GmSc"].tolist()
                    for idx, player in enumerate(players):
                        game_scores[player] = gmscs[idx]
                if "+/-" in df.columns.values.tolist():
                    plusminuses = df["GmSc"].tolist()
                    for idx, player in enumerate(players):
                        point_differentials[player] = plusminuses[idx]
    except Exception as exc:
        logging.error(url)
        logging.error(response.text)
        logging.error(str(exc))
        return None

    scorebox_meta_div = soup.find("div", class_="scorebox_meta")
    if not isinstance(scorebox_meta_div, Tag):
        dt, teams, venue_name = _find_old_dt(
            dfs=dfs,
            session=session,
            soup=soup,
            url=url,
            league=league,
            player_urls=player_urls,
            fg=fg,
            fga=fga,
            offensive_rebounds=offensive_rebounds,
            assists=assists,
            turnovers=turnovers,
            response=response,
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
        )
    else:
        dt, teams, venue_name = _find_new_dt(
            soup=soup,
            scorebox_meta_div=scorebox_meta_div,
            url=url,
            session=session,
            league=league,
            player_urls=player_urls,
            scores=scores,
            fg=fg,
            fga=fga,
            offensive_rebounds=offensive_rebounds,
            assists=assists,
            turnovers=turnovers,
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
        )
    for team in teams:
        if team.name == "File Not Found":
            raise ValueError("team name is File Not Found (invalid)")

    season_type = SeasonType.REGULAR
    for h2 in soup.find_all("h2"):
        a = h2.find("a")
        if a is None:
            continue
        season_text = a.get_text().strip()
        match season_text:
            case "Big Sky Conference":
                season_type = SeasonType.REGULAR
            case "Big East Conference":
                season_type = SeasonType.REGULAR
            case "Big West Conference":
                season_type = SeasonType.REGULAR
            case "Big Ten Conference":
                season_type = SeasonType.REGULAR
            case "Mid-American Conference":
                season_type = SeasonType.REGULAR
            case "Horizon League":
                season_type = SeasonType.REGULAR
            case "Atlantic 10 Conference":
                season_type = SeasonType.REGULAR
            case "Mountain West Conference":
                season_type = SeasonType.REGULAR
            case "West Coast Conference":
                season_type = SeasonType.REGULAR
            case "American Athletic Conference":
                season_type = SeasonType.REGULAR
            case "Coastal Athletic Association":
                season_type = SeasonType.REGULAR
            case "Conference USA":
                season_type = SeasonType.REGULAR
            case "America East Conference":
                season_type = SeasonType.REGULAR
            case "Sun Belt Conference":
                season_type = SeasonType.REGULAR
            case "Metro Atlantic Athletic Conference":
                season_type = SeasonType.REGULAR
            case "Atlantic Sun Conference":
                season_type = SeasonType.REGULAR
            case "Ohio Valley Conference":
                season_type = SeasonType.REGULAR
            case "Mid-Eastern Athletic Conference":
                season_type = SeasonType.REGULAR
            case "Big South Conference":
                season_type = SeasonType.REGULAR
            case "Summit League":
                season_type = SeasonType.REGULAR
            case "Western Athletic Conference":
                season_type = SeasonType.REGULAR
            case "Big 12 Conference":
                season_type = SeasonType.REGULAR
            case "Southeastern Conference":
                season_type = SeasonType.REGULAR
            case "Patriot League":
                season_type = SeasonType.REGULAR
            case "Southern Conference":
                season_type = SeasonType.REGULAR
            case "Missouri Valley Conference":
                season_type = SeasonType.REGULAR
            case "Atlantic Coast Conference":
                season_type = SeasonType.REGULAR
            case "Southwest Athletic Conference":
                season_type = SeasonType.REGULAR
            case "Southland Conference":
                season_type = SeasonType.REGULAR
            case "Northeast Conference":
                season_type = SeasonType.REGULAR
            case "Ivy League":
                season_type = SeasonType.REGULAR
            case "NCAA Men's Tournament":
                season_type = SeasonType.REGULAR
            case "Pac-12 Conference":
                season_type = SeasonType.REGULAR
            case "Colonial Athletic Association":
                season_type = SeasonType.REGULAR
            case "Pacific-12 Conference":
                season_type = SeasonType.REGULAR
            case "NCAA Women's Tournament":
                season_type = SeasonType.REGULAR
            case "Pacific-10 Conference":
                season_type = SeasonType.REGULAR
            case "Great West Conference":
                season_type = SeasonType.REGULAR
            case _:
                logging.warning("Unrecognised Season Text: %s", season_text)
        break

    return GameModel(
        dt=dt,
        week=None,
        game_number=None,
        venue=create_sportsreference_venue_model(venue_name, session, dt),  # pyright: ignore
        teams=teams,
        league=str(league),
        year=dt.year,
        season_type=season_type,
        end_dt=None,
        attendance=None,
        postponed=None,
        play_off=None,
        distance=None,
        dividends=[],
        pot=None,
        version=version,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_sportsreference_game_model(
    session: ScrapeSession,
    url: str,
    league: League,
    positions_validator: dict[str, str],
    version: str,
) -> GameModel | None:
    return _create_sportsreference_game_model(
        session=session,
        url=url,
        league=league,
        positions_validator=positions_validator,
        version=version,
    )


def create_sportsreference_game_model(
    session: ScrapeSession,
    url: str,
    league: League,
    positions_validator: dict[str, str],
) -> GameModel | None:
    """Create a sports reference game model."""
    if not pytest_is_running.is_running():
        return _cached_create_sportsreference_game_model(
            session=session,
            url=url,
            league=league,
            positions_validator=positions_validator,
            version=VERSION,
        )
    with session.cache_disabled():
        return _create_sportsreference_game_model(
            session=session,
            url=url,
            league=league,
            positions_validator=positions_validator,
            version=VERSION,
        )
