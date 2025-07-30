"""The enumeration of the different supported leagues."""

from enum import StrEnum


class League(StrEnum):
    """An enumeration over the different leagues."""

    AFL = "afl"
    HKJC = "hkjc"
    NBA = "nba"
    NCAAB = "ncaab"
    NCAAF = "ncaaf"
    NFL = "nfl"


def long_name(league: League) -> str:
    """Find the leagues long name."""
    match league:
        case League.AFL:
            return "Australia Football League"
        case League.HKJC:
            return "Hong Kong Jockey Club"
        case League.NBA:
            return "National Basketball League"
        case League.NCAAB:
            return "NCAA Division I Basketball"
        case League.NCAAF:
            return "NCAA Division I Football"
        case League.NFL:
            return "National Football League"


def league_from_str(league_str: str) -> League:
    """Find the league matching the string."""
    league_str = league_str.lower()
    match league_str:
        case str(League.AFL):
            return League.AFL
        case str(League.HKJC):
            return League.HKJC
        case str(League.NBA):
            return League.NBA
        case str(League.NCAAB):
            return League.NCAAB
        case str(League.NCAAF):
            return League.NCAAF
        case str(League.NFL):
            return League.NFL
        case _:
            raise ValueError(f"Unrecognised League: {league_str}")
