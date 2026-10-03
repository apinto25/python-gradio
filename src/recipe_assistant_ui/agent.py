from datetime import date

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from .deps import RecipeDeps
from .models import Recipe

load_dotenv()

agent = Agent(
    'google:gemini-3.6-flash',
    instructions='Eres un asistente de cocina. Recomiendas recetas según los '
                 'ingredientes que el usuario tiene disponibles. Sé breve y práctico. '
                 'Si el usuario hace una pregunta que no es sobre recomendarle una receta, '
                 'respóndele en texto libre en lugar de generar una receta. '
                 'Si el usuario pregunta algo que no tiene relación con cocina o recetas, '
                 'indícale amablemente que ese no es tu trabajo y que sólo puedes ayudar '
                 'con temas de cocina.',
    output_type=Recipe | str,
    deps_type=RecipeDeps,
    retries=3,
)


@agent.instructions
def add_season() -> str:
    month = date.today().month
    if month == 12:
        return (
            'Estamos en diciembre. Si es posible, prioriza recetas navideñas '
            'o de fin de año, y menciona en tu respuesta que la receta es de temporada.'
        )
    return (
        f'Estamos en el mes {month}. Prioriza ingredientes de temporada cuando sea '
        'relevante, y menciona en tu respuesta que la receta es de temporada.'
    )


@agent.instructions
def add_diet_preference(ctx: RunContext[RecipeDeps]) -> str:
    if ctx.deps and ctx.deps.diet:
        return f"El usuario tiene esta preferencia allimenticia: {ctx.deps.diet}. Ajusta la receta para que la cumpla"
    return ""


@agent.tool
def get_available_ingredients(ctx: RunContext[RecipeDeps]) -> list[str]:
    """Return available ingredients."""
    return ctx.deps.available_ingredients
