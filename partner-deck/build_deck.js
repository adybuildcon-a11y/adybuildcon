// The Furnish Atellier - Business Partner Program: 8-slide deck (5 project + 3 goal).
// Run:  NODE_PATH=<dir with pptxgenjs, react-icons, react, react-dom, sharp> node build_deck.js
// Writes The_Furnish_Atellier_Partner_Program.pptx next to this script.

const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa6");
const { applyTheme } = require(process.env.PPTX_SKILL_DIR + "/scripts/apply_theme.js");

const OUT = path.join(__dirname, "The_Furnish_Atellier_Partner_Program.pptx");

// ---- brand (taken from the partner-program brochure: navy, gold, light grey) ----
const THEME = {
  name: "The Furnish Atellier",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2333",   // body text
    lt1: "FFFFFF",
    dk2: "1F2A44",   // brand navy
    lt2: "EEF0F3",   // card grey
    accent1: "B08A55", // brand gold
    accent2: "E9DCC7", // soft gold
    accent3: "2B3A5C", // navy, lighter (cards on dark)
    accent4: "6B7280", // muted grey
    accent5: "86643A", // deep gold (small text on white)
    accent6: "F6F1EA", // cream
    hlink: "86643A",
    folHlink: "6B7280",
  },
};
const H = THEME.colors;

// ---- facts used on the slides ----
const FOUNDING_SECURITY = 69000;   // first 100 founding partners
const STANDARD_SECURITY = 135000;  // every partner after the first 100
const MILESTONES = [
  { phase: "Launch", by: "March 2027", partners: 100 },
  { phase: "Build", by: "March 2028", partners: 500 },
  { phase: "Scale", by: "March 2029", partners: 1000 },
  { phase: "Global", by: "March 2032", partners: 5000 },
];
const inr = (n) => n.toLocaleString("en-IN");

