"""Instruction workbook (openpyxl) with live formulas driven by the Parameters sheet."""

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule

from data import EXTRA, LADDER, P, TRANSCRIPT
from printfiles import draft_src

INK, HEAD, BAND, LINE = "2B2723", "2B2723", "F3EEE5", "D9D0C0"
F_H = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
F_T = Font(name="Calibri", bold=True, size=14, color=INK)
F_S = Font(name="Calibri", italic=True, size=9, color="6E655A")
F_B = Font(name="Calibri", size=10, color=INK)
F_BB = Font(name="Calibri", size=10, bold=True, color=INK)
THIN = Side(style="thin", color=LINE)
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
STATUS_FILL = {"Confirmed": "E3EDD9", "Pending": "FBE9C9", "Reconsider": "F6D6D0", "Details needed": "F6D6D0"}


def header(ws, row, cols, widths=None):
    for i, c in enumerate(cols, 1):
        cell = ws.cell(row=row, column=i, value=c)
        cell.font, cell.fill, cell.border = F_H, PatternFill("solid", fgColor=HEAD), BOX
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[row].height = 30
    ws.freeze_panes = ws.cell(row=row + 1, column=1)


def title(ws, text, sub):
    ws["A1"], ws["A2"] = text, sub
    ws["A1"].font, ws["A2"].font = F_T, F_S


def body(ws, r, c, v, bold=False, fmt=None):
    cell = ws.cell(row=r, column=c, value=v)
    cell.font, cell.border, cell.alignment = (F_BB if bold else F_B), BOX, WRAP
    if fmt:
        cell.number_format = fmt
    return cell


def fabric_entries(bd):
    """(role label, swatch count, grid, metres noted per shade) for one ready board."""
    b, out = bd["books"][0], []
    hero = [pn for pn in bd["panels"] if pn["kind"] == "hero"]
    if hero:
        out.append(("Main", sum(len(pn["shades"]) for pn in hero), hero[0]["grid"], b["m_main"]))
    sw = [pn for pn in bd["panels"] if pn["kind"] == "swatch"]
    if sw:
        allsh = [s for pn in sw for s in pn["shades"]]
        mains = [s for s in allsh if s and s in b["mains"]]
        if mains:
            out.append(("Main (same size)", len(mains), sw[0]["grid"], b["m_main"]))
        out.append(("Shade", len(allsh) - len(mains), sw[0]["grid"], b["m_other"]))
    return out


