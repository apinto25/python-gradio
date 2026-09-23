from pydantic import BaseModel, field_validator


class Recipe(BaseModel):
    name: str
    ingredients: list[str]
    prep_time_minutes: int
    steps: list[str]

    @field_validator('ingredients')
    @classmethod
    def must_have_ingredients(cls, value: list[str]) -> list[str]:
        if len(value) <= 0:
            raise ValueError('La receta debe tener al menos un ingrediente.')
        return value
