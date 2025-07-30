from __future__ import annotations

from typing import List
from collections import defaultdict, deque

import fitz  # type: ignore

__all__ = [
    "rect_area",
    "is_degenerate",
    "expand_rect",
    "_group_vectors",
    "_build_rect_groups",
]


def rect_area(r: fitz.Rect) -> float:
    """Return area in square points, clamped ≥0."""
    return max(0.0, (r.x1 - r.x0) * (r.y1 - r.y0))


def is_degenerate(r: fitz.Rect, min_len: float = 1.0) -> bool:
    """True if *r* is basically a line or point."""
    return (r.x1 - r.x0) < min_len or (r.y1 - r.y0) < min_len


def expand_rect(r: fitz.Rect, margin: int = 20) -> fitz.Rect:
    """Return a rectangle enlarged by *margin* in all directions (asym‑scale)."""
    return fitz.Rect(r.x0 - 5 * margin, r.y0 - 2.5 * margin, r.x1 + 5 * margin, r.y1 + 2.5 * margin)


# ╭──────────────────────────────────────────────────────────────────────╮
# │ Vector‑diagram grouping helpers                                     │
# ╰──────────────────────────────────────────────────────────────────────╯

def _group_vectors(rects: List[fitz.Rect], y_thresh: int = 50):
    """Cluster *rects* based on vertical proximity."""
    rects = sorted(rects, key=lambda r: r.y0)
    groups: List[List[fitz.Rect]] = []
    current: List[fitz.Rect] = [rects[0]] if rects else []

    for r in rects[1:]:
        if abs(r.y0 - current[-1].y1) <= y_thresh:
            current.append(r)
        else:
            groups.append(current)
            current = [r]
    if current:
        groups.append(current)
    return groups


def _build_rect_groups(bboxes: List[fitz.Rect], iou_thresh: float = 0.1, prox: int = 25):
    """Connected‑component grouping using IoU or proximity."""

    def connected(a: fitz.Rect, b: fitz.Rect):
        inter = a & b
        union = a | b
        u_area = rect_area(union)
        iou = rect_area(inter) / u_area if u_area else 1.0
        near = (
            a.x1 >= b.x0 - prox and a.x0 <= b.x1 + prox and a.y1 >= b.y0 - prox and a.y0 <= b.y1 + prox
        )
        return iou > iou_thresh or near

    adj: defaultdict[int, List[int]] = defaultdict(list)
    for i in range(len(bboxes)):
        for j in range(i + 1, len(bboxes)):
            if connected(bboxes[i], bboxes[j]):
                adj[i].append(j)
                adj[j].append(i)

    visited: set[int] = set()
    groups: List[List[fitz.Rect]] = []
    for i in range(len(bboxes)):
        if i in visited:
            continue
        q, comp = deque([i]), []
        while q:
            idx = q.popleft()
            if idx in visited:
                continue
            visited.add(idx)
            comp.append(bboxes[idx])
            q.extend(adj[idx])
        groups.append(comp)
    return groups