def build(path, books, bds, spine_in, stack_mm):
    wb = Workbook()

    # ------------------------------------------------ README
    ws = wb.active
    ws.title = "README"
    title(ws, "Curated Fabrics Collection - Book Production Instructions",
          "Source: handwritten notes (7 pages), Sep 2026 price list, fabric e-catalogue, sample covers. Nothing is guessed - unknowns are blank and listed in Open_Questions.")
    rows = [
        ("What this book is", "One 4-ring master binder (11 x 13 in) holding one fold-out mood-board leaf per collection: 20 collections on 19 boards (Eeco Dimout and Double Shade share a board). Each board is 9 x 12 in per panel, 2-fold or 3-fold, with a photo + name front cover. No company branding anywhere."),
        ("Swatch rule", "Same design / texture in colour variations = main fabric BIG, other shades small cuttings (max 2.5 x 1.6 in). Different designs and textures (e.g. Neo Luna, Texture Dimout, Breeze) = all swatches the SAME size."),
        ("Order of books", "By light control - Sheer > Curtain > Texture Dimout > Dimout > Blackout > Lining - then by fabric weight (GSM, light to heavy). A customer moves through the book from airy to room-darkening."),
        ("Sheets", "Parameters - every size and allowance (change here, formulas update).\nBook_List - the 20 books, folds, shades, mains, status.\nBoard_Plan - what goes on every panel of every board.\nShade_Register - one row per swatch slot (slot IDs are printed on the boards).\nFabric_Requirement - metres to buy and copies you can make, live formulas.\nProduction_Steps - the build sequence with checks.\nOpen_Questions - decisions needed before print.\nTranscription - the handwritten notes, word for word."),
        ("Status colours", "Green = Confirmed (inside layout printed).  Amber = Pending (cover printed, inside waits for shade list).  Red = Reconsider / Details needed."),
        ("Print files", "04_Print_Ready/: one CMYK PDF per leaf (page 1 = side 1 outside with cover, page 2 = side 2 inside swatch layout, duplex) + master binder cover wrap. Crop marks, 0.125 in bleed, score ticks, TrimBox/BleedBox set."),
    ]
    for i, (k, v) in enumerate(rows, 4):
        body(ws, i, 1, k, bold=True); body(ws, i, 2, v)
        ws.row_dimensions[i].height = 18 * max(2, v.count("\n") + 2)
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 22, 120

    # ------------------------------------------------ Parameters (named cells)
    ws = wb.create_sheet("Parameters")
    title(ws, "Parameters", "Change a blue value and every formula in the workbook recalculates. Inches unless stated.")
    header(ws, 3, ["Parameter", "Value", "Unit", "Source / reason"], [34, 12, 10, 90])
    params = [
        ("cover_w", "Master cover width", P["cover_w"], "in", "HW-p4: COVER 11 x 13 INCH"),
        ("cover_h", "Master cover height", P["cover_h"], "in", "HW-p4"),
        ("board_w", "Inside board panel width", P["board_w"], "in", "HW-p4: INSIDE BOARDS 9 x 12 INCH"),
        ("board_h", "Inside board panel height", P["board_h"], "in", "HW-p4"),
        ("bleed", "Print bleed", P["bleed"], "in", "Standard 3 mm"),
        ("turn_in", "Wrap turn-in", P["turn_in"], "in", "15-16 mm folded over the board edge"),
        ("liner_inset", "Inside liner inset", P["liner_inset"], "in", "Liner sits 3 mm inside each board edge"),
        ("hinge", "Fold allowance (double score)", P["hinge"], "in", "Room for two fabric layers when the leaf closes"),
        ("roll_fold", "3-fold: panel C narrower by", P["roll_fold"], "in", "So the in-folding panel closes flat"),
        ("margin", "Panel margin", P["margin"], "in", "Safe zone"),
        ("bind_margin", "Binding-side margin (panel A)", P["bind_margin"], "in", "Kept clear for screw-post / ring option"),
        ("cut_allow", "Swatch cut allowance per side", 0.04, "in", "Cut 1 mm larger than the printed frame"),
        ("fabric_width", "Usable fabric width", P["fabric_width_in"], "in", "Price list: 54 in for almost every quality"),
        ("wastage", "Cutting wastage (pinking, nesting)", P["wastage"], "ratio", "15% allowance"),
        ("copies", "Books to produce", P["copies"], "pcs", "HW-p4 Neo Luna note '100 PCS' - confirm"),
        ("board_mm", "Leaf thickness", P["board_mm"], "mm", "350 GSM card, as in the reference ring binder"),
        ("fabric_mm", "Fabric layer thickness", P["fabric_mm"], "mm", "Dimout / blackout average"),
    ]
    for i, (key, label, val, unit, src) in enumerate(params, 4):
        body(ws, i, 1, label); c = body(ws, i, 2, val); c.font = Font(color="1F4E99", bold=True)
        body(ws, i, 3, unit); body(ws, i, 4, src)
        wb.defined_names[key] = DefinedName(key, attr_text=f"Parameters!$B${i}")

    # ------------------------------------------------ Book_List
    ws = wb.create_sheet("Book_List")
    title(ws, "Book List - 20 collections in book order", "Seq = position in the master book. List No. = number on the handwritten list.")
    cols = ["Seq", "List No.", "Book", "Board", "Light control", "Cover line", "Fold", "Fold source", "Total shades",
            "Main shade(s)", "No. of mains", "Other shades", "Swatch mode", "Width (in)", "Weight (GSM)", "Composition",
            "Metres / main (notes)", "Metres / other (notes)", "Status", "Notes (verbatim)", "Cross-check (price list / catalogue)"]
    header(ws, 3, cols, [5, 7, 17, 7, 14, 22, 6, 10, 8, 18, 7, 8, 30, 8, 9, 20, 9, 9, 13, 50, 50])
    board_of = {b["id"]: bd for bd in bds for b in bd["books"]}
    catname = {k: n for k, n, *_ in LADDER}
    for r, b in enumerate(books, 4):
        bd = board_of[b["id"]]
        mains = [m for m in b["mains"] if m]
        other = None
        if b.get("groups"):
            other = sum(len(g) for _, g in b["groups"])
        elif b["others"]:
            other = len(b["others"])
        vals = [b["seq"], b["list_no"], b["name"], bd["no"], catname[b["cat"]], b["line"], bd["fold"],
                bd["fold_src"], b["shades"], ", ".join(mains) if mains else (f"{len(b['mains'])} (numbers TBC)" if b["mains"] else ""),
                len(b["mains"]) or None, other,
                ("Mixed designs - all same size" if b["mode"] == "mixed" else "Colour range - main big, others small") + f' ({b["mode_src"]})',
                b["width"], b["gsm"], b["comp"], b["m_main"], b["m_other"], b["status"],
                b["notes"], b["xref"]]
        for c, v in enumerate(vals, 1):
            cell = body(ws, r, c, v, bold=(c == 3))
        ws.cell(row=r, column=19).fill = PatternFill("solid", fgColor=STATUS_FILL[b["status"]])
        ws.row_dimensions[r].height = 42
    r += 2
    body(ws, r, 3, "Not on the 20-book list", bold=True); body(ws, r, 20, EXTRA["notes"]); body(ws, r, 21, EXTRA["xref"])
    dv = DataValidation(type="list", formula1='"Confirmed,Pending,Reconsider,Details needed"', allow_blank=True)
    ws.add_data_validation(dv); dv.add(f"S4:S{3 + len(books)}")
    ws.auto_filter.ref = f"A3:{get_column_letter(len(cols))}{3 + len(books)}"

    # ------------------------------------------------ Board_Plan
    ws = wb.create_sheet("Board_Plan")
    title(ws, "Board Plan - what goes on every panel", "Panels are read on the inside, left to right. Cover = outside of panel B. Grid sizes from the layout engine (largest legible swatch).")
    header(ws, 3, ["Board", "Book(s)", "Fold", "Open size (in)", "Panel", "Panel width (in)", "Content",
                   "Swatches", "Grid (cols x rows)", "Swatch W (in)", "Swatch H (in)", "Inside layout", "Thickness (mm) - unknown fold counted as 3"],
           [7, 26, 6, 13, 7, 10, 30, 9, 11, 10, 10, 30, 11])
    r = 4
    for bd in bds:
        names = " & ".join(b["name"] for b in bd["books"])
        fold = bd["fold"]
        if not bd["panels"] or not bd["ready"]:
            reason = "Pending - shade list not confirmed" if bd["books"][0]["status"] != "Reconsider" else "On hold - under reconsideration"
            for c, v in enumerate([bd["no"], names, fold, "", "", "", "Cover printed; inside waits for data", "", "", "", "", reason,
                                   f"=IF(C{r}=\"\",3,C{r})*(board_mm+fabric_mm)"], 1):
                body(ws, r, c, v, bold=c == 2)
            r += 1
            continue
        widths = [P["board_w"]] * fold
        if fold == 3:
            widths[2] -= P["roll_fold"]
        open_w = sum(widths) + P["hinge"] * (fold - 1)
        for i, pn in enumerate(bd["panels"]):
            g = pn["grid"]
            what = ("Hero - main fabric" + ("s " if len(pn["shades"]) > 1 else " ") + ", ".join(s or "TBC" for s in pn["shades"])) if pn["kind"] == "hero" \
                else (pn.get("title") or "Shades") + f" ({len(pn['shades'])})"
            vals = [bd["no"] if i == 0 else "", names if i == 0 else "", fold if i == 0 else "",
                    f"{open_w:.3f} x {P['board_h']}" if i == 0 else "", pn["letter"], widths[i], what, len(pn["shades"]),
                    f"{g['cols']} x {g['rows']}", round(g["w"], 3), round(g["h"], 3),
                    ("DRAFT - provisional count: " + draft_src(bd) if bd.get("draft") else "Ready - printed on side 2") if i == 0 else "",
                    f"=C{r}*(board_mm+fabric_mm)" if i == 0 else ""]
            for c, v in enumerate(vals, 1):
                body(ws, r, c, v, bold=c == 2)
            r += 1
    r += 1
    body(ws, r, 12, "Leaf stack (mm)", bold=True); body(ws, r, 13, f"=SUM(M4:M{r - 2})", bold=True)
    body(ws, r + 1, 12, "4-D-ring needed (mm, 25% headroom)", bold=True)
    body(ws, r + 1, 13, f"=IF(M{r}*1.25<=25,25,IF(M{r}*1.25<=38,38,IF(M{r}*1.25<=50,50,IF(M{r}*1.25<=65,65,75))))", bold=True)
    body(ws, r + 2, 12, "Binder spine (in)", bold=True); body(ws, r + 2, 13, f"=ROUND((M{r + 1}+2*2.5+12)/25.4,2)", bold=True)

    # ------------------------------------------------ Shade_Register
    ws = wb.create_sheet("Shade_Register")
    title(ws, "Shade Register - one row per swatch slot", "Slot ID is printed beside every swatch on the inside liner. Fill blank shade numbers here, then re-run make.py to print them.")
    header(ws, 3, ["Board", "Book", "Panel", "Slot ID", "Role", "Group", "Shade No.", "Source", "Printed on liner"],
           [7, 18, 7, 8, 8, 11, 12, 34, 10])
    r = 4
    for bd in bds:
        if not bd["ready"]:
            continue
        for pn in bd["panels"]:
            b = pn.get("book") or bd["eff"]
            for k, s in enumerate(pn["shades"], 1):
                src = "Handwritten notes" if s else "TBC - fill in"
                if b.get("is_draft"):
                    src = ("Provisional - " if s else "TBC (draft) - ") + b["draft"]["src"]
                if b["id"] == "glorious-dimout" and s is None:
                    src = "Duplicate '634' in notes - correct"
                vals = [bd["no"], b["name"], pn["letter"], f"{pn['letter']}{k:02d}", "Main" if pn["kind"] == "hero" else "Shade",
                        (pn.get("title") if not pn.get("book") else "") or "", s or "", src, "Yes" if s else "No"]
                for c, v in enumerate(vals, 1):
                    cell = body(ws, r, c, v)
                if not s:
                    ws.cell(row=r, column=7).fill = PatternFill("solid", fgColor="FBE9C9")
                r += 1
    ws.auto_filter.ref = f"A3:I{r - 1}"

    # ------------------------------------------------ Fabric_Requirement
    ws = wb.create_sheet("Fabric_Requirement")
    title(ws, "Fabric Requirement - metres to cut for the production run",
          "Metres per shade = (W + 2*allowance) x (H + 2*allowance) x copies x (1 + wastage) / (fabric width x 39.37). Copies possible = metres noted / metres per copy.")
    cols = ["Board", "Book", "Role", "Swatches per book", "Swatch W (in)", "Swatch H (in)", "Cut area per swatch (sq in)",
            "Metres per shade for run", "Metres for all these shades", "Metres per shade noted", "Books possible from noted metres", "Check"]
    header(ws, 3, cols, [7, 18, 8, 10, 10, 10, 12, 12, 12, 12, 13, 26])
    r = 4
    for bd in bds:
        if not bd["ready"]:
            continue
        b = bd["books"][0]
        for label, n, g, noted in fabric_entries(bd):
            vals = [bd["no"], " & ".join(x["name"] for x in bd["books"]), label, n, round(g["w"], 3), round(g["h"], 3),
                    f"=(E{r}+2*cut_allow)*(F{r}+2*cut_allow)",
                    f"=ROUND(G{r}*copies*(1+wastage)/(fabric_width*39.37),2)",
                    f"=ROUND(H{r}*D{r},2)",
                    noted,
                    f'=IF(J{r}="","",ROUNDDOWN(J{r}*fabric_width*39.37/(G{r}*(1+wastage)),0))',
                    f'=IF(J{r}="","Enter metres to check",IF(K{r}>=copies,"OK - enough for the run","SHORT - increase metres"))']
            for c, v in enumerate(vals, 1):
                body(ws, r, c, v, fmt="0.00" if c in (7, 8, 9) else None)
            r += 1
    body(ws, r + 1, 8, "Total metres", bold=True); body(ws, r + 1, 9, f"=SUM(I4:I{r - 1})", bold=True, fmt="0.0")
    ws.conditional_formatting.add(f"L4:L{r}", CellIsRule(operator="equal", formula=['"SHORT - increase metres"'], fill=PatternFill("solid", fgColor="F6D6D0")))

    # ------------------------------------------------ Production_Steps
    ws = wb.create_sheet("Production_Steps")
    title(ws, "Production Steps", "Work top to bottom. Each step has a check that must pass before the next.")
    header(ws, 3, ["#", "Step", "Detail", "Check / acceptance", "Owner", "Status"], [4, 26, 70, 50, 12, 12])
    steps = [
        ("Close open questions", "Answer every row in Open_Questions; update Book_List and Shade_Register.", "No red rows left in Book_List."),
        ("Shoot / source photos", "One portrait lifestyle photo per book (see Design Guide, Photo spec). Save as assets/photos/<book-id>.jpg.", "Min 1200 x 2850 px; curtain is the hero; no logos or text."),
        ("Regenerate files", "Run python3 make.py - covers pick up photos, liners pick up shade numbers.", "Slug line on every cover no longer says 'placeholder'."),
        ("Pre-press check", "Open each PDF: TrimBox/BleedBox present, CMYK, fonts embedded, nothing in the 0.5 in margin.", "Printer pre-flight report clean."),
        ("Hard proof", "Print one leaf both sides at 100% on 350 GSM card, score, fold, punch.", "Cover sits on top; panel C closes flat; sides back up exactly."),
        ("Cut fabric", "Cut per Fabric_Requirement; pinking shears for swatches; 1 mm larger than frames.", "Count per Shade_Register = swatches cut."),
        ("Make leaves", "Duplex print (turn on long edge), matt laminate, double-score folds, 4-hole punch in panel A binding zone.", "Leaf folds square; holes clear of print."),
        ("Mount swatches", "Glue each swatch inside its printed frame, matching Slot ID to Shade_Register.", "Two-person check: shade number under every swatch matches the fabric."),
        ("Master binder", "11 x 13 in 4-D-ring binder; wrap with 00_Master_Binder_Cover (spine from stack).", "All 19 leaves turn freely on the rings."),
        ("Final QC", "Order boards by Seq, tabs visible, metal corners fitted, rope handle if used.", "Book opens Sheer -> Lining in order."),
    ]
    for i, (s, d, c) in enumerate(steps, 1):
        for col, v in enumerate([i, s, d, c, "", "Not started"], 1):
            body(ws, 3 + i, col, v, bold=col == 2)
        ws.row_dimensions[3 + i].height = 32
    dv = DataValidation(type="list", formula1='"Not started,In progress,Done,Blocked"'); ws.add_data_validation(dv); dv.add("F4:F20")

    # ------------------------------------------------ Open_Questions
    ws = wb.create_sheet("Open_Questions")
    title(ws, "Open Questions - decisions needed before print", "Found by cross-checking the notes against the price list and e-catalogue.")
    header(ws, 3, ["#", "Book", "Question", "Why it matters", "Answer"], [4, 18, 70, 40, 30])
    qs = []
    for b in books:
        for q in b["issues"]:
            qs.append((b["name"], q))
    qs.append(("3 Pass Blackout", EXTRA["issue"]))
    qs.append(("All", f"19 leaves stack to {stack_mm:.0f} mm on 350 GSM card -> {P['ring_mm']} mm 4-D-ring binder (as in the reference binder). Confirm card leaves rather than rigid greyboard (10 cm, too thick)."))
    qs.append(("All", "Photos: one lifestyle photo per book is needed for the covers. Placeholder curtain art is printed until supplied."))
    why = {"Shade": "Liner prints shade numbers", "Fold": "Changes board size and price", "Main": "Hero swatch & cover"}
    for i, (bk, q) in enumerate(qs, 1):
        reason = next((v for k, v in why.items() if k.lower() in q.lower()), "Accuracy of the printed book")
        for c, v in enumerate([i, bk, q, reason, ""], 1):
            body(ws, 3 + i, c, v, bold=c == 2)
        ws.row_dimensions[3 + i].height = 30

    # ------------------------------------------------ Transcription
    ws = wb.create_sheet("Transcription")
    title(ws, "Handwritten Notes - Transcription", "Word for word. (?) marks an overwritten or unclear character.")
    header(ws, 3, ["Page", "Text"], [26, 140])
    for i, (pg, txt) in enumerate(TRANSCRIPT, 4):
        body(ws, i, 1, pg, bold=True); body(ws, i, 2, txt)
        ws.row_dimensions[i].height = 15 * (len(txt) // 120 + 2)

    for w in wb.worksheets:
        w.sheet_view.showGridLines = False
        w.page_setup.orientation = "landscape"
        w.page_setup.fitToWidth = 1
    wb.save(path)
