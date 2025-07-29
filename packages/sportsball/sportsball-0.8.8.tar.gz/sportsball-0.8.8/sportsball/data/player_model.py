"""The prototype class for a player."""

# pylint: disable=duplicate-code
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
VERSION = DELIMITER.join(["0.0.1", ADDRESS_VERSION, OWNER_VERSION])


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
