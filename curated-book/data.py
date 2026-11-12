"""Single source of truth for the Curated Fabrics Collection book.

Every value is traced to a source:
  HW-pN  = handwritten notes, page N (assets/reference/handwritten-pNN.jpg)
  PL     = Osho Decor price list effective 01 Sep 2026
  EC     = Osho Decor fabric e-catalogue (supplier shade cards)
  COVER  = photographed sample covers (Neo Luna, Virinchi)
Values not in any source are None and are listed as open questions - nothing is guessed.

Swatch mode (owner's rule, 12 Nov):
  range = one design / texture in colour variations -> main fabric BIG, other shades small cuttings
  mixed = different designs and textures -> every swatch the SAME size (e.g. Neo Luna)
"""

# ---------------------------------------------------------------- production parameters (inches unless noted)
P = dict(
    cover_w=11.0, cover_h=13.0,          # HW-p4  "COVER : 11 INCH x 13 INCH"
    board_w=9.0, board_h=12.0,           # HW-p4  "INSIDE BOARDS : 9 INCH x 12 INCH"
    bleed=0.125,                         # 3 mm print bleed
    turn_in=0.625,                       # 15-16 mm wrap turned over the master binder boards
    liner_inset=0.125,                   # (rigid-board option only)
    hinge=0.06,                          # double score: room for two fabric layers when a leaf folds
    roll_fold=0.125,                     # 3-fold: inward-folding panel C is 3 mm narrower
    margin=0.5, bind_margin=1.0,         # 1 in kept clear on the binding edge of panel A
    header=0.9, footer=0.35,
    gutter=0.22, label_h=0.26,
    min_sw_w=1.6, min_sw_h=0.95,         # smallest readable swatch
    cap_per_panel=18,                    # 3 x 6 grid at minimum size
    board_mm=0.45, fabric_mm=0.5,        # 350 GSM card leaf (as in the reference binder) + fabric layer
    rings_mm=(25, 38, 50, 65, 75),       # standard 4-D-ring capacities
    case_board_mm=2.5, joint=0.3,
    fabric_width_in=54,                  # PL: almost every quality is 54"
    wastage=0.15, copies=100,            # HW-p4 Neo Luna "100 PCS"
)

# Light-control ladder (open -> closed). Lining is an accessory, shown last.
LADDER = [
    ("sheer",   "Sheer",           "Filters light, keeps the view",        "#A3B5BD"),
    ("curtain", "Curtain",         "Soft daylight, decorative main fabric", "#B79C7A"),
    ("texture", "Texture Dimout",  "Textured face, strong light reduction", "#8C896B"),
    ("dimout",  "Dimout",          "Room-darkening, plain or textured",    "#7D6F88"),
    ("blackout","Blackout",        "Blocks light fully",                   "#414955"),
    ("lining",  "Lining",          "Backing for drape & fall",             "#B89D99"),
]
LEVEL = {k: i for i, (k, *_ ) in enumerate(LADDER)}

def rng(a, b):
    return [str(n) for n in range(a, b + 1)]

GLORIOUS = ["Cream", "603", "604", "605", "606", "609", "612", "613", "614", "649", "618",
            "634", "637", "631", "645", "666", "646", "602", "601", "669", "668", "674",
            "665", "670", None, "625", "644", "660", "619", "622", "658", "642", "655", "657"]
# None above = the second "634" written in HW-p7 (duplicate) - left blank until corrected.

