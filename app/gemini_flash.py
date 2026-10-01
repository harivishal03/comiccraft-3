"""Gemini Flash: fast, structured 5-panel comic outline."""
import json

import google.generativeai as genai

from app.config import GEMINI_API_KEY, GEMINI_FLASH_MODEL

_model = None


def _get_model():
    """Create the model lazily so the app can start without an API key."""
    global _model
    if _model is None:
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel(GEMINI_FLASH_MODEL)
    return _model


def generate_outline(user_prompt: str) -> list:
    """
    Generates a 5-panel comic layout based on the user's story idea using Gemini.

    Args:
        user_prompt (str): The user's comic idea prompt (includes character,
            setting, tone and art style).

    Returns:
        list: A list of dictionaries, one for each panel. On failure, a list with
        a single {"error": "..."} dictionary.
    """
    prompt = f"""
You are a professional AI comic planner.

Your task is to generate a *strictly formatted* JSON array containing 5 panel descriptions for a comic based on the story idea below:

STORY: "{user_prompt}"

Each JSON object must include:
- "panel" (integer)
- "title" (string)
- "scene_description" (string)
- "image_prompt" (string) - a vivid prompt for Stable Diffusion that mentions the art style and keeps the main character looking consistent

Respond ONLY in this valid JSON format, without any explanations or markdown:
[
  {{
    "panel": 1,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Image prompt for Stable Diffusion"
  }},
  ...
]
"""
    output_text = ""
    try:
        model = _get_model()
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
        )
        output_text = response.text.strip()
        print("\n🔥 RAW GEMINI RESPONSE 🔥\n", output_text)

        # Remove any markdown formatting if present
        if output_text.startswith("```"):
            output_text = (
                output_text.replace("```json", "").replace("```", "").strip()
            )

        panel_data = json.loads(output_text)

        # Additional structure validation
        if not isinstance(panel_data, list):
            raise ValueError("Gemini response is not a list.")

        required = ("panel", "title", "scene_description", "image_prompt")
        for panel in panel_data:
            if not isinstance(panel, dict) or not all(k in panel for k in required):
                raise ValueError(f"Invalid panel format or missing keys: {panel}")

        return panel_data

    except json.JSONDecodeError as e:
        print("❌ JSON Decode Error:", e)
        print("❌ Full Text Received:\n", output_text)
        return [{"error": f"JSON parsing failed: {str(e)}"}]

    except Exception as e:
        print("❌ Unexpected Error:", e)
        return [{"error": f"Generation failed: {str(e)}"}]
