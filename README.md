# ComicCraft - AI Comic Story Creator

FastAPI web app that turns a story idea into a 5-panel comic:
Gemini Flash (outline) -> Gemini Pro (narration/dialogue) -> Stable Diffusion (panel images) -> PDF export (FPDF).

## Setup

```bash
python -m venv env
# Windows
env\Scripts\activate
# macOS / Linux
source env/bin/activate

pip install -r requirements.txt
cp .env.example .env      # Windows: copy .env.example .env
# then edit .env and add GEMINI_API_KEY (and HF_API_KEY if needed)
```

## Run

```bash
uvicorn app.main:app --reload
```

- App: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

## Routes

| Route | Purpose |
|---|---|
| `GET /` | Input form |
| `POST /generate` | Form submit -> comic preview page |
| `POST /generate-comic/json` | JSON API -> layout data + PDF path |
| `GET /download/{filename}` | Download exported PDF |
| `GET /export-success` | Export confirmation page |
| `GET /test-image` | Test Stable Diffusion with a prompt |

Example JSON call:

```bash
curl -X POST http://127.0.0.1:8000/generate-comic/json \
  -H "Content-Type: application/json" \
  -d '{"prompt":"A brave fox exploring an enchanted forest","character_name":"Finn","setting":"forest","tone":"funny","style":"comic book"}'
```

## Notes

- The first image request downloads Stable Diffusion (~4 GB). A GPU is strongly
  recommended; on CPU each panel can take minutes.
- Model names are set in `.env`. The PDF names `gemini-1.5-*` and
  `runwayml/stable-diffusion-v1-5`, but those have been retired/removed, so the
  defaults here are newer equivalents. Change them if needed.
- Generated images go to `static/panels/`, PDFs to `static/exports/`.