BOOKS = [
 dict(id="breeze", mode="mixed", mode_src="PL lists 9 Breeze qualities (Pure, Slub, Malta, Moldovo, ...)", name="Breeze", list_no=2, cat="sheer", line="Sheer", fold=2, fold_src="HW-p2",
      shades=32, mains=[], others=[None]*32, gsm=100, width=54, comp=None,
      m_main=None, m_other=2, status="Confirmed",
      notes="BREEZE - 2 FOLD - 32 SHADES - 2 MTR EACH (one character overwritten)",
      xref="PL: Breeze qualities Pure, Slub, Malta, Moldovo, Monacco, Gauze, Ruler, Como, Fermo - 100 GSM, 54in.",
      issues=["Metres per shade written '2? MTR' - one character overwritten. Confirm 2 m.",
              "Which Breeze qualities make up the 32 shades? Shade numbers needed."]),
 dict(id="linen-sheer", mode="mixed", mode_src="PL: several linen-sheer qualities (Brazil, Thailand, Milan, Ebiza)", name="Linen Sheer", list_no=9, cat="sheer", line="Linen Sheer", fold=None, fold_src=None,
      shades=None, mains=[], others=[], gsm=None, width=None, comp=None, m_main=None, m_other=None,
      status="Pending", notes="On PENDING list (HW-p6). No fold / shades written.",
      xref="PL: Linen Sheer (Brazil, Thailand, Milan, Ebiza ...). EC: Taspa, Thailand, Milan, Ebiza, Brazil sheers.",
      issues=["Fold, shade count, main shade and which linen-sheer qualities to include."]),
 dict(id="aria", mode="range", mode_src="PL: one Jacquard quality, 24 colours", name="Aria", list_no=6, cat="curtain", line="Jacquard", fold=2, fold_src="HW-p2",
      shades=24, mains=[], others=[None]*24, gsm=None, width=54, comp=None, m_main=None, m_other=3,
      status="Confirmed", notes="ARIA - 2FOLD - 24 SHADES - 3 MTR EACH",
      xref="PL: Aria (Jacquard) 54in, 24 colours - matches.", issues=["Shade numbers for the 24 swatches."]),
 dict(id="sereno", draft=dict(shades=30, mains=[], others=[None]*30, src="price list: Sereno 30 colours (Venice, Rome, Florance, Tuscan)"), mode="mixed", mode_src="PL: Venice, Rome, Florance, Tuscan designs", name="Sereno", list_no=19, cat="curtain", line="Curtain Fabric", fold=None, fold_src=None,
      shades=None, mains=[], others=[], gsm=260, width=54, comp=None, m_main=None, m_other=None,
      status="Pending", notes="On PENDING list as 'SERANO' (HW-p6); book list spells 'SERENO'.",
      xref="PL: Sereno (Venice, Rome, Florance, Tuscan) 260 GSM, 54in, 30 colours.",
      issues=["Spelling: SERENO (book list, price list) vs SERANO (pending list) - using Sereno.",
              "Fold, shade count and main shade."]),
 dict(id="virinche", mode="range", mode_src="One quality, colours 701-727", name="Virinche", list_no=1, cat="curtain", line="Cotton-Blend Curtain Fabric", fold=3, fold_src="HW-p2",
      shades=21, mains=["705"], others=[None]*20, gsm=300, width=54, comp="50% Cotton, 50% Polyester",
      m_main=None, m_other=None, status="Confirmed", notes="VIRINCHE - 3 FOLD - MAIN 705 - 21 SHADES",
      xref="PL: Virinche 54in, 300 GSM, 27 colours. EC: SR. 701-727. COVER: 50% cotton / 50% polyester.",
      issues=["Which 20 of the 27 Virinche shades (701-727) go in the book?",
              "Sample cover is spelt VIRINCHI; book list VIRINCHE - using the book-list spelling."]),
 dict(id="glory-cotton", mode="range", mode_src="One quality, colour range", name="Glory Cotton", list_no=10, cat="curtain", line="Cotton-Look Curtain Fabric", fold=None, fold_src="derived",
      shades=19, mains=["3110"], others=[None]*18, gsm=280, width=54, comp=None, m_main=None, m_other=None,
      status="Confirmed", notes="GLORY COTTON - 3110 MAIN - 19 SHADES",
      xref="PL: Glory Cotton 54in, 280 GSM, 30 colours.", issues=["Fold not written - derived as 2-fold (1 hero + 18 swatches fit one panel).",
              "Shade numbers for the 18 other swatches."]),
 dict(id="neo-soft", mode="range", mode_src="One quality, 8001-8029", name="Neo Soft", list_no=4, cat="curtain", line="Curtain Fabric", fold=2, fold_src="HW-p4",
      shades=7, mains=["8028"], others=[None]*6, gsm=180, width=54, comp=None, m_main=None, m_other=None,
      status="Confirmed", notes="NEO SOFT - 2FOLD - 7? SHADES (second digit struck) - MAIN 8028",
      xref="PL: Neo Soft (8001-8029) 54in, 180 GSM, 7 colours - supports 7.",
      issues=["Shade count written '7' with a struck second digit; price list shows 7. Confirm.",
              "Light-control type of Neo Soft (curtain / dimout / blackout)?"]),
 dict(id="noble-texture", mode="range", mode_src="Assumed single texture - confirm", name="Noble Texture", list_no=8, cat="texture", line="Texture Dimout", fold=None, fold_src=None,
      shades=None, mains=[], others=[], gsm=None, width=54, comp=None, m_main=None, m_other=None,
      status="Details needed", notes="On book list only - no notes written.",
      xref="PL: Noble Texture Dimout 54in.", issues=["Fold, shade count, main shade - nothing written yet."]),
 dict(id="lexus-texture", mode="range", mode_src="Two designs (Grunge, Raindrop), each a colour range - one panel per design", name="Lexus Texture", list_no=13, cat="texture", line="Texture Dimout", fold=None, fold_src="derived",
      shades=25, mains=["1302"], groups=[("Grunge", ["1301","1302","1327","1326","1324","1325","1304","1328","1309","1315","1333","1305"]),
                                         ("Raindrop", ["1301","1302","1327","1326","1324","1325","1304","1328","1309","1315","1333","1329","1306"])],
      others=None, gsm=None, width=54, comp=None, m_main=None, m_other=None, status="Confirmed",
      notes="LEXUS TEXTURE - MAIN 1302 - 25 SHADES - GRUNGE (12) / RAINDROP (13)",
      xref="PL: Lexus Texture Dimout 54in.",
      issues=["Fold not written - derived as 3-fold (Grunge panel, Raindrop panel, hero 1302).",
              "Main 1302 exists in both Grunge and Raindrop - which design is the hero?"]),
 dict(id="texture-dimout", mode="mixed", mode_src="20 different supplier qualities (Prodigar, Gleam, Horten, Donald, Orion, Unison)", name="Texture Dimout", list_no=11, cat="texture", line="Texture Dimout", fold=3, fold_src="HW-p2",
      shades=27, mains=rng(6031, 6034), others=rng(6051,6054)+rng(6451,6454)+rng(6471,6474)+rng(6461,6464)+rng(6712,6714)+rng(6611,6614),
      gsm=None, width=None, comp=None, m_main=3, m_other=1, status="Confirmed",
      notes="TEXTURE DIMOUT - 3FOLD - 27 SHADES - FOUR MAIN [6031-6034]; SELECTED 6051-54, 6451-54, 6471-74, 6461-64, 6712-14, 6611-14; 4 MAIN 3 MTR EACH, REST 1 MTR EACH",
      supplier=["PRODIGAR-44","GLEAM-04","GLEAM-02","GLEAM-01","VIENNA +","HORTEN-70A","HORTEN-77A","DONALD-70","DONALD-60","DONALD-68",
                "DONALD-66","DONALD-62","ORION-04","ORION-26","ORION-22","HORTEN-352","HORTEN-739","UNISON-12","UNISON-15","UNISON-13"],
      xref="Counts check: 4 main + (4+4+4+4+3+4) = 27 - matches.",
      issues=["Different qualities, so all 27 swatches are the same size (owner's rule); the 4 mains are placed first and marked MAIN - the 3 m per main is still useful for hangers.",
              "HW-p5 lists 20 supplier qualities (Prodigar, Gleam, Vienna, Horten, Donald, Orion, Unison) - map each to an Osho shade no. (23 selected)."]),
 dict(id="texture-coated", draft=dict(shades=52, mains=[], others=[None]*52, src="notes: 52 shades, under reconsideration"), mode="range", mode_src="Assumed single texture - confirm", name="Texture Coated", list_no=3, cat="texture", line="Coated Texture", fold=None, fold_src="derived",
      shades=52, mains=[], others=[None]*52, gsm=None, width=None, comp=None, m_main=None, m_other=None,
      status="Reconsider", notes="TEXTURE COATED - 52 SHADES [RE CONSIDERATION]",
      xref="Not in price list.", issues=["Marked 'reconsideration' - keep, cut down, or drop? 52 shades need a full 3-fold board at minimum swatch size."]),
 dict(id="eeco-dimout", draft=dict(shades=12, mains=[], others=[None]*12, src="price list: EECO DIMOUT 12 colours"), mode="range", mode_src="One quality, colour range", name="Eeco Dimout", list_no=16, cat="dimout", line="Dimout", fold=2, fold_src="HW-p3", board="eeco-double",
      shades=None, mains=[], others=[], gsm=219, gsm_src="derived: 30 kg per 100 m at 54in", width=54, comp=None, m_main=None, m_other=None,
      status="Pending", notes="[EECO DIMOUT x DOUBLE SHADE] - 2 FOLD - 1 PAGE FOR EACH",
      xref="PL: EECO DIMOUT 54in, 12 colours, 30 kg / 100 m (= 219 GSM).",
      issues=["Shared board with Double Shade (1 panel each). Shade count and numbers pending."]),
 dict(id="double-shade", draft=dict(shades=8, mains=[], others=[None]*8, src="price list: Double Shaded 8 colours"), mode="range", mode_src="One quality, colour range", name="Double Shade", list_no=12, cat="dimout", line="Double-Shade Dimout", fold=2, fold_src="HW-p3", board="eeco-double",
      shades=None, mains=[], others=[], gsm=260, width=54, comp=None, m_main=None, m_other=None,
      status="Pending", notes="[EECO DIMOUT x DOUBLE SHADE] - 2 FOLD - 1 PAGE FOR EACH",
      xref="PL: Double Shaded 54in, 260 GSM, 8 colours.", issues=["Shade count and numbers pending."]),
 dict(id="lord-dimout", draft=dict(shades=23, mains=["424"], others=["425","461","462","2101","2103","2107","2109","2111","2112","2113","2114","2116","2120","2121","2122","2124","2125","2126","2127","2129","2130","2134"], src="e-catalogue Lord Dimout card (23 shades, hero 424)"), mode="range", mode_src="One quality, colour range", name="Lord Dimout", list_no=18, cat="dimout", line="Textured Dimout", fold=None, fold_src=None,
      shades=None, mains=[], others=[], gsm=260, width=54, comp=None, m_main=None, m_other=None,
      status="Details needed", notes="On book list only - no notes written.",
      xref="PL: Lord Dimout 54in, 260 GSM. EC: 23 shades (424 hero, 425-2134).",
      issues=["Nothing written. Use the 23-shade e-catalogue card (hero 424)?"]),
 dict(id="glorious-dimout", mode="range", mode_src="One quality, colours 601-674", name="Glorious Dimout", list_no=15, cat="dimout", line="Dimout", fold=None, fold_src="derived",
      shades=34, mains=["606"], others=[s for s in GLORIOUS if s != "606"], gsm=270, width=54, comp=None, m_main=None, m_other=None,
      status="Confirmed", notes="GLORIOUS DIMOUT - 606 MAIN - 34 SHADES (list of 34 written)",
      xref="PL: Glorious Dimout 54in, 270 GSM, 58 colours. EC: 601-658.",
      issues=["'634' is written twice in the list - the second one is left blank until corrected.",
              "Fold not written - derived as 3-fold (hero + 33 swatches over 2 panels)."]),
 dict(id="paris-dimout", mode="range", mode_src="One quality, 1101-1118", name="Paris Dimout", list_no=17, cat="dimout", line="Textured Dimout", fold=3, fold_src="HW-p3",
      shades=27, mains=["1109"], others=[None]*26, gsm=305, width=54, comp=None, m_main=None, m_other=None,
      status="Confirmed", notes="PARIS DIMOUT - 1109 MAIN - 3FOLD - 27 SHADES",
      xref="PL: Paris Dimout 54in, 305 GSM, 19 colours. EC card: 18 shades (1101-1118).",
      issues=["27 shades written, but the price list shows 19 and the shade card 18 - confirm the count and numbers."]),
 dict(id="premium-dimouts", mode="range", mode_src="8 main fabrics + 25 others - confirm whether the 8 are different qualities", name="Premium Dimouts", list_no=20, cat="dimout", line="Dimout", fold=None, fold_src="derived",
      shades=33, mains=[None]*8, others=[None]*25, gsm=None, width=None, comp=None, m_main=None, m_other=None,
      status="Confirmed", notes="PREMIUM DIMOUTS - 33 SHADES - MAIN FABRICS 08 SHADES",
      xref="Not named in price list.", issues=["Which 8 shades are the main fabrics, and which 25 others?",
              "Are the 8 mains different qualities? If yes, switch to same-size swatches (mode 'mixed').",
              "Fold not written - derived as 3-fold."]),
 dict(id="neo-crest", mode="range", mode_src="One quality, 101-111", name="Neo Crest", list_no=5, cat="blackout", line="100% Blackout", fold=2, fold_src="HW-p4",
      shades=8, mains=["103"], others=[None]*7, gsm=200, width=54, comp=None, m_main=None, m_other=None,
      status="Confirmed", notes="NEO CREST - 2FOLD - 8 SHADES - MAIN 103",
      xref="PL: Neo Crest (101-111) 54in, 200 GSM, 8 colours - matches. EC: 101,102,103,105,106,108,109,110.",
      issues=["Confirm the other 7 = 101, 102, 105, 106, 108, 109, 110 (e-catalogue)."]),
 dict(id="neo-luna", draft=dict(shades=6, mains=rng(101, 106), others=[], src="notes: 3-fold, 6 main designs 101-106; owner rule - different designs, same size"), mode="mixed", mode_src="Owner: different designs - same-size swatches", name="Neo Luna", list_no=7, cat="blackout", line="100% Blackout", fold=3, fold_src="HW-p4",
      shades=None, mains=rng(101, 106), others=[], gsm=None, width=None, comp=None, m_main=3, m_other=2,
      features=["Kids friendly", "Breathable", "Eco friendly", "Soft on skin", "Colour fast to light"],
      status="Pending", notes="NEO LUNA - 3 FOLD - MAIN 101-106 - 100 PCS 2 MTR EACH FABRIC - 6 PCS 3 MTR EACH FOR MAIN [101-106]",
      xref="COVER: 100% Blackout; kids friendly, breathable, eco friendly, soft on skin, colour fastness to light.",
      issues=["On the PENDING list. Total shade count not written.",
              "'100 PCS 2 MTR EACH FABRIC' - does 100 PCS mean 100 books to be made, or 100 fabric pieces?"]),
 dict(id="ritz-satin", mode="range", mode_src="One quality, colour range", name="Ritz Satin", list_no=14, cat="lining", line="Satin Lining", fold=3, fold_src="HW-p3",
      shades=33, mains=["184", "152"], others=[None]*31, gsm=135, width=54, comp=None, m_main=None, m_other=None,
      status="Confirmed", notes="RITZ SATIN - MAIN 184 & 152 - 33 SHADES - 3 FOLD",
      xref="PL: Ritz Satin 48in & 54in, 135 GSM. EC: 151-189 + White = 33 shades, but no 184.",
      issues=["Main '184' does not appear on the Ritz Satin shade card (183 and 189 do). Confirm 184."]),
]

