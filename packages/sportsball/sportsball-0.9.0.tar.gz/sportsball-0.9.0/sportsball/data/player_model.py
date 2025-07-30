"""The prototype class for a player."""

# pylint: disable=duplicate-code,too-many-lines
from __future__ import annotations

import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from .address_model import VERSION as ADDRESS_VERSION
from .address_model import AddressModel
from .delimiter import DELIMITER
from .field_type import FFILL_KEY, TYPE_KEY, FieldType
from .owner_model import VERSION as OWNER_VERSION
from .owner_model import OwnerModel
from .sex import (FEMALE_GENDERS, GENDER_DETECTOR, MALE_GENDERS,
                  UNCERTAIN_GENDERS, Sex)
from .venue_model import VERSION as VENUE_VERSION
from .venue_model import VenueModel

PLAYER_KICKS_COLUMN: Literal["kicks"] = "kicks"
PLAYER_IDENTIFIER_COLUMN: Literal["identifier"] = "identifier"
PLAYER_FUMBLES_COLUMN: Literal["fumbles"] = "fumbles"
PLAYER_FUMBLES_LOST_COLUMN: Literal["fumbles_lost"] = "fumbles_lost"
FIELD_GOALS_COLUMN: Literal["field_goals"] = "field_goals"
FIELD_GOALS_ATTEMPTED_COLUMN: Literal["field_goals_attempted"] = "field_goals_attempted"
OFFENSIVE_REBOUNDS_COLUMN: Literal["offensive_rebounds"] = "offensive_rebounds"
ASSISTS_COLUMN: Literal["assists"] = "assists"
TURNOVERS_COLUMN: Literal["turnovers"] = "turnovers"
PLAYER_MARKS_COLUMN: Literal["marks"] = "marks"
PLAYER_HANDBALLS_COLUMN: Literal["handballs"] = "handballs"
PLAYER_DISPOSALS_COLUMN: Literal["disposals"] = "disposals"
PLAYER_GOALS_COLUMN: Literal["goals"] = "goals"
PLAYER_BEHINDS_COLUMN: Literal["behinds"] = "behinds"
PLAYER_HIT_OUTS_COLUMN: Literal["hit_outs"] = "hit_outs"
PLAYER_TACKLES_COLUMN: Literal["tackles"] = "tackles"
PLAYER_REBOUNDS_COLUMN: Literal["rebounds"] = "rebounds"
PLAYER_INSIDES_COLUMN: Literal["insides"] = "insides"
PLAYER_CLEARANCES_COLUMN: Literal["clearances"] = "clearances"
PLAYER_CLANGERS_COLUMN: Literal["clangers"] = "clangers"
PLAYER_FREE_KICKS_FOR_COLUMN: Literal["free_kicks_for"] = "free_kicks_for"
PLAYER_FREE_KICKS_AGAINST_COLUMN: Literal["free_kicks_against"] = "free_kicks_against"
PLAYER_BROWNLOW_VOTES_COLUMN: Literal["brownlow_votes"] = "brownlow_votes"
PLAYER_CONTESTED_POSSESSIONS_COLUMN: Literal["contested_possessions"] = (
    "contested_possessions"
)
PLAYER_UNCONTESTED_POSSESSIONS_COLUMN: Literal["uncontested_possessions"] = (
    "uncontested_possessions"
)
PLAYER_CONTESTED_MARKS_COLUMN: Literal["contested_marks"] = "contested_marks"
PLAYER_MARKS_INSIDE_COLUMN: Literal["marks_inside"] = "marks_inside"
PLAYER_ONE_PERCENTERS_COLUMN: Literal["one_percenters"] = "one_percenters"
PLAYER_BOUNCES_COLUMN: Literal["bounces"] = "bounces"
PLAYER_GOAL_ASSISTS_COLUMN: Literal["goal_assists"] = "goal_assists"
PLAYER_PERCENTAGE_PLAYED_COLUMN: Literal["percentage_played"] = "percentage_played"
PLAYER_NAME_COLUMN: Literal["name"] = "name"
PLAYER_BIRTH_DATE_COLUMN: Literal["birth_date"] = "birth_date"
PLAYER_SPECIES_COLUMN: Literal["species"] = "species"
PLAYER_HANDICAP_WEIGHT_COLUMN: Literal["handicap_weight"] = "handicap_weight"
PLAYER_FATHER_COLUMN: Literal["father"] = "father"
PLAYER_SEX_COLUMN: Literal["sex"] = "sex"
PLAYER_AGE_COLUMN: Literal["age"] = "age"
PLAYER_STARTING_POSITION_COLUMN: Literal["starting_position"] = "starting_position"
PLAYER_WEIGHT_COLUMN: Literal["weight"] = "weight"
PLAYER_BIRTH_ADDRESS_COLUMN: Literal["birth_address"] = "birth_address"
PLAYER_OWNER_COLUMN: Literal["owner"] = "owner"
PLAYER_SECONDS_PLAYED_COLUMN: Literal["seconds_played"] = "seconds_played"
PLAYER_FIELD_GOALS_PERCENTAGE_COLUMN: Literal["field_goals_percentage"] = (
    "field_goals_percentage"
)
PLAYER_THREE_POINT_FIELD_GOALS_COLUMN: Literal["three_point_field_goals"] = (
    "three_point_field_goals"
)
PLAYER_THREE_POINT_FIELD_GOALS_ATTEMPTED_COLUMN: Literal[
    "three_point_field_goals_attempted"
] = "three_point_field_goals_attempted"
PLAYER_THREE_POINT_FIELD_GOALS_PERCENTAGE_COLUMN: Literal[
    "three_point_field_goals_percentage"
] = "three_point_field_goals_percentage"
PLAYER_FREE_THROWS_COLUMN: Literal["free_throws"] = "free_throws"
PLAYER_FREE_THROWS_ATTEMPTED_COLUMN: Literal["free_throws_attempted"] = (
    "free_throws_attempted"
)
PLAYER_FREE_THROWS_PERCENTAGE_COLUMN: Literal["free_throws_percentage"] = (
    "free_throws_percentage"
)
PLAYER_DEFENSIVE_REBOUNDS_COLUMN: Literal["defensive_rebounds"] = "defensive_rebounds"
PLAYER_TOTAL_REBOUNDS_COLUMN: Literal["total_rebounds"] = "total_rebounds"
PLAYER_STEALS_COLUMN: Literal["steals"] = "steals"
PLAYER_BLOCKS_COLUMN: Literal["blocks"] = "blocks"
PLAYER_PERSONAL_FOULS_COLUMN: Literal["personal_fouls"] = "personal_fouls"
PLAYER_POINTS_COLUMN: Literal["points"] = "points"
PLAYER_GAME_SCORE_COLUMN: Literal["game_score"] = "game_score"
PLAYER_POINT_DIFFERENTIAL_COLUMN: Literal["point_differential"] = "point_differential"
PLAYER_HEIGHT_COLUMN: Literal["height"] = "height"
PLAYER_COLLEGES_COLUMN: Literal["colleges"] = "colleges"
PLAYER_HEADSHOT_COLUMN: Literal["headshot"] = "headshot"
PLAYER_FORCED_FUMBLES_COLUMN: Literal["forced_fumbles"] = "forced_fumbles"
PLAYER_FUMBLES_RECOVERED_COLUMN: Literal["fumbles_recovered"] = "fumbles_recovered"
PLAYER_FUMBLES_RECOVERED_YARDS_COLUMN: Literal["fumbles_recovered_yards"] = (
    "fumbles_recovered_yards"
)
PLAYER_FUMBLES_TOUCHDOWNS_COLUMN: Literal["fumbles_touchdowns"] = "fumbles_touchdowns"
PLAYER_OFFENSIVE_TWO_POINT_RETURNS_COLUMN: Literal["offensive_two_point_returns"] = (
    "offensive_two_point_returns"
)
PLAYER_OFFENSIVE_FUMBLES_TOUCHDOWNS_COLUMN: Literal["offensive_fumbles_touchdowns"] = (
    "offensive_fumbles_touchdowns"
)
PLAYER_DEFENSIVE_FUMBLES_TOUCHDOWNS_COLUMN: Literal["defensive_fumbles_touchdowns"] = (
    "defensive_fumbles_touchdowns"
)
PLAYER_AVERAGE_GAIN_COLUMN: Literal["average_gain"] = "average_gain"
PLAYER_COMPLETION_PERCENTAGE_COLUMN: Literal["completion_percentage"] = (
    "completion_percentage"
)
PLAYER_COMPLETIONS_COLUMN: Literal["completions"] = "completions"
PLAYER_ESPN_QUARTERBACK_RATING_COLUMN: Literal["espn_quarterback_rating"] = (
    "espn_quarterback_rating"
)
PLAYER_INTERCEPTION_PERCENTAGE_COLUMN: Literal["interception_percentage"] = (
    "interception_percentage"
)
PLAYER_INTERCEPTIONS_COLUMN: Literal["interceptions"] = "interceptions"
PLAYER_LONG_PASSING_COLUMN: Literal["long_passing"] = "long_passing"
PLAYER_MISC_YARDS_COLUMN: Literal["misc_yards"] = "misc_yards"
PLAYER_NET_PASSING_YARDS_COLUMN: Literal["net_passing_yards"] = "net_passing_yards"
PLAYER_NET_TOTAL_YARDS_COLUMN: Literal["net_total_yards"] = "net_total_yards"
PLAYER_PASSING_ATTEMPTS_COLUMN: Literal["passing_attempts"] = "passing_attempts"
PLAYER_PASSING_BIG_PLAYS_COLUMN: Literal["passing_big_plays"] = "passing_big_plays"
PLAYER_PASSING_FIRST_DOWNS_COLUMN: Literal["passing_first_downs"] = (
    "passing_first_downs"
)
PLAYER_PASSING_FUMBLES_COLUMN: Literal["passing_fumbles"] = "passing_fumbles"
PLAYER_PASSING_FUMBLES_LOST_COLUMN: Literal["passing_fumbles_lost"] = (
    "passing_fumbles_lost"
)
PLAYER_PASSING_TOUCHDOWN_PERCENTAGE_COLUMN: Literal["passing_touchdown_percentage"] = (
    "passing_touchdown_percentage"
)
PLAYER_PASSING_TOUCHDOWNS_COLUMN: Literal["passing_touchdowns"] = "passing_touchdowns"
PLAYER_PASSING_YARDS_COLUMN: Literal["passing_yards"] = "passing_yards"
PLAYER_PASSING_YARDS_AFTER_CATCH_COLUMN: Literal["passing_yards_after_catch"] = (
    "passing_yards_after_catch"
)
PLAYER_PASSING_YARDS_AT_CATCH_COLUMN: Literal["passing_yards_at_catch"] = (
    "passing_yards_at_catch"
)
PLAYER_QUARTERBACK_RATING_COLUMN: Literal["quarterback_rating"] = "quarterback_rating"
PLAYER_SACKS_COLUMN: Literal["sacks"] = "sacks"
PLAYER_SACKS_YARDS_LOST_COLUMN: Literal["sacks_yards_lost"] = "sacks_yards_lost"
PLAYER_NET_PASSING_ATTEMPTS_COLUMN: Literal["net_passing_attempts"] = (
    "net_passing_attempts"
)
PLAYER_TOTAL_OFFENSIVE_PLAYS_COLUMN: Literal["total_offensive_plays"] = (
    "total_offensive_plays"
)
PLAYER_TOTAL_POINTS_COLUMN: Literal["total_points"] = "total_points"
PLAYER_TOTAL_TOUCHDOWNS_COLUMN: Literal["total_touchdowns"] = "total_touchdowns"
PLAYER_TOTAL_YARDS_COLUMN: Literal["total_yards"] = "total_yards"
PLAYER_TOTAL_YARDS_FROM_SCRIMMAGE_COLUMN: Literal["total_yards_from_scrimmage"] = (
    "total_yards_from_scrimmage"
)
PLAYER_TWO_POINT_PASS_COLUMN: Literal["two_point_pass"] = "two_point_pass"
PLAYER_TWO_POINT_PASS_ATTEMPT_COLUMN: Literal["two_point_pass_attempt"] = (
    "two_point_pass_attempt"
)
PLAYER_YARDS_PER_COMPLETION_COLUMN: Literal["yards_per_completion"] = (
    "yards_per_completion"
)
PLAYER_YARDS_PER_PASS_ATTEMPT_COLUMN: Literal["yards_per_pass_attempt"] = (
    "yards_per_pass_attempt"
)
PLAYER_NET_YARDS_PER_PASS_ATTEMPT_COLUMN: Literal["net_yards_per_pass_attempt"] = (
    "net_yards_per_pass_attempt"
)
PLAYER_ESPN_RUNNINGBACK_RATING_COLUMN: Literal["espn_runningback"] = "espn_runningback"
PLAYER_LONG_RUSHING_COLUMN: Literal["long_rushing"] = "long_rushing"
PLAYER_RUSHING_ATTEMPTS_COLUMN: Literal["rushing_attempts"] = "rushing_attempts"
PLAYER_RUSHING_BIG_PLAYS_COLUMN: Literal["rushing_big_plays"] = "rushing_big_plays"
PLAYER_RUSHING_FIRST_DOWNS_COLUMN: Literal["rushing_first_downs"] = (
    "rushing_first_downs"
)
PLAYER_RUSHING_FUMBLES_COLUMN: Literal["rushing_fumbles"] = "rushing_fumbles"
PLAYER_RUSHING_FUMBLES_LOST_COLUMN: Literal["rushing_fumbles_lost"] = (
    "rushing_fumbles_lost"
)
PLAYER_RUSHING_TOUCHDOWNS_COLUMN: Literal["rushing_touchdowns"] = "rushing_touchdowns"
PLAYER_RUSHING_YARDS_COLUMN: Literal["rushing_yards"] = "rushing_yards"
PLAYER_STUFFS_COLUMN: Literal["stuffs"] = "stuffs"
PLAYER_STUFF_YARDS_LOST: Literal["stuff_yards_lost"] = "stuff_yards_lost"
PLAYER_TWO_POINT_RUSH_COLUMN: Literal["two_point_rush"] = "two_point_rush"
PLAYER_TWO_POINT_RUSH_ATTEMPTS_COLUMN: Literal["two_point_rush_attempts"] = (
    "two_point_rush_attempts"
)
PLAYER_YARDS_PER_RUSH_ATTEMPT_COLUMN: Literal["yards_per_rush_attempt"] = (
    "yards_per_rush_attempt"
)
PLAYER_ESPN_WIDERECEIVER_COLUMN: Literal["espn_widereceiver"] = "espn_widereceiver"
PLAYER_LONG_RECEPTION_COLUMN: Literal["long_reception"] = "long_reception"
PLAYER_RECEIVING_BIG_PLAYS_COLUMN: Literal["receiving_big_plays"] = (
    "receiving_big_plays"
)
PLAYER_RECEIVING_FIRST_DOWNS_COLUMN: Literal["receiving_first_downs"] = (
    "receiving_first_downs"
)
PLAYER_RECEIVING_FUMBLES_COLUMN: Literal["receiving_fumbles"] = "receiving_fumbles"
PLAYER_RECEIVING_FUMBLES_LOST_COLUMN: Literal["receiving_fumbles_lost"] = (
    "receiving_fumbles_lost"
)
PLAYER_RECEIVING_TARGETS_COLUMN: Literal["receiving_targets"] = "receiving_targets"
PLAYER_RECEIVING_TOUCHDOWNS_COLUMN: Literal["receiving_touchdowns"] = (
    "receiving_touchdowns"
)
PLAYER_RECEIVING_YARDS_COLUMN: Literal["receiving_yards"] = "receiving_yards"
PLAYER_RECEIVING_YARDS_AFTER_CATCH_COLUMN: Literal["receiving_yards_after_catch"] = (
    "receiving_yards_after_catch"
)
PLAYER_RECEIVING_YARDS_AT_CATCH_COLUMN: Literal["receiving_yards_at_catch"] = (
    "receiving_yards_at_catch"
)
PLAYER_RECEPTIONS_COLUMN: Literal["receptions"] = "receptions"
PLAYER_TWO_POINT_RECEPTIONS_COLUMN: Literal["two_point_receptions"] = (
    "two_point_receptions"
)
PLAYER_TWO_POINT_RECEPTION_ATTEMPTS_COLUMN: Literal["two_point_reception_attempts"] = (
    "two_point_reception_attempts"
)
PLAYER_YARDS_PER_RECEPTION_COLUMN: Literal["yards_per_reception"] = (
    "yards_per_reception"
)
PLAYER_ASSIST_TACKLES_COLUMN: Literal["assist_tackles"] = "assist_tackles"
PLAYER_AVERAGE_INTERCEPTION_YARDS_COLUMN: Literal["average_interception_yards"] = (
    "average_interception_yards"
)
PLAYER_AVERAGE_SACK_YARDS_COLUMN: Literal["average_sack_yards"] = "average_sack_yards"
PLAYER_AVERAGE_STUFF_YARDS_COLUMN: Literal["average_stuff_yards"] = (
    "average_stuff_yards"
)
PLAYER_BLOCKED_FIELD_GOAL_TOUCHDOWNS_COLUMN: Literal[
    "blocked_field_goal_touchdowns"
] = "blocked_field_goal_touchdowns"
PLAYER_BLOCKED_PUNT_TOUCHDOWNS_COLUMN: Literal["blocked_punt_touchdowns"] = (
    "blocked_punt_touchdowns"
)
PLAYER_DEFENSIVE_TOUCHDOWNS_COLUMN: Literal["defensive_touchdowns"] = (
    "defensive_touchdowns"
)
PLAYER_HURRIES_COLUMN: Literal["hurries"] = "hurries"
PLAYER_KICKS_BLOCKED_COLUMN: Literal["kicks_blocked"] = "kicks_blocked"
PLAYER_LONG_INTERCEPTION_COLUMN: Literal["long_interception"] = "long_interception"
PLAYER_MISC_TOUCHDOWNS_COLUMN: Literal["misc_touchdowns"] = "misc_touchdowns"
PLAYER_PASSES_BATTED_DOWN_COLUMN: Literal["passes_batted_down"] = "passes_batted_down"
PLAYER_PASSES_DEFENDED_COLUMN: Literal["passes_defended"] = "passes_defended"
PLAYER_QUARTERBACK_HITS_COLUMN: Literal["quarterback_hits"] = "quarterback_hits"
PLAYER_SACKS_ASSISTED_COLUMN: Literal["sacks_assisted"] = "sacks_assisted"
PLAYER_SACKS_UNASSISTED_COLUMN: Literal["sacks_unassisted"] = "sacks_unassisted"
PLAYER_SACKS_YARDS_COLUMN: Literal["sacks_yards"] = "sacks_yards"
PLAYER_SAFETIES_COLUMN: Literal["safeties"] = "safeties"
PLAYER_SOLO_TACKLES_COLUMN: Literal["solo_tackles"] = "solo_tackles"
PLAYER_STUFF_YARDS_COLUMN: Literal["stuff_yards"] = "stuff_yards"
PLAYER_TACKLES_FOR_LOSS_COLUMN: Literal["tackles_for_loss"] = "tackles_for_loss"
PLAYER_TACKLES_YARDS_LOST_COLUMN: Literal["tackles_yards_lost"] = "tackles_yards_lost"
PLAYER_YARDS_ALLOWED_COLUMN: Literal["yards_allowed"] = "yards_allowed"
PLAYER_POINTS_ALLOWED_COLUMN: Literal["points_allowed"] = "points_allowed"
PLAYER_ONE_POINT_SAFETIES_MADE_COLUMN: Literal["one_point_safeties_made"] = (
    "one_point_safeties_made"
)
PLAYER_MISSED_FIELD_GOAL_RETURN_TD_COLUMN: Literal["missed_field_goal_return_td"] = (
    "missed_field_goal_return_td"
)
PLAYER_BLOCKED_PUNT_EZ_REC_TD_COLUMN: Literal["blocked_punt_ez_rec_td"] = (
    "blocked_punt_ez_rec_td"
)
PLAYER_INTERCEPTION_TOUCHDOWNS_COLUMN: Literal["interception_touchdowns"] = (
    "interception_touchdowns"
)
PLAYER_INTERCEPTION_YARDS_COLUMN: Literal["interception_yards"] = "interception_yards"
PLAYER_AVERAGE_KICKOFF_RETURN_YARDS_COLUMN: Literal["average_kickoff_return_yards"] = (
    "average_kickoff_return_yards"
)
PLAYER_AVERAGE_KICKOFF_YARDS_COLUMN: Literal["average_kickoff_yards"] = (
    "average_kickoff_yards"
)
PLAYER_EXTRA_POINT_ATTEMPTS_COLUMN: Literal["extra_point_attempts"] = (
    "extra_point_attempts"
)
PLAYER_EXTRA_POINT_PERCENTAGE_COLUMN: Literal["extra_point_percentage"] = (
    "extra_point_percentage"
)
PLAYER_EXTRA_POINT_BLOCKED_COLUMN: Literal["extra_point_blocked"] = (
    "extra_point_blocked"
)
PLAYER_EXTRA_POINTS_BLOCKED_PERCENTAGE_COLUMN: Literal[
    "extra_points_blocked_percentage"
] = "extra_points_blocked_percentage"
PLAYER_EXTRA_POINTS_MADE_COLUMN: Literal["extra_points_made"] = "extra_points_made"
PLAYER_FAIR_CATCHES_COLUMN: Literal["fair_catches"] = "fair_catches"
PLAYER_FAIR_CATCH_PERCENTAGE_COLUMN: Literal["fair_catch_percentage"] = (
    "fair_catch_percentage"
)
PLAYER_FIELD_GOAL_ATTEMPTS_MAX_19_YARDS_COLUMN: Literal[
    "field_goal_attempts_max_19_yards"
] = "field_goal_attempts_max_19_yards"
PLAYER_FIELD_GOAL_ATTEMPTS_MAX_29_YARDS_COLUMN: Literal[
    "field_goal_attempts_max_29_yards"
] = "field_goal_attempts_max_29_yards"
PLAYER_FIELD_GOAL_ATTEMPTS_MAX_39_YARDS_COLUMN: Literal[
    "field_goal_attempts_max_39_yards"
] = "field_goal_attempts_max_39_yards"
PLAYER_FIELD_GOAL_ATTEMPTS_MAX_49_YARDS_COLUMN: Literal[
    "field_goal_attempts_max_49_yards"
] = "field_goal_attempts_max_49_yards"
PLAYER_FIELD_GOAL_ATTEMPTS_MAX_59_YARDS_COLUMN: Literal[
    "field_goal_attempts_max_59_yards"
] = "field_goal_attempts_max_59_yards"
PLAYER_FIELD_GOAL_ATTEMPTS_MAX_99_YARDS_COLUMN: Literal[
    "field_goal_attempts_max_99_yards"
] = "field_goal_attempts_max_99_yards"
PLAYER_FIELD_GOAL_ATTEMPTS_ABOVE_50_YARDS_COLUMN: Literal[
    "field_goal_attempts_above_50_yards"
] = "field_goal_attempts_above_50_yards"
PLAYER_FIELD_GOAL_ATTEMPT_YARDS_COLUMN: Literal["field_goal_attempt_yards"] = (
    "field_goal_attempt_yards"
)
PLAYER_FIELD_GOALS_BLOCKED_COLUMN: Literal["field_goals_blocked"] = (
    "field_goals_blocked"
)
PLAYER_FIELD_GOALS_BLOCKED_PERCENTAGE_COLUMN: Literal[
    "field_goals_blocked_percentage"
] = "field_goals_blocked_percentage"
PLAYER_FIELD_GOALS_MADE_COLUMN: Literal["field_goals_made"] = "field_goals_made"
PLAYER_FIELD_GOALS_MADE_MAX_19_YARDS_COLUMN: Literal[
    "field_goals_made_max_19_yards"
] = "field_goals_made_max_19_yards"
PLAYER_FIELD_GOALS_MADE_MAX_29_YARDS_COLUMN: Literal[
    "field_goals_made_max_29_yards"
] = "field_goals_made_max_29_yards"
PLAYER_FIELD_GOALS_MADE_MAX_39_YARDS_COLUMN: Literal[
    "field_goals_made_max_39_yards"
] = "field_goals_made_max_39_yards"
PLAYER_FIELD_GOALS_MADE_MAX_49_YARDS_COLUMN: Literal[
    "field_goals_made_max_49_yards"
] = "field_goals_made_max_49_yards"
PLAYER_FIELD_GOALS_MADE_MAX_59_YARDS_COLUMN: Literal[
    "field_goals_made_max_59_yards"
] = "field_goals_made_max_59_yards"
PLAYER_FIELD_GOALS_MADE_MAX_99_YARDS_COLUMN: Literal[
    "field_goals_made_max_99_yards"
] = "field_goals_made_max_99_yards"
PLAYER_FIELD_GOALS_MADE_ABOVE_50_YARDS_COLUMN: Literal[
    "field_goals_made_above_50_yards"
] = "field_goals_made_above_50_yards"
PLAYER_FIELD_GOALS_MADE_YARDS_COLUMN: Literal["field_goals_made_yards"] = (
    "field_goals_made_yards"
)
PLAYER_FIELD_GOALS_MISSED_YARDS_COLUMN: Literal["field_goals_missed_yards"] = (
    "field_goals_missed_yards"
)
PLAYER_KICKOFF_OUT_OF_BOUNDS_COLUMN: Literal["kickoff_out_of_bounds"] = (
    "kickoff_out_of_bounds"
)
PLAYER_KICKOFF_RETURNS_COLUMN: Literal["kickoff_returns"] = "kickoff_returns"
PLAYER_KICKOFF_RETURNS_TOUCHDOWNS_COLUMN: Literal["kickoff_returns_touchdowns"] = (
    "kickoff_returns_touchdowns"
)
PLAYER_KICKOFF_RETURN_YARDS_COLUMN: Literal["kickoff_return_yards"] = (
    "kickoff_return_yards"
)
PLAYER_KICKOFFS_COLUMN: Literal["kickoffs"] = "kickoffs"
PLAYER_KICKOFF_YARDS_COLUMN: Literal["kickoff_yards"] = "kickoff_yards"
PLAYER_LONG_FIELD_GOAL_ATTEMPT_COLUMN: Literal["long_field_goal_attempt"] = (
    "long_field_goal_attempt"
)
PLAYER_LONG_FIELD_GOAL_MADE_COLUMN: Literal["long_field_goal_made"] = (
    "long_field_goal_made"
)
PLAYER_LONG_KICKOFF_COLUMN: Literal["long_kickoff"] = "long_kickoff"
PLAYER_TOTAL_KICKING_POINTS_COLUMN: Literal["total_kicking_points"] = (
    "total_kicking_points"
)
PLAYER_TOUCHBACK_PERCENTAGE_COLUMN: Literal["touchback_percentage"] = (
    "touchback_percentage"
)
PLAYER_TOUCHBACKS_COLUMN: Literal["touchbacks"] = "touchbacks"
PLAYER_DEFENSIVE_FUMBLE_RETURNS_COLUMN: Literal["defensive_fumble_returns"] = (
    "defensive_fumble_returns"
)
PLAYER_DEFENSIVE_FUMBLE_RETURN_YARDS_COLUMN: Literal[
    "defensive_fumble_return_yards"
] = "defensive_fumble_return_yards"
PLAYER_FUMBLE_RECOVERIES_COLUMN: Literal["fumble_recoveries"] = "fumble_recoveries"
PLAYER_FUMBLE_RECOVERY_YARDS_COLUMN: Literal["fumble_recovery_yards"] = (
    "fumble_recovery_yards"
)
PLAYER_KICK_RETURN_FAIR_CATCHES_COLUMN: Literal["kick_return_fair_catches"] = (
    "kick_return_fair_catches"
)
PLAYER_KICK_RETURN_FAIR_CATCH_PERCENTAGE_COLUMN: Literal[
    "kick_return_fair_catch_percentage"
] = "kick_return_fair_catch_percentage"
PLAYER_KICK_RETURN_FUMBLES_COLUMN: Literal["kick_return_fumbles"] = (
    "kick_return_fumbles"
)
PLAYER_KICK_RETURN_FUMBLES_LOST_COLUMN: Literal["kick_return_fumbles_lost"] = (
    "kick_return_fumbles_lost"
)
PLAYER_KICK_RETURNS_COLUMN: Literal["kick_returns"] = "kick_returns"
PLAYER_KICK_RETURN_TOUCHDOWNS_COLUMN: Literal["kick_return_touchdowns"] = (
    "kick_return_touchdowns"
)
PLAYER_KICK_RETURN_YARDS_COLUMN: Literal["kick_return_yards"] = "kick_return_yards"
PLAYER_LONG_KICK_RETURN_COLUMN: Literal["long_kick_return"] = "long_kick_return"
PLAYER_LONG_PUNT_RETURN_COLUMN: Literal["long_punt_return"] = "long_punt_return"
PLAYER_MISC_FUMBLE_RETURNS_COLUMN: Literal["misc_fumble_returns"] = (
    "misc_fumble_returns"
)
PLAYER_MISC_FUMBLE_RETURN_YARDS_COLUMN: Literal["misc_fumble_return_yards"] = (
    "misc_fumble_return_yards"
)
PLAYER_OPPOSITION_FUMBLE_RECOVERIES_COLUMN: Literal["opposition_fumble_recoveries"] = (
    "opposition_fumble_recoveries"
)
PLAYER_OPPOSITION_FUMBLE_RECOVERY_YARDS_COLUMN: Literal[
    "opposition_fumble_recovery_yards"
] = "opposition_fumble_recovery_yards"
PLAYER_OPPOSITION_SPECIAL_TEAM_FUMBLE_RETURNS_COLUMN: Literal[
    "opposition_special_team_fumble_returns"
] = "opposition_special_team_fumble_returns"
PLAYER_OPPOSITION_SPECIAL_TEAM_FUMBLE_RETURN_YARDS_COLUMN: Literal[
    "opposition_special_team_fumble_return_yards"
] = "opposition_special_team_fumble_return_yards"
PLAYER_PUNT_RETURN_FAIR_CATCHES_COLUMN: Literal["punt_return_fair_catches"] = (
    "punt_return_fair_catches"
)
PLAYER_PUNT_RETURN_FAIR_CATCH_PERCENTAGE_COLUMN: Literal[
    "punt_return_fair_catch_percentage"
] = "punt_return_fair_catch_percentage"
PLAYER_PUNT_RETURN_FUMBLES_COLUMN: Literal["punt_return_fumbles"] = (
    "punt_return_fumbles"
)
PLAYER_PUNT_RETURN_FUMBLES_LOST_COLUMN: Literal["punt_return_fumbles_lost"] = (
    "punt_return_fumbles_lost"
)
PLAYER_PUNT_RETURNS_COLUMN: Literal["punt_returns"] = "punt_returns"
PLAYER_PUNT_RETURNS_STARTED_INSIDE_THE_10_COLUMN: Literal[
    "punt_returns_started_inside_the_10"
] = "punt_returns_started_inside_the_10"
PLAYER_PUNT_RETURNS_STARTED_INSIDE_THE_20_COLUMN: Literal[
    "punt_returns_started_inside_the_20"
] = "punt_returns_started_inside_the_20"
PLAYER_PUNT_RETURN_TOUCHDOWNS_COLUMN: Literal["punt_return_touchdowns"] = (
    "punt_return_touchdowns"
)
PLAYER_PUNT_RETURN_YARDS_COLUMN: Literal["punt_return_yards"] = "punt_return_yards"
PLAYER_SPECIAL_TEAM_FUMBLE_RETURNS_COLUMN: Literal["special_team_fumble_returns"] = (
    "special_team_fumble_returns"
)
PLAYER_SPECIAL_TEAM_FUMBLE_RETURN_YARDS_COLUMN: Literal[
    "special_team_fumble_return_yards"
] = "special_team_fumble_return_yards"
PLAYER_YARDS_PER_KICK_RETURN_COLUMN: Literal["yards_per_kick_return"] = (
    "yards_per_kick_return"
)
PLAYER_YARDS_PER_PUNT_RETURN_COLUMN: Literal["yards_per_punt_return"] = (
    "yards_per_punt_return"
)
PLAYER_YARDS_PER_RETURN_COLUMN: Literal["yards_per_return"] = "yards_per_return"
PLAYER_AVERAGE_PUNT_RETURN_YARDS_COLUMN: Literal["average_punt_return_yards"] = (
    "average_punt_return_yards"
)
PLAYER_GROSS_AVERAGE_PUNT_YARDS_COLUMN: Literal["gross_average_punt_yards"] = (
    "gross_average_punt_yards"
)
PLAYER_LONG_PUNT_COLUMN: Literal["long_punt"] = "long_punt"
PLAYER_NET_AVERAGE_PUNT_YARDS_COLUMN: Literal["net_average_punt_yards"] = (
    "net_average_punt_yards"
)
PLAYER_PUNTS_COLUMN: Literal["punts"] = "punts"
PLAYER_PUNTS_BLOCKED_COLUMN: Literal["punts_blocked"] = "punts_blocked"
PLAYER_PUNTS_BLOCKED_PERCENTAGE_COLUMN: Literal["punts_blocked_percentage"] = (
    "punts_blocked_percentage"
)
PLAYER_PUNTS_INSIDE_10_COLUMN: Literal["punts_inside_10"] = "punts_inside_10"
PLAYER_PUNTS_INSIDE_10_PERCENTAGE_COLUMN: Literal["punts_inside_10_percentage"] = (
    "punts_inside_10_percentage"
)
PLAYER_PUNTS_INSIDE_20_COLUMN: Literal["punts_inside_20"] = "punts_inside_20"
PLAYER_PUNTS_INSIDE_20_PERCENTAGE_COLUMN: Literal["punts_inside_20_percentage"] = (
    "punts_inside_20_percentage"
)
PLAYER_PUNTS_OVER_50_COLUMN: Literal["punts_over_50"] = "punts_over_50"
PLAYER_PUNT_YARDS_COLUMN: Literal["punt_yards"] = "punt_yards"
PLAYER_DEFENSIVE_POINTS_COLUMN: Literal["defensive_points"] = "defensive_points"
PLAYER_MISC_POINTS_COLUMN: Literal["misc_points"] = "misc_points"
PLAYER_RETURN_TOUCHDOWNS_COLUMN: Literal["return_touchdowns"] = "return_touchdowns"
PLAYER_TOTAL_TWO_POINT_CONVERSIONS_COLUMN: Literal["total_two_point_conversions"] = (
    "total_two_point_conversions"
)
PLAYER_PASSING_TOUCHDOWNS_9_YARDS_COLUMN: Literal["passing_touchdowns_9_yards"] = (
    "passing_touchdowns_9_yards"
)
PLAYER_PASSING_TOUCHDOWNS_19_YARDS_COLUMN: Literal["passing_touchdowns_19_yards"] = (
    "passing_touchdowns_19_yards"
)
PLAYER_PASSING_TOUCHDOWNS_29_YARDS_COLUMN: Literal["passing_touchdowns_29_yards"] = (
    "passing_touchdowns_29_yards"
)
PLAYER_PASSING_TOUCHDOWNS_39_YARDS_COLUMN: Literal["passing_touchdowns_39_yards"] = (
    "passing_touchdowns_39_yards"
)
PLAYER_PASSING_TOUCHDOWNS_49_YARDS_COLUMN: Literal["passing_touchdowns_49_yards"] = (
    "passing_touchdowns_49_yards"
)
PLAYER_PASSING_TOUCHDOWNS_ABOVE_50_YARDS_COLUMN: Literal[
    "passing_touchdowns_above_50_yards"
] = "passing_touchdowns_above_50_yards"
PLAYER_RECEIVING_TOUCHDOWNS_9_YARDS_COLUMN: Literal["receiving_touchdowns_9_yards"] = (
    "receiving_touchdowns_9_yards"
)
PLAYER_RECEIVING_TOUCHDOWNS_19_YARDS_COLUMN: Literal[
    "receiving_touchdowns_19_yards"
] = "receiving_touchdowns_19_yards"
PLAYER_RECEIVING_TOUCHDOWNS_29_YARDS_COLUMN: Literal[
    "receiving_touchdowns_29_yards"
] = "receiving_touchdowns_29_yards"
PLAYER_RECEIVING_TOUCHDOWNS_39_YARDS_COLUMN: Literal[
    "receiving_touchdowns_39_yards"
] = "receiving_touchdowns_39_yards"
PLAYER_RECEIVING_TOUCHDOWNS_49_YARDS_COLUMN: Literal[
    "receiving_touchdowns_49_yards"
] = "receiving_touchdowns_49_yards"
PLAYER_RECEIVING_TOUCHDOWNS_ABOVE_50_YARDS_COLUMN: Literal[
    "receiving_touchdowns_above_50_yards"
] = "receiving_touchdowns_above_50_yards"
PLAYER_RUSHING_TOUCHDOWNS_9_YARDS_COLUMN: Literal["rushing_touchdowns_9_yards"] = (
    "rushing_touchdowns_9_yards"
)
PLAYER_RUSHING_TOUCHDOWNS_19_YARDS_COLUMN: Literal["rushing_touchdowns_19_yards"] = (
    "rushing_touchdowns_19_yards"
)
PLAYER_RUSHING_TOUCHDOWNS_29_YARDS_COLUMN: Literal["rushing_touchdowns_29_yards"] = (
    "rushing_touchdowns_29_yards"
)
PLAYER_RUSHING_TOUCHDOWNS_39_YARDS_COLUMN: Literal["rushing_touchdowns_39_yards"] = (
    "rushing_touchdowns_39_yards"
)
PLAYER_RUSHING_TOUCHDOWNS_49_YARDS_COLUMN: Literal["rushing_touchdowns_49_yards"] = (
    "rushing_touchdowns_49_yards"
)
PLAYER_RUSHING_TOUCHDOWNS_ABOVE_50_YARDS_COLUMN: Literal[
    "rushing_touchdowns_above_50_yards"
] = "rushing_touchdowns_above_50_yards"
VERSION = DELIMITER.join(["0.0.2", ADDRESS_VERSION, OWNER_VERSION, VENUE_VERSION])


