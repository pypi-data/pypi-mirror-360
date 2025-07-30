from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

import fitz  # type: ignore
import re
from tqdm.notebook import tqdm

__all__ = ["normalize", "extract_headers_and_footers"]


def normalize(text: str, strip_digits: bool = False) -> str:
    t = text.strip().lower()
    if strip_digits:
        t = re.sub(r"\d+", "", t)
    return re.sub(r"\s+", " ", t)


def extract_headers_and_footers(
    doc: fitz.Document,
    *,
    top_pct: float = 0.12,
    bottom_pct: float = 0.12,
    min_pages: int = 3,
    verbose: bool = False,
):
    """Detect repeating header/footer texts and return rect maps."""

    page_h = doc[0].rect.height
    head_band = page_h * top_pct
    foot_band = page_h * (1 - bottom_pct)

    hdr_pages: Dict[str, set[int]] = defaultdict(set)
    ftr_pages: Dict[str, set[int]] = defaultdict(set)
    hdr_blocks: Dict[str, Dict[int, List[fitz.Rect]]] = defaultdict(lambda: defaultdict(list))
    ftr_blocks: Dict[str, Dict[int, List[fitz.Rect]]] = defaultdict(lambda: defaultdict(list))

    for pno, page in enumerate(tqdm(doc, desc="Scanning Headers/Footers", disable=not verbose), 1):
        for x0, y0, x1, y1, text, *_ in page.get_text("blocks"):
            txt = text.strip()
            if not txt:
                continue
            rect = fitz.Rect(x0, y0, x1, y1)

            if y0 <= head_band:
                norm = normalize(txt, strip_digits=False)
                hdr_pages[norm].add(pno)
                hdr_blocks[norm][pno].append(rect)
            elif y1 >= foot_band:
                norm = normalize(txt, strip_digits=True)
                ftr_pages[norm].add(pno)
                ftr_blocks[norm][pno].append(rect)

    good_hdr = {n for n, pgset in hdr_pages.items() if len(pgset) >= min_pages}
    good_ftr = {n for n, pgset in ftr_pages.items() if len(pgset) >= min_pages}

    page_hdr_rects: Dict[int, List[fitz.Rect]] = defaultdict(list)
    page_ftr_rects: Dict[int, List[fitz.Rect]] = defaultdict(list)

    for n in good_hdr:
        for p, rects in hdr_blocks[n].items():
            page_hdr_rects[p].extend(rects)
    for n in good_ftr:
        for p, rects in ftr_blocks[n].items():
            page_ftr_rects[p].extend(rects)

    return {
        "page_header_rects": page_hdr_rects,
        "page_footer_rects": page_ftr_rects,
    }
