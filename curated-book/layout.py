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
    """Group books into physical boards (Stand A: Neo Crest + Glory Cotton + Eeco Dimout share one 3-fold board)."""
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
        bd["round"] = min(b["round"] for b in bd["books"])
        bd["stand"] = "A" if bd["id"] == "stand-a" else None
        derive(bd)
    return out


def board_name(bd):
    names = [b["name"] for b in bd["books"]]
    if len(names) > 2:
        return f"Stand {bd['stand']}: " + ", ".join(names[:-1]) + " & " + names[-1]
    return " & ".join(names)


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
            bd["panels"] = [dict(kind="swatch", title=b["name"], book=b, letter="ABC"[i], mains=[m for m in b["mains"]],
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
    if b.get("mode") == "mixed":                         # different designs -> equal swatches; mains -> waterfall
        others = [s for _, g in groups for s in g]
        hero = 1 if b["mains"] else 0
        fold = b["fold"] or max(2, hero + math.ceil(len(others) / P["cap_per_panel"]))
        bd["fold"], bd["fold_src"] = fold, b["fold_src"] if b["fold"] else "derived"
        free = fold - hero
        size = math.ceil(len(others) / free) if others else 0
        sw = [dict(kind="swatch", title=None, shades=others[i * size:(i + 1) * size]) for i in range(free)]
        hp = [dict(kind="hero", shades=list(b["mains"]))] if hero else []
        bd["panels"] = (hp + sw) if fold == 2 else (sw + hp)
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


HERO_SPEC_H = 2.75          # spec block under a single main
HERO_SPEC_COMPACT = 1.45    # spec block when several mains need the height
WF_LABEL = 0.62             # label column left of the waterfall
WF_MAX_STEP = 0.6           # largest step between stacked mains (in)


def hero_spec_h(n):
    return HERO_SPEC_H if n <= 1 else HERO_SPEC_COMPACT


def main_size(b):
    return b.get("main_size") or (P["main_w"], P["main_h"])


def waterfall(n, box, size=None):
    """Main fabrics as a waterfall of ready-cut 5 x 7 in pieces (HW-p8): each piece is stepped down
    and to the right of the one before, so every main shows an edge and the last one shows whole."""
    x0, y0, x1, y1 = box
    W, H = x1 - x0 - WF_LABEL, y1 - y0
    sw_, sh_ = size or (P["main_w"], P["main_h"])
    mw, mh = min(sw_, W), min(sh_, H)
    dx = min(WF_MAX_STEP, (W - mw) / (n - 1)) if n > 1 else 0
    dy = min(WF_MAX_STEP, (H - mh) / (n - 1)) if n > 1 else 0
    cells = [(x0 + WF_LABEL + i * dx, y0 + i * dy, mw, mh) for i in range(n)]
    return dict(cols=1, rows=n, w=mw, h=mh, band=max(dx, dy), dx=dx, dy=dy, waterfall=True), cells


CUT_SIZES = [(2.5, 1.6), (2.2, 1.4), (2.0, 1.25), (1.8, 1.1), (1.6, 1.0), (1.4, .9), (1.25, .8), (1.1, .7), (1.0, .6)]


def stand_cells(n_main, n_other, box, size=None):
    """Stand panel: the 5 x 7 main at top-left, small cuttings to its right and below it."""
    x0, y0, x1, y1 = box
    g, lab = P["gutter"], P["label_h"]
    mw, mh = size or (P["main_w"], P["main_h"])
    mains = [(x0, y0, mw, mh)] if n_main else []
    if n_main:
        zones = [(x0 + mw + g, y0, x1, y0 + mh + lab),
                 (x0, y0 + mh + lab + g, x1, y1)]
    else:
        zones = [(x0, y0, x1, y1)]
    def fit(w, h):
        cells = []
        for zx0, zy0, zx1, zy1 in zones:
            cols = int((zx1 - zx0 + g) // (w + g))
            rows = int((zy1 - zy0 + g) // (h + lab + g))
            for r_ in range(rows):
                for c_ in range(cols):
                    cells.append((zx0 + c_ * (w + g), zy0 + r_ * (h + lab + g), w, h))
        return cells
    for w, h in CUT_SIZES:
        cells = fit(w, h)
        if len(cells) >= n_other:
            return dict(cols=None, rows=None, w=w, h=h, stand=True, cuttings=n_other), mains + cells[:n_other]
    raise ValueError(f"{n_other} cuttings do not fit a stand panel")
SMALL_CUT = (2.5, 1.6)      # range books: other shades are small cuttings, max 2.5 x 1.6 in


def layout_board(bd):
    """Attach swatch cells to every inside panel of a ready board."""
    fold = bd["fold"]
    sw = [(i, pn) for i, pn in enumerate(bd["panels"]) if pn["kind"] == "swatch" and not pn.get("book")]
    shared = None
    if sw:                                   # one grid for every swatch panel on the board
        boxes = [content_box(fold, i) for i, _ in sw]
        W = min(b[2] - b[0] for b in boxes); H = min(b[3] - b[1] for b in boxes)
        mixed = bd["books"][0].get("mode") == "mixed"
        kw = dict(aspect=1.15) if mixed else dict(max_w=SMALL_CUT[0], max_h=SMALL_CUT[1])
        shared = solve_grid(max(len(pn["shades"]) for _, pn in sw), W, H, **kw)
    for i, pn in enumerate(bd["panels"]):
        box = content_box(fold, i)
        if pn.get("book"):                                  # stand panel: one book per panel
            nm = len([s for s in pn["mains"]])
            pn["grid"], pn["cells"] = stand_cells(nm, len(pn["shades"]) - nm, box, main_size(pn["book"]))
        elif pn["kind"] == "swatch":
            pn["grid"], pn["cells"] = place(len(pn["shades"]), box, grid=shared)
        elif pn["kind"] == "hero":
            sh = hero_spec_h(len(pn["shades"]))
            hb = (box[0], box[1], box[2], box[3] - sh)
            pn["grid"], pn["cells"] = waterfall(len(pn["shades"]), hb, main_size(bd["eff"]))
            pn["spec_box"] = (box[0], box[3] - sh + 0.2, box[2], box[3])
    return bd


def thickness_mm(bd):
    f = bd["fold"] or 3
    return f * (P["board_mm"] + P["fabric_mm"])


def level_of(b):
    return LEVEL[b["cat"]]


def ladder_color(cat):
    return dict((k, c) for k, _, _, c in LADDER)[cat]


# ---------------------------------------------------------------- fabric (HW-p8)
def fabric_lines(bds):
    """One line per book: main pieces (ready-cut 5 x 7 in, main_m metres of each main fabric) and
    small swatches (swatch_m metres of each shade).  Counts come from the board layout when it is
    ready; otherwise from the notes (None = not known yet)."""
    out = []
    for bd in bds:
        for b in bd["books"]:
            e = effective(b)
            mains_list = [m for m in e["mains"]]
            n_main, n_small = len(mains_list), None
            if bd["ready"]:
                n_small = 0
                for pn in bd["panels"]:
                    if pn.get("book") and pn["book"]["id"] != b["id"]:
                        continue
                    if pn["kind"] == "hero":
                        continue
                    k = len(pn.get("mains", [])) if pn.get("book") else 0
                    n_small += len(pn["shades"]) - k
                if not any(pn["kind"] == "hero" or pn.get("book") for pn in bd["panels"]):
                    n_small -= n_main               # mains placed among equal swatches
            elif e["shades"]:
                n_small = e["shades"] - n_main
            smalls = []
            if bd["ready"]:
                for pn in bd["panels"]:
                    if pn["kind"] == "hero" or (pn.get("book") and pn["book"]["id"] != b["id"]):
                        continue
                    k = len(pn.get("mains", [])) if pn.get("book") else 0
                    has_main_slot = any(q["kind"] == "hero" or q.get("book") for q in bd["panels"])
                    smalls += [s for s in pn["shades"][k:] if has_main_slot or not (s and s in mains_list)]
            out.append(dict(board=bd, book=b, round=b["round"], mains=mains_list, n_main=n_main, main_size=main_size(b),
                            n_small=n_small, smalls=smalls, provisional=bool(e.get("is_draft")),
                            m_main=n_main * P["main_m"],
                            m_small=None if n_small is None else round(n_small * P["swatch_m"], 2)))
    return out