def _guess_sex(data: dict[str, Any]) -> str | None:
    name = data[PLAYER_NAME_COLUMN]
    gender_tag = GENDER_DETECTOR.get_gender(name)
    if gender_tag in MALE_GENDERS:
        return str(Sex.MALE)
    if gender_tag in FEMALE_GENDERS:
        return str(Sex.FEMALE)
    if gender_tag in UNCERTAIN_GENDERS:
        return None
    return None


def _calculate_field_goals_percentage(data: dict[str, Any]) -> float | None:
    field_goals = data.get(FIELD_GOALS_COLUMN)
    if field_goals is None:
        return None
    field_goals_attempted = data.get(FIELD_GOALS_ATTEMPTED_COLUMN)
    if field_goals_attempted is None:
        return None
    if field_goals_attempted == 0:
        return 0.0
    return float(field_goals) / float(field_goals_attempted)  # type: ignore


def _calculate_three_point_field_goals_percentage(data: dict[str, Any]) -> float | None:
    three_point_field_goals = data.get(PLAYER_THREE_POINT_FIELD_GOALS_COLUMN)
    if three_point_field_goals is None:
        return None
    three_point_field_goals_attempted = data.get(
        PLAYER_THREE_POINT_FIELD_GOALS_ATTEMPTED_COLUMN
    )
    if three_point_field_goals_attempted is None:
        return None
    if three_point_field_goals_attempted == 0:
        return 0.0
    return float(three_point_field_goals) / float(three_point_field_goals_attempted)  # type: ignore


