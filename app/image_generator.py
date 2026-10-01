"""Stable Diffusion image generation via Hugging Face Diffusers."""
import re
import uuid

from app.config import HF_API_KEY, PANELS_DIR, SD_MODEL_ID

_pipe = None


def _get_pipe():
    """Load the Stable Diffusion pipeline once, on first use."""
    global _pipe
    if _pipe is None:
        import torch
        from diffusers import StableDiffusionPipeline

        use_cuda = torch.cuda.is_available()
        _pipe = StableDiffusionPipeline.from_pretrained(
            SD_MODEL_ID,
            torch_dtype=torch.float16 if use_cuda else torch.float32,
            token=HF_API_KEY or None,
        )
        _pipe = _pipe.to("cuda" if use_cuda else "cpu")
        _pipe.enable_attention_slicing()
    return _pipe


def sanitize_filename(prompt: str) -> str:
    """Turn a prompt into a safe, unique .png filename."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", prompt).strip("_")[:40] or "panel"
    return f"{slug}_{uuid.uuid4().hex[:8]}.png"


def generate_image(prompt: str, filename: str = None) -> str:
    """
    Generates a comic-style image with Stable Diffusion and saves it to
    static/panels. Returns the absolute file path of the saved image.
    """
    if not filename:
        filename = sanitize_filename(prompt)

    # CLIP (Stable Diffusion's text encoder) only reads ~77 tokens; keep it short.
    image = _get_pipe()(prompt[:300]).images[0]
    PANELS_DIR.mkdir(parents=True, exist_ok=True)
    path = PANELS_DIR / filename
    image.save(path)
    return str(path)
