"""Combined player model."""

# pylint: disable=too-many-locals,too-many-branches,too-many-statements,duplicate-code,too-many-lines
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
    height = None
    colleges = None
    headshot = None
    forced_fumbles = None
    fumbles_recovered = None
    fumbles_recovered_yards = None
    fumbles_touchdowns = None
    offensive_two_point_returns = None
    offensive_fumbles_touchdowns = None
    defensive_fumbles_touchdowns = None
    average_gain = None
    completion_percentage = None
    completions = None
    espn_quarterback_rating = None
    interception_percentage = None
    interceptions = None
    long_passing = None
    misc_yards = None
    net_passing_yards = None
    net_total_yards = None
    passing_attempts = None
    passing_big_plays = None
    passing_first_downs = None
    passing_fumbles = None
    passing_fumbles_lost = None
    passing_touchdown_percentage = None
    passing_touchdowns = None
    passing_yards = None
    passing_yards_after_catch = None
    passing_yards_at_catch = None
    quarterback_rating = None
    sacks = None
    sacks_yards_lost = None
    net_passing_attempts = None
    total_offensive_plays = None
    total_points = None
    total_touchdowns = None
    total_yards = None
    total_yards_from_scrimmage = None
    two_point_pass = None
    two_point_pass_attempt = None
    yards_per_completion = None
    yards_per_pass_attempt = None
    net_yards_per_pass_attempt = None
    long_rushing = None
    rushing_attempts = None
    rushing_big_plays = None
    rushing_first_downs = None
    rushing_fumbles = None
    rushing_fumbles_lost = None
    rushing_touchdowns = None
    rushing_yards = None
    stuffs = None
    stuff_yards_lost = None
    two_point_rush = None
    two_point_rush_attempts = None
    yards_per_rush_attempt = None
    espn_widereceiver = None
    long_reception = None
    receiving_big_plays = None
    receiving_first_downs = None
    receiving_fumbles = None
    receiving_fumbles_lost = None
    receiving_targets = None
    receiving_touchdowns = None
    receiving_yards = None
    receiving_yards_after_catch = None
    receiving_yards_at_catch = None
    receptions = None
    two_point_receptions = None
    two_point_reception_attempts = None
    yards_per_reception = None
    assist_tackles = None
    average_interception_yards = None
    average_sack_yards = None
    average_stuff_yards = None
    blocked_field_goal_touchdowns = None
    blocked_punt_touchdowns = None
    defensive_touchdowns = None
    hurries = None
    kicks_blocked = None
    long_interception = None
    misc_touchdowns = None
    passes_batted_down = None
    passes_defended = None
    quarterback_hits = None
    sacks_assisted = None
    sacks_unassisted = None
    sacks_yards = None
    safeties = None
    solo_tackles = None
    stuff_yards = None
    tackles_for_loss = None
    tackles_yards_lost = None
    yards_allowed = None
    points_allowed = None
    one_point_safeties_made = None
    missed_field_goal_return_td = None
    blocked_punt_ez_rec_td = None
    interception_touchdowns = None
    interception_yards = None
    average_kickoff_return_yards = None
    average_kickoff_yards = None
    extra_point_attempts = None
    extra_point_percentage = None
    extra_point_blocked = None
    extra_points_blocked_percentage = None
    extra_points_made = None
    fair_catches = None
    fair_catch_percentage = None
    field_goal_attempts_max_19_yards = None
    field_goal_attempts_max_29_yards = None
    field_goal_attempts_max_39_yards = None
    field_goal_attempts_max_49_yards = None
    field_goal_attempts_max_59_yards = None
    field_goal_attempts_max_99_yards = None
    field_goal_attempts_above_50_yards = None
    field_goal_attempt_yards = None
    field_goals_blocked = None
    field_goals_blocked_percentage = None
    field_goals_made = None
    field_goals_made_max_19_yards = None
    field_goals_made_max_29_yards = None
    field_goals_made_max_39_yards = None
    field_goals_made_max_49_yards = None
    field_goals_made_max_59_yards = None
    field_goals_made_max_99_yards = None
    field_goals_made_above_50_yards = None
    field_goals_made_yards = None
    field_goals_missed_yards = None
    kickoff_out_of_bounds = None
    kickoff_returns = None
    kickoff_returns_touchdowns = None
    kickoff_return_yards = None
    kickoffs = None
    kickoff_yards = None
    long_field_goal_attempt = None
    long_field_goal_made = None
    long_kickoff = None
    total_kicking_points = None
    touchback_percentage = None
    touchbacks = None
    defensive_fumble_returns = None
    defensive_fumble_return_yards = None
    fumble_recoveries = None
    fumble_recovery_yards = None
    kick_return_fair_catches = None
    kick_return_fair_catch_percentage = None
    kick_return_fumbles = None
    kick_return_fumbles_lost = None
    kick_returns = None
    kick_return_touchdowns = None
    kick_return_yards = None
    long_kick_return = None
    long_punt_return = None
    misc_fumble_returns = None
    misc_fumble_return_yards = None
    opposition_fumble_recoveries = None
    opposition_fumble_recovery_yards = None
    opposition_special_team_fumble_returns = None
    opposition_special_team_fumble_return_yards = None
    punt_return_fair_catches = None
    punt_return_fair_catch_percentage = None
    punt_return_fumbles = None
    punt_return_fumbles_lost = None
    punt_returns = None
    punt_returns_started_inside_the_10 = None
    punt_returns_started_inside_the_20 = None
    punt_return_touchdowns = None
    punt_return_yards = None
    special_team_fumble_returns = None
    yards_per_kick_return = None
    yards_per_punt_return = None
    yards_per_return = None
    average_punt_return_yards = None
    gross_average_punt_yards = None
    long_punt = None
    net_average_punt_yards = None
    punts = None
    punts_blocked = None
    punts_blocked_percentage = None
    punts_inside_10 = None
    punts_inside_10_percentage = None
    punts_inside_20 = None
    punts_inside_20_percentage = None
    punts_over_50 = None
    punt_yards = None
    defensive_points = None
    misc_points = None
    return_touchdowns = None
    total_two_point_conversions = None
    passing_touchdowns_9_yards = None
    passing_touchdowns_19_yards = None
    passing_touchdowns_29_yards = None
    passing_touchdowns_39_yards = None
    passing_touchdowns_49_yards = None
    passing_touchdowns_above_50_yards = None
    receiving_touchdowns_9_yards = None
    receiving_touchdowns_19_yards = None
    receiving_touchdowns_29_yards = None
    receiving_touchdowns_39_yards = None
    receiving_touchdowns_49_yards = None
    receiving_touchdowns_above_50_yards = None
    rushing_touchdowns_9_yards = None
    rushing_touchdowns_19_yards = None
    rushing_touchdowns_29_yards = None
    rushing_touchdowns_39_yards = None
    rushing_touchdowns_49_yards = None
    rushing_touchdowns_above_50_yards = None
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
        player_model_height = player_model.height
        if not is_null(player_model_height):
            height = player_model_height
        player_model_colleges = player_model.colleges
        if not is_null(player_model_colleges):
            colleges = player_model_colleges
        player_model_headshot = player_model.headshot
        if not is_null(player_model_headshot):
            headshot = player_model_headshot
        player_model_forced_fumbles = player_model.forced_fumbles
        if not is_null(player_model_forced_fumbles):
            forced_fumbles = player_model_forced_fumbles
        player_model_fumbles_recovered = player_model.fumbles_recovered
        if not is_null(player_model_fumbles_recovered):
            fumbles_recovered = player_model_fumbles_recovered
        player_model_fumbles_recovered_yards = player_model.fumbles_recovered_yards
        if not is_null(player_model_fumbles_recovered_yards):
            fumbles_recovered_yards = player_model_fumbles_recovered_yards
        player_model_fumbles_touchdowns = player_model.fumbles_touchdowns
        if not is_null(player_model_fumbles_touchdowns):
            fumbles_touchdowns = player_model_fumbles_touchdowns
        player_model_offensive_two_point_returns = (
            player_model.offensive_two_point_returns
        )
        if not is_null(player_model_offensive_two_point_returns):
            offensive_two_point_returns = player_model_offensive_two_point_returns
        player_model_offensive_fumbles_touchdowns = (
            player_model.offensive_fumbles_touchdowns
        )
        if not is_null(player_model_offensive_fumbles_touchdowns):
            offensive_fumbles_touchdowns = player_model_offensive_fumbles_touchdowns
        player_model_defensive_fumbles_touchdowns = (
            player_model.defensive_fumbles_touchdowns
        )
        if not is_null(player_model_defensive_fumbles_touchdowns):
            defensive_fumbles_touchdowns = player_model_defensive_fumbles_touchdowns
        player_model_average_gain = player_model.average_gain
        if not is_null(player_model_average_gain):
            average_gain = player_model_average_gain
        player_model_completion_percentage = player_model.completion_percentage
        if not is_null(player_model_completion_percentage):
            completion_percentage = player_model_completion_percentage
        player_model_completions = player_model.completions
        if not is_null(player_model_completions):
            completions = player_model_completions
        player_model_espn_quarterback_rating = player_model.espn_quarterback_rating
        if not is_null(player_model_espn_quarterback_rating):
            espn_quarterback_rating = player_model_espn_quarterback_rating
        player_model_interception_percentage = player_model.interception_percentage
        if not is_null(player_model_interception_percentage):
            interception_percentage = player_model_interception_percentage
        player_model_interceptions = player_model.interceptions
        if not is_null(player_model_interceptions):
            interceptions = player_model_interceptions
        player_model_long_passing = player_model.long_passing
        if not is_null(player_model_long_passing):
            long_passing = player_model_long_passing
        player_model_misc_yards = player_model.misc_yards
        if not is_null(player_model_misc_yards):
            misc_yards = player_model_misc_yards
        player_model_net_passing_yards = player_model.net_passing_yards
        if not is_null(player_model_net_passing_yards):
            net_passing_yards = player_model_net_passing_yards
        player_model_net_total_yards = player_model.net_total_yards
        if not is_null(player_model_net_total_yards):
            net_total_yards = player_model_net_total_yards
        player_model_passing_attempts = player_model.passing_attempts
        if not is_null(player_model_passing_attempts):
            passing_attempts = player_model_passing_attempts
        player_model_passing_big_plays = player_model.passing_big_plays
        if not is_null(player_model_passing_big_plays):
            passing_big_plays = player_model_passing_big_plays
        player_model_passing_first_downs = player_model.passing_first_downs
        if not is_null(player_model_passing_first_downs):
            passing_first_downs = player_model_passing_first_downs
        player_model_passing_fumbles = player_model.passing_fumbles
        if not is_null(player_model_passing_fumbles):
            passing_fumbles = player_model_passing_fumbles
        player_model_passing_fumbles_lost = player_model.passing_fumbles_lost
        if not is_null(player_model_passing_fumbles_lost):
            passing_fumbles_lost = player_model_passing_fumbles_lost
        player_model_passing_touchdown_percentage = (
            player_model.passing_touchdown_percentage
        )
        if not is_null(player_model_passing_touchdown_percentage):
            passing_touchdown_percentage = player_model_passing_touchdown_percentage
        player_model_passing_touchdowns = player_model.passing_touchdowns
        if not is_null(player_model_passing_touchdowns):
            passing_touchdowns = player_model_passing_touchdowns
        player_model_passing_yards = player_model.passing_yards
        if not is_null(player_model_passing_yards):
            passing_yards = player_model_passing_yards
        player_model_passing_yards_after_catch = player_model.passing_yards_after_catch
        if not is_null(player_model_passing_yards_after_catch):
            passing_yards_after_catch = player_model_passing_yards_after_catch
        player_model_passing_yards_at_catch = player_model.passing_yards_at_catch
        if not is_null(player_model_passing_yards_at_catch):
            passing_yards_at_catch = player_model_passing_yards_at_catch
        player_model_quarterback_rating = player_model.quarterback_rating
        if not is_null(player_model_quarterback_rating):
            quarterback_rating = player_model_quarterback_rating
        player_model_sacks = player_model.sacks
        if not is_null(player_model_sacks):
            sacks = player_model_sacks
        player_model_sacks_yards_lost = player_model.sacks_yards_lost
        if not is_null(player_model_sacks_yards_lost):
            sacks_yards_lost = player_model_sacks_yards_lost
        player_model_net_passing_attempts = player_model.net_passing_attempts
        if not is_null(player_model_net_passing_attempts):
            net_passing_attempts = player_model_net_passing_attempts
        player_model_total_offensive_plays = player_model.total_offensive_plays
        if not is_null(player_model_total_offensive_plays):
            total_offensive_plays = player_model_total_offensive_plays
        player_model_total_points = player_model.total_points
        if not is_null(player_model_total_points):
            total_points = player_model_total_points
        player_model_total_touchdowns = player_model.total_touchdowns
        if not is_null(player_model_total_touchdowns):
            total_touchdowns = player_model_total_touchdowns
        player_model_total_yards = player_model.total_yards
        if not is_null(player_model_total_yards):
            total_yards = player_model_total_yards
        player_model_total_yards_from_scrimmage = (
            player_model.total_yards_from_scrimmage
        )
        if not is_null(player_model_total_yards_from_scrimmage):
            total_yards_from_scrimmage = player_model_total_yards_from_scrimmage
        player_model_two_point_pass = player_model.two_point_pass
        if not is_null(player_model_two_point_pass):
            two_point_pass = player_model_two_point_pass
        player_model_two_point_pass_attempt = player_model.two_point_pass_attempt
        if not is_null(player_model_two_point_pass_attempt):
            two_point_pass_attempt = player_model_two_point_pass_attempt
        player_model_yards_per_completion = player_model.yards_per_completion
        if not is_null(player_model_yards_per_completion):
            yards_per_completion = player_model_yards_per_completion
        player_model_yards_per_pass_attempt = player_model.yards_per_pass_attempt
        if not is_null(player_model_yards_per_pass_attempt):
            yards_per_pass_attempt = player_model_yards_per_pass_attempt
        player_model_net_yards_per_pass_attempt = (
            player_model.net_yards_per_pass_attempt
        )
        if not is_null(player_model_net_yards_per_pass_attempt):
            net_yards_per_pass_attempt = player_model_net_yards_per_pass_attempt
        player_model_long_rushing = player_model.long_rushing
        if not is_null(player_model_long_rushing):
            long_rushing = player_model_long_rushing
        player_model_rushing_attempts = player_model.rushing_attempts
        if not is_null(player_model_rushing_attempts):
            rushing_attempts = player_model_rushing_attempts
        player_model_rushing_big_plays = player_model.rushing_big_plays
        if not is_null(player_model_rushing_big_plays):
            rushing_big_plays = player_model_rushing_big_plays
        player_model_rushing_first_downs = player_model.rushing_first_downs
        if not is_null(player_model_rushing_first_downs):
            rushing_first_downs = player_model_rushing_first_downs
        player_model_rushing_fumbles = player_model.rushing_fumbles
        if not is_null(player_model_rushing_fumbles):
            rushing_fumbles = player_model_rushing_fumbles
        player_model_rushing_fumbles_lost = player_model.rushing_fumbles_lost
        if not is_null(player_model_rushing_fumbles_lost):
            rushing_fumbles_lost = player_model_rushing_fumbles_lost
        player_model_rushing_touchdowns = player_model.rushing_touchdowns
        if not is_null(player_model_rushing_touchdowns):
            rushing_touchdowns = player_model_rushing_touchdowns
        player_model_rushing_yards = player_model.rushing_yards
        if not is_null(player_model_rushing_yards):
            rushing_yards = player_model_rushing_yards
        player_model_stuffs = player_model.stuffs
        if not is_null(player_model_stuffs):
            stuffs = player_model_stuffs
        player_model_stuff_yards_lost = player_model.stuff_yards_lost
        if not is_null(player_model_stuff_yards_lost):
            stuff_yards_lost = player_model_stuff_yards_lost
        player_model_two_point_rush = player_model.two_point_rush
        if not is_null(player_model_two_point_rush):
            two_point_rush = player_model_two_point_rush
        player_model_two_point_rush_attempts = player_model.two_point_rush_attempts
        if not is_null(player_model_two_point_rush_attempts):
            two_point_rush_attempts = player_model_two_point_rush_attempts
        player_model_yards_per_rush_attempt = player_model.yards_per_rush_attempt
        if not is_null(player_model_yards_per_rush_attempt):
            yards_per_rush_attempt = player_model_yards_per_rush_attempt
        player_model_espn_widereceiver = player_model.espn_widereceiver
        if not is_null(player_model_espn_widereceiver):
            espn_widereceiver = player_model_espn_widereceiver
        player_model_long_reception = player_model.long_reception
        if not is_null(player_model_long_reception):
            long_reception = player_model_long_reception
        player_model_receiving_big_plays = player_model.receiving_big_plays
        if not is_null(player_model_receiving_big_plays):
            receiving_big_plays = player_model_receiving_big_plays
        player_model_receiving_first_downs = player_model.receiving_first_downs
        if not is_null(player_model_receiving_first_downs):
            receiving_first_downs = player_model_receiving_first_downs
        player_model_receiving_fumbles = player_model.receiving_fumbles
        if not is_null(player_model_receiving_fumbles):
            receiving_fumbles = player_model_receiving_fumbles
        player_model_receiving_fumbles_lost = player_model.receiving_fumbles_lost
        if not is_null(player_model_receiving_fumbles_lost):
            receiving_fumbles_lost = player_model_receiving_fumbles_lost
        player_model_receiving_targets = player_model.receiving_targets
        if not is_null(player_model_receiving_targets):
            receiving_targets = player_model_receiving_targets
        player_model_receiving_touchdowns = player_model.receiving_touchdowns
        if not is_null(player_model_receiving_touchdowns):
            receiving_touchdowns = player_model_receiving_touchdowns
        player_model_receiving_yards = player_model.receiving_yards
        if not is_null(player_model_receiving_yards):
            receiving_yards = player_model_receiving_yards
        player_model_receiving_yards_after_catch = (
            player_model.receiving_yards_after_catch
        )
        if not is_null(player_model_receiving_yards_after_catch):
            receiving_yards_after_catch = player_model_receiving_yards_after_catch
        player_model_receiving_yards_at_catch = player_model.receiving_yards_at_catch
        if not is_null(player_model_receiving_yards_at_catch):
            receiving_yards_at_catch = player_model_receiving_yards_at_catch
        player_model_receptions = player_model.receptions
        if not is_null(player_model_receptions):
            receptions = player_model_receptions
        player_model_two_point_receptions = player_model.two_point_receptions
        if not is_null(player_model_two_point_receptions):
            two_point_receptions = player_model_two_point_receptions
        player_model_two_point_reception_attempts = (
            player_model.two_point_reception_attempts
        )
        if not is_null(player_model_two_point_reception_attempts):
            two_point_reception_attempts = player_model_two_point_reception_attempts
        player_model_yards_per_reception = player_model.yards_per_reception
        if not is_null(player_model_yards_per_reception):
            yards_per_reception = player_model_yards_per_reception
        player_model_assist_tackles = player_model.assist_tackles
        if not is_null(player_model_assist_tackles):
            assist_tackles = player_model_assist_tackles
        player_model_average_interception_yards = (
            player_model.average_interception_yards
        )
        if not is_null(player_model_average_interception_yards):
            average_interception_yards = player_model_average_interception_yards
        player_model_average_sack_yards = player_model.average_sack_yards
        if not is_null(player_model_average_sack_yards):
            average_sack_yards = player_model_average_sack_yards
        player_model_average_stuff_yards = player_model.average_stuff_yards
        if not is_null(player_model_average_stuff_yards):
            average_stuff_yards = player_model_average_stuff_yards
        player_model_blocked_field_goal_touchdowns = (
            player_model.blocked_field_goal_touchdowns
        )
        if not is_null(player_model_blocked_field_goal_touchdowns):
            blocked_field_goal_touchdowns = player_model_blocked_field_goal_touchdowns
        player_model_blocked_punt_touchdowns = player_model.blocked_punt_touchdowns
        if not is_null(player_model_blocked_punt_touchdowns):
            blocked_punt_touchdowns = player_model_blocked_punt_touchdowns
        player_model_defensive_touchdowns = player_model.defensive_touchdowns
        if not is_null(player_model_defensive_touchdowns):
            defensive_touchdowns = player_model_defensive_touchdowns
        player_model_hurries = player_model.hurries
        if not is_null(player_model_hurries):
            hurries = player_model_hurries
        player_model_kicks_blocked = player_model.kicks_blocked
        if not is_null(player_model_kicks_blocked):
            kicks_blocked = player_model_kicks_blocked
        player_model_long_interception = player_model.long_interception
        if not is_null(player_model_long_interception):
            long_interception = player_model_long_interception
        player_model_misc_touchdowns = player_model.misc_touchdowns
        if not is_null(player_model_misc_touchdowns):
            misc_touchdowns = player_model_misc_touchdowns
        player_model_passes_batted_down = player_model.passes_batted_down
        if not is_null(player_model_passes_batted_down):
            passes_batted_down = player_model_passes_batted_down
        player_model_passes_defended = player_model.passes_defended
        if not is_null(player_model_passes_defended):
            passes_defended = player_model_passes_defended
        player_model_quarterback_hits = player_model.quarterback_hits
        if not is_null(player_model_quarterback_hits):
            quarterback_hits = player_model_quarterback_hits
        player_model_sacks_assisted = player_model.sacks_assisted
        if not is_null(player_model_sacks_assisted):
            sacks_assisted = player_model_sacks_assisted
        player_model_sacks_unassisted = player_model.sacks_unassisted
        if not is_null(player_model_sacks_unassisted):
            sacks_unassisted = player_model_sacks_unassisted
        player_model_sacks_yards = player_model.sacks_yards
        if not is_null(player_model_sacks_yards):
            sacks_yards = player_model_sacks_yards
        player_model_safeties = player_model.safeties
        if not is_null(player_model_safeties):
            safeties = player_model_safeties
        player_model_solo_tackles = player_model.solo_tackles
        if not is_null(player_model_solo_tackles):
            solo_tackles = player_model_solo_tackles
        player_model_stuff_yards = player_model.stuff_yards
        if not is_null(player_model_stuff_yards):
            stuff_yards = player_model_stuff_yards
        player_model_tackles_for_loss = player_model.tackles_for_loss
        if not is_null(player_model_tackles_for_loss):
            tackles_for_loss = player_model_tackles_for_loss
        player_model_tackles_yards_lost = player_model.tackles_yards_lost
        if not is_null(player_model_tackles_yards_lost):
            tackles_yards_lost = player_model_tackles_yards_lost
        player_model_yards_allowed = player_model.yards_allowed
        if not is_null(player_model_yards_allowed):
            yards_allowed = player_model_yards_allowed
        player_model_points_allowed = player_model.points_allowed
        if not is_null(player_model_points_allowed):
            points_allowed = player_model_points_allowed
        player_model_one_point_safeties_made = player_model.one_point_safeties_made
        if not is_null(player_model_one_point_safeties_made):
            one_point_safeties_made = player_model_one_point_safeties_made
        player_model_missed_field_goal_return_td = (
            player_model.missed_field_goal_return_td
        )
        if not is_null(player_model_missed_field_goal_return_td):
            missed_field_goal_return_td = player_model_missed_field_goal_return_td
        player_model_blocked_punt_ez_rec_td = player_model.blocked_punt_ez_rec_td
        if not is_null(player_model_blocked_punt_ez_rec_td):
            blocked_punt_ez_rec_td = player_model_blocked_punt_ez_rec_td
        player_model_interception_touchdowns = player_model.interception_touchdowns
        if not is_null(player_model_interception_touchdowns):
            interception_touchdowns = player_model_interception_touchdowns
        player_model_interception_yards = player_model.interception_yards
        if not is_null(player_model_interception_yards):
            interception_yards = player_model_interception_yards
        player_model_average_kickoff_return_yards = (
            player_model.average_kickoff_return_yards
        )
        if not is_null(player_model_average_kickoff_return_yards):
            average_kickoff_return_yards = player_model_average_kickoff_return_yards
        player_model_average_kickoff_yards = player_model.average_kickoff_yards
        if not is_null(player_model_average_kickoff_yards):
            average_kickoff_yards = player_model_average_kickoff_yards
        player_model_extra_point_attempts = player_model.extra_point_attempts
        if not is_null(player_model_extra_point_attempts):
            extra_point_attempts = player_model_extra_point_attempts
        player_model_extra_point_percentage = player_model.extra_point_percentage
        if not is_null(player_model_extra_point_percentage):
            extra_point_percentage = player_model_extra_point_percentage
        player_model_extra_point_blocked = player_model.extra_point_blocked
        if not is_null(player_model_extra_point_blocked):
            extra_point_blocked = player_model_extra_point_blocked
        player_model_extra_points_blocked_percentage = (
            player_model.extra_points_blocked_percentage
        )
        if not is_null(player_model_extra_points_blocked_percentage):
            extra_points_blocked_percentage = (
                player_model_extra_points_blocked_percentage
            )
        player_model_extra_points_made = player_model.extra_points_made
        if not is_null(player_model_extra_points_made):
            extra_points_made = player_model_extra_points_made
        player_model_fair_catches = player_model.fair_catches
        if not is_null(player_model_fair_catches):
            fair_catches = player_model_fair_catches
        player_model_fair_catch_percentage = player_model.fair_catch_percentage
        if not is_null(player_model_fair_catch_percentage):
            fair_catch_percentage = player_model_fair_catch_percentage
        player_model_field_goal_attempts_max_19_yards = (
            player_model.field_goal_attempts_max_19_yards
        )
        if not is_null(player_model_field_goal_attempts_max_19_yards):
            field_goal_attempts_max_19_yards = (
                player_model_field_goal_attempts_max_19_yards
            )
        player_model_field_goal_attempts_max_29_yards = (
            player_model.field_goal_attempts_max_29_yards
        )
        if not is_null(player_model_field_goal_attempts_max_29_yards):
            field_goal_attempts_max_29_yards = (
                player_model_field_goal_attempts_max_29_yards
            )
        player_model_field_goal_attempts_max_39_yards = (
            player_model.field_goal_attempts_max_39_yards
        )
        if not is_null(player_model_field_goal_attempts_max_39_yards):
            field_goal_attempts_max_39_yards = (
                player_model_field_goal_attempts_max_39_yards
            )
        player_model_field_goal_attempts_max_49_yards = (
            player_model.field_goal_attempts_max_49_yards
        )
        if not is_null(player_model_field_goal_attempts_max_49_yards):
            field_goal_attempts_max_49_yards = (
                player_model_field_goal_attempts_max_49_yards
            )
        player_model_field_goal_attempts_max_59_yards = (
            player_model.field_goal_attempts_max_59_yards
        )
        if not is_null(player_model_field_goal_attempts_max_59_yards):
            field_goal_attempts_max_59_yards = (
                player_model_field_goal_attempts_max_59_yards
            )
        player_model_field_goal_attempts_max_99_yards = (
            player_model.field_goal_attempts_max_99_yards
        )
        if not is_null(player_model_field_goal_attempts_max_99_yards):
            field_goal_attempts_max_99_yards = (
                player_model_field_goal_attempts_max_99_yards
            )
        player_model_field_goal_attempts_above_50_yards = (
            player_model.field_goal_attempts_above_50_yards
        )
        if not is_null(player_model_field_goal_attempts_above_50_yards):
            field_goal_attempts_above_50_yards = (
                player_model_field_goal_attempts_above_50_yards
            )
        player_model_field_goal_attempt_yards = player_model.field_goal_attempt_yards
        if not is_null(player_model_field_goal_attempt_yards):
            field_goal_attempt_yards = player_model_field_goal_attempt_yards
        player_model_field_goals_blocked = player_model.field_goals_blocked
        if not is_null(player_model_field_goals_blocked):
            field_goals_blocked = player_model_field_goals_blocked
        player_model_field_goals_blocked_percentage = (
            player_model.field_goals_blocked_percentage
        )
        if not is_null(player_model_field_goals_blocked_percentage):
            field_goals_blocked_percentage = player_model_field_goals_blocked_percentage
        player_model_field_goals_made = player_model.field_goals_made
        if not is_null(player_model_field_goals_made):
            field_goals_made = player_model_field_goals_made
        player_model_field_goals_made_max_19_yards = (
            player_model.field_goals_made_max_19_yards
        )
        if not is_null(player_model_field_goals_made_max_19_yards):
            field_goals_made_max_19_yards = player_model_field_goals_made_max_19_yards
        player_model_field_goals_made_max_29_yards = (
            player_model.field_goals_made_max_29_yards
        )
        if not is_null(player_model_field_goals_made_max_29_yards):
            field_goals_made_max_29_yards = player_model_field_goals_made_max_29_yards
        player_model_field_goals_made_max_39_yards = (
            player_model.field_goals_made_max_39_yards
        )
        if not is_null(player_model_field_goals_made_max_39_yards):
            field_goals_made_max_39_yards = player_model_field_goals_made_max_39_yards
        player_model_field_goals_made_max_49_yards = (
            player_model.field_goals_made_max_49_yards
        )
        if not is_null(player_model_field_goals_made_max_49_yards):
            field_goals_made_max_49_yards = player_model_field_goals_made_max_49_yards
        player_model_field_goals_made_max_59_yards = (
            player_model.field_goals_made_max_59_yards
        )
        if not is_null(player_model_field_goals_made_max_59_yards):
            field_goals_made_max_59_yards = player_model_field_goals_made_max_59_yards
        player_model_field_goals_made_max_99_yards = (
            player_model.field_goals_made_max_99_yards
        )
        if not is_null(player_model_field_goals_made_max_99_yards):
            field_goals_made_max_99_yards = player_model_field_goals_made_max_99_yards
        player_model_field_goals_made_above_50_yards = (
            player_model.field_goals_made_above_50_yards
        )
        if not is_null(player_model_field_goals_made_above_50_yards):
            field_goals_made_above_50_yards = (
                player_model_field_goals_made_above_50_yards
            )
        player_model_field_goals_made_yards = player_model.field_goals_made_yards
        if not is_null(player_model_field_goals_made_yards):
            field_goals_made_yards = player_model_field_goals_made_yards
        player_model_field_goals_missed_yards = player_model.field_goals_missed_yards
        if not is_null(player_model_field_goals_missed_yards):
            field_goals_missed_yards = player_model_field_goals_missed_yards
        player_model_kickoff_out_of_bounds = player_model.kickoff_out_of_bounds
        if not is_null(player_model_kickoff_out_of_bounds):
            kickoff_out_of_bounds = player_model_kickoff_out_of_bounds
        player_model_kickoff_returns = player_model.kickoff_returns
        if not is_null(player_model_kickoff_returns):
            kickoff_returns = player_model_kickoff_returns
        player_model_kickoff_returns_touchdowns = (
            player_model.kickoff_returns_touchdowns
        )
        if not is_null(player_model_kickoff_returns_touchdowns):
            kickoff_returns_touchdowns = player_model_kickoff_returns_touchdowns
        player_model_kickoff_return_yards = player_model.kickoff_return_yards
        if not is_null(player_model_kickoff_return_yards):
            kickoff_return_yards = player_model_kickoff_return_yards
        player_model_kickoffs = player_model.kickoffs
        if not is_null(player_model_kickoffs):
            kickoffs = player_model_kickoffs
        player_model_kickoff_yards = player_model.kickoff_yards
        if not is_null(player_model_kickoff_yards):
            kickoff_yards = player_model_kickoff_yards
        player_model_long_field_goal_attempt = player_model.long_field_goal_attempt
        if not is_null(player_model_long_field_goal_attempt):
            long_field_goal_attempt = player_model_long_field_goal_attempt
        player_model_long_field_goal_made = player_model.long_field_goal_made
        if not is_null(player_model_long_field_goal_made):
            long_field_goal_made = player_model_long_field_goal_made
        player_model_long_kickoff = player_model.long_kickoff
        if not is_null(player_model_long_kickoff):
            long_kickoff = player_model_long_kickoff
        player_model_total_kicking_points = player_model.total_kicking_points
        if not is_null(player_model_total_kicking_points):
            total_kicking_points = player_model_total_kicking_points
        player_model_touchback_percentage = player_model.touchback_percentage
        if not is_null(player_model_touchback_percentage):
            touchback_percentage = player_model_touchback_percentage
        player_model_touchbacks = player_model.touchbacks
        if not is_null(player_model_touchbacks):
            touchbacks = player_model_touchbacks
        player_model_defensive_fumble_returns = player_model.defensive_fumble_returns
        if not is_null(player_model_defensive_fumble_returns):
            defensive_fumble_returns = player_model_defensive_fumble_returns
        player_model_defensive_fumble_return_yards = (
            player_model.defensive_fumble_return_yards
        )
        if not is_null(player_model_defensive_fumble_return_yards):
            defensive_fumble_return_yards = player_model_defensive_fumble_return_yards
        player_model_fumble_recoveries = player_model.fumble_recoveries
        if not is_null(player_model_fumble_recoveries):
            fumble_recoveries = player_model_fumble_recoveries
        player_model_fumble_recovery_yards = player_model.fumble_recovery_yards
        if not is_null(player_model_fumble_recovery_yards):
            fumble_recovery_yards = player_model_fumble_recovery_yards
        player_model_kick_return_fair_catches = player_model.kick_return_fair_catches
        if not is_null(player_model_kick_return_fair_catches):
            kick_return_fair_catches = player_model_kick_return_fair_catches
        player_model_kick_return_fair_catch_percentage = (
            player_model.kick_return_fair_catch_percentage
        )
        if not is_null(player_model_kick_return_fair_catch_percentage):
            kick_return_fair_catch_percentage = (
                player_model_kick_return_fair_catch_percentage
            )
        player_model_kick_return_fumbles = player_model.kick_return_fumbles
        if not is_null(player_model_kick_return_fumbles):
            kick_return_fumbles = player_model_kick_return_fumbles
        player_model_kick_return_fumbles_lost = player_model.kick_return_fumbles_lost
        if not is_null(player_model_kick_return_fumbles_lost):
            kick_return_fumbles_lost = player_model_kick_return_fumbles_lost
        player_model_kick_returns = player_model.kick_returns
        if not is_null(player_model_kick_returns):
            kick_returns = player_model_kick_returns
        player_model_kick_return_touchdowns = player_model.kick_return_touchdowns
        if not is_null(player_model_kick_return_touchdowns):
            kick_return_touchdowns = player_model_kick_return_touchdowns
        player_model_kick_return_yards = player_model.kick_return_yards
        if not is_null(player_model_kick_return_yards):
            kick_return_yards = player_model_kick_return_yards
        player_model_long_kick_return = player_model.long_kick_return
        if not is_null(player_model_long_kick_return):
            long_kick_return = player_model_long_kick_return
        player_model_long_punt_return = player_model.long_punt_return
        if not is_null(player_model_long_punt_return):
            long_punt_return = player_model_long_punt_return
        player_model_misc_fumble_returns = player_model.misc_fumble_returns
        if not is_null(player_model_misc_fumble_returns):
            misc_fumble_returns = player_model_misc_fumble_returns
        player_model_misc_fumble_return_yards = player_model.misc_fumble_return_yards
        if not is_null(player_model_misc_fumble_return_yards):
            misc_fumble_return_yards = player_model_misc_fumble_return_yards
        player_model_opposition_fumble_recoveries = (
            player_model.opposition_fumble_recoveries
        )
        if not is_null(player_model_opposition_fumble_recoveries):
            opposition_fumble_recoveries = player_model_opposition_fumble_recoveries
        player_model_opposition_fumble_recovery_yards = (
            player_model.opposition_fumble_recovery_yards
        )
        if not is_null(player_model_opposition_fumble_recovery_yards):
            opposition_fumble_recovery_yards = (
                player_model_opposition_fumble_recovery_yards
            )
        player_model_opposition_special_team_fumble_returns = (
            player_model.opposition_special_team_fumble_returns
        )
        if not is_null(player_model_opposition_special_team_fumble_returns):
            opposition_special_team_fumble_returns = (
                player_model_opposition_special_team_fumble_returns
            )
        player_model_opposition_special_team_fumble_return_yards = (
            player_model.opposition_special_team_fumble_return_yards
        )
        if not is_null(player_model_opposition_special_team_fumble_return_yards):
            opposition_special_team_fumble_return_yards = (
                player_model_opposition_special_team_fumble_return_yards
            )
        player_model_punt_return_fair_catches = player_model.punt_return_fair_catches
        if not is_null(player_model_punt_return_fair_catches):
            punt_return_fair_catches = player_model_punt_return_fair_catches
        player_model_punt_return_fair_catch_percentage = (
            player_model.punt_return_fair_catch_percentage
        )
        if not is_null(player_model_punt_return_fair_catch_percentage):
            punt_return_fair_catch_percentage = (
                player_model_punt_return_fair_catch_percentage
            )
        player_model_punt_return_fumbles = player_model.punt_return_fumbles
        if not is_null(player_model_punt_return_fumbles):
            punt_return_fumbles = player_model_punt_return_fumbles
        player_model_punt_return_fumbles_lost = player_model.punt_return_fumbles_lost
        if not is_null(player_model_punt_return_fumbles_lost):
            punt_return_fumbles_lost = player_model_punt_return_fumbles_lost
        player_model_punt_returns = player_model.punt_returns
        if not is_null(player_model_punt_returns):
            punt_returns = player_model_punt_returns
        player_model_punt_returns_started_inside_the_10 = (
            player_model.punt_returns_started_inside_the_10
        )
        if not is_null(player_model_punt_returns_started_inside_the_10):
            punt_returns_started_inside_the_10 = (
                player_model_punt_returns_started_inside_the_10
            )
        player_model_punt_returns_started_inside_the_20 = (
            player_model.punt_returns_started_inside_the_20
        )
        if not is_null(player_model_punt_returns_started_inside_the_20):
            punt_returns_started_inside_the_20 = (
                player_model_punt_returns_started_inside_the_20
            )
        player_model_punt_return_touchdowns = player_model.punt_return_touchdowns
        if not is_null(player_model_punt_return_touchdowns):
            punt_return_touchdowns = player_model_punt_return_touchdowns
        player_model_punt_return_yards = player_model.punt_return_yards
        if not is_null(player_model_punt_return_yards):
            punt_return_yards = player_model_punt_return_yards
        player_model_special_team_fumble_returns = (
            player_model.special_team_fumble_returns
        )
        if not is_null(player_model_special_team_fumble_returns):
            special_team_fumble_returns = player_model_special_team_fumble_returns
        player_model_yards_per_kick_return = player_model.yards_per_kick_return
        if not is_null(player_model_yards_per_kick_return):
            yards_per_kick_return = player_model_yards_per_kick_return
        player_model_yards_per_punt_return = player_model.yards_per_punt_return
        if not is_null(player_model_yards_per_punt_return):
            yards_per_punt_return = player_model_yards_per_punt_return
        player_model_yards_per_return = player_model.yards_per_return
        if not is_null(player_model_yards_per_return):
            yards_per_return = player_model_yards_per_return
        player_model_average_punt_return_yards = player_model.average_punt_return_yards
        if not is_null(player_model_average_punt_return_yards):
            average_punt_return_yards = player_model_average_punt_return_yards
        player_model_gross_average_punt_yards = player_model.gross_average_punt_yards
        if not is_null(player_model_gross_average_punt_yards):
            gross_average_punt_yards = player_model_gross_average_punt_yards
        player_model_long_punt = player_model.long_punt
        if not is_null(player_model_long_punt):
            long_punt = player_model_long_punt
        player_model_net_average_punt_yards = player_model.net_average_punt_yards
        if not is_null(player_model_net_average_punt_yards):
            net_average_punt_yards = player_model_net_average_punt_yards
        player_model_punts = player_model.punts
        if not is_null(player_model_punts):
            punts = player_model_punts
        player_model_punts_blocked = player_model.punts_blocked
        if not is_null(player_model_punts_blocked):
            punts_blocked = player_model_punts_blocked
        player_model_punts_blocked_percentage = player_model.punts_blocked_percentage
        if not is_null(player_model_punts_blocked_percentage):
            punts_blocked_percentage = player_model_punts_blocked_percentage
        player_model_punts_inside_10 = player_model.punts_inside_10
        if not is_null(player_model_punts_inside_10):
            punts_inside_10 = player_model_punts_inside_10
        player_model_punts_inside_10_percentage = (
            player_model.punts_inside_10_percentage
        )
        if not is_null(player_model_punts_inside_10_percentage):
            punts_inside_10_percentage = player_model_punts_inside_10_percentage
        player_model_punts_inside_20 = player_model.punts_inside_20
        if not is_null(player_model_punts_inside_20):
            punts_inside_20 = player_model_punts_inside_20
        player_model_punts_inside_20_percentage = (
            player_model.punts_inside_20_percentage
        )
        if not is_null(player_model_punts_inside_20_percentage):
            punts_inside_20_percentage = player_model_punts_inside_20_percentage
        player_model_punts_over_50 = player_model.punts_over_50
        if not is_null(player_model_punts_over_50):
            punts_over_50 = player_model_punts_over_50
        player_model_punt_yards = player_model.punt_yards
        if not is_null(player_model_punt_yards):
            punt_yards = player_model_punt_yards
        player_model_defensive_points = player_model.defensive_points
        if not is_null(player_model_defensive_points):
            defensive_points = player_model_defensive_points
        player_model_misc_points = player_model.misc_points
        if not is_null(player_model_misc_points):
            misc_points = player_model_misc_points
        player_model_return_touchdowns = player_model.return_touchdowns
        if not is_null(player_model_return_touchdowns):
            return_touchdowns = player_model_return_touchdowns
        player_model_total_two_point_conversions = (
            player_model.total_two_point_conversions
        )
        if not is_null(player_model_total_two_point_conversions):
            total_two_point_conversions = player_model_total_two_point_conversions
        player_model_passing_touchdowns_9_yards = (
            player_model.passing_touchdowns_9_yards
        )
        if not is_null(player_model_passing_touchdowns_9_yards):
            passing_touchdowns_9_yards = player_model_passing_touchdowns_9_yards
        player_model_passing_touchdowns_19_yards = (
            player_model.passing_touchdowns_19_yards
        )
        if not is_null(player_model_passing_touchdowns_19_yards):
            passing_touchdowns_19_yards = player_model_passing_touchdowns_19_yards
        player_model_passing_touchdowns_29_yards = (
            player_model.passing_touchdowns_29_yards
        )
        if not is_null(player_model_passing_touchdowns_29_yards):
            passing_touchdowns_29_yards = player_model_passing_touchdowns_29_yards
        player_model_passing_touchdowns_39_yards = (
            player_model.passing_touchdowns_39_yards
        )
        if not is_null(player_model_passing_touchdowns_39_yards):
            passing_touchdowns_39_yards = player_model_passing_touchdowns_39_yards
        player_model_passing_touchdowns_49_yards = (
            player_model.passing_touchdowns_49_yards
        )
        if not is_null(player_model_passing_touchdowns_49_yards):
            passing_touchdowns_49_yards = player_model_passing_touchdowns_49_yards
        player_model_passing_touchdowns_above_50_yards = (
            player_model.passing_touchdowns_above_50_yards
        )
        if not is_null(player_model_passing_touchdowns_above_50_yards):
            passing_touchdowns_above_50_yards = (
                player_model_passing_touchdowns_above_50_yards
            )
        player_model_receiving_touchdowns_9_yards = (
            player_model.receiving_touchdowns_9_yards
        )
        if not is_null(player_model_receiving_touchdowns_9_yards):
            receiving_touchdowns_9_yards = player_model_receiving_touchdowns_9_yards
        player_model_receiving_touchdowns_19_yards = (
            player_model.receiving_touchdowns_19_yards
        )
        if not is_null(player_model_receiving_touchdowns_19_yards):
            receiving_touchdowns_19_yards = player_model_receiving_touchdowns_19_yards
        player_model_receiving_touchdowns_29_yards = (
            player_model.receiving_touchdowns_29_yards
        )
        if not is_null(player_model_receiving_touchdowns_29_yards):
            receiving_touchdowns_29_yards = player_model_receiving_touchdowns_29_yards
        player_model_receiving_touchdowns_39_yards = (
            player_model.receiving_touchdowns_39_yards
        )
        if not is_null(player_model_receiving_touchdowns_39_yards):
            receiving_touchdowns_39_yards = player_model_receiving_touchdowns_39_yards
        player_model_receiving_touchdowns_49_yards = (
            player_model.receiving_touchdowns_49_yards
        )
        if not is_null(player_model_receiving_touchdowns_49_yards):
            receiving_touchdowns_49_yards = player_model_receiving_touchdowns_49_yards
        player_model_receiving_touchdowns_above_50_yards = (
            player_model.receiving_touchdowns_above_50_yards
        )
        if not is_null(player_model_receiving_touchdowns_above_50_yards):
            receiving_touchdowns_above_50_yards = (
                player_model_receiving_touchdowns_above_50_yards
            )
        player_model_rushing_touchdowns_9_yards = (
            player_model.rushing_touchdowns_9_yards
        )
        if not is_null(player_model_rushing_touchdowns_9_yards):
            rushing_touchdowns_9_yards = player_model_rushing_touchdowns_9_yards
        player_model_rushing_touchdowns_19_yards = (
            player_model.rushing_touchdowns_19_yards
        )
        if not is_null(player_model_rushing_touchdowns_19_yards):
            rushing_touchdowns_19_yards = player_model_rushing_touchdowns_19_yards
        player_model_rushing_touchdowns_29_yards = (
            player_model.rushing_touchdowns_29_yards
        )
        if not is_null(player_model_rushing_touchdowns_29_yards):
            rushing_touchdowns_29_yards = player_model_rushing_touchdowns_29_yards
        player_model_rushing_touchdowns_39_yards = (
            player_model.rushing_touchdowns_39_yards
        )
        if not is_null(player_model_rushing_touchdowns_39_yards):
            rushing_touchdowns_39_yards = player_model_rushing_touchdowns_39_yards
        player_model_rushing_touchdowns_49_yards = (
            player_model.rushing_touchdowns_49_yards
        )
        if not is_null(player_model_rushing_touchdowns_49_yards):
            rushing_touchdowns_49_yards = player_model_rushing_touchdowns_49_yards
        player_model_rushing_touchdowns_above_50_yards = (
            player_model.rushing_touchdowns_above_50_yards
        )
        if not is_null(player_model_rushing_touchdowns_above_50_yards):
            rushing_touchdowns_above_50_yards = (
                player_model_rushing_touchdowns_above_50_yards
            )
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
        height=height,
        colleges=colleges if colleges is not None else [],
        headshot=headshot,
        forced_fumbles=forced_fumbles,
        fumbles_recovered=fumbles_recovered,
        fumbles_recovered_yards=fumbles_recovered_yards,
        fumbles_touchdowns=fumbles_touchdowns,
        offensive_two_point_returns=offensive_two_point_returns,
        offensive_fumbles_touchdowns=offensive_fumbles_touchdowns,
        defensive_fumbles_touchdowns=defensive_fumbles_touchdowns,
        average_gain=average_gain,
        completion_percentage=completion_percentage,
        completions=completions,
        espn_quarterback_rating=espn_quarterback_rating,
        interception_percentage=interception_percentage,
        interceptions=interceptions,
        long_passing=long_passing,
        misc_yards=misc_yards,
        net_passing_yards=net_passing_yards,
        net_total_yards=net_total_yards,
        passing_attempts=passing_attempts,
        passing_big_plays=passing_big_plays,
        passing_first_downs=passing_first_downs,
        passing_fumbles=passing_fumbles,
        passing_fumbles_lost=passing_fumbles_lost,
        passing_touchdown_percentage=passing_touchdown_percentage,
        passing_touchdowns=passing_touchdowns,
        passing_yards=passing_yards,
        passing_yards_after_catch=passing_yards_after_catch,
        passing_yards_at_catch=passing_yards_at_catch,
        quarterback_rating=quarterback_rating,
        sacks=sacks,
        sacks_yards_lost=sacks_yards_lost,
        net_passing_attempts=net_passing_attempts,
        total_offensive_plays=total_offensive_plays,
        total_points=total_points,
        total_touchdowns=total_touchdowns,
        total_yards=total_yards,
        total_yards_from_scrimmage=total_yards_from_scrimmage,
        two_point_pass=two_point_pass,
        two_point_pass_attempt=two_point_pass_attempt,
        yards_per_completion=yards_per_completion,
        yards_per_pass_attempt=yards_per_pass_attempt,
        net_yards_per_pass_attempt=net_yards_per_pass_attempt,
        long_rushing=long_rushing,
        rushing_attempts=rushing_attempts,
        rushing_big_plays=rushing_big_plays,
        rushing_first_downs=rushing_first_downs,
        rushing_fumbles=rushing_fumbles,
        rushing_fumbles_lost=rushing_fumbles_lost,
        rushing_touchdowns=rushing_touchdowns,
        rushing_yards=rushing_yards,
        stuffs=stuffs,
        stuff_yards_lost=stuff_yards_lost,
        two_point_rush=two_point_rush,
        two_point_rush_attempts=two_point_rush_attempts,
        yards_per_rush_attempt=yards_per_rush_attempt,
        espn_widereceiver=espn_widereceiver,
        long_reception=long_reception,
        receiving_big_plays=receiving_big_plays,
        receiving_first_downs=receiving_first_downs,
        receiving_fumbles=receiving_fumbles,
        receiving_fumbles_lost=receiving_fumbles_lost,
        receiving_targets=receiving_targets,
        receiving_touchdowns=receiving_touchdowns,
        receiving_yards=receiving_yards,
        receiving_yards_after_catch=receiving_yards_after_catch,
        receiving_yards_at_catch=receiving_yards_at_catch,
        receptions=receptions,
        two_point_receptions=two_point_receptions,
        two_point_reception_attempts=two_point_reception_attempts,
        yards_per_reception=yards_per_reception,
        assist_tackles=assist_tackles,
        average_interception_yards=average_interception_yards,
        average_sack_yards=average_sack_yards,
        average_stuff_yards=average_stuff_yards,
        blocked_field_goal_touchdowns=blocked_field_goal_touchdowns,
        blocked_punt_touchdowns=blocked_punt_touchdowns,
        defensive_touchdowns=defensive_touchdowns,
        hurries=hurries,
        kicks_blocked=kicks_blocked,
        long_interception=long_interception,
        misc_touchdowns=misc_touchdowns,
        passes_batted_down=passes_batted_down,
        passes_defended=passes_defended,
        quarterback_hits=quarterback_hits,
        sacks_assisted=sacks_assisted,
        sacks_unassisted=sacks_unassisted,
        sacks_yards=sacks_yards,
        safeties=safeties,
        solo_tackles=solo_tackles,
        stuff_yards=stuff_yards,
        tackles_for_loss=tackles_for_loss,
        tackles_yards_lost=tackles_yards_lost,
        yards_allowed=yards_allowed,
        points_allowed=points_allowed,
        one_point_safeties_made=one_point_safeties_made,
        missed_field_goal_return_td=missed_field_goal_return_td,
        blocked_punt_ez_rec_td=blocked_punt_ez_rec_td,
        interception_touchdowns=interception_touchdowns,
        interception_yards=interception_yards,
        average_kickoff_return_yards=average_kickoff_return_yards,
        average_kickoff_yards=average_kickoff_yards,
        extra_point_attempts=extra_point_attempts,
        extra_point_percentage=extra_point_percentage,
        extra_point_blocked=extra_point_blocked,
        extra_points_blocked_percentage=extra_points_blocked_percentage,
        extra_points_made=extra_points_made,
        fair_catches=fair_catches,
        fair_catch_percentage=fair_catch_percentage,
        field_goal_attempts_max_19_yards=field_goal_attempts_max_19_yards,
        field_goal_attempts_max_29_yards=field_goal_attempts_max_29_yards,
        field_goal_attempts_max_39_yards=field_goal_attempts_max_39_yards,
        field_goal_attempts_max_49_yards=field_goal_attempts_max_49_yards,
        field_goal_attempts_max_59_yards=field_goal_attempts_max_59_yards,
        field_goal_attempts_max_99_yards=field_goal_attempts_max_99_yards,
        field_goal_attempts_above_50_yards=field_goal_attempts_above_50_yards,
        field_goal_attempt_yards=field_goal_attempt_yards,
        field_goals_blocked=field_goals_blocked,
        field_goals_blocked_percentage=field_goals_blocked_percentage,
        field_goals_made=field_goals_made,
        field_goals_made_max_19_yards=field_goals_made_max_19_yards,
        field_goals_made_max_29_yards=field_goals_made_max_29_yards,
        field_goals_made_max_39_yards=field_goals_made_max_39_yards,
        field_goals_made_max_49_yards=field_goals_made_max_49_yards,
        field_goals_made_max_59_yards=field_goals_made_max_59_yards,
        field_goals_made_max_99_yards=field_goals_made_max_99_yards,
        field_goals_made_above_50_yards=field_goals_made_above_50_yards,
        field_goals_made_yards=field_goals_made_yards,
        field_goals_missed_yards=field_goals_missed_yards,
        kickoff_out_of_bounds=kickoff_out_of_bounds,
        kickoff_returns=kickoff_returns,
        kickoff_returns_touchdowns=kickoff_returns_touchdowns,
        kickoff_return_yards=kickoff_return_yards,
        kickoffs=kickoffs,
        kickoff_yards=kickoff_yards,
        long_field_goal_attempt=long_field_goal_attempt,
        long_field_goal_made=long_field_goal_made,
        long_kickoff=long_kickoff,
        total_kicking_points=total_kicking_points,
        touchback_percentage=touchback_percentage,
        touchbacks=touchbacks,
        defensive_fumble_returns=defensive_fumble_returns,
        defensive_fumble_return_yards=defensive_fumble_return_yards,
        fumble_recoveries=fumble_recoveries,
        fumble_recovery_yards=fumble_recovery_yards,
        kick_return_fair_catches=kick_return_fair_catches,
        kick_return_fair_catch_percentage=kick_return_fair_catch_percentage,
        kick_return_fumbles=kick_return_fumbles,
        kick_return_fumbles_lost=kick_return_fumbles_lost,
        kick_returns=kick_returns,
        kick_return_touchdowns=kick_return_touchdowns,
        kick_return_yards=kick_return_yards,
        long_kick_return=long_kick_return,
        long_punt_return=long_punt_return,
        misc_fumble_returns=misc_fumble_returns,
        misc_fumble_return_yards=misc_fumble_return_yards,
        opposition_fumble_recoveries=opposition_fumble_recoveries,
        opposition_fumble_recovery_yards=opposition_fumble_recovery_yards,
        opposition_special_team_fumble_returns=opposition_special_team_fumble_returns,
        opposition_special_team_fumble_return_yards=opposition_special_team_fumble_return_yards,
        punt_return_fair_catches=punt_return_fair_catches,
        punt_return_fair_catch_percentage=punt_return_fair_catch_percentage,
        punt_return_fumbles=punt_return_fumbles,
        punt_return_fumbles_lost=punt_return_fumbles_lost,
        punt_returns=punt_returns,
        punt_returns_started_inside_the_10=punt_returns_started_inside_the_10,
        punt_returns_started_inside_the_20=punt_returns_started_inside_the_20,
        punt_return_touchdowns=punt_return_touchdowns,
        punt_return_yards=punt_return_yards,
        special_team_fumble_returns=special_team_fumble_returns,
        yards_per_kick_return=yards_per_kick_return,
        yards_per_punt_return=yards_per_punt_return,
        yards_per_return=yards_per_return,
        average_punt_return_yards=average_punt_return_yards,
        gross_average_punt_yards=gross_average_punt_yards,
        long_punt=long_punt,
        net_average_punt_yards=net_average_punt_yards,
        punts=punts,
        punts_blocked=punts_blocked,
        punts_blocked_percentage=punts_blocked_percentage,
        punts_inside_10=punts_inside_10,
        punts_inside_10_percentage=punts_inside_10_percentage,
        punts_inside_20=punts_inside_20,
        punts_inside_20_percentage=punts_inside_20_percentage,
        punts_over_50=punts_over_50,
        punt_yards=punt_yards,
        defensive_points=defensive_points,
        misc_points=misc_points,
        return_touchdowns=return_touchdowns,
        total_two_point_conversions=total_two_point_conversions,
        passing_touchdowns_9_yards=passing_touchdowns_9_yards,
        passing_touchdowns_19_yards=passing_touchdowns_19_yards,
        passing_touchdowns_29_yards=passing_touchdowns_29_yards,
        passing_touchdowns_39_yards=passing_touchdowns_39_yards,
        passing_touchdowns_49_yards=passing_touchdowns_49_yards,
        passing_touchdowns_above_50_yards=passing_touchdowns_above_50_yards,
        receiving_touchdowns_9_yards=receiving_touchdowns_9_yards,
        receiving_touchdowns_19_yards=receiving_touchdowns_19_yards,
        receiving_touchdowns_29_yards=receiving_touchdowns_29_yards,
        receiving_touchdowns_39_yards=receiving_touchdowns_39_yards,
        receiving_touchdowns_49_yards=receiving_touchdowns_49_yards,
        receiving_touchdowns_above_50_yards=receiving_touchdowns_above_50_yards,
        rushing_touchdowns_9_yards=rushing_touchdowns_9_yards,
        rushing_touchdowns_19_yards=rushing_touchdowns_19_yards,
        rushing_touchdowns_29_yards=rushing_touchdowns_29_yards,
        rushing_touchdowns_39_yards=rushing_touchdowns_39_yards,
        rushing_touchdowns_49_yards=rushing_touchdowns_49_yards,
        rushing_touchdowns_above_50_yards=rushing_touchdowns_above_50_yards,
    )

    ffill(player_ffill, identifier, player_model)

    return player_model
