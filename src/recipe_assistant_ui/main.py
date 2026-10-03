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

async def handle_chat_message(message:str, history: list, message_history: list, diet: str, image: Image.Image):
    if image is not None:
        identified = await indentify_ingredients(image)
        available_ingredients = [item.strip() for item in identified.split(",")]
    else:
        available_ingredients = ["arroz", "pollo", "cebolla", "tomate"]

    if not message:
        raise gr.Error("Escribe una pregunta antes de enviar")
    
    deps = RecipeDeps(
        available_ingredients=available_ingredients,
        diet=diet if diet != "Ninguna" else None,
    )
    try:
        async with agent.run_stream(message, deps=deps, message_history=message_history) as result:
            async for output in result.stream_output(debounce_by=0.01):
                if isinstance(output, str):
                    yield output, message_history

            final_output = await result.get_output()
            new_history = result.all_messages()
            if isinstance(final_output, Recipe):
                recipe = final_output
                response = (
                    f"{recipe.name} ({recipe.prep_time_minutes} min)\n\n"
                    f"Ingredientes: {", ".join(recipe.ingredients)}"
                    f"Pasos: {"\n".join(recipe.steps)}"
                )
            else:
                response = final_output
            yield response, new_history
    except Exception:
        raise gr.Error("No pudimos generar una respuesta, intenta de nuevo en unos segundos")


def image_to_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


async def indentify_ingredients(image: Image.Image) -> str:
    if image is None:
        return "Sube una foto de tus ingredientes"

    result = await agent.run([
        "Qué ingredientes puedes identificar en esta imagen? Enumeralos separados por comas.",
        BinaryContent(data=image_to_bytes(image), media_type="image/png")
    ])

    return result.output


def main() -> None:

    message_history_state = gr.State([])

    interface = gr.ChatInterface(
        fn=handle_chat_message,
        title="Asistente de recetas",
        additional_inputs=[
            message_history_state,
            gr.Dropdown(label="Preferencia alimenticia",
                       choices=["Ninguna", "Vegetariana", "Vegana"]),
            gr.Image(label="Foto de los ingredientes", type="pil")
        ],
        additional_outputs=[message_history_state]
    )

    # with gr.Blocks() as interface:
    #     with gr.Row():
    #         ingredients_image = gr.Image(label="Foto de los ingredientes", type="pil")

    #     image_info = gr.Textbox(label="Info de la imagen")

    #     with gr.Row():
    #         question = gr.Textbox(label="Pregunta")
    #         diet = gr.Dropdown(label="Preferencia alimenticia",
    #                            choices=["Ninguna", "Vegetariana", "Vegana"])
    #         ask_button = gr.Button("Preguntar")

    #     with gr.Row():
    #         with gr.Column():
    #             recipe_name = gr.Textbox(label="Receta")
    #             prep_time = gr.Number(label="Tiempo en minutos")
    #         with gr.Column():
    #             ingredients = gr.Textbox(label="Ingredientes")
    #             steps = gr.Textbox(label="Pasos")

    #     ingredients_image.upload(
    #         fn=indentify_ingredients,
    #         inputs=ingredients_image,
    #         outputs=image_info,
    #     )

    #     question.submit(
    #         fn=ask_recipe_stream,
    #         inputs=[question, diet],
    #         outputs=[recipe_name, ingredients, prep_time, steps]
    #     )

    #     ask_button.click(
    #         fn=ask_recipe_stream,
    #         inputs=[question, diet],
    #         outputs=[recipe_name, ingredients, prep_time, steps]
    #     )

    interface.launch(
        theme=gr.themes.Soft(
            primary_hue="orange",
            secondary_hue="amber"
        )
    )
