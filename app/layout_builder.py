"""Combine panel outline, images and story text into a single layout."""
import re
from pathlib import PurePath

_PANEL_HEADING = re.compile(r"^\s*\**\s*Panel\s*\d+\b[^\n]*$", re.IGNORECASE | re.MULTILINE)


def _split_story(full_story: str) -> list:
    """Split the story into one text block per panel (heading line removed)."""
    matches = list(_PANEL_HEADING.finditer(full_story))
    if not matches:
        return [full_story.strip()] if full_story.strip() else []
    blocks = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_story)
        blocks.append(full_story[m.end():end].strip())
    return blocks


def build_comic_layout(image_paths, full_story, outline):
    """
    Returns a list of dicts: panel number, title, image_path (filesystem),
    image_url (web path), text and scene_description.
    """
    story_panels = _split_story(full_story)
    layout = []
    for idx, (image, panel_info) in enumerate(zip(image_paths, outline), start=1):
        text = story_panels[idx - 1] if idx - 1 < len(story_panels) else ""
        layout.append({
            "panel": idx,
            "title": panel_info.get("title", f"Panel {idx}"),
            "image_path": image,
            "image_url": "/static/panels/" + PurePath(image).name,
            "text": text,
            "scene_description": panel_info.get("scene_description", ""),
        })
    return layout
