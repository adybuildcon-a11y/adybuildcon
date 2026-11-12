"""Geometry engine: book order, fold derivation, panel sizes and swatch grids (all in inches)."""

import math
from data import BOOKS, LADDER, LEVEL, P


# ---------------------------------------------------------------- order
def ordered_books():
    """Light control (open -> closed); within a level by weight (GSM, light -> heavy);
    unknown GSM after known, alphabetical. Gives every book its sequence number."""
    bs = sorted(BOOKS, key=lambda b: (LEVEL[b["cat"]], b["gsm"] is None, b["gsm"] or 0, b["name"]))
    for i, b in enumerate(bs, 1):
        b["seq"] = i
    return bs


def boards():
    """Group books into physical boards (Eeco Dimout + Double Shade share one)."""
    out, seen = [], {}
    for b in ordered_books():
        key = b.get("board", b["id"])
        if key in seen:
            seen[key]["books"].append(b)
            continue
        bd = dict(id=key, books=[b])
        seen[key] = bd
        out.append(bd)
    for i, bd in enumerate(out, 1):
        bd["no"] = i
        derive(bd)
    return out


# ---------------------------------------------------------------- folds & panels
def swatch_groups(b):
    if b.get("groups"):
        return [(t, list(s)) for t, s in b["groups"]]
    if b["others"] is None or b["shades"] is None:
        return None
    others, cap = list(b["others"]), P["cap_per_panel"]
    if not others:
        return []
    n = math.ceil(len(others) / cap)
    size = math.ceil(len(others) / n)
    return [(None, others[i * size:(i + 1) * size]) for i in range(n)]


def effective(b):
    """Book values used for the inside layout: confirmed notes, or a clearly flagged draft."""
    if b["status"] != "Confirmed" and b.get("draft"):
        e = dict(b)
        e.update(shades=b["draft"]["shades"], mains=b["draft"]["mains"], others=b["draft"]["others"], is_draft=True)
        return e
    return b


def derive(bd):
    books = [effective(b) for b in bd["books"]]
    bd["eff"], bd["draft"] = books[0], any(b.get("is_draft") for b in books)
    if len(books) > 1:                                   # shared board: one panel per book
        bd["fold"], bd["fold_src"] = len(books), bd["books"][0]["fold_src"]
        if all(b["shades"] for b in books):
            bd["panels"] = [dict(kind="swatch", title=b["name"], book=b, letter="ABC"[i],
                                 shades=list(b["mains"]) + list(b["others"])) for i, b in enumerate(books)]
            bd["ready"] = True
        else:
            bd["panels"], bd["ready"] = [], False
        return
    b = books[0]
    groups = swatch_groups(b)
    if groups is None:                                   # count not known -> no inside layout yet
        bd["fold"] = b["fold"] or None
        bd["fold_src"] = b["fold_src"] if b["fold"] else "pending"
        bd["panels"], bd["ready"] = [], False
        return
    if b.get("mode") == "mixed":                         # different designs -> equal swatches, mains first
        allsw = list(b["mains"]) + [s for _, g in groups for s in g]
        fold = b["fold"] or max(2, math.ceil(len(allsw) / P["cap_per_panel"]))
        bd["fold"], bd["fold_src"] = fold, b["fold_src"] if b["fold"] else "derived"
        size = math.ceil(len(allsw) / fold)
        bd["panels"] = [dict(kind="swatch", title=None, shades=allsw[i * size:(i + 1) * size]) for i in range(fold)]
        bd["ready"] = b["status"] == "Confirmed" or b.get("is_draft", False)
        for pi, pn in enumerate(bd["panels"]):
            pn["letter"] = "ABC"[pi]
        return
    needed = (1 if b["mains"] else 0) + len(groups)
    fold = b["fold"] or max(2, needed)
    bd["fold"], bd["fold_src"] = fold, b["fold_src"] if b["fold"] else "derived"
    # redistribute plain swatch lists over the panels that are free
    free = fold - (1 if b["mains"] else 0)
    if not b.get("groups") and free != len(groups):
        others = [s for _, g in groups for s in g]
        size = math.ceil(len(others) / free)
        groups = [(None, others[i * size:(i + 1) * size]) for i in range(free)]
    sw = [dict(kind="swatch", title=t, shades=g) for t, g in groups]
    hero = [dict(kind="hero", shades=list(b["mains"]))] if b["mains"] else []
    bd["panels"] = (hero + sw) if fold == 2 else (sw + hero)       # 2-fold [hero|swatch]; 3-fold [sw|sw|hero]
    bd["ready"] = b["status"] == "Confirmed" or b.get("is_draft", False)
    # running swatch numbering for labels / Excel register
    letters = "ABC"
    for pi, pn in enumerate(bd["panels"]):
        pn["letter"] = letters[pi]


