from __future__ import annotations

from functools import reduce
from typing import List

import fitz  # type: ignore

from .geometry import is_degenerate, _group_vectors, _build_rect_groups

__all__ = [
    "_is_valid_vector",
    "get_visible_image_xrefs",
    "is_full_page_image",
    "_detect_diagrams",
]


def _is_valid_vector(d):
    rect = d.get("rect")
    if not rect:
        return False
    if rect.width < 1 and rect.height < 1:
        return False
    if d.get("type") not in {"s", "fs"}:
        return False
    return True


def get_visible_image_xrefs(page: fitz.Page):
    visible_xrefs = set()
    page_rect = page.rect
    for img in page.get_images(full=True):
        xref = img[0]
        name = img[7]
        try:
            bbox = page.get_image_bbox(name)
            if bbox is not None and bbox.intersects(page_rect):
                pix = fitz.Pixmap(page.parent, xref)
                if pix.width < page.rect.width - 5 or pix.height < page.rect.height - 5:
                    visible_xrefs.add(xref)
        except Exception:
            continue
    return visible_xrefs


def is_full_page_image(page: fitz.Page):
    page_width, page_height = page.rect.width, page.rect.height
    for img in page.get_images(full=True):
        xref = img[0]
        try:
            pix = fitz.Pixmap(page.parent, xref)
            if pix.width >= page_width - 5 and pix.height >= page_height - 5:
                return True
        except Exception:
            continue
    return False


def _detect_diagrams(page: fitz.Page):
    drawings = page.get_drawings()
    rects = [d["rect"] for d in drawings if _is_valid_vector(d)]
    if len(rects) < 3:
        return []
    groups = _group_vectors(rects)
    has_d = any(d.get("dashes") for d in drawings if _is_valid_vector(d))
    flat = sum(1 for r in rects if r.width < 2 or r.height < 2) / len(rects)
    score = int(has_d) + int(flat < 0.6) + int(len(groups) >= 2)
    if score < 2:
        return []
    raw: List[fitz.Rect] = [reduce(lambda a, b: a | b, g) for g in groups if not is_degenerate(reduce(lambda a, b: a | b, g))]
    return [reduce(lambda a, b: a | b, c) for c in _build_rect_groups(raw, 0.05, 25)]
