import gradio as gr

from .agent import agent
from .deps import RecipeDeps
from .models import Recipe


def ask_recipe(question: str) -> tuple[str, str, int, str]:
    deps = RecipeDeps(
        available_ingredients=["arroz", "pollo", "cebolla", "tomate"]
    )
    result = agent.run_sync(question, deps=deps)

    if isinstance(result.output, Recipe):
        recipe = result.output
        return recipe.name, ", ".join(recipe.ingredients), recipe.prep_time_minutes, "\n".join(recipe.steps)
    return result.output, "", 0, ""


def main() -> None:
    interface = gr.Interface(
        fn=ask_recipe,
        inputs=gr.Textbox(label="Pregunta"),
        outputs=[
            gr.Textbox(label="Receta"),
            gr.Textbox(label="Ingredientes"),
            gr.Number(label="Tiempo en minutos"),
            gr.Textbox(label="Pasos"),
        ],
    )

    interface.launch()