EXTRA = dict(name="3 Pass Blackout - Carnation", notes="* 3 PASS BLACKOUT CARNATION - 803 MAIN - 14 SHADES (HW-p5)",
             xref="PL: 3 Pass Plain Blackout (801-830) 54in, 255 GSM, 14 colours - matches.",
             issue="Written in the notes but not on the 20-book list. Add as a 21st book?")

TRANSCRIPT = [
 ("HW-p1  OSHO DECOR - BOOK LIST", "1) VIRINCHE  2) BREEZE  3) TEXTURE COATED  4) NEO SOFT  5) NEO CREST  6) ARIA  7) NEO LUNA  8) NOBLE TEXTURE  "
  "9) LINEN SHEER  10) GLORY COTTON  11) TEXTURE DIMOUT  12) DOUBLE SHADE  13) LEXUS TEXTURE  14) RITZ SATIN  15) GLORIOUS DIMOUT  "
  "16) EECO DIMOUT  17) PARIS DIMOUT  18) LORD DIMOUT  19) SERENO  20) PREMIUM DIMOUTS"),
 ("HW-p4  NEW OSHO BOOK DESIGN - INSTRUCTIONS", "COVER : 11 INCH x 13 INCH.  INSIDE BOARDS : 9 INCH x 12 INCH.  NOTES BOOK WISE:  "
  "PREMIUM DIMOUTS - 33 SHADES, MAIN FABRICS - 08 SHADES.  NEO SOFT - 2FOLD - 7(?) SHADES, MAIN - 8028 [SHADE NO.].  "
  "NEO CREST - 2FOLD - 8 SHADES, MAIN - 103 [SHADE NO.].  NEO LUNA - 3 FOLD, MAIN - 101-106, 100 PCS 2 MTR EACH FABRIC, 6 PCS 3 MTR EACH FOR MAIN [101-106]."),
 ("HW-p2", "TEXTURE COATED - 52 SHADES [RE CONSIDERATION].  ARIA - 2FOLD - 24 SHADES, 3 MTR EACH.  VIRINCHE - 3 FOLD - 21 SHADES, MAIN - 705.  "
  "BREEZE - 2 FOLD - 32 SHADES, 2(?) MTR EACH.  TEXTURE DIMOUT - 3FOLD - 27 SHADES, FOUR MAIN FABRIC [6031-6034]; SELECTED FABRICS 6051-6054, "
  "6451-6454, 6471-6474, 6461-6464, 6712-6714, 6611-6614; 4 MAIN - 3 MTR EACH, REST - 1 MTR EACH."),
 ("HW-p3", "[EECO DIMOUT x DOUBLE SHADE] - 2 FOLD - 1 PAGE FOR EACH.  PARIS DIMOUT - 1109 MAIN - 3FOLD - 27 SHADES.  RITZ SATIN - MAIN 184 & 152 - 33 SHADES - 3 FOLD.  "
  "LEXUS TEXTURE - MAIN 1302 - 25 SHADES.  GRUNGE: 1301, 1302, 1327, 1326, 1324, 1325, 1304, 1328, 1309, 1315, 1333, 1305.  "
  "RAINDROP: 1301, 1302, 1327, 1326, 1324, 1325, 1304, 1328, 1309, 1315, 1333, 1329, 1306."),
 ("HW-p5", "* TEXTURE DIMOUT - SELECTED FABRICS: 1) PRODIGAR-44 2) GLEAM-04 3) GLEAM-02 4) GLEAM-01 5) VIENNA + 6) HORTEN-70A 7) HORTEN-77A 8) DONALD-70 "
  "9) DONALD-60 10) DONALD-68 11) DONALD-66 12) DONALD-62 13) ORION-04 14) ORION-26 15) ORION-22 16) HORTEN-352 17) HORTEN-739 18) UNISON-12 19) UNISON-15 20) UNISON-13.  "
  "* 3 PASS BLACKOUT CARNATION - 803 MAIN - 14 SHADES."),
 ("HW-p6  PENDING", "NEO LUNA, EECO DIMOUT, DOUBLE SHADE, LINEN SHEER, SERANO."),
 ("HW-p7", "GLORY COTTON - 3110 MAIN - 19 SHADES.  GLORIOUS DIMOUT - 606 MAIN - 34 SHADES: CREAM, 603, 604, 605, 606, 609, 612, 613, 614, 649, 618 | "
  "634, 637, 631, 645, 666, 646, 602, 601, 669, 668, 674 | 665, 670, 634, 625, 644, 660, 619, 622, 658, 642, 655 | 657."),
]
