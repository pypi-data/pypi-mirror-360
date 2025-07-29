"""Tests for the sportsreference player model class."""
import datetime
import os
import unittest

import requests_mock
import requests_cache
from sportsball.data.sportsreference.sportsreference_player_model import create_sportsreference_player_model
from sportsball.data.sex import Sex


class TestSportsReferencePlayerModel(unittest.TestCase):

    def setUp(self):
        self.session = requests_cache.CachedSession(backend="memory")
        self.dir = os.path.dirname(__file__)

    def test_field_goals(self):
        url = "https://www.basketball-reference.com/players/b/barnesc01.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "barnesc01.html"), "rb") as f:
                m.get(url, content=f.read())
            player_model = create_sportsreference_player_model(
                session=self.session,
                player_url=url,
                fg={"Scottie Barnes": 8},
                fga={},
                offensive_rebounds={},
                assists={},
                turnovers={},
                positions={},
                positions_validator={},
                sex=Sex.MALE,
                dt=datetime.datetime(2022, 10, 10),
                minutes_played={},
                three_point_field_goals={},
                three_point_field_goals_attempted={},
                free_throws={},
                free_throws_attempted={},
                defensive_rebounds={},
                steals={},
                blocks={},
                personal_fouls={},
                points={},
                game_scores={},
                point_differentials={},
            )
            self.assertEqual(player_model.field_goals, 8)
