"""Export the comic layout as a multi-page PDF using FPDF."""
import os
import re
from datetime import datetime

from fpdf import FPDF

from app.config import EXPORTS_DIR, FONT_PATH


def _clean(text: str) -> str:
    """Strip markdown bold markers for the PDF."""
    return re.sub(r"\*\*|__", "", text or "").strip()


def save_pdf(layout):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Unicode font (bundled in static/fonts)
    pdf.add_font("DejaVu", "", str(FONT_PATH), uni=True)
    pdf.set_font("DejaVu", "", 12)

    for panel in layout:
        image_path = panel["image_path"]
        story_text = _clean(panel["text"])

        pdf.add_page()

        # Panel title
        pdf.set_font("DejaVu", "", 14)
        pdf.cell(0, 10, f"Panel {panel['panel']}: {panel['title']}", ln=True, align="C")
        pdf.set_font("DejaVu", "", 12)

        # Image placement (square, centered)
        y_image = 30
        image_size = 100
        spacing_after_image = 15

        if os.path.exists(image_path):
            pdf.image(image_path, x=(pdf.w - image_size) / 2, y=y_image,
                      w=image_size, h=image_size)
        else:
            pdf.set_y(y_image)
            pdf.multi_cell(0, 10, f"Image missing: {image_path}")

        # Scene description (smaller), then narration below the image
        pdf.set_y(y_image + image_size + spacing_after_image)
        if panel.get("scene_description"):
            pdf.set_font("DejaVu", "", 10)
            pdf.multi_cell(0, 6, _clean(panel["scene_description"]))
            pdf.ln(3)
            pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 8, story_text)

    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    pdf_path = os.path.join(str(EXPORTS_DIR), filename)
    pdf.output(pdf_path)

    return pdf_path