def _calculate_free_throws_percentage(data: dict[str, Any]) -> float | None:
    free_throws = data.get(PLAYER_FREE_THROWS_COLUMN)
    if free_throws is None:
        return None
    free_throws_attempted = data.get(PLAYER_FREE_THROWS_ATTEMPTED_COLUMN)
    if free_throws_attempted is None:
        return None
    if free_throws_attempted == 0:
        return 0.0
    return float(free_throws) / float(free_throws_attempted)  # type: ignore


def _calculate_total_rebounds(data: dict[str, Any]) -> int | None:
    offensive_rebounds = data.get(OFFENSIVE_REBOUNDS_COLUMN)
    if offensive_rebounds is None:
        return None
    defensive_rebounds = data.get(PLAYER_DEFENSIVE_REBOUNDS_COLUMN)
    if defensive_rebounds:
        return None
    return offensive_rebounds + defensive_rebounds


class PlayerModel(BaseModel):
    """The serialisable player class."""

    identifier: str = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.CATEGORICAL},
        alias=PLAYER_IDENTIFIER_COLUMN,
    )
    jersey: str | None = Field(..., json_schema_extra={TYPE_KEY: FieldType.CATEGORICAL})
    kicks: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICKS_COLUMN,
    )
    fumbles: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FUMBLES_COLUMN,
    )
    fumbles_lost: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FUMBLES_LOST_COLUMN,
    )
    field_goals: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=FIELD_GOALS_COLUMN,
    )
    field_goals_attempted: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=FIELD_GOALS_ATTEMPTED_COLUMN,
    )
    offensive_rebounds: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=OFFENSIVE_REBOUNDS_COLUMN,
    )
    assists: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=ASSISTS_COLUMN,
    )
    turnovers: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TURNOVERS_COLUMN,
    )
    name: str = Field(..., alias=PLAYER_NAME_COLUMN)
    marks: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_MARKS_COLUMN,
    )
    handballs: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_HANDBALLS_COLUMN,
    )
    disposals: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_DISPOSALS_COLUMN,
    )
    goals: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_GOALS_COLUMN,
    )
    behinds: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_BEHINDS_COLUMN,
    )
    hit_outs: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_HIT_OUTS_COLUMN,
    )
    tackles: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TACKLES_COLUMN,
    )
    rebounds: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_REBOUNDS_COLUMN,
    )
    insides: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_INSIDES_COLUMN,
    )
    clearances: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_CLEARANCES_COLUMN,
    )
    clangers: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_CLANGERS_COLUMN,
    )
    free_kicks_for: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FREE_KICKS_FOR_COLUMN,
    )
    free_kicks_against: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FREE_KICKS_AGAINST_COLUMN,
    )
    brownlow_votes: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_BROWNLOW_VOTES_COLUMN,
    )
    contested_possessions: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_CONTESTED_POSSESSIONS_COLUMN,
    )
    uncontested_possessions: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_UNCONTESTED_POSSESSIONS_COLUMN,
    )
    contested_marks: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_CONTESTED_MARKS_COLUMN,
    )
    marks_inside: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_MARKS_INSIDE_COLUMN,
    )
    one_percenters: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_ONE_PERCENTERS_COLUMN,
    )
    bounces: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_BOUNCES_COLUMN,
    )
    goal_assists: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_GOAL_ASSISTS_COLUMN,
    )
    percentage_played: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PERCENTAGE_PLAYED_COLUMN,
    )
    birth_date: datetime.date | None = Field(
        ..., json_schema_extra={FFILL_KEY: True}, alias=PLAYER_BIRTH_DATE_COLUMN
    )
    species: str = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.CATEGORICAL, FFILL_KEY: True},
        alias=PLAYER_SPECIES_COLUMN,
    )
    handicap_weight: float | None = Field(..., alias=PLAYER_HANDICAP_WEIGHT_COLUMN)
    father: PlayerModel | None = Field(
        ..., json_schema_extra={FFILL_KEY: True}, alias=PLAYER_FATHER_COLUMN
    )
    sex: str | None = Field(
        default_factory=_guess_sex,
        json_schema_extra={TYPE_KEY: FieldType.CATEGORICAL, FFILL_KEY: True},
        alias=PLAYER_SEX_COLUMN,
    )
    age: int | None = Field(..., alias=PLAYER_AGE_COLUMN)
    starting_position: str | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.CATEGORICAL},
        alias=PLAYER_STARTING_POSITION_COLUMN,
    )
    weight: float | None = Field(
        ..., json_schema_extra={FFILL_KEY: True}, alias=PLAYER_WEIGHT_COLUMN
    )
    birth_address: AddressModel | None = Field(
        ..., json_schema_extra={FFILL_KEY: True}, alias=PLAYER_BIRTH_ADDRESS_COLUMN
    )
    owner: OwnerModel | None = Field(
        ..., json_schema_extra={FFILL_KEY: True}, alias=PLAYER_OWNER_COLUMN
    )
    seconds_played: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_SECONDS_PLAYED_COLUMN,
    )
    field_goals_percentage: float | None = Field(
        default_factory=_calculate_field_goals_percentage,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOALS_PERCENTAGE_COLUMN,
    )
    three_point_field_goals: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_THREE_POINT_FIELD_GOALS_COLUMN,
    )
    three_point_field_goals_attempted: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_THREE_POINT_FIELD_GOALS_ATTEMPTED_COLUMN,
    )
    three_point_field_goals_percentage: float | None = Field(
        default_factory=_calculate_three_point_field_goals_percentage,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_THREE_POINT_FIELD_GOALS_PERCENTAGE_COLUMN,
    )
    free_throws: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FREE_THROWS_COLUMN,
    )
    free_throws_attempted: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FREE_THROWS_ATTEMPTED_COLUMN,
    )
    free_throws_percentage: float | None = Field(
        default_factory=_calculate_free_throws_percentage,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FREE_THROWS_PERCENTAGE_COLUMN,
    )
    defensive_rebounds: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_DEFENSIVE_REBOUNDS_COLUMN,
    )
    total_rebounds: int | None = Field(
        default_factory=_calculate_total_rebounds,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TOTAL_REBOUNDS_COLUMN,
    )
    steals: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_STEALS_COLUMN,
    )
    blocks: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_BLOCKS_COLUMN,
    )
    personal_fouls: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PERSONAL_FOULS_COLUMN,
    )
    points: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_POINTS_COLUMN,
    )
    game_score: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_GAME_SCORE_COLUMN,
    )
    point_differential: int | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_POINT_DIFFERENTIAL_COLUMN,
    )
    version: str
    height: float | None = Field(
        ..., json_schema_extra={FFILL_KEY: True}, alias=PLAYER_HEIGHT_COLUMN
    )
    colleges: list[VenueModel] = Field(
        ..., json_schema_extra={FFILL_KEY: True}, alias=PLAYER_COLLEGES_COLUMN
    )
    headshot: str | None = Field(
        ..., json_schema_extra={FFILL_KEY: True}, alias=PLAYER_HEADSHOT_COLUMN
    )
    forced_fumbles: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FORCED_FUMBLES_COLUMN,
    )
    fumbles_recovered: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FUMBLES_RECOVERED_COLUMN,
    )
    fumbles_recovered_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FUMBLES_RECOVERED_YARDS_COLUMN,
    )
    fumbles_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FUMBLES_TOUCHDOWNS_COLUMN,
    )
    offensive_two_point_returns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_OFFENSIVE_TWO_POINT_RETURNS_COLUMN,
    )
    offensive_fumbles_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_OFFENSIVE_FUMBLES_TOUCHDOWNS_COLUMN,
    )
    defensive_fumbles_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_DEFENSIVE_FUMBLES_TOUCHDOWNS_COLUMN,
    )
    average_gain: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_AVERAGE_GAIN_COLUMN,
    )
    completion_percentage: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_COMPLETION_PERCENTAGE_COLUMN,
    )
    completions: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_COMPLETIONS_COLUMN,
    )
    espn_quarterback_rating: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_ESPN_QUARTERBACK_RATING_COLUMN,
    )
    interception_percentage: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_INTERCEPTION_PERCENTAGE_COLUMN,
    )
    interceptions: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_INTERCEPTIONS_COLUMN,
    )
    long_passing: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_LONG_PASSING_COLUMN,
    )
    misc_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_MISC_YARDS_COLUMN,
    )
    net_passing_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_NET_PASSING_YARDS_COLUMN,
    )
    net_total_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_NET_TOTAL_YARDS_COLUMN,
    )
    passing_attempts: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_ATTEMPTS_COLUMN,
    )
    passing_big_plays: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_BIG_PLAYS_COLUMN,
    )
    passing_first_downs: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_FIRST_DOWNS_COLUMN,
    )
    passing_fumbles: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_FUMBLES_COLUMN,
    )
    passing_fumbles_lost: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_FUMBLES_LOST_COLUMN,
    )
    passing_touchdown_percentage: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_TOUCHDOWN_PERCENTAGE_COLUMN,
    )
    passing_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_TOUCHDOWNS_COLUMN,
    )
    passing_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_YARDS_COLUMN,
    )
    passing_yards_after_catch: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_YARDS_AFTER_CATCH_COLUMN,
    )
    passing_yards_at_catch: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_YARDS_AT_CATCH_COLUMN,
    )
    quarterback_rating: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_QUARTERBACK_RATING_COLUMN,
    )
    sacks: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_SACKS_COLUMN,
    )
    sacks_yards_lost: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_SACKS_YARDS_LOST_COLUMN,
    )
    net_passing_attempts: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_NET_PASSING_ATTEMPTS_COLUMN,
    )
    total_offensive_plays: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TOTAL_OFFENSIVE_PLAYS_COLUMN,
    )
    total_points: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TOTAL_POINTS_COLUMN,
    )
    total_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TOTAL_TOUCHDOWNS_COLUMN,
    )
    total_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TOTAL_YARDS_COLUMN,
    )
    total_yards_from_scrimmage: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TOTAL_YARDS_FROM_SCRIMMAGE_COLUMN,
    )
    two_point_pass: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TWO_POINT_PASS_COLUMN,
    )
    two_point_pass_attempt: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TWO_POINT_PASS_ATTEMPT_COLUMN,
    )
    yards_per_completion: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_YARDS_PER_COMPLETION_COLUMN,
    )
    yards_per_pass_attempt: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_YARDS_PER_PASS_ATTEMPT_COLUMN,
    )
    net_yards_per_pass_attempt: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_NET_YARDS_PER_PASS_ATTEMPT_COLUMN,
    )
    long_rushing: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_LONG_RUSHING_COLUMN,
    )
    rushing_attempts: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RUSHING_ATTEMPTS_COLUMN,
    )
    rushing_big_plays: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RUSHING_BIG_PLAYS_COLUMN,
    )
    rushing_first_downs: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RUSHING_FIRST_DOWNS_COLUMN,
    )
    rushing_fumbles: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RUSHING_FUMBLES_COLUMN,
    )
    rushing_fumbles_lost: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RUSHING_FUMBLES_LOST_COLUMN,
    )
    rushing_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RUSHING_TOUCHDOWNS_COLUMN,
    )
    rushing_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RUSHING_YARDS_COLUMN,
    )
    stuffs: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_STUFFS_COLUMN,
    )
    stuff_yards_lost: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_STUFF_YARDS_LOST,
    )
    two_point_rush: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TWO_POINT_RUSH_COLUMN,
    )
    two_point_rush_attempts: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TWO_POINT_RUSH_ATTEMPTS_COLUMN,
    )
    yards_per_rush_attempt: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_YARDS_PER_RUSH_ATTEMPT_COLUMN,
    )
    espn_widereceiver: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_ESPN_WIDERECEIVER_COLUMN,
    )
    long_reception: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_LONG_RECEPTION_COLUMN,
    )
    receiving_big_plays: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_BIG_PLAYS_COLUMN,
    )
    receiving_first_downs: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_FIRST_DOWNS_COLUMN,
    )
    receiving_fumbles: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_FUMBLES_COLUMN,
    )
    receiving_fumbles_lost: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_FUMBLES_LOST_COLUMN,
    )
    receiving_targets: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_TARGETS_COLUMN,
    )
    receiving_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_TOUCHDOWNS_COLUMN,
    )
    receiving_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_YARDS_COLUMN,
    )
    receiving_yards_after_catch: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_YARDS_AFTER_CATCH_COLUMN,
    )
    receiving_yards_at_catch: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_YARDS_AT_CATCH_COLUMN,
    )
    receptions: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEPTIONS_COLUMN,
    )
    two_point_receptions: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TWO_POINT_RECEPTIONS_COLUMN,
    )
    two_point_reception_attempts: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TWO_POINT_RECEPTION_ATTEMPTS_COLUMN,
    )
    yards_per_reception: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_YARDS_PER_RECEPTION_COLUMN,
    )
    assist_tackles: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_ASSIST_TACKLES_COLUMN,
    )
    average_interception_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_AVERAGE_INTERCEPTION_YARDS_COLUMN,
    )
    average_sack_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_AVERAGE_SACK_YARDS_COLUMN,
    )
    average_stuff_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_AVERAGE_STUFF_YARDS_COLUMN,
    )
    blocked_field_goal_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_BLOCKED_FIELD_GOAL_TOUCHDOWNS_COLUMN,
    )
    blocked_punt_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_BLOCKED_PUNT_TOUCHDOWNS_COLUMN,
    )
    defensive_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_DEFENSIVE_TOUCHDOWNS_COLUMN,
    )
    hurries: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_HURRIES_COLUMN,
    )
    kicks_blocked: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICKS_BLOCKED_COLUMN,
    )
    long_interception: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_LONG_INTERCEPTION_COLUMN,
    )
    misc_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_MISC_TOUCHDOWNS_COLUMN,
    )
    passes_batted_down: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSES_BATTED_DOWN_COLUMN,
    )
    passes_defended: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSES_DEFENDED_COLUMN,
    )
    quarterback_hits: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_QUARTERBACK_HITS_COLUMN,
    )
    sacks_assisted: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_SACKS_ASSISTED_COLUMN,
    )
    sacks_unassisted: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_SACKS_UNASSISTED_COLUMN,
    )
    sacks_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_SACKS_YARDS_COLUMN,
    )
    safeties: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_SAFETIES_COLUMN,
    )
    solo_tackles: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_SOLO_TACKLES_COLUMN,
    )
    stuff_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_STUFF_YARDS_COLUMN,
    )
    tackles_for_loss: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TACKLES_FOR_LOSS_COLUMN,
    )
    tackles_yards_lost: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TACKLES_YARDS_LOST_COLUMN,
    )
    yards_allowed: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_YARDS_ALLOWED_COLUMN,
    )
    points_allowed: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_POINTS_ALLOWED_COLUMN,
    )
    one_point_safeties_made: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_ONE_POINT_SAFETIES_MADE_COLUMN,
    )
    missed_field_goal_return_td: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_MISSED_FIELD_GOAL_RETURN_TD_COLUMN,
    )
    blocked_punt_ez_rec_td: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_BLOCKED_PUNT_EZ_REC_TD_COLUMN,
    )
    interception_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_INTERCEPTION_TOUCHDOWNS_COLUMN,
    )
    interception_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_INTERCEPTION_YARDS_COLUMN,
    )
    average_kickoff_return_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_AVERAGE_KICKOFF_RETURN_YARDS_COLUMN,
    )
    average_kickoff_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_AVERAGE_KICKOFF_YARDS_COLUMN,
    )
    extra_point_attempts: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_EXTRA_POINT_ATTEMPTS_COLUMN,
    )
    extra_point_percentage: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_EXTRA_POINT_PERCENTAGE_COLUMN,
    )
    extra_point_blocked: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_EXTRA_POINT_BLOCKED_COLUMN,
    )
    extra_points_blocked_percentage: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_EXTRA_POINTS_BLOCKED_PERCENTAGE_COLUMN,
    )
    extra_points_made: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_EXTRA_POINTS_MADE_COLUMN,
    )
    fair_catches: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FAIR_CATCHES_COLUMN,
    )
    fair_catch_percentage: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FAIR_CATCH_PERCENTAGE_COLUMN,
    )
    field_goal_attempts_max_19_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOAL_ATTEMPTS_MAX_19_YARDS_COLUMN,
    )
    field_goal_attempts_max_29_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOAL_ATTEMPTS_MAX_29_YARDS_COLUMN,
    )
    field_goal_attempts_max_39_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOAL_ATTEMPTS_MAX_39_YARDS_COLUMN,
    )
    field_goal_attempts_max_49_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOAL_ATTEMPTS_MAX_49_YARDS_COLUMN,
    )
    field_goal_attempts_max_59_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOAL_ATTEMPTS_MAX_59_YARDS_COLUMN,
    )
    field_goal_attempts_max_99_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOAL_ATTEMPTS_MAX_99_YARDS_COLUMN,
    )
    field_goal_attempts_above_50_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOAL_ATTEMPTS_ABOVE_50_YARDS_COLUMN,
    )
    field_goal_attempt_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOAL_ATTEMPT_YARDS_COLUMN,
    )
    field_goals_blocked: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOALS_BLOCKED_COLUMN,
    )
    field_goals_blocked_percentage: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOALS_BLOCKED_PERCENTAGE_COLUMN,
    )
    field_goals_made: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOALS_MADE_COLUMN,
    )
    field_goals_made_max_19_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOALS_MADE_MAX_19_YARDS_COLUMN,
    )
    field_goals_made_max_29_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOALS_MADE_MAX_29_YARDS_COLUMN,
    )
    field_goals_made_max_39_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOALS_MADE_MAX_39_YARDS_COLUMN,
    )
    field_goals_made_max_49_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOALS_MADE_MAX_49_YARDS_COLUMN,
    )
    field_goals_made_max_59_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOALS_MADE_MAX_59_YARDS_COLUMN,
    )
    field_goals_made_max_99_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOALS_MADE_MAX_99_YARDS_COLUMN,
    )
    field_goals_made_above_50_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOALS_MADE_ABOVE_50_YARDS_COLUMN,
    )
    field_goals_made_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOALS_MADE_YARDS_COLUMN,
    )
    field_goals_missed_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FIELD_GOALS_MISSED_YARDS_COLUMN,
    )
    kickoff_out_of_bounds: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICKOFF_OUT_OF_BOUNDS_COLUMN,
    )
    kickoff_returns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICKOFF_RETURNS_COLUMN,
    )
    kickoff_returns_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICKOFF_RETURNS_TOUCHDOWNS_COLUMN,
    )
    kickoff_return_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICKOFF_RETURN_YARDS_COLUMN,
    )
    kickoffs: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICKOFFS_COLUMN,
    )
    kickoff_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICKOFF_YARDS_COLUMN,
    )
    long_field_goal_attempt: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_LONG_FIELD_GOAL_ATTEMPT_COLUMN,
    )
    long_field_goal_made: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_LONG_FIELD_GOAL_MADE_COLUMN,
    )
    long_kickoff: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_LONG_KICKOFF_COLUMN,
    )
    total_kicking_points: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TOTAL_KICKING_POINTS_COLUMN,
    )
    touchback_percentage: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TOUCHBACK_PERCENTAGE_COLUMN,
    )
    touchbacks: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TOUCHBACKS_COLUMN,
    )
    defensive_fumble_returns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_DEFENSIVE_FUMBLE_RETURNS_COLUMN,
    )
    defensive_fumble_return_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_DEFENSIVE_FUMBLE_RETURN_YARDS_COLUMN,
    )
    fumble_recoveries: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FUMBLE_RECOVERIES_COLUMN,
    )
    fumble_recovery_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_FUMBLE_RECOVERY_YARDS_COLUMN,
    )
    kick_return_fair_catches: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICK_RETURN_FAIR_CATCHES_COLUMN,
    )
    kick_return_fair_catch_percentage: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICK_RETURN_FAIR_CATCH_PERCENTAGE_COLUMN,
    )
    kick_return_fumbles: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICK_RETURN_FUMBLES_COLUMN,
    )
    kick_return_fumbles_lost: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICK_RETURN_FUMBLES_LOST_COLUMN,
    )
    kick_returns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICK_RETURNS_COLUMN,
    )
    kick_return_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICK_RETURN_TOUCHDOWNS_COLUMN,
    )
    kick_return_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_KICK_RETURN_YARDS_COLUMN,
    )
    long_kick_return: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_LONG_KICK_RETURN_COLUMN,
    )
    long_punt_return: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_LONG_PUNT_RETURN_COLUMN,
    )
    misc_fumble_returns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_MISC_FUMBLE_RETURNS_COLUMN,
    )
    misc_fumble_return_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_MISC_FUMBLE_RETURN_YARDS_COLUMN,
    )
    opposition_fumble_recoveries: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_OPPOSITION_FUMBLE_RECOVERIES_COLUMN,
    )
    opposition_fumble_recovery_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_OPPOSITION_FUMBLE_RECOVERY_YARDS_COLUMN,
    )
    opposition_special_team_fumble_returns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_OPPOSITION_SPECIAL_TEAM_FUMBLE_RETURNS_COLUMN,
    )
    opposition_special_team_fumble_return_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_OPPOSITION_SPECIAL_TEAM_FUMBLE_RETURN_YARDS_COLUMN,
    )
    punt_return_fair_catches: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNT_RETURN_FAIR_CATCHES_COLUMN,
    )
    punt_return_fair_catch_percentage: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNT_RETURN_FAIR_CATCH_PERCENTAGE_COLUMN,
    )
    punt_return_fumbles: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNT_RETURN_FUMBLES_COLUMN,
    )
    punt_return_fumbles_lost: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNT_RETURN_FUMBLES_LOST_COLUMN,
    )
    punt_returns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNT_RETURNS_COLUMN,
    )
    punt_returns_started_inside_the_10: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNT_RETURNS_STARTED_INSIDE_THE_10_COLUMN,
    )
    punt_returns_started_inside_the_20: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNT_RETURNS_STARTED_INSIDE_THE_20_COLUMN,
    )
    punt_return_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNT_RETURN_TOUCHDOWNS_COLUMN,
    )
    punt_return_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNT_RETURN_YARDS_COLUMN,
    )
    special_team_fumble_returns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_SPECIAL_TEAM_FUMBLE_RETURNS_COLUMN,
    )
    yards_per_kick_return: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_YARDS_PER_KICK_RETURN_COLUMN,
    )
    yards_per_punt_return: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_YARDS_PER_PUNT_RETURN_COLUMN,
    )
    yards_per_return: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_YARDS_PER_RETURN_COLUMN,
    )
    average_punt_return_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_AVERAGE_PUNT_RETURN_YARDS_COLUMN,
    )
    gross_average_punt_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_GROSS_AVERAGE_PUNT_YARDS_COLUMN,
    )
    long_punt: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_LONG_PUNT_COLUMN,
    )
    net_average_punt_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_NET_AVERAGE_PUNT_YARDS_COLUMN,
    )
    punts: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNTS_COLUMN,
    )
    punts_blocked: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNTS_BLOCKED_COLUMN,
    )
    punts_blocked_percentage: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNTS_BLOCKED_PERCENTAGE_COLUMN,
    )
    punts_inside_10: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNTS_INSIDE_10_COLUMN,
    )
    punts_inside_10_percentage: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNTS_INSIDE_10_PERCENTAGE_COLUMN,
    )
    punts_inside_20: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNTS_INSIDE_20_COLUMN,
    )
    punts_inside_20_percentage: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNTS_INSIDE_20_PERCENTAGE_COLUMN,
    )
    punts_over_50: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNTS_OVER_50_COLUMN,
    )
    punt_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PUNT_YARDS_COLUMN,
    )
    defensive_points: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_DEFENSIVE_POINTS_COLUMN,
    )
    misc_points: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_MISC_POINTS_COLUMN,
    )
    return_touchdowns: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RETURN_TOUCHDOWNS_COLUMN,
    )
    total_two_point_conversions: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_TOTAL_TWO_POINT_CONVERSIONS_COLUMN,
    )
    passing_touchdowns_9_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_TOUCHDOWNS_9_YARDS_COLUMN,
    )
    passing_touchdowns_19_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_TOUCHDOWNS_19_YARDS_COLUMN,
    )
    passing_touchdowns_29_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_TOUCHDOWNS_29_YARDS_COLUMN,
    )
    passing_touchdowns_39_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_TOUCHDOWNS_39_YARDS_COLUMN,
    )
    passing_touchdowns_49_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_TOUCHDOWNS_49_YARDS_COLUMN,
    )
    passing_touchdowns_above_50_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_PASSING_TOUCHDOWNS_ABOVE_50_YARDS_COLUMN,
    )
    receiving_touchdowns_9_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_TOUCHDOWNS_9_YARDS_COLUMN,
    )
    receiving_touchdowns_19_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_TOUCHDOWNS_19_YARDS_COLUMN,
    )
    receiving_touchdowns_29_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_TOUCHDOWNS_29_YARDS_COLUMN,
    )
    receiving_touchdowns_39_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_TOUCHDOWNS_39_YARDS_COLUMN,
    )
    receiving_touchdowns_49_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_TOUCHDOWNS_49_YARDS_COLUMN,
    )
    receiving_touchdowns_above_50_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RECEIVING_TOUCHDOWNS_ABOVE_50_YARDS_COLUMN,
    )
    rushing_touchdowns_9_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RUSHING_TOUCHDOWNS_9_YARDS_COLUMN,
    )
    rushing_touchdowns_19_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RUSHING_TOUCHDOWNS_19_YARDS_COLUMN,
    )
    rushing_touchdowns_29_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RUSHING_TOUCHDOWNS_29_YARDS_COLUMN,
    )
    rushing_touchdowns_39_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RUSHING_TOUCHDOWNS_39_YARDS_COLUMN,
    )
    rushing_touchdowns_49_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RUSHING_TOUCHDOWNS_49_YARDS_COLUMN,
    )
    rushing_touchdowns_above_50_yards: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=PLAYER_RUSHING_TOUCHDOWNS_ABOVE_50_YARDS_COLUMN,
    )
