"""Tests for the player model class."""
import unittest

from sportsball.data.player_model import PlayerModel, VERSION
from sportsball.data.species import Species


class TestPlayerModel(unittest.TestCase):

    def setUp(self):
        self._player_model = PlayerModel(
            identifier="a",
            jersey="45",
            kicks=None,
            fumbles=None,
            fumbles_lost=None,
            field_goals=None,
            field_goals_attempted=10,
            offensive_rebounds=None,
            assists=None,
            turnovers=None,
            name="James Jones",
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
            starting_position=None,
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

    def test_field_goals_attempted(self):
        self.assertEqual(self._player_model.field_goals_attempted, 10)
