from dataclasses import dataclass


@dataclass
class RecipeDeps:
    available_ingredients: list[str]
    diet: str | None = None
