import gradio as gr
import io

from PIL import Image
from pydantic_ai import BinaryContent

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


async def ask_recipe_stream(question: str, diet: str):
    deps = RecipeDeps(
        available_ingredients=["arroz", "pollo", "cebolla", "tomate"],
        diet=diet if diet != "Ninguna" else None,
    )
    async with agent.run_stream(question, deps=deps) as result:
        async for output in result.stream_output(debounce_by=0.01):
            if isinstance(output, str):
                yield output, "", 0, ""

        recipe = await result.get_output()
        if isinstance(recipe, Recipe):
            yield (
                recipe.name,
                ", ".join(recipe.ingredients),
                recipe.prep_time_minutes,
                "\n".join(recipe.steps)
            )


def image_to_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def indentify_ingredients(image: Image.Image) -> str:
    if image is None:
        return "Sube una foto de tus ingredientes"

    result = agent.run_sync([
        "Qué ingredientes puedes identificar en esta imagen?",
        BinaryContent(data=image_to_bytes(image), media_type="image/png")
    ])

    return result.output


def main() -> None:

    with gr.Blocks() as interface:
        with gr.Row():
            ingredients_image = gr.Image(label="Foto de los ingredientes", type="pil")

        image_info = gr.Textbox(label="Info de la imagen")

        with gr.Row():
            question = gr.Textbox(label="Pregunta")
            diet = gr.Dropdown(label="Preferencia alimenticia",
                               choices=["Ninguna", "Vegetariana", "Vegana"])
            ask_button = gr.Button("Preguntar")

        with gr.Row():
            with gr.Column():
                recipe_name = gr.Textbox(label="Receta")
                prep_time = gr.Number(label="Tiempo en minutos")
            with gr.Column():
                ingredients = gr.Textbox(label="Ingredientes")
                steps = gr.Textbox(label="Pasos")

        ingredients_image.upload(
            fn=indentify_ingredients,
            inputs=ingredients_image,
            outputs=image_info,
        )

        question.submit(
            fn=ask_recipe_stream,
            inputs=[question, diet],
            outputs=[recipe_name, ingredients, prep_time, steps]
        )

        ask_button.click(
            fn=ask_recipe_stream,
            inputs=[question, diet],
            outputs=[recipe_name, ingredients, prep_time, steps]
        )

    interface.launch()
