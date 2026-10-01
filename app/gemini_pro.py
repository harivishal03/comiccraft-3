"""Gemini Pro: detailed narration and dialogue for each panel."""
import google.generativeai as genai

from app.config import GEMINI_API_KEY, GEMINI_PRO_MODEL

_model = None


def _get_model():
    global _model
    if _model is None:
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel(GEMINI_PRO_MODEL)
    return _model


def generate_story(outline: list, tone: str = "") -> str:
    """
    Generates a detailed comic story with narration and character dialogue
    from a list of comic panel outlines using Gemini Pro.

    Args:
        outline (list): Panel dictionaries (panel, title, scene_description, ...).
        tone (str): Optional story tone (e.g. "funny", "dramatic").

    Returns:
        str: The generated comic story text or an error message.
    """
    formatted_outline = "\n".join(
        f"{i + 1}. {item.get('title', '')}: {item.get('scene_description', '')}"
        if isinstance(item, dict)
        else f"{i + 1}. {item}"
        for i, item in enumerate(outline)
    )
    tone_line = f"- The overall tone must be: {tone}." if tone else ""

    prompt = f"""
You're a comic book writer.

Given the following panel breakdown, write a comic-style story with engaging narration and character dialogues for each panel.

Panel Outline:
{formatted_outline}

Guidelines:
- Use a fun and engaging tone, like an actual comic book.
{tone_line}
- Include narration and clearly marked character lines.
- Keep each panel self-contained but part of a cohesive story.
- Start every panel with a heading line in EXACTLY this format: **Panel N: Title**
- Under each heading write a **CAPTION:** line, a **NARRATION:** line and, where it fits, a **DIALOGUE:** line.
- Do not add any introduction or conclusion outside the panels.
"""
    try:
        response = _get_model().generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating story: {str(e)}"
