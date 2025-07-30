"""Sports reference league model."""

# pylint: disable=line-too-long
import datetime
import urllib.parse
from typing import Iterator
from urllib.parse import parse_qs, urlparse

import tqdm
from bs4 import BeautifulSoup, Tag
from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ..game_model import GameModel
from ..league import League
from ..league_model import LeagueModel
from .sportsreference_game_model import create_sportsreference_game_model

REPLACEMENT_URLS = {
    "https://www.sports-reference.com/cbb/boxscores/2022-11-07-20-southeastern-louisian.html": "https://www.sports-reference.com/cbb/boxscores/2022-11-07-20-southeastern-louisiana.html",
}
BAD_URLS = {
    "https://www.sports-reference.com/cbb/boxscores/2024-12-28-01-austin-peay_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2023-12-30-14-northwestern-state_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2023-02-21-16-central-arkansas_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2023-02-17-13-alabama-birmingham_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2023-02-06-15-abilene-christian.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-12-17-19-pacific.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-12-13-21-pacific.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-12-11-19-pacific.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-11-07-17-north-carolina-greens.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-11-07-20-southern-illinois-edw.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-03-04-17-san-diego_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-02-17-21-san-diego_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2021-12-19-17-san-diego_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2021-11-27-19-san-diego_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2016-04-04-north-carolina.html",
    "https://www.sports-reference.com/cbb/boxscores/2009-12-09-00-mcneese-state_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2009-11-16-00-mcneese-state_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2009-11-14-san-diego_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2009-04-03-texas-el-paso.html",
    "https://www.sports-reference.com/cbb/boxscores/2009-04-01-texas-el-paso.html",
    "https://www.sports-reference.com/cbb/boxscores/2009-03-15-florida-state.html",
    "https://www.sports-reference.com/cbb/boxscores/2009-03-15-purdue.html",
    "https://www.sports-reference.com/cbb/boxscores/2008-11-19-alabama-am_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2008-04-04-tulsa.html",
}


def _find_game_urls(soup: BeautifulSoup, base_url: str) -> list[str]:
    urls = []
    for td in soup.find_all("td", class_="gamelink"):
        for a in td.find_all("a"):
            game_url = urllib.parse.urljoin(base_url, a.get("href"))
            if game_url.endswith(".htm"):
                game_url += "l"
            if game_url.endswith("."):
                game_url += "html"
            if game_url.endswith(".ht"):
                game_url += "ml"
            if game_url.endswith(".h"):
                game_url += "tml"
            if not game_url.endswith(".html"):
                game_url += ".html"
            game_url = REPLACEMENT_URLS.get(game_url, game_url)
            if game_url in BAD_URLS:
                continue
            urls.append(game_url)
    return urls


class SportsReferenceLeagueModel(LeagueModel):
    """Sports Reference implementation of the league model."""

    def __init__(
        self,
        session: ScrapeSession,
        league: League,
        base_url: str,
        position: int | None = None,
    ) -> None:
        super().__init__(league, session, position=position)
        self._base_url = base_url

    @classmethod
    def name(cls) -> str:
        return "sportsreference-league-model"

    @classmethod
    def position_validator(cls) -> dict[str, str]:
        """A dictionary that contains the mapping from positions to standard positions."""
        raise NotImplementedError(
            "position_validator is not implemented by parent class"
        )

    def _produce_games(
        self, soup: BeautifulSoup, pbar: tqdm.tqdm, url: str
    ) -> Iterator[GameModel]:
        for game_url in _find_game_urls(soup, url):
            pbar.update(1)
            game_model = create_sportsreference_game_model(
                self.session, game_url, self.league, self.position_validator()
            )
            if game_model is None:
                continue
            pbar.set_description(
                f"SportsReference {game_model.year} - {game_model.season_type} - {game_model.dt}"
            )
            yield game_model

    @property
    def games(self) -> Iterator[GameModel]:
        # pylint: disable=too-many-locals
        final_path: str | None = ""
        with tqdm.tqdm(position=self.position) as pbar:
            while final_path is not None:
                url = self._base_url + final_path
                if final_path:
                    response = self.session.get(url)
                else:
                    with self.session.cache_disabled():
                        response = self.session.get(url)
                response.raise_for_status()
                dt = datetime.datetime.now()
                if final_path:
                    parsed_url = urlparse(url)
                    query = parse_qs(parsed_url.query)
                    dt = datetime.datetime(
                        int(query["year"][0]),
                        int(query["month"][0]),
                        int(query["day"][0]),
                    )
                    if dt.year <= 1945:
                        break
                soup = BeautifulSoup(response.text, "lxml")
                yield from self._produce_games(soup, pbar, url)
                prev_a = soup.find("a", class_="prev")
                if isinstance(prev_a, Tag):
                    href = prev_a.get("href")
                    if isinstance(href, str):
                        prev_url = urllib.parse.urljoin(url, href)
                        final_path = prev_url.split("/")[-1]
                    else:
                        final_path = None
                else:
                    final_path = None