// ---- icons: react-icons -> white PNG ----
async function icon(Comp, color = "#FFFFFF") {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color, size: 256 }));
  const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
  pres.title = "The Furnish Atellier - Business Partner Program";
  pres.subject = "Project overview and the goal of 5,000 business partners across the globe by March 2032";
  pres.author = "Ady Buildcon Pvt. Ltd.";
  pres.company = "Ady Buildcon Pvt. Ltd.";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;

  const FOOT = "THE FURNISH ATELLIER  ·  BUSINESS PARTNER PROGRAM";
  const kicker = (color) => ({ placeholder: { options: {
    name: "kicker", type: "body", x: 0.5, y: 0.34, w: 9, h: 0.28, fontSize: 11, bold: true,
    color, charSpacing: 3, margin: 0, valign: "top" }, text: "" } });
  const title = (color) => ({ placeholder: { options: {
    name: "title", type: "title", x: 0.5, y: 0.62, w: 9, h: 0.62, fontSize: 28, bold: true,
    color, margin: 0, valign: "top", align: "left" }, text: "" } });
  const footer = (color) => ({ text: { text: FOOT, options: {
    x: 0.5, y: 5.2, w: 6, h: 0.25, fontSize: 10, color, charSpacing: 1, margin: 0 } } });

  pres.defineSlideMaster({
    title: "COVER",
    background: { color: H.lt1 },
    objects: [
      { placeholder: { options: { name: "kicker", type: "body", x: 0.8, y: 1.05, w: 6, h: 0.3,
          fontSize: 11, bold: true, color: C.accent5, charSpacing: 4, margin: 0 }, text: "" } },
      { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.4, w: 7.5, h: 0.95,
          fontSize: 44, bold: true, color: C.text2, margin: 0, valign: "top", align: "left" }, text: "" } },
      { placeholder: { options: { name: "subtitle", type: "body", x: 0.8, y: 2.35, w: 7, h: 0.45,
          fontSize: 20, color: C.accent5, charSpacing: 2, margin: 0, valign: "top" }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "CONTENT",
    background: { color: H.lt1 },
    objects: [kicker(C.accent5), title(C.text2), footer(C.accent4)],
    slideNumber: { x: 9.0, y: 5.2, w: 0.5, h: 0.25, fontSize: 10, color: H.accent4, align: "right" },
  });

  // ---- helpers ----
  let n = 0;
  const name = (s) => `${s}-${++n}`;
  const T = (slide, text, o) => slide.addText(text, { isTextBox: true, margin: 0, objectName: name("text"), ...o });
  const card = (slide, x, y, w, h, color, shadow = true) => slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.08, fill: { color }, line: { type: "none" }, objectName: name("card"),
    ...(shadow ? { shadow: { type: "outer", color: "1F2A44", opacity: 0.12, blur: 6, offset: 2, angle: 90 } } : {}),
  });
  async function badge(slide, x, y, d, Comp, fill = C.accent1) {
    slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { type: "none" },
      objectName: name("badge") });
    const pad = d * 0.27;
    slide.addImage({ data: await icon(Comp), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad,
      altText: "", objectName: name("icon") });
  }
  const numBadge = (slide, x, y, d, num) => {
    slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: C.accent1 }, line: { type: "none" },
      objectName: name("num") });
    T(slide, String(num), { x, y, w: d, h: d, fontSize: 16, bold: true, color: C.background1,
      align: "center", valign: "middle", fontFace: "+mj-lt" });
  };

  // ================= THE PROJECT (5 slides) =================
  pres.addSection({ title: "The Project" });

  // 1 - cover
  let s = pres.addSlide({ masterName: "COVER", sectionTitle: "The Project" });
  s.addShape(pres.shapes.OVAL, { x: 6.9, y: -1.7, w: 4.6, h: 4.6, fill: { color: C.accent6 }, line: { type: "none" }, objectName: "cover-circle-1" });
  s.addShape(pres.shapes.OVAL, { x: 8.2, y: 3.6, w: 2.6, h: 2.6, line: { color: H.accent1, width: 1.5 }, fill: { type: "none" }, objectName: "cover-ring" });
  s.addText("A VENTURE BY ADY BUILDCON PVT. LTD.", { placeholder: "kicker" });
  s.addText("The Furnish Atellier", { placeholder: "title" });
  s.addText("BUSINESS PARTNER PROGRAM", { placeholder: "subtitle" });
  T(s, "Premium fabrics for curtains & upholstery — and a ready-made business for every partner.",
    { x: 0.8, y: 2.95, w: 5.6, h: 0.65, fontSize: 16, italic: true, color: C.text1, valign: "top" });
  const facts = [["Since 1994", "a fabric legacy"], ["1,200", "fabrics in every kit"], ["5,000", "global partners by 2032"]];
  facts.forEach(([big, small], i) => {
    const x = 0.8 + i * 2.05;
    T(s, big, { x, y: 3.85, w: 1.9, h: 0.45, fontSize: 22, bold: true, color: C.accent5, fontFace: "+mj-lt" });
    T(s, small, { x, y: 4.3, w: 1.9, h: 0.3, fontSize: 12, color: C.accent4 });
  });
  T(s, "Kamlesh Agrawal, Director   ·   +91 98105 27231   ·   adybuildcon@gmail.com",
    { x: 0.8, y: 5.0, w: 7, h: 0.3, fontSize: 11, color: C.accent4 });
  s.addNotes("The Furnish Atellier Business Partner Program: a premium fabric brand for curtains and upholstery from Ady Buildcon Pvt. Ltd., offered to partners as a complete business kit against a security amount (₹69,000 for the first 100 founding partners, ₹1,35,000 after that). Goal: a network of 5,000 business partners across the globe by March 2032.");

  // 2 - the project
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "The Project" });
  s.addText("01  ·  THE PROJECT", { placeholder: "kicker" });
  s.addText("A Ready-Made Fabric Business, Backed by 30 Years", { placeholder: "title" });
  T(s, "The Furnish Atellier is a premium fabric brand for curtains and upholstery, started by Ady Buildcon Pvt. Ltd. Partners build their own business with our collection, training and support.",
    { x: 0.5, y: 1.45, w: 4.2, h: 1.0, fontSize: 14, color: C.text1, valign: "top" });
  const legacy = [["1994", "Our journey began through Osho Decor, under Osho International."],
                  ["30 yrs", "Serving homes and businesses across North India."],
                  ["Zero", "Showroom or inventory needed to start."]];
  legacy.forEach(([big, txt], i) => {
    const y = 2.6 + i * 0.78;
    T(s, big, { x: 0.5, y, w: 1.15, h: 0.6, fontSize: 24, bold: true, color: C.accent5, fontFace: "+mj-lt", valign: "middle" });
    T(s, txt, { x: 1.7, y, w: 3.0, h: 0.6, fontSize: 14, color: C.text1, valign: "middle" });
  });
  T(s, "HOW IT WORKS  ·  SIX STEPS", { x: 5.1, y: 1.45, w: 4.4, h: 0.28, fontSize: 11, bold: true, color: C.accent5, charSpacing: 2 });
  ["Become a Partner", "Receive the Kit", "Complete Training", "Meet Customers", "Take Orders & Earn", "Grow With Support"]
    .forEach((t, i) => {
      const x = 5.1 + (i % 2) * 2.25, y = 1.85 + Math.floor(i / 2) * 1.0;
      card(s, x, y, 2.1, 0.85, C.background2);
      numBadge(s, x + 0.15, y + 0.2, 0.45, i + 1);
      T(s, t, { x: x + 0.72, y: y + 0.08, w: 1.3, h: 0.69, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
    });
  s.addNotes("Partners do not need a shop, showroom or stock. They join as the official partner for their area, receive the kit, finish training, meet customers, take orders and earn their margin on every completed order, with ongoing support.");

  // 3 - the business kit
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "The Project" });
  s.addText("02  ·  THE BUSINESS KIT", { placeholder: "kicker" });
  s.addText("A Complete Showroom in One Trolley Bag", { placeholder: "title" });
  [["4", "Swatch Books"], ["300", "Samples per Book"], ["1,200", "Total Fabrics"], ["600+", "Mood Boards"]]
    .forEach(([big, small], i) => {
      const x = 0.5 + i * 1.35;
      card(s, x, 1.45, 1.2, 1.05, C.background2);
      T(s, big, { x, y: 1.55, w: 1.2, h: 0.5, fontSize: 26, bold: true, color: C.text2, align: "center", fontFace: "+mj-lt" });
      T(s, small, { x, y: 2.07, w: 1.2, h: 0.3, fontSize: 11, color: C.accent4, align: "center" });
    });
  T(s, "Mood-board style books, plus an AI styling app that shows each fabric on the customer's own windows.",
    { x: 0.5, y: 2.68, w: 5.25, h: 0.55, fontSize: 13, italic: true, color: C.text1, valign: "top" });
  T(s, "YOUR BUSINESS TOOLS", { x: 0.5, y: 3.38, w: 5, h: 0.28, fontSize: 11, bold: true, color: C.accent5, charSpacing: 2 });
  const tools = [[fa.FaTabletScreenButton, "AI Styling Tablet"], [fa.FaSignHanging, "Promotional Standee"],
                 [fa.FaAddressCard, "Visiting Cards"], [fa.FaSuitcaseRolling, "Trolley Bag"]];
  for (let i = 0; i < tools.length; i++) {
    const x = 0.5 + i * 1.35;
    await badge(s, x + 0.33, 3.75, 0.55, tools[i][0]);
    T(s, tools[i][1], { x, y: 4.36, w: 1.2, h: 0.5, fontSize: 12, bold: true, color: C.text2, align: "center", valign: "top" });
  }
  card(s, 6.05, 1.45, 3.45, 3.45, C.background2);
  T(s, "SECURITY AMOUNT AGAINST THE KIT", { x: 6.3, y: 1.62, w: 3.1, h: 0.28, fontSize: 11, bold: true, color: C.accent5, charSpacing: 1 });
  T(s, "₹" + inr(FOUNDING_SECURITY), { x: 6.3, y: 1.9, w: 3, h: 0.7, fontSize: 40, bold: true, color: C.text2, fontFace: "+mj-lt" });
  T(s, `First 100 founding partners · then ₹${inr(STANDARD_SECURITY)}`, { x: 6.3, y: 2.6, w: 3.1, h: 0.3, fontSize: 12, color: C.accent4 });
  T(s, "ALSO INCLUDED", { x: 6.3, y: 3.05, w: 3, h: 0.28, fontSize: 11, bold: true, color: C.accent5, charSpacing: 2 });
  T(s, ["Rights to the brand name", "Welcome training programme", "Support, always on call", "Weekly webinars", "Ready digital marketing content"]
    .map((t, i, a) => ({ text: t, options: { bullet: true, breakLine: i < a.length - 1 } })),
    { x: 6.3, y: 3.35, w: 3.1, h: 1.45, fontSize: 14, color: C.text1, paraSpaceAfter: 2, valign: "top" });
  s.addNotes("Each partner receives 4 swatch books with 300 samples each - 1,200 fabrics in 600+ curated mood boards - plus an AI styling tablet, standee, visiting cards and a trolley bag. The kit is given against a security amount: ₹69,000 for the first 100 founding partners and ₹1,35,000 for every partner after that.");

  // 4 - markets & earnings
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "The Project" });
  s.addText("03  ·  THE OPPORTUNITY", { placeholder: "kicker" });
  s.addText("Four Markets, Four Ways to Earn", { placeholder: "title" });
  const markets = [[fa.FaHouseChimney, "New Home Owners", "Families setting up a home."],
                   [fa.FaPenRuler, "Designers & Architects", "Need a trusted fabric partner."],
                   [fa.FaHotel, "Hotels", "Resorts and boutique stays."],
                   [fa.FaHospital, "Hospitals", "Hospital curtains & fabrics."]];
  for (let i = 0; i < 4; i++) {
    const x = 0.5 + (i % 2) * 2.55, y = 1.45 + Math.floor(i / 2) * 1.75;
    card(s, x, y, 2.4, 1.6, C.background2);
    await badge(s, x + 0.2, y + 0.2, 0.5, markets[i][0]);
    T(s, markets[i][1], { x: x + 0.2, y: y + 0.8, w: 2.05, h: 0.32, fontSize: 14, bold: true, color: C.text2 });
    T(s, markets[i][2], { x: x + 0.2, y: y + 1.12, w: 2.05, h: 0.35, fontSize: 12, color: C.accent4, valign: "top" });
  }
  T(s, "HOW PARTNERS EARN", { x: 5.85, y: 1.45, w: 3.6, h: 0.28, fontSize: 11, bold: true, color: C.accent5, charSpacing: 2 });
  const earn = [[fa.FaIndianRupeeSign, "Order margins", "On every completed order."],
                [fa.FaUserPlus, "₹5,000 referral bonus", "Per new partner — no cap."],
                [fa.FaGift, "First-month gift", "Free steam iron at ₹50,000+ sales."],
                [fa.FaCartShopping, "Online affiliate income", "From our upcoming décor e-store."]];
  for (let i = 0; i < 4; i++) {
    const y = 1.85 + i * 0.8;
    await badge(s, 5.85, y + 0.05, 0.5, earn[i][0], C.text2);
    T(s, earn[i][1], { x: 6.5, y, w: 3.0, h: 0.3, fontSize: 14, bold: true, color: C.text2 });
    T(s, earn[i][2], { x: 6.5, y: y + 0.3, w: 3.0, h: 0.3, fontSize: 12, color: C.accent4 });
  }
  s.addNotes("One kit opens four very different customer segments. Partners earn margins on every completed order, ₹5,000 for every partner they refer (no cap), a free steam iron for ₹50,000+ first-month sales, and affiliate income from the upcoming home-décor e-commerce store.");

  // 5 - investment
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "The Project" });
  s.addText("04  ·  THE INVESTMENT", { placeholder: "kicker" });
  s.addText("A Security Amount, Not a Cost", { placeholder: "title" });
  const tiles = [["₹" + inr(FOUNDING_SECURITY), "First 100 founding partners", true],
                 ["₹" + inr(STANDARD_SECURITY), "Every partner after the first 100", false],
                 ["₹5,000 off", "For women entrepreneurs", false],
                 ["₹7 Lakh", "Sales at which your security amount is adjusted in full", false]];
  tiles.forEach(([big, small, hi], i) => {
    const x = 0.5 + i * 2.3;
    card(s, x, 1.45, 2.1, 1.15, hi ? C.accent1 : C.background2);
    T(s, big, { x: x + 0.15, y: 1.55, w: 1.8, h: 0.5, fontSize: 24, bold: true, color: hi ? C.background1 : C.text2, align: "center", fontFace: "+mj-lt" });
    T(s, small, { x: x + 0.12, y: 2.05, w: 1.86, h: 0.48, fontSize: 11, color: hi ? C.background1 : C.accent4, align: "center", valign: "top" });
  });
  const hdr = (t, fill, color) => ({ text: t, options: { bold: true, fill: { color: fill }, color, fontSize: 13 } });
  const rows = [["Investment", "₹10 lakh+ for catalogues of many brands", "One kit against a security amount"],
                ["Space", "300–400 sq. ft. of storage", "Fits in one trolley bag"],
                ["Access", "Most brands won't supply individuals", "Branded collection from day one"],
                ["Trust", "Years to build a name", "A 30-year legacy from day one"]];
  s.addTable([
    [hdr("", H.dk2, H.lt1), hdr("Doing it yourself", H.dk2, H.lt1), hdr("With The Furnish Atellier", H.accent1, H.lt1)],
    ...rows.map((r, i) => r.map((t, j) => ({ text: t, options: {
      bold: j !== 1, color: j === 0 ? H.accent5 : H.dk1, fontSize: 13,
      fill: { color: i % 2 ? H.lt1 : H.lt2 } } }))),
  ], { x: 0.5, y: 2.85, w: 9.0, colW: [1.3, 3.85, 3.85], rowH: 0.4, margin: [0, 0.12, 0, 0.12], valign: "middle",
       border: { type: "solid", pt: 0.5, color: "D9DCE1" }, objectName: name("table") });
  s.addNotes("The Business Kit is given against a security amount, not sold: ₹69,000 for the first 100 founding partners and ₹1,35,000 for every partner after that. Women entrepreneurs get ₹5,000 off, and the security amount is adjusted in full once the partner's sales cross ₹7 lakh (₹7,00,000). Building a comparable range alone costs ₹10 lakh+ in catalogues and 300-400 sq. ft. of storage.");

  // ================= OUR GOAL (3 slides) =================
  pres.addSection({ title: "Our Goal" });

  // 6 - the goal
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Our Goal" });
  s.addText("05  ·  OUR GOAL", { placeholder: "kicker" });
  s.addText("5,000 Business Partners Across the Globe", { placeholder: "title" });
  T(s, "5,000", { x: 0.5, y: 1.3, w: 4.2, h: 1.15, fontSize: 80, bold: true, color: C.accent1, fontFace: "+mj-lt" });
  T(s, "Business partners by March 2032, each running their own fabric business with our support.",
    { x: 0.5, y: 2.62, w: 4.4, h: 0.65, fontSize: 15, color: C.text1, valign: "top" });
  [["30 Years", "of fabric legacy behind every partner"], ["Worldwide", "a partner network across the globe"]].forEach(([big, small], i) => {
    const x = 5.4 + i * 2.1;
    card(s, x, 1.5, 1.95, 1.45, C.background2);
    T(s, big, { x: x + 0.1, y: 1.68, w: 1.75, h: 0.55, fontSize: 22, bold: true, color: C.text2, align: "center", fontFace: "+mj-lt" });
    T(s, small, { x: x + 0.1, y: 2.25, w: 1.75, h: 0.5, fontSize: 12, color: C.accent4, align: "center", valign: "top" });
  });
  s.addShape(pres.shapes.LINE, { x: 1.2, y: 3.85, w: 7.6, h: 0, line: { color: "D9DCE1", width: 2 }, objectName: name("timeline") });
  const sizes = [0.3, 0.4, 0.5, 0.66];
  MILESTONES.forEach((m, i) => {
    const cx = 1.2 + i * (7.6 / 3), d = sizes[i];
    s.addShape(pres.shapes.OVAL, { x: cx - d / 2, y: 3.85 - d / 2, w: d, h: d, fill: { color: C.accent1 },
      line: { color: H.lt1, width: 2 }, objectName: name("milestone") });
    T(s, inr(m.partners), { x: cx - 1.0, y: 4.25, w: 2.0, h: 0.42, fontSize: 22, bold: true, color: C.text2, align: "center", fontFace: "+mj-lt" });
    T(s, m.by.toUpperCase(), { x: cx - 1.0, y: 4.67, w: 2.0, h: 0.28, fontSize: 11, bold: true, color: C.accent5, align: "center", charSpacing: 2 });
  });
  s.addNotes("Our goal is a network of 5,000 business partners across the globe by March 2032, each running their own fabric business with The Furnish Atellier's brand, collection and support. Milestones: 100 partners by March 2027, 500 by March 2028, 1,000 by March 2029 and 5,000 by March 2032.");

  // 7 - roadmap
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Our Goal" });
  s.addText("06  ·  THE ROADMAP", { placeholder: "kicker" });
  s.addText("Four Phases from 100 to 5,000 Partners", { placeholder: "title" });
  s.addChart(pres.charts.BAR, [{ name: "Business partners (cumulative)",
    labels: MILESTONES.map((m) => m.by.replace("March ", "Mar ")), values: MILESTONES.map((m) => m.partners) }], {
    x: 0.4, y: 1.4, w: 4.7, h: 3.55, barDir: "col", barGapWidthPct: 55,
    chartColors: [H.accent1], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0",
    dataLabelColor: H.dk2, dataLabelFontSize: 13, dataLabelFontBold: true, dataLabelFontFace: "+mn-lt",
    showTitle: true, title: "Business partners (cumulative)", titleFontSize: 12, titleColor: H.accent4, titleFontFace: "+mn-lt",
    catAxisLabelColor: H.dk1, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt",
    catAxisLineShow: true, catAxisLineColor: "D9DCE1",
    valAxisHidden: true, valAxisMaxVal: 5800, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showLegend: false, objectName: name("chart"),
  });
  let prev = 0;
  MILESTONES.forEach((m, i) => {
    const y = 1.45 + i * 0.87;
    card(s, 5.4, y, 4.1, 0.77, C.background2);
    numBadge(s, 5.55, y + 0.16, 0.45, i + 1);
    T(s, `${m.phase}`, { x: 6.15, y: y + 0.08, w: 1.6, h: 0.32, fontSize: 14, bold: true, color: C.text2 });
    T(s, `by ${m.by}`, { x: 7.6, y: y + 0.08, w: 1.75, h: 0.32, fontSize: 12, bold: true, color: C.accent5, align: "right" });
    T(s, i === 0 ? "100 founding partners" : `${inr(m.partners)} partners  ·  +${inr(m.partners - prev)} new partners`,
      { x: 6.15, y: y + 0.4, w: 3.2, h: 0.3, fontSize: 12, color: C.accent4 });
    prev = m.partners;
  });
  s.addNotes("Phase 1 Launch: 100 partners by March 2027. Phase 2 Build: 500 by March 2028 (400 new partners). Phase 3 Scale: 1,000 by March 2029 (500 new partners). Phase 4 Global: 5,000 partners across the globe by March 2032 (4,000 new partners) - about 1,333 new partners a year over the last three years.");

  // 8 - how we get there
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Our Goal" });
  s.addText("07  ·  HOW WE GET THERE", { placeholder: "kicker" });
  s.addText("Six Engines That Take Us to 5,000", { placeholder: "title" });
  const engines = [[fa.FaShareNodes, "Partner referrals", "₹5,000 per new partner turns every partner into a recruiter."],
                   [fa.FaPersonDress, "Women entrepreneurs", "₹5,000 off the security amount widens who can start."],
                   [fa.FaChalkboardUser, "Training at scale", "Welcome training and weekly webinars for every partner."],
                   [fa.FaPhotoFilm, "Ready digital content", "Images, videos and posts that market every partner."],
                   [fa.FaCartShopping, "More ways to earn", "The décor e-store adds affiliate income."],
                   [fa.FaAward, "30 years of trust", "Customers buy from a name they know."]];
  for (let i = 0; i < 6; i++) {
    const x = 0.5 + (i % 3) * 3.05, y = 1.45 + Math.floor(i / 3) * 1.38;
    card(s, x, y, 2.9, 1.25, C.background2);
    await badge(s, x + 0.18, y + 0.2, 0.48, engines[i][0]);
    T(s, engines[i][1], { x: x + 0.8, y: y + 0.2, w: 1.95, h: 0.48, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
    T(s, engines[i][2], { x: x + 0.18, y: y + 0.75, w: 2.6, h: 0.45, fontSize: 11, color: C.accent4, valign: "top" });
  }
  const contact = [[fa.FaUserTie, "Kamlesh Agrawal, Director"], [fa.FaPhone, "+91 98105 27231"], [fa.FaEnvelope, "adybuildcon@gmail.com"]];
  for (let i = 0; i < 3; i++) {
    const x = 0.5 + i * 3.05;
    await badge(s, x, 4.38, 0.4, contact[i][0]);
    T(s, contact[i][1], { x: x + 0.52, y: 4.38, w: 2.45, h: 0.4, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
  }
  s.addNotes("Growth comes from six engines: referral bonuses, the women-entrepreneur discount, training and weekly webinars that scale, ready digital content, extra income from the upcoming e-store, and 30 years of brand trust. Contact: Kamlesh Agrawal, Director, +91 98105 27231.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("Wrote", OUT);
}

main().catch((e) => { console.error(e); process.exit(1); });
