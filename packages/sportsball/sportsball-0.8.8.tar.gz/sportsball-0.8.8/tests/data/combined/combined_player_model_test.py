"""Tests for the combined player model class."""
import os
import unittest

import requests_mock
import requests_cache
from sportsball.data.combined.combined_player_model import create_combined_player_model
from sportsball.data.player_model import PlayerModel, VERSION
from sportsball.data.species import Species


class TestCombinedPlayerModel(unittest.TestCase):

    def setUp(self):
        self._session = requests_cache.CachedSession(backend="memory")
        self.dir = os.path.dirname(__file__)

    def test_field_goals_attempted(self):
        identifier = "a"
        field_goals_attempted = 10
        with requests_mock.Mocker() as m:
            player_model = PlayerModel(
                identifier="a",
                jersey="35",
                kicks=None,
                fumbles=None,
                fumbles_lost=None,
                field_goals=None,
                field_goals_attempted=field_goals_attempted,
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
            players_ffill = {}
            combined_player_model = create_combined_player_model(
                player_models=[player_model],
                identifier=identifier,
                player_ffill=players_ffill,
            )
            self.assertEqual(combined_player_model.field_goals_attempted, field_goals_attempted)
