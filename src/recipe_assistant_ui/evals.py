import asyncio

from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import IsInstance

from .main import agent, deps
from .models import Recipe

case = Case(
    name='pregunta_con_ingredientes',
    inputs='¿Qué puedo cocinar con lo que tengo disponible?',
)

dataset = Dataset(
    name='recipe_assistant_eval',
    cases=[case],
    evaluators=[IsInstance(type_name='Recipe')],
)


async def run_agent(user_message: str) -> Recipe | str:
    result = await agent.run(user_message, deps=deps)
    return result.output


async def run_evals() -> None:
    report = await dataset.evaluate(run_agent)
    report.print()


if __name__ == '__main__':
    asyncio.run(run_evals())
