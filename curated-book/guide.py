"""Guide Book for the new Osho Decor books - Round 1 and Round 2 (owner, 18 Nov), as Excel and PDF.

Round 1: book | main fabric (2 m of each main) | other shades (0.6 m of each)
Round 2: every swatch the same size (0.6 m of each) - except Neo Luna, whose mains are given (2 m each)
"""

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.workbook.defined_name import DefinedName

from data import P
from docs import CSS, esc, page
from layout import fabric_lines, main_size

INK, BAND, LINE, AMBER = "2B2723", "F3EEE5", "D9D0C0", "FBE9C9"
THIN = Side(style="thin", color=LINE)
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")


def rows_for(bds, rd):
    out = []
    for l in sorted([l for l in fabric_lines(bds) if l["round"] == rd], key=lambda l: l["book"]["list_no"]):
        b = l["book"]
        known = [x for x in l["smalls"] if x]
        if l["n_small"] is None:
            others, note = "", "Shade list not written yet"
        elif known and len(known) == l["n_small"]:
            others, note = ", ".join(known), ""
        elif known:
            others, note = ", ".join(known), f"+{l['n_small'] - len(known)} shade numbers to fill"
        else:
            others, note = "", f"{l['n_small']} shades - numbers to fill"
        mw, mh = main_size(b)
        mains = ", ".join(m or "TBC" for m in l["mains"])
        if b["id"] == "eeco-dimout":
            mains = f"Count not written ({mw:g} x {mh:g} in)"
        issues = [q for q in b["issues"] if "18 Nov" in q]
        out.append(dict(no=b["list_no"], name=b["name"], board=l["board"]["no"], stand=l["board"].get("stand"),
                        mains=mains, n_main=l["n_main"], size=f"{mw:g} x {mh:g} in" if (l["n_main"] or b["id"] == "eeco-dimout") else "",
                        others=others, n_other=l["n_small"], note="; ".join(x for x in [note] + issues if x),
                        provisional=l["provisional"]))
    return out


