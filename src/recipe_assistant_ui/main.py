import gradio as gr

from PIL import Image

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


def describe_image(image: Image.Image) -> str:
    if image is None:
        return "Sube una foto de tus ingredientes"

    return f"Imagen recibida: {image.size[0]}x{image.size[1]} pixeles, formato: {image.format or "desconocido"}."


def main() -> None:

    with gr.Blocks() as interface:
        with gr.Row():
            ingredients_image = gr.Image(label="Foto de los ingredientes", type="pil")

        image_info = gr.Textbox(label="Info de la imagen")

        with gr.Row():
            question = gr.Textbox(label="Pregunta")
            ask_button = gr.Button("Preguntar")

        with gr.Row():
            with gr.Column():
                recipe_name = gr.Textbox(label="Receta")
                prep_time = gr.Number(label="Tiempo en minutos")
            with gr.Column():
                ingredients = gr.Textbox(label="Ingredientes")
                steps = gr.Textbox(label="Pasos")

        ingredients_image.upload(
            fn=describe_image,
            inputs=ingredients_image,
            outputs=image_info,
        )

        question.submit(
            fn=ask_recipe,
            inputs=question,
            outputs=[ recipe_name, prep_time, ingredients, steps]
        )

        ask_button.click(
            fn=ask_recipe,
            inputs=question,
            outputs=[ recipe_name, prep_time, ingredients, steps]
        )

    interface.launch()
