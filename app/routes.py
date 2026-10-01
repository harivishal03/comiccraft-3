"""All FastAPI routes for ComicCraft."""
import re
import traceback
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from markupsafe import Markup, escape
from pydantic import BaseModel

from app.config import EXPORTS_DIR, TEMPLATES_DIR
from app.exporters import save_pdf
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _md_bold(text: str) -> Markup:
    """Escape text, then turn **bold** into <strong> and keep line breaks."""
    safe = str(escape(text or ""))
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    return Markup(safe.replace("\n", "<br>"))


templates.env.filters["md"] = _md_bold

STYLE_HINTS = {
    "anime": "anime style, vibrant colors, clean line art",
    "pixel art": "pixel art, 16-bit retro game style",
    "comic book": "classic comic book style, bold ink outlines, halftone shading",
    "realistic": "realistic digital painting, detailed, cinematic lighting",
}


class PromptRequest(BaseModel):
    prompt: str
    character_name: str = "Hero"
    setting: str = "forest"
    tone: str = "dramatic"
    style: str = "comic book"


def run_pipeline(prompt: str, character_name: str, setting: str, tone: str, style: str):
    """Outline -> story -> images -> layout -> PDF. Returns (layout, pdf_path)."""
    # Combine user input into a single full prompt
    full_prompt = (
        f"{prompt}\n"
        f"The main character is {character_name}. "
        f"The setting is a {setting}. "
        f"The tone is {tone}. The art style is {style}."
    )

    # Step 1: panel outline (Gemini Flash)
    outline = generate_outline(full_prompt)
    if not isinstance(outline, list) or not outline:
        raise ValueError("Invalid outline structure from Gemini response.")
    if "error" in outline[0]:
        raise ValueError(outline[0]["error"])
    if not all("image_prompt" in panel for panel in outline):
        raise ValueError("Invalid outline structure from Gemini response.")

    # Step 2: narration + dialogue (Gemini Pro)
    full_story = generate_story(outline, tone)
    if full_story.startswith("Error generating story"):
        raise ValueError(full_story)

    # Step 3: images (Stable Diffusion), nudged toward the chosen art style
    hint = STYLE_HINTS.get(style.lower(), style)
    images = [generate_image(f"{panel['image_prompt']}, {hint}") for panel in outline]

    # Step 4: layout
    layout = build_comic_layout(images, full_story, outline)

    # Step 5: PDF
    pdf_path = save_pdf(layout)
    return layout, pdf_path


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@router.post("/generate", response_class=HTMLResponse)
def generate_comic(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    style: str = Form(...),
):
    try:
        layout, pdf_path = run_pipeline(prompt, character_name, setting, tone, style)
        return templates.TemplateResponse(
            request,
            "comic_preview.html",
            {"layout": layout, "pdf_filename": Path(pdf_path).name},
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-comic/json")
def generate_comic_json(data: PromptRequest):
    try:
        layout, pdf_path = run_pipeline(
            data.prompt, data.character_name, data.setting, data.tone, data.style
        )
        return {
            "layout": layout,
            "pdf_path": "/static/exports/" + Path(pdf_path).name,
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
def download_pdf(filename: str):
    safe_name = Path(filename).name  # blocks path traversal
    file_path = EXPORTS_DIR / safe_name
    if not file_path.is_file() or file_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(file_path, media_type="application/pdf", filename=safe_name)


@router.get("/export-success", response_class=HTMLResponse)
def export_success(request: Request, pdf_path: str = ""):
    return templates.TemplateResponse(
        request, "export_success.html", {"pdf_path": Path(pdf_path).name}
    )


@router.get("/test-image")
def test_image(
    prompt: str = "A futuristic city at sunset, sci-fi, cinematic, artstation",
):
    try:
        image_path = generate_image(prompt)
        return {
            "message": "Image generated successfully",
            "path": "/static/panels/" + Path(image_path).name,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
