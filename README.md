# Recipe Assistant UI

Interfaz web para un asistente de recetas, construida con [Gradio](https://www.gradio.app/) y [PydanticAI](https://ai.pydantic.dev/) como proyecto del curso **Interfaces web con Gradio y Python**.

El asistente conversa en español dentro de un chat, recomienda recetas de temporada según los ingredientes disponibles (que también puede identificar a partir de una foto) y respeta la preferencia alimenticia del usuario.

## Estructura de `src/recipe_assistant_ui/`

| Archivo | Descripción |
|---|---|
| `__init__.py` | Expone `main` como punto de entrada del comando `recipe-assistant-ui`. |
| `main.py` | Define la interfaz de Gradio (`gr.ChatInterface`), el manejo del chat con streaming, la identificación de ingredientes por imagen y el manejo de errores. |
| `agent.py` | Define el agente de PydanticAI, el modelo, sus instrucciones y las instrucciones dinámicas (temporada, dieta e ingredientes). |
| `models.py` | Modelo `Recipe` (Pydantic) con la validación de la receta generada. |
| `deps.py` | Dependencias (`RecipeDeps`) con los ingredientes disponibles y la preferencia alimenticia que se inyectan al agente. |
| `evals.py` | Evaluaciones del asistente con `pydantic-evals`. |

## Uso

Requiere Python 3.14 o superior y [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run recipe-assistant-ui   # lanza la interfaz web de Gradio
```

Gradio muestra en la terminal la URL local (por defecto `http://127.0.0.1:7860`).

## Configuración de variables de entorno

El proyecto lee sus credenciales desde un archivo `.env` (cargado con `python-dotenv` en `agent.py`). Este archivo contiene secretos y **no se sube al repositorio** (está en `.gitignore`).

Crea un archivo `.env` en la raíz del proyecto con estas variables:

| Variable | Obligatoria | Descripción |
|---|---|---|
| `ANTHROPIC_API_KEY` | Sí | Clave de API de Anthropic, necesaria para el modelo del agente (`claude-haiku-4-5`). Se obtiene en la [consola de Anthropic](https://console.anthropic.com/). |
| `GOOGLE_API_KEY` | No | Clave de API de Google Gemini, solo si cambias el modelo del agente a uno de Gemini. Se obtiene en [Google AI Studio](https://aistudio.google.com/apikey). |

## Contenido del curso

### 1. Introducción a Gradio
- Gradio para proyectos de IA en Python
- Creando un asistente de recetas con IA

**En el proyecto:** el punto de partida del asistente de recetas, un agente de cocina (`agent.py`) que se mostrará en una interfaz web.

### 2. Interfaces con Gradio
- Instalación y configuración de un proyecto con Gradio y Python
- Creando una interfaz web con Gradio
- Componentes básicos con Gradio

**En el proyecto:** `pyproject.toml` con la dependencia `gradio` y el comando `recipe-assistant-ui`, y `main()` en `main.py`, que lanza la interfaz con `interface.launch()`.

### 3. Componentes avanzados con Gradio
- Layouts y organización de interfaces con Gradio
- Eventos e interactividad con Gradio
- Carga y procesamiento de imágenes con Gradio

**En el proyecto:** la versión con `gr.Blocks`, `gr.Row` y `gr.Column` (comentada en `main()`), con eventos `submit`, `click` y `upload`, y el componente `gr.Image` para subir la foto de los ingredientes (convertida a bytes con `image_to_bytes`).

### 4. Integrando un LLM a la interfaz de Gradio
- Agentes de identificación de imágenes con Gradio
- Respuestas en streaming con Gradio
- Parámetros configurables con Gradio

**En el proyecto:** `indentify_ingredients` envía la imagen al agente como `BinaryContent`; `ask_recipe_stream` usa `run_stream` para mostrar la respuesta mientras se genera; y el `gr.Dropdown` de preferencia alimenticia se pasa al agente mediante `RecipeDeps.diet` y la instrucción dinámica `add_diet_preference`.

### 5. Creando un chatbot con Gradio
- Interfaz de Gradio para la integración de chats
- Conectando la imagen al chat
- Historia y contexto de la conversación

**En el proyecto:** `gr.ChatInterface` con `handle_chat_message`, que recibe la imagen como entrada adicional e identifica los ingredientes antes de responder. El historial se conserva con `gr.State` y `message_history` de PydanticAI, devolviendo `result.all_messages()` en cada turno.

### 6. Personalización y cierre del proyecto
- Temas y estilos personalizados con Gradio
- Manejo de errores y mejoras finales con Gradio

**En el proyecto:** el tema `gr.themes.Soft` con tonos naranja y ámbar en `interface.launch()`, y el manejo de errores con `gr.Error` para mensajes vacíos y fallos al generar la respuesta.

## Autor

[Ana Maria Pinto](https://www.linkedin.com/in/ana-maria-pinto-v/)
