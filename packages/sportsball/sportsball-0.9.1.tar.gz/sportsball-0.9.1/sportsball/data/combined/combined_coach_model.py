"""Combined coach model."""

from typing import Any

from ..coach_model import VERSION, CoachModel
from .ffill import ffill
from .null_check import is_null


def create_combined_coach_model(
    coach_models: list[CoachModel],
    identifier: str,
    coach_ffill: dict[str, dict[str, Any]],
) -> CoachModel:
    """Create a coach model by combining many coach models."""
    name = None
    birth_date = None
    age = None
    sex = None
    for coach_model in coach_models:
        coach_model_name = coach_model.name
        if not is_null(coach_model_name):
            name = coach_model_name
        coach_model_birthdate = coach_model.birth_date
        if not is_null(coach_model_birthdate):
            birth_date = coach_model_birthdate
        coach_model_age = coach_model.age
        if not is_null(coach_model_age):
            age = coach_model_age
        coach_model_sex = coach_model.sex
        if not is_null(coach_model_sex):
            sex = coach_model_sex
    if name is None:
        raise ValueError("name is null.")
    coach_model = CoachModel(
        identifier=identifier,
        name=name,
        birth_date=birth_date,
        age=age,
        version=VERSION,
        sex=sex,
    )

    ffill(coach_ffill, identifier, coach_model)

    return coach_model
