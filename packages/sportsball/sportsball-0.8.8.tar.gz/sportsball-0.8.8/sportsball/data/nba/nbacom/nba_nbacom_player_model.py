"""NBA NBA.com player model."""

# pylint: disable=duplicate-code
from typing import Any

from ...player_model import VERSION, PlayerModel
from ...sex import Sex
from ...species import Species
from ..position import position_from_str


def create_nba_nbacom_player_model(player_dict: dict[str, Any]) -> PlayerModel:
    """Create a player model from AFL AFL."""
    return PlayerModel(
        identifier=str(player_dict["personId"]),
        jersey=None,
        kicks=None,
        fumbles=None,
        fumbles_lost=None,
        field_goals=None,
        field_goals_attempted=None,
        offensive_rebounds=None,
        assists=None,
        turnovers=None,
        name=player_dict["playerName"],
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
        birth_date=None,
        age=None,
        species=str(Species.HUMAN),
        handicap_weight=None,
        father=None,
        sex=str(Sex.MALE),
        starting_position=str(position_from_str(player_dict["position"])),
        weight=None,
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
        version=VERSION,
    )
