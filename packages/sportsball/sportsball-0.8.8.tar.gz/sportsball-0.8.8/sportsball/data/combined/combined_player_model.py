"""Combined player model."""

# pylint: disable=too-many-locals,too-many-branches,too-many-statements,duplicate-code
from typing import Any

from ..player_model import VERSION, PlayerModel
from .ffill import ffill
from .null_check import is_null


def create_combined_player_model(
    player_models: list[PlayerModel],
    identifier: str,
    player_ffill: dict[str, dict[str, Any]],
) -> PlayerModel:
    """Create a player model by combining many player models."""
    jersey = None
    kicks = None
    fumbles = None
    fumbles_lost = None
    field_goals = None
    field_goals_attempted = None
    offensive_rebounds = None
    assists = None
    turnovers = None
    name = None
    marks = None
    handballs = None
    disposals = None
    goals = None
    behinds = None
    hit_outs = None
    tackles = None
    rebounds = None
    insides = None
    clearances = None
    clangers = None
    free_kicks_for = None
    free_kicks_against = None
    brownlow_votes = None
    contested_possessions = None
    uncontested_possessions = None
    contested_marks = None
    marks_inside = None
    one_percenters = None
    bounces = None
    goal_assists = None
    percentage_played = None
    birth_date = None
    species = None
    handicap_weight = None
    father = None
    sex = None
    age = None
    starting_position = None
    weight = None
    birth_address = None
    owner = None
    seconds_played = None
    three_point_field_goals = None
    three_point_field_goals_attempted = None
    free_throws = None
    free_throws_attempted = None
    defensive_rebounds = None
    steals = None
    blocks = None
    personal_fouls = None
    points = None
    game_score = None
    point_differential = None
    for player_model in player_models:
        player_model_jersey = player_model.jersey
        if not is_null(player_model_jersey):
            jersey = player_model_jersey
        player_model_kicks = player_model.kicks
        if not is_null(player_model_kicks):
            kicks = player_model_kicks
        player_model_fumbles = player_model.fumbles
        if not is_null(player_model_fumbles):
            fumbles = player_model_fumbles
        player_model_fumbles_lost = player_model.fumbles_lost
        if not is_null(player_model_fumbles_lost):
            fumbles_lost = player_model_fumbles_lost
        player_model_field_goals = player_model.field_goals
        if not is_null(player_model_field_goals):
            field_goals = player_model_field_goals
        player_model_field_goals_attempted = player_model.field_goals_attempted
        if not is_null(player_model_field_goals_attempted):
            field_goals_attempted = player_model_field_goals_attempted
        player_model_offensive_rebounds = player_model.offensive_rebounds
        if not is_null(player_model_offensive_rebounds):
            offensive_rebounds = player_model_offensive_rebounds
        player_model_assists = player_model.assists
        if not is_null(player_model_assists):
            assists = player_model_assists
        player_model_turnovers = player_model.turnovers
        if not is_null(player_model_turnovers):
            turnovers = player_model_turnovers
        player_model_name = player_model.name
        if not is_null(player_model_name):
            name = player_model_name
        player_model_marks = player_model.marks
        if not is_null(player_model_marks):
            marks = player_model_marks
        player_model_handballs = player_model.handballs
        if not is_null(player_model_handballs):
            handballs = player_model_handballs
        player_model_disposals = player_model.disposals
        if not is_null(player_model_disposals):
            disposals = player_model_disposals
        player_model_goals = player_model.goals
        if not is_null(player_model_goals):
            goals = player_model_goals
        player_model_behinds = player_model.behinds
        if not is_null(player_model_behinds):
            behinds = player_model_behinds
        player_model_hit_outs = player_model.hit_outs
        if not is_null(player_model_hit_outs):
            hit_outs = player_model_hit_outs
        player_model_tackles = player_model.tackles
        if not is_null(player_model_tackles):
            tackles = player_model_tackles
        player_model_rebounds = player_model.rebounds
        if not is_null(player_model_rebounds):
            rebounds = player_model_rebounds
        player_model_insides = player_model.insides
        if not is_null(player_model_insides):
            insides = player_model_insides
        player_model_clearances = player_model.clearances
        if not is_null(player_model_clearances):
            clearances = player_model_clearances
        player_model_clangers = player_model.clangers
        if not is_null(player_model_clangers):
            clangers = player_model_clangers
        player_model_free_kicks_for = player_model.free_kicks_for
        if not is_null(player_model_free_kicks_for):
            free_kicks_for = player_model_free_kicks_for
        player_model_free_kicks_against = player_model.free_kicks_against
        if not is_null(player_model_free_kicks_against):
            free_kicks_against = player_model_free_kicks_against
        player_model_brownlow_votes = player_model.brownlow_votes
        if not is_null(player_model_brownlow_votes):
            brownlow_votes = player_model_brownlow_votes
        player_model_contested_possessions = player_model.contested_possessions
        if not is_null(player_model_contested_possessions):
            contested_possessions = player_model_contested_possessions
        player_model_uncontested_possessions = player_model.uncontested_possessions
        if not is_null(player_model_uncontested_possessions):
            uncontested_possessions = player_model_uncontested_possessions
        player_model_contested_marks = player_model.contested_marks
        if not is_null(player_model_contested_marks):
            contested_marks = player_model_contested_marks
        player_model_marks_inside = player_model.marks_inside
        if not is_null(player_model_marks_inside):
            marks_inside = player_model_marks_inside
        player_model_one_percenters = player_model.one_percenters
        if not is_null(player_model_one_percenters):
            one_percenters = player_model_one_percenters
        player_model_bounces = player_model.bounces
        if not is_null(player_model_bounces):
            bounces = player_model_bounces
        player_model_goal_assists = player_model.goal_assists
        if not is_null(player_model_goal_assists):
            goal_assists = player_model_goal_assists
        player_model_percentage_played = player_model.percentage_played
        if not is_null(player_model_percentage_played):
            percentage_played = player_model_percentage_played
        player_model_birth_date = player_model.birth_date
        if not is_null(player_model_birth_date):
            birth_date = player_model_birth_date
        player_model_species = player_model.species
        if not is_null(player_model_species):
            species = player_model_species
        player_model_handicap_weight = player_model.handicap_weight
        if not is_null(player_model_handicap_weight):
            handicap_weight = player_model_handicap_weight
        player_model_father = player_model.father
        if not is_null(player_model_father):
            father = player_model_father
        player_model_sex = player_model.sex
        if not is_null(player_model_sex):
            sex = player_model_sex
        player_model_age = player_model.age
        if not is_null(player_model_age):
            age = player_model_age
        player_model_starting_position = player_model.starting_position
        if not is_null(player_model_starting_position):
            starting_position = player_model_starting_position
        player_model_weight = player_model.weight
        if not is_null(player_model_weight):
            weight = player_model_weight
        player_model_birth_address = player_model.birth_address
        if not is_null(player_model_birth_address):
            birth_address = player_model_birth_address
        player_model_owner = player_model.owner
        if not is_null(player_model_owner):
            owner = player_model_owner
        player_model_seconds_played = player_model.seconds_played
        if not is_null(player_model_seconds_played):
            seconds_played = player_model_seconds_played
        player_model_three_point_field_goals = player_model.three_point_field_goals
        if not is_null(player_model_three_point_field_goals):
            three_point_field_goals = player_model_three_point_field_goals
        player_model_three_point_field_goals_attempted = (
            player_model.three_point_field_goals_attempted
        )
        if not is_null(player_model_three_point_field_goals_attempted):
            three_point_field_goals_attempted = (
                player_model_three_point_field_goals_attempted
            )
        player_model_free_throws = player_model.free_throws
        if not is_null(player_model_free_throws):
            free_throws = player_model_free_throws
        player_model_free_throws_attempted = player_model.free_throws_attempted
        if not is_null(player_model_free_throws_attempted):
            free_throws_attempted = player_model_free_throws_attempted
        player_model_defensive_rebounds = player_model.defensive_rebounds
        if not is_null(player_model_defensive_rebounds):
            defensive_rebounds = player_model_defensive_rebounds
        player_model_steals = player_model.steals
        if not is_null(player_model_steals):
            steals = player_model_steals
        player_model_blocks = player_model.blocks
        if not is_null(player_model_blocks):
            blocks = player_model_blocks
        player_model_personal_fouls = player_model.personal_fouls
        if not is_null(player_model_personal_fouls):
            personal_fouls = player_model_personal_fouls
        player_model_points = player_model.points
        if not is_null(player_model_points):
            points = player_model_points
        player_model_game_score = player_model.game_score
        if not is_null(player_model_game_score):
            game_score = player_model_game_score
        player_model_point_differential = player_model.point_differential
        if not is_null(player_model_point_differential):
            point_differential = player_model_point_differential
    if name is None:
        raise ValueError("name is null")
    if species is None:
        raise ValueError("species is null")

    player_model = PlayerModel(
        identifier=identifier,
        jersey=jersey,
        kicks=kicks,
        fumbles=fumbles,
        fumbles_lost=fumbles_lost,
        field_goals=field_goals,
        field_goals_attempted=field_goals_attempted,
        offensive_rebounds=offensive_rebounds,
        assists=assists,
        turnovers=turnovers,
        name=name,
        marks=marks,
        handballs=handballs,
        disposals=disposals,
        goals=goals,
        behinds=behinds,
        hit_outs=hit_outs,
        tackles=tackles,
        rebounds=rebounds,
        insides=insides,
        clearances=clearances,
        clangers=clangers,
        free_kicks_for=free_kicks_for,
        free_kicks_against=free_kicks_against,
        brownlow_votes=brownlow_votes,
        contested_possessions=contested_possessions,
        uncontested_possessions=uncontested_possessions,
        contested_marks=contested_marks,
        marks_inside=marks_inside,
        one_percenters=one_percenters,
        bounces=bounces,
        goal_assists=goal_assists,
        percentage_played=percentage_played,
        birth_date=birth_date,
        species=species,
        handicap_weight=handicap_weight,
        father=father,
        sex=sex,
        age=age,
        starting_position=starting_position,
        weight=weight,
        birth_address=birth_address,
        owner=owner,
        seconds_played=seconds_played,
        three_point_field_goals=three_point_field_goals,
        three_point_field_goals_attempted=three_point_field_goals_attempted,
        free_throws=free_throws,
        free_throws_attempted=free_throws_attempted,
        defensive_rebounds=defensive_rebounds,
        steals=steals,
        blocks=blocks,
        personal_fouls=personal_fouls,
        points=points,
        game_score=game_score,
        point_differential=point_differential,
        version=VERSION,
    )

    ffill(player_ffill, identifier, player_model)

    return player_model