def panel_widths(fold):
    w = [P["board_w"]] * fold
    if fold == 3:
        w[2] -= P["roll_fold"]
    return w


def open_size(fold):
    return sum(panel_widths(fold)) + P["hinge"] * (fold - 1), P["board_h"]


def panel_x(fold, i):
    ws = panel_widths(fold)
    return sum(ws[:i]) + P["hinge"] * i


def content_box(fold, i):
    """Content box of inside panel i (board coordinates, inches)."""
    x0 = panel_x(fold, i)
    w = panel_widths(fold)[i]
    left = P["bind_margin"] if i == 0 else P["margin"]
    top = P["margin"] + P["header"]
    return (x0 + left, top, x0 + w - P["margin"], P["board_h"] - P["margin"] - P["footer"])


# ---------------------------------------------------------------- grid solver
def solve_grid(n, W, H, min_w=None, min_h=None, aspect=1.6, label=None, max_w=99, max_h=99):
    """Most legible grid for n swatches in W x H: largest swatch area, biased to a 1.6:1 landscape
    swatch (how fabric reads best), never below the minimum size."""
    min_w = P["min_sw_w"] if min_w is None else min_w
    min_h = P["min_sw_h"] if min_h is None else min_h
    label = P["label_h"] if label is None else label
    g, best = P["gutter"], None
    for cols in range(1, 7):
        rows = math.ceil(n / cols)
        sw = (W - g * (cols - 1)) / cols
        sh = (H - rows * label - g * (rows - 1)) / rows
        if sw < min_w or sh < min_h:
            continue
        sh = min(sh, sw * 1.25, max_h)                  # never taller than 1.25 x width
        sw = min(sw, max_w)
        score = sw * sh * math.exp(-abs(math.log((sw / sh) / aspect)))
        if best is None or score > best[0]:
            best = (score, cols, rows, sw, sh)
    if best is None:
        raise ValueError(f"{n} swatches do not fit {W:.2f} x {H:.2f} in")
    _, cols, rows, sw, sh = best
    return dict(cols=cols, rows=rows, w=sw, h=sh)


def place(n, box, grid=None, **kw):
    """Cell rectangles (x, y, w, h) centred in box; last row centred."""
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    gr = grid or solve_grid(n, W, H, **kw)
    g, lab = P["gutter"], kw.get("label", P["label_h"])
    cw, ch = gr["w"], gr["h"]
    total_h = gr["rows"] * (ch + lab) + (gr["rows"] - 1) * g
    y = y0 + (H - total_h) / 2
    cells = []
    for r in range(gr["rows"]):
        k = min(gr["cols"], n - r * gr["cols"])
        row_w = k * cw + (k - 1) * g
        x = x0 + (W - row_w) / 2
        for c in range(k):
            cells.append((x + c * (cw + g), y, cw, ch))
        y += ch + lab + g
    return gr, cells


HERO_SPEC_H = 2.75
SMALL_CUT = (2.5, 1.6)      # range books: other shades are small cuttings, max 2.5 x 1.6 in


def layout_board(bd):
    """Attach swatch cells to every inside panel of a ready board."""
    fold = bd["fold"]
    sw = [(i, pn) for i, pn in enumerate(bd["panels"]) if pn["kind"] == "swatch"]
    shared = None
    if sw:                                   # one grid for every swatch panel on the board
        boxes = [content_box(fold, i) for i, _ in sw]
        W = min(b[2] - b[0] for b in boxes); H = min(b[3] - b[1] for b in boxes)
        mixed = bd["books"][0].get("mode") == "mixed"
        kw = dict(aspect=1.15) if mixed else dict(max_w=SMALL_CUT[0], max_h=SMALL_CUT[1])
        shared = solve_grid(max(len(pn["shades"]) for _, pn in sw), W, H, **kw)
    for i, pn in enumerate(bd["panels"]):
        box = content_box(fold, i)
        if pn["kind"] == "swatch":
            pn["grid"], pn["cells"] = place(len(pn["shades"]), box, grid=shared)
        elif pn["kind"] == "hero":
            hb = (box[0], box[1], box[2], box[3] - HERO_SPEC_H)
            pn["grid"], pn["cells"] = place(len(pn["shades"]), hb, min_w=2.0, min_h=1.4, aspect=1.25, label=0.32)
            pn["spec_box"] = (box[0], box[3] - HERO_SPEC_H + 0.2, box[2], box[3])
    return bd


def thickness_mm(bd):
    f = bd["fold"] or 3
    return f * (P["board_mm"] + P["fabric_mm"])


def level_of(b):
    return LEVEL[b["cat"]]


def ladder_color(cat):
    return dict((k, c) for k, _, _, c in LADDER)[cat]