# ---------------------------------------------------------------- Excel
def excel(path, bds):
    wb = Workbook()
    ws = wb.active
    ws.title = "Rules"
    ws["A1"] = "Osho Decor - New Books Guide Book (Round 1 & Round 2)"
    ws["A1"].font = Font(bold=True, size=14, color=INK)
    ws["A2"] = "Change a blue value - every metre total in Round 1 and Round 2 updates."
    ws["A2"].font = Font(italic=True, size=9, color="6E655A")
    rules = [("main_m", "Main fabric - metres of EVERY main fabric", P["main_m"], "m"),
             ("swatch_m", "Other shades / same-size swatches - metres of EVERY shade", P["swatch_m"], "m")]
    for i, (key, label, val, unit) in enumerate(rules, 4):
        ws.cell(row=i, column=1, value=label).border = BOX
        c = ws.cell(row=i, column=2, value=val); c.font = Font(bold=True, color="1F4E99"); c.border = BOX
        ws.cell(row=i, column=3, value=unit).border = BOX
        wb.defined_names[key] = DefinedName(key, attr_text=f"Rules!$B${i}")
    notes = ["Round 1 = double-ticked books on the book list. Each book: main fabric (ready-cut 5 x 7 in; Double Shade & Eeco Dimout 5 x 5 in) + small swatches of the other shades.",
             "Round 2 = books marked '2nd'. Every swatch the SAME size, no main - except Neo Luna (mains 101-106).",
             "Correction 18 Nov: Texture Coated is the Round 1 book (it was written as Texture Dimout); Texture Dimout moves to Round 2.",
             "Stand A: Glory Cotton, Eeco Dimout and Neo Crest share one 3-fold board (one panel each).",
             "Amber rows: shade numbers or counts still to be written - fill them on the Missing Data Form."]
    for i, t in enumerate(notes, 8):
        ws.cell(row=i, column=1, value=t).alignment = WRAP
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=3)
        ws.row_dimensions[i].height = 30
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width, ws.column_dimensions["C"].width = 70, 10, 8

    def sheet(title, sub, cols, widths, data, rd):
        w = wb.create_sheet(title)
        w["A1"], w["A2"] = title, sub
        w["A1"].font, w["A2"].font = Font(bold=True, size=14, color=INK), Font(italic=True, size=9, color="6E655A")
        for i, (c, wd) in enumerate(zip(cols, widths), 1):
            cell = w.cell(row=4, column=i, value=c)
            cell.font, cell.fill, cell.border = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor=INK), BOX
            cell.alignment = Alignment(wrap_text=True, vertical="center")
            w.column_dimensions[cell.column_letter].width = wd
        w.row_dimensions[4].height = 34
        r = 5
        for row in data:
            vals = row(r)
            for c, v in enumerate(vals, 1):
                cell = w.cell(row=r, column=c, value=v)
                cell.border, cell.alignment = BOX, WRAP
                if c == 2:
                    cell.font = Font(bold=True)
            if vals[-1]:
                for c in range(1, len(vals) + 1):
                    w.cell(row=r, column=c).fill = PatternFill("solid", fgColor=AMBER)
            w.row_dimensions[r].height = 15 * max(2, len(str(vals[6] if rd == 1 else vals[2])) // 60 + 1)
            r += 1
        last = r - 1
        tcol = "K" if rd == 1 else "K"
        w.cell(row=r + 1, column=10, value=f"Round {rd} total (m)").font = Font(bold=True)
        c = w.cell(row=r + 1, column=11, value=f"=SUM({tcol}5:{tcol}{last})"); c.font = Font(bold=True); c.number_format = "0.0"
        w.freeze_panes = "C5"
        return w

    r1 = rows_for(bds, 1)
    sheet("Round 1", "Double tick on the book list. Main fabric: 2 m of each main. Other shades: 0.6 m of each.",
          ["List No.", "Book name", "Main fabric shade(s)", "Main size", "No. of mains", "Main metres (2 m each)",
           "Other shades - list", "No. of other shades", "Other metres (0.6 m each)", "Board", "Total metres", "To fill / note"],
          [7, 18, 22, 10, 8, 12, 60, 9, 12, 10, 10, 50],
          [(lambda x: (lambda r: [x["no"], x["name"], x["mains"] or "-", x["size"], x["n_main"], f"=E{r}*main_m",
                                  x["others"] or ("Shade list not written yet" if x["n_other"] is None else f"{x['n_other']} shades"),
                                  x["n_other"] if x["n_other"] is not None else "", f'=IF(H{r}="","",H{r}*swatch_m)',
                                  f'{x["board"]:02d}' + (f" Stand {x['stand']}" if x["stand"] else ""),
                                  f'=F{r}+IF(I{r}="",0,I{r})', x["note"]]))(x) for x in r1], 1)
    r2 = rows_for(bds, 2)
    sheet("Round 2", "Marked '2nd'. Every swatch the SAME size (0.6 m of each) - except Neo Luna, main given (2 m each).",
          ["List No.", "Book name", "Same-size shades - list", "No. of shades", "Metres (0.6 m each)", "Main (Neo Luna only)",
           "No. of mains", "Main size", "Main metres (2 m each)", "Board", "Total metres", "To fill / note"],
          [7, 18, 60, 9, 12, 24, 8, 10, 12, 10, 10, 50],
          [(lambda x: (lambda r: [x["no"], x["name"],
                                  x["others"] or ("Shade list not written yet" if x["n_other"] is None else f"{x['n_other']} shades"),
                                  x["n_other"] if x["n_other"] is not None else "", f'=IF(D{r}="","",D{r}*swatch_m)',
                                  x["mains"] or "-", x["n_main"] or "", x["size"], f'=IF(G{r}="",0,G{r}*main_m)',
                                  f'{x["board"]:02d}', f'=I{r}+IF(E{r}="",0,E{r})', x["note"]]))(x) for x in r2], 2)
    for w in wb.worksheets:
        w.sheet_view.showGridLines = False
        w.page_setup.orientation = "landscape"
        w.page_setup.fitToWidth = 1
    wb.save(path)


# ---------------------------------------------------------------- PDF
def pdf_html(bds, books):
    pages, n = [], 0

    def add(inner):
        nonlocal n
        n += 1
        pages.append(page("Pt", inner, n, "GUIDE BOOK - NEW OSHO DECOR BOOKS"))

    def mt(v):
        return "TBC" if v is None else f"{v:.1f}"

    r1, r2 = rows_for(bds, 1), rows_for(bds, 2)
    tot = {}
    for rd, rows in ((1, r1), (2, r2)):
        tot[rd] = sum((x["n_main"] or 0) * P["main_m"] + (x["n_other"] or 0) * P["swatch_m"] for x in rows)

    add(f'''<div class="k">Guide book</div><h1 style="font-size:34pt">New Osho Decor books<br>Round 1 &amp; Round 2</h1>
      <p class="lead">Which books to make in each round, the main fabric and the other shades of every book, and the fabric to pull.</p>
      <div class="cols" style="margin:.22in 0">
        <div class="tile"><b>{len(r1)}</b><span>books in Round 1 · {tot[1]:.0f} m known so far</span></div>
        <div class="tile"><b>{len(r2)}</b><span>books in Round 2 · {tot[2]:.0f} m known so far</span></div></div>
      <h2>Rules</h2><table>
      <tr><th>Round</th><th>What goes in the book</th><th>Fabric to pull</th></tr>
      <tr><td><b>Round 1</b><br>double tick</td><td>Main fabric as a ready-cut piece - <b>5 × 7 in</b> (Double Shade and Eeco Dimout <b>5 × 5 in</b>) - plus small swatches of every other shade</td><td><b>{P["main_m"]:g} m</b> of every main fabric · <b>{P["swatch_m"]:g} m</b> of every other shade</td></tr>
      <tr><td><b>Round 2</b><br>marked 2nd</td><td>Every swatch the <b>same size</b>, no main - <b>except Neo Luna</b>, main given (101-106)</td><td><b>{P["swatch_m"]:g} m</b> of every shade · Neo Luna mains <b>{P["main_m"]:g} m</b> each</td></tr></table>
      <h2>Corrections in this guide</h2><ul>
        <li><b>Texture Coated</b> is the Round 1 book - it was written as Texture Dimout by mistake. <b>Texture Dimout</b> moves to Round 2.</li>
        <li><b>Double Shade</b>: 6 main fabrics, 5 × 5 in. &nbsp; <b>Eeco Dimout</b>: main 5 × 5 in (number of mains still to write). &nbsp; <b>Premium Dimouts</b>: 5 main fabrics.</li>
        <li><b>Stand A</b>: Glory Cotton, Eeco Dimout and Neo Crest share one 3-fold board, one panel each.</li></ul>
      <div class="note">Rows marked in amber still need shade numbers or counts - write them on the Missing Data Form. The Excel version of this guide recalculates every metre total when you change 2 m or 0.6 m.</div>''')

    def r1_row(x):
        mm = (x["n_main"] or 0) * P["main_m"]
        om = None if x["n_other"] is None else x["n_other"] * P["swatch_m"]
        amber = ' style="background:#FBE9C9"' if x["note"] else ""
        others = esc(x["others"]) if x["others"] else ('<i>Shade list not written yet</i>' if x["n_other"] is None else f'<i>{x["n_other"]} shades - numbers to fill</i>')
        if x["others"] and x["n_other"] and len(x["others"].split(", ")) < x["n_other"]:
            others += f' <i>(+{x["n_other"] - len(x["others"].split(", "))} to fill)</i>'
        stand = f' · Stand {x["stand"]}' if x["stand"] else ""
        return (f'<tr{amber}><td>{x["no"]}</td><td><b>{esc(x["name"])}</b><br><span style="color:#6E655A;font-size:7pt">Board {x["board"]:02d}{stand}</span></td>'
                f'<td><b>{esc(x["mains"]) or "-"}</b><br><span style="color:#6E655A;font-size:7pt">{x["n_main"] or 0} × {x["size"] or "-"} · {mm:.1f} m</span></td>'
                f'<td style="font-size:7.2pt">{others}<br><span style="color:#6E655A">{x["n_other"] if x["n_other"] is not None else "?"} × {P["swatch_m"]:g} m = {mt(om)} m</span></td>'
                f'<td><b>{mt(mm + (om or 0)) if om is not None else mt(mm) + "+"}</b></td></tr>')

    def r2_row(x):
        mm = (x["n_main"] or 0) * P["main_m"]
        om = None if x["n_other"] is None else x["n_other"] * P["swatch_m"]
        amber = ' style="background:#FBE9C9"' if x["note"] else ""
        others = esc(x["others"]) if x["others"] else ('<i>Shade list not written yet</i>' if x["n_other"] is None else f'<i>{x["n_other"]} shades - numbers to fill</i>')
        main = f'<b>{esc(x["mains"])}</b><br><span style="color:#6E655A;font-size:7pt">{x["n_main"]} × {x["size"]} · {mm:.1f} m</span>' if x["n_main"] else "-"
        return (f'<tr{amber}><td>{x["no"]}</td><td><b>{esc(x["name"])}</b><br><span style="color:#6E655A;font-size:7pt">Board {x["board"]:02d}</span></td>'
                f'<td style="font-size:7.2pt">{others}<br><span style="color:#6E655A">{x["n_other"] if x["n_other"] is not None else "?"} × {P["swatch_m"]:g} m = {mt(om)} m</span></td>'
                f'<td>{main}</td><td><b>{mt(mm + (om or 0)) if om is not None else mt(mm) + "+"}</b></td></tr>')

    th1 = (f'<tr><th>No.</th><th>Book name</th><th>Main fabric<br>{P["main_m"]:g} m each</th><th>Other shades - list<br>{P["swatch_m"]:g} m each</th><th>Total m</th></tr>')
    th2 = (f'<tr><th>No.</th><th>Book name</th><th>All shades - same size<br>{P["swatch_m"]:g} m each</th><th>Main (Neo Luna only)<br>{P["main_m"]:g} m each</th><th>Total m</th></tr>')
    for rd, rows, th, fn, title in ((1, r1, th1, r1_row, "Round 1 - double tick"), (2, r2, th2, r2_row, "Round 2 - marked 2nd")):
        chunk, h, first = [], 0, True
        trs = [fn(x) for x in rows]
        for tr in trs:
            est = .5 + tr.count(",") * .018
            if chunk and h + est > 8.6:
                add(f'<div class="k">Round {rd}</div><h1>{title}{"" if first else " (cont.)"}</h1><table style="font-size:8.2pt">{th}{"".join(chunk)}</table>')
                chunk, h, first = [], 0, False
            chunk.append(tr); h += est
        foot = f'<tr><td></td><td><b>Round {rd} total</b></td><td></td><td></td><td><b>{tot[rd]:.1f}</b></td></tr>'
        add(f'<div class="k">Round {rd}</div><h1>{title}{"" if first else " (cont.)"}</h1><table style="font-size:8.2pt">{th}{"".join(chunk)}{foot}</table>'
            f'<p style="margin-top:.08in">Amber = shade numbers or counts still to write. "+" = more metres to add once the shade list is known.</p>')

    # what to fill
    todo = [(x["no"], x["name"], x["note"]) for x in r1 + r2 if x["note"]]
    trs = "".join(f'<tr><td>{no}</td><td><b>{esc(nm)}</b></td><td>{esc(nt)}</td></tr>' for no, nm, nt in todo)
    add(f'<div class="k">To complete</div><h1>Still to write in</h1><table><tr><th>No.</th><th>Book</th><th>What is missing</th></tr>{trs}</table>')
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}@page{{size:8.27in 11.69in;margin:0}}</style></head><body>{"".join(pages)}</body></html>'
