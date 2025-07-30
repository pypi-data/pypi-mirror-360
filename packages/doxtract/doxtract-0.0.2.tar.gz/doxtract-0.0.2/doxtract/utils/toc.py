from __future__ import annotations

import re
from typing import List

from tqdm import tqdm
import fitz  # type: ignore

__all__ = [
    "is_probable_toc_page",
    "is_probable_toc_line",
    "detect_toc_candidates",
    "filter_page_sequence",
]


# ──────────────────────────────────────────────────────────────────────────
# ToC heuristics
# ──────────────────────────────────────────────────────────────────────────

def is_probable_toc_page(text: str, *, threshold: int = 3) -> bool:
    lines = text.splitlines()
    dot_leader = multi_section = chapter = dotted_num = 0

    for line in lines:
        if re.search(r"\.{3,}.*(?:\b\d{1,4}\b|\b[ivxlcdm]+\b)$", line, re.I):
            dot_leader += 1
        if re.match(r"^\d+(?:\.\d+)+(\s|$)", line):
            multi_section += 1
        if re.search(r"\b(chapter|appendix)\b", line, re.I):
            chapter += 1
        if re.match(r".+\.{2,}\s*\d{1,4}$", line.strip()):
            dotted_num += 1

    score = (
        (dot_leader >= threshold)
        + (multi_section >= threshold)
        + (chapter >= threshold)
        + (dotted_num >= threshold)
    )
    return score >= 2


def is_probable_toc_line(line: str) -> bool:
    line = line.strip()
    return (
        re.search(r"\.{3,}.*(?:\b\d{1,4}\b|\b[ivxlcdm]+\b)$", line, re.I)
        or re.match(r"^\d+(?:\.\d+)+(\s|$)", line)
        or re.search(r"\b(chapter|appendix)\b", line, re.I)
        or re.match(r".+\.{2,}\s*\d{1,4}$", line.strip())
    )


def detect_toc_candidates(doc: fitz.Document, *, threshold: int = 3, verbose: bool = False):
    toc_pages: List[int] = []
    previous_is_toc = False

    for page in tqdm(doc, desc="Scanning pages for ToC", disable=not verbose):
        page_number = page.number + 1
        text = page.get_text()

        is_toc = is_probable_toc_page(text, threshold=threshold)

        if not is_toc and previous_is_toc:
            first_lines = text.splitlines()[:6]
            if any(is_probable_toc_line(ln) for ln in first_lines):
                is_toc = True

        if is_toc:
            toc_pages.append(page_number)
            previous_is_toc = True
        else:
            previous_is_toc = False

    return toc_pages


def filter_page_sequence(pages: List[int], max_gap: int = 5):
    filtered: List[int] = []
    for i, pg in enumerate(pages):
        if not filtered:
            filtered.append(pg)
            continue

        gap = pg - filtered[-1]
        if gap <= max_gap:
            filtered.append(pg)
            continue

        look_ahead = pages[i + 1 : i + 4]
        expected = [pg + n for n in range(1, len(look_ahead) + 1)]

        if look_ahead == expected:
            filtered.append(pg)
            continue
        else:
            break
    return filtered
