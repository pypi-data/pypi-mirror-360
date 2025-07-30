from __future__ import annotations

import fitz  # type: ignore
from collections import defaultdict, Counter
import re
from typing import List

from .headers import normalize  # reuse

__all__ = [
    "classify_span",
    "extract_text_skip_rects",
    "extract_markdown_layout",
    "sanitize",
]


def classify_span(span):
    fname = span["font"].lower()
    size = span["size"]
    bold = "bold" in fname or "black" in fname
    italic = "italic" in fname or "oblique" in fname
    return size, bold, italic


def extract_text_skip_rects(page: fitz.Page, skip_rects, *, y_tol: int = 2, space_thresh: int = 5) -> List[str]:
    lines = defaultdict(list)
    min_x = float("inf")

    td = page.get_text("dict")
    for blk in td["blocks"]:
        for ln in blk.get("lines", []):
            for sp in ln.get("spans", []):
                if not sp["text"].strip():
                    continue
                srect = fitz.Rect(sp["bbox"])
                if any(srect in r for r in skip_rects):
                    continue
                x0 = srect.x0
                yk = round(srect.y0 / y_tol) * y_tol
                lines[yk].append((x0, sp["text"].strip()))
                min_x = min(min_x, x0)

    out: List[str] = []
    for y in sorted(lines):
        parts = sorted(lines[y], key=lambda t: t[0])
        if not parts:
            continue
        first_x = parts[0][0]
        indent = int((first_x - min_x) / space_thresh)
        line = " " * max(0, indent)
        last_x = first_x
        for x, txt in parts:
            gap = int((x - last_x) / space_thresh)
            line += " " * max(1, gap) + txt
            last_x = x + len(txt) * 2
        out.append(line.rstrip())
    return out


def extract_markdown_layout(page: fitz.Page, skip_rects, *, y_tol: int = 2, space_thresh: int = 5, gap_multiplier: float = 1.2) -> List[str]:
    lines_by_y = defaultdict(list)
    min_x = float("inf")
    spans = []

    td = page.get_text("dict")
    for blk in td["blocks"]:
        for ln in blk.get("lines", []):
            for sp in ln.get("spans", []):
                if not sp["text"].strip():
                    continue
                srect = fitz.Rect(sp["bbox"])
                if any(srect in r for r in skip_rects):
                    continue
                x0 = srect.x0
                ykey = round(srect.y0 / y_tol) * y_tol
                lines_by_y[ykey].append((x0, sp))
                spans.append(sp)
                min_x = min(min_x, x0)

    if not spans:
        return []

    body_size = Counter(round(s["size"]) for s in spans).most_common(1)[0][0]

    sorted_ys = sorted(lines_by_y)
    y_gaps = [b - a for a, b in zip(sorted_ys, sorted_ys[1:])]
    para_gap = (sum(y_gaps) / len(y_gaps)) * gap_multiplier if y_gaps else 10

    md_lines, prev_y = [], None
    for y in sorted_ys:
        parts = sorted(lines_by_y[y], key=lambda t: t[0])
        if not parts:
            continue
        if prev_y is not None and (y - prev_y) > para_gap:
            md_lines.append("")
        prev_y = y

        max_size = max(sp["size"] for _, sp in parts)
        if max_size >= body_size + 6:
            heading = "# "
        elif max_size >= body_size + 3:
            heading = "## "
        elif max_size >= body_size + 2:
            heading = "### "
        else:
            heading = ""

        first_x = parts[0][0]
        indent = "" if heading else " " * int((first_x - min_x) / space_thresh)
        line = heading + indent
        last_x = first_x

        for x0, sp in parts:
            gap = int((x0 - last_x) / space_thresh)
            if line and not line.endswith(" "):
                line += " " * max(1, gap)

            size, bold, italic = classify_span(sp)
            text = sp["text"].strip()

            if re.match(r'^[-•*]\s', text):
                text = f"- {text[2:].strip()}"

            if bold and italic:
                text = f"***{text}***"
            elif bold:
                text = f"**{text}**"
            elif italic:
                text = f"*{text}*"

            line += text
            last_x = x0 + len(text) * 2

        md_lines.append(line.rstrip())
    return md_lines


def sanitize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())
