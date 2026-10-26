#!/usr/bin/env python
"""
Build the take-home deck as a PowerPoint file from reports/data/ and reports/figures/.

Usage, from the repo root:

    python reports/pull_deck_data.py      # on the Mac: runs the queries, writes data/
    python reports/build_charts.py        # anywhere: writes figures/
    python reports/build_deck.py          # anywhere: writes Aurora_Construction_Take_Home.pptx

Needs python-pptx. The deck is an output; this script is the source. A number that
changes means re-pulling and re-running, never editing the slides by hand. Every slide's
footer names the query its numbers came from.

The deck walks through the work in the order it happened: environment, a first look at
the data, the problems found, the staging rules that came out of them, then the four
questions, then how the answers would be delivered to two audiences and how AI was used.
"""

import csv
import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt, Emu
from lxml import etree

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGURES = HERE / "figures"
MEDIA = HERE / "media"
OUT = HERE / "Aurora_Construction_Take_Home.pptx"

# --- brand -------------------------------------------------------------------
BLUE = RGBColor(0x13, 0x68, 0xE5)      # Aurora blue, sampled from the wordmark
INK = RGBColor(0x1F, 0x29, 0x37)
MUTED = RGBColor(0x6B, 0x7B, 0x8C)
RULE = RGBColor(0xDC, 0xE3, 0xEA)
LIGHT = RGBColor(0xF1, 0xF4, 0xF8)
HI = RGBColor(0xE6, 0xF0, 0xFD)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Calibri"

SLIDE_W, SLIDE_H = 13.333, 7.5
MARGIN = 0.6
TITLE_Y, TITLE_H = 0.42, 0.9
BODY_Y = 1.45
FOOTER_Y = 6.82

NO_GRID_STYLE = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"   # "No Style, No Grid"


# --- data --------------------------------------------------------------------
def read(name: str) -> list[dict]:
    with open(DATA / f"{name}.csv", newline="") as f:
        return list(csv.DictReader(f))


def package() -> dict:
    p = DATA / "package.json"
    return json.loads(p.read_text()) if p.exists() else {}


def n(x) -> float:
    return float(x) if x not in ("", None) else 0.0


def millions(x) -> str:
    v = n(x) / 1e6
    return f"{v:.1f}M" if v < 100 else f"{v:.0f}M"


def thousands(x) -> str:
    return f"{n(x):,.0f}"


def compact(x) -> str:
    v = n(x)
    if v >= 1e6:
        return millions(v)
    if v >= 1e4:
        return f"{v/1e3:.0f}k"
    return f"{v:,.0f}"


# --- primitives --------------------------------------------------------------
class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = Inches(SLIDE_W)
        self.prs.slide_height = Inches(SLIDE_H)
        self.blank = self.prs.slide_layouts[6]
        self.pulled = package().get("pulled_at", "")[:10]
        self.count = 0

    # -- text ----------------------------------------------------------------
    def text(self, slide, x, y, w, h, paragraphs, size=14, color=INK, bold=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.1, space_after=4):
        """paragraphs: list of str, or list of lists of (text, {bold, color, size, italic})."""
        box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = anchor
        first = True
        for para in paragraphs:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.alignment = align
            p.line_spacing = line_spacing
            p.space_after = Pt(space_after)
            runs = [(para, {})] if isinstance(para, str) else para
            for txt, opts in runs:
                r = p.add_run()
                r.text = txt
                f = r.font
                f.name = FONT
                f.size = Pt(opts.get("size", size))
                f.bold = opts.get("bold", bold)
                f.italic = opts.get("italic", False)
                f.color.rgb = opts.get("color", color)
        return box

    def bullets(self, slide, x, y, w, h, items, size=14, color=INK, space_after=6):
        """Plain bullet list. Each item is a str or a list of (text, opts) runs."""
        box = self.text(slide, x, y, w, h, items, size=size, color=color, space_after=space_after)
        for p in box.text_frame.paragraphs:
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", str(Emu(Inches(0.22))))
            pPr.set("indent", str(-Emu(Inches(0.22))))
            bu = etree.SubElement(pPr, qn("a:buChar"))
            bu.set("char", "•")
        return box

    # -- shapes --------------------------------------------------------------
    def rect(self, slide, x, y, w, h, fill=LIGHT, line=None, shape=MSO_SHAPE.RECTANGLE):
        s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
        s.fill.solid()
        s.fill.fore_color.rgb = fill
        if line is None:
            s.line.fill.background()
        else:
            s.line.color.rgb = line
            s.line.width = Pt(0.75)
        s.shadow.inherit = False
        s.text_frame.text = ""
        return s

    def hline(self, slide, x, y, w, color=RULE, weight=0.75):
        ln = slide.shapes.add_connector(1, Inches(x), Inches(y), Inches(x + w), Inches(y))
        ln.line.color.rgb = color
        ln.line.width = Pt(weight)
        return ln

    def card(self, slide, x, y, w, h, heading, number, lines, size=12.5):
        self.rect(slide, x, y, w, h, fill=LIGHT)
        self.text(slide, x + 0.25, y + 0.2, w - 0.5, 0.4, [heading], size=14, bold=True)
        self.text(slide, x + 0.25, y + 0.6, w - 0.5, 0.7, [number], size=30, bold=True, color=BLUE)
        self.text(slide, x + 0.25, y + 1.35, w - 0.5, h - 1.5, lines, size=size, space_after=5)

    def stat(self, slide, x, y, w, number, label, size=34):
        self.text(slide, x, y, w, 0.65, [number], size=size, bold=True, color=BLUE)
        self.text(slide, x, y + 0.62, w, 0.5, [label], size=12, color=MUTED)

    # -- tables --------------------------------------------------------------
    def table(self, slide, x, y, widths, rows, size=11.5, row_h=0.32, highlight=None,
              align_right_from=1, header_size=None, header=True):
        """rows[0] is the header unless header=False. highlight: set of row indexes to tint."""
        highlight = highlight or set()
        n_rows, n_cols = len(rows), len(rows[0])
        shape = slide.shapes.add_table(n_rows, n_cols, Inches(x), Inches(y),
                                       Inches(sum(widths)), Inches(row_h * n_rows))
        tbl = shape.table
        tblPr = tbl._tbl.tblPr
        style = tblPr.find(qn("a:tableStyleId"))
        if style is None:
            style = etree.SubElement(tblPr, qn("a:tableStyleId"))
        style.text = NO_GRID_STYLE
        tbl.first_row = False
        tbl.horz_banding = False
        for j, w in enumerate(widths):
            tbl.columns[j].width = Inches(w)
        for i in range(n_rows):
            tbl.rows[i].height = Inches(row_h)
            for j in range(n_cols):
                cell = tbl.cell(i, j)
                cell.margin_left = cell.margin_right = Inches(0.08)
                cell.margin_top = cell.margin_bottom = Inches(0.03)
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                tf = cell.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.alignment = PP_ALIGN.RIGHT if j >= align_right_from else PP_ALIGN.LEFT
                r = p.add_run()
                r.text = str(rows[i][j])
                r.font.name = FONT
                is_header = header and i == 0
                r.font.size = Pt(header_size or size) if is_header else Pt(size)
                r.font.bold = is_header or (i in highlight) or (not header and j == 0)
                r.font.color.rgb = MUTED if is_header else INK
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT if is_header else (HI if i in highlight else WHITE)
                if is_header:
                    self._border(cell, "a:lnB", RULE, 1.0)
        return shape

    @staticmethod
    def _border(cell, side, color, width_pt):
        tcPr = cell._tc.get_or_add_tcPr()
        ln = etree.SubElement(tcPr, qn(side))
        ln.set("w", str(int(width_pt * 12700)))
        solid = etree.SubElement(ln, qn("a:solidFill"))
        clr = etree.SubElement(solid, qn("a:srgbClr"))
        clr.set("val", "%02X%02X%02X" % (color[0], color[1], color[2]))

    def caption(self, slide, x, y, w, text):
        self.text(slide, x, y, w, 0.35, [text], size=10, color=MUTED)

    # -- slide frames --------------------------------------------------------
    def content_slide(self, title, takeaway=None, source=None):
        slide = self.prs.slides.add_slide(self.blank)
        self.count += 1
        self.text(slide, MARGIN, TITLE_Y, SLIDE_W - 2 * MARGIN - 0.9, TITLE_H, [title],
                  size=26, bold=True, anchor=MSO_ANCHOR.TOP, line_spacing=1.0)
        mark = MEDIA / "aurora_mark.png"
        if mark.exists():
            slide.shapes.add_picture(str(mark), Inches(SLIDE_W - MARGIN - 0.42), Inches(0.45),
                                     height=Inches(0.46))
        self.hline(slide, MARGIN, FOOTER_Y - 0.08, SLIDE_W - 2 * MARGIN)
        if takeaway:
            self.text(slide, MARGIN, FOOTER_Y, 8.2, 0.55, [takeaway], size=12, color=INK)
        right = []
        if source:
            right.append(f"Source: {source}" + (f"  ·  data pulled {self.pulled}" if self.pulled else ""))
        right.append(f"{self.count + 1}")
        self.text(slide, SLIDE_W - MARGIN - 3.7, FOOTER_Y, 3.7, 0.55,
                  ["   ·   ".join(right)], size=9, color=MUTED, align=PP_ALIGN.RIGHT)
        return slide

    def cover(self, title, subtitle, byline):
        slide = self.prs.slides.add_slide(self.blank)
        panel_w = 5.3
        photo = MEDIA / "aurora_truck.jpg"
        if photo.exists():
            pic = slide.shapes.add_picture(str(photo), Inches(panel_w), 0,
                                           Inches(SLIDE_W - panel_w), Inches(SLIDE_H))
            src_aspect = 2576 / 1449
            box_aspect = (SLIDE_W - panel_w) / SLIDE_H
            visible = box_aspect / src_aspect          # fraction of source width shown
            pic.crop_left = pic.crop_right = (1 - visible) / 2
        wordmark = MEDIA / "aurora_wordmark.png"
        if wordmark.exists():
            slide.shapes.add_picture(str(wordmark), Inches(MARGIN), Inches(0.75), width=Inches(2.3))
        self.text(slide, MARGIN, 2.4, panel_w - MARGIN - 0.3, 1.0, [title], size=36, bold=True,
                  line_spacing=1.0)
        self.text(slide, MARGIN, 3.45, panel_w - MARGIN - 0.3, 0.6, [subtitle[0]], size=17, color=BLUE,
                  bold=True, line_spacing=1.1)
        self.text(slide, MARGIN, 4.2, panel_w - MARGIN - 0.3, 1.8, [subtitle[1]], size=14, color=INK,
                  line_spacing=1.2)
        self.text(slide, MARGIN, 6.55, panel_w - MARGIN - 0.3, 0.6, [byline], size=11, color=MUTED)
        return slide

    def figure(self, slide, name, x, y, w=None, h=None):
        path = FIGURES / name
        kwargs = {}
        if w:
            kwargs["width"] = Inches(w)
        if h:
            kwargs["height"] = Inches(h)
        return slide.shapes.add_picture(str(path), Inches(x), Inches(y), **kwargs)

    def save(self):
        self.prs.save(OUT)
        print(f"wrote {OUT.relative_to(HERE.parent)} ({self.count + 1} slides)")


# --- the slides --------------------------------------------------------------
def build():
    d = Deck()
    counts = {r["measure"]: n(r["value"]) for r in read("12_row_counts")}
    flags = {r["event_type"]: r for r in read("10_staging_flags")}
    con = flags["construction"]
    ten = read("02_q1_ten_cities")
    nyc = next(r for r in ten if r["city"] == "New York")
    phx = next(r for r in ten if r["city"] == "Phoenix")
    cmp_rows = read("07_q3_city_comparison")
    routes_all = [r for r in read("08_q4_route_exposure") if r["year"] == "all"]
    routes_year = [r for r in read("08_q4_route_exposure") if r["year"] != "all"]
    decomp = read("05_q2_decomposition_by_year")
    ny_year = read("06_q2_new_york_by_year")
    by_year = read("03_q2_ten_cities_by_year")

    # 1 — cover
    d.cover("Construction, counted",
            ("A take-home for the Data Analyst role",
             "How the road-construction dataset was loaded, checked and modelled, what it says "
             "about the ten largest cities and five Bay Area routes, and where it cannot be trusted."),
            "Andrew McDonald   ·   October 2026   ·   US Road Construction and Closures, 2016–2021")

    # 2 — what was asked, how it was built
    s = d.content_slide("What was asked, and how I chose to build it",
                        takeaway="A warehouse layout for a six-question take-home is more setup than a notebook needs; the trade is that every number here is a model someone else can run.")
    d.text(s, MARGIN, BODY_Y, 5.9, 0.4, ["The six questions"], size=15, bold=True)
    d.bullets(s, MARGIN, BODY_Y + 0.45, 5.9, 4.6, [
        "Q1  Over the past five years, which city has had the most hours of construction?",
        "Q2  How has that changed over time?",
        "Q3  Accounting for city size, how do the ten largest US cities compare?",
        "Q4  Of five candidate Bay Area routes, which carries the most construction risk?",
        "Q5  How would the Q4 answer be presented to engineers versus executives?",
        "Q6  What AI tools were used, how, and why?",
    ], size=13.5, space_after=8)
    d.text(s, 7.0, BODY_Y, 5.7, 0.4, ["The build"], size=15, bold=True)
    d.bullets(s, 7.0, BODY_Y + 0.45, 5.7, 4.6, [
        [("Postgres 17 and dbt, SQL throughout. ", {"bold": True}),
         ("The role's stack; and dbt makes every transformation a named, documented, tested model rather than a step in a notebook.", {})],
        [("Python only where SQL isn't the tool: ", {"bold": True}),
         ("loading the 2.7 GB file, drawing the charts, building this deck.", {})],
        [("Raw → staging → intermediate → marts. ", {"bold": True}),
         ("Raw is a faithful copy; every judgment lives in a model where it can be read.", {})],
        [("Flags, not filters. ", {"bold": True}),
         ("Nothing is dropped except exact duplicates. Every other call is a column, applied downstream, so the number with and without it is one query apart.", {})],
        [("A log kept as it happened ", {"bold": True}),
         ("(process.md in the repo): what was tried, what was wrong, what changed.", {})],
    ], size=13.5, space_after=8)

    # 3 — environment and load
    s = d.content_slide("Environment and load: a raw layer that is a faithful copy of the file",
                        takeaway="A typed load fails loudly on a bad value, which is the cheapest data-quality check there is; it passed on every row.",
                        source="scripts/load_raw.py, queries/12")
    boxes = [("raw", "The CSV as-is: 47 typed columns, snake_case names, nothing filtered or derived."),
             ("staging", "One row per event: deduplicated, flagged, New York rolled up."),
             ("intermediate", "Hours allocated to the months each event overlaps; route matches."),
             ("marts", "The answers: city totals, the ten normalized, route exposure.")]
    bx, bw, gap = MARGIN, 2.75, 0.3
    for i, (name, desc) in enumerate(boxes):
        x = bx + i * (bw + gap)
        d.rect(s, x, BODY_Y + 0.1, bw, 0.7, fill=BLUE if name == "raw" else LIGHT)
        d.text(s, x, BODY_Y + 0.1, bw, 0.7, [name], size=16, bold=True,
               color=WHITE if name == "raw" else INK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        d.text(s, x, BODY_Y + 0.95, bw, 1.2, [desc], size=12, color=INK)
        if i < 3:
            d.text(s, x + bw, BODY_Y + 0.1, gap, 0.7, ["→"], size=20, color=MUTED,
                   align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    d.stat(s, MARGIN, 3.55, 3.0, thousands(counts["raw rows"]), "rows loaded, every id unique")
    d.stat(s, 3.75, 3.55, 3.0, "47 → 13", "columns in the file → columns that touch the questions")
    d.stat(s, 6.9, 3.55, 3.0, "2.7 GB", "streamed in with COPY; indexes added after")
    d.stat(s, 10.05, 3.55, 2.7, "5 rows", "the routes, loaded as a versioned seed")
    d.bullets(s, MARGIN, 5.05, 12.1, 1.6, [
        "A second Postgres instance on its own port, so the case study never touches anything else on the machine.",
        "The 70 KB routes file is small, static reference data, so it is a dbt seed and lives in git. The 2.7 GB file is not seed material; it is loaded once and declared as a source.",
        "Weather, point-of-interest and twilight columns (34 of the 47) are loaded for completeness and never used.",
    ], size=12.5, space_after=5)

    # 4 — what the data is
    s = d.content_slide("What the data is, and what “hours of construction” means here",
                        takeaway="Every number that follows is hours of reported traffic impact, not hours of roadwork, and that distinction carries through to the end.",
                        source="docs/data_dictionary.md")
    d.table(s, MARGIN, BODY_Y, [2.2, 5.3], [
        ["Source", "Kaggle: US Road Construction and Closures (Moosavi), 49 states, Jan 2016 – Dec 2021"],
        ["Collection", "“Multiple APIs that provide streaming traffic incident data” fed by state DOTs, police, cameras and sensors. The providers are not named and there is no provider column."],
        ["What a row is", "One reported event: a start point, usually an end point, a start and end time, a severity of 1–4 (traffic impact), a free-text description."],
        ["What “hours” means", "end time minus start time, where the dictionary defines the end as “when the impact on traffic flow was dismissed”. Reported impact, not work done."],
        ["Event length", "“Ranging from fixing pavements to substantial projects that could take months”, in the author's words. Multi-month events are expected, not errors."],
    ], size=11.5, row_h=0.62, align_right_from=99, header=False)
    d.text(s, 8.5, BODY_Y, 4.2, 0.4, ["What it is not"], size=15, bold=True)
    d.bullets(s, 8.5, BODY_Y + 0.5, 4.2, 4.5, [
        "Not a census of construction. It is whatever the feeds broadcast, and feed coverage varies by state and over time.",
        "Not a road geometry. An event is two points; the road between them is unknown.",
        "Not observed times on every row. Many starts and ends are administrative stamps shared by thousands of rows.",
        "Not one record per project. The same closure can be re-published daily as a fresh event.",
    ], size=12.5, space_after=7)

    # 5 — three problems
    dup = counts["duplicates removed"]
    s = d.content_slide("Three problems found before any question was answered",
                        takeaway="Each of these changes an answer. Each came from reading the data before modelling it, and each became a staging rule.",
                        source="queries/12, process.md §8")
    cw, ch, cy = 3.9, 4.75, BODY_Y + 0.05
    d.card(s, MARGIN, cy, cw, ch, "Duplicate reports",
           f"{thousands(dup)} rows",
           [f"{dup / counts['raw rows'] * 100:.1f}% of the file. The same event, re-pulled by the provider on a different day: the weather columns differ, nothing else does.",
            [("Rule: ", {"bold": True}), ("one row per start, end, start coordinates and description.", {})]])
    d.card(s, MARGIN + cw + 0.2, cy, cw, ch, "New York is five cities",
           "Five boroughs",
           ["The boroughs appear as separate cities, so city = “New York” is Manhattan. Each borough is exactly one New York county.",
            [("Rule: ", {"bold": True}), ("roll up the five county-boroughs to one city; check the other nine for the same trap (Los Angeles is the reverse case).", {})]])
    d.card(s, MARGIN + 2 * (cw + 0.2), cy, cw, ch, "Closures that aren't roadwork",
           f"{thousands(counts['seasonal closures'])} events",
           ["Mountain passes “closed for the winter”. The first pattern matched the word winter and swept up Winter St and Winter Haven Dr; rebuilt from the real phrasings.",
            [("Rule: ", {"bold": True}), ("flag as seasonal closure, keep the rows, exclude downstream. Under 0.1% of hours.", {})]])

    # 6 — staging
    s = d.content_slide("Staging: every judgment is a flag, applied downstream",
                        takeaway="Nothing is dropped except exact duplicates, so any answer can be re-run with a rule switched off.",
                        source="stg_construction, queries/10")
    d.table(s, MARGIN, BODY_Y, [2.6, 6.3, 3.2], [
        ["Column", "What it does", "Rows touched"],
        ["dedup (row_number)", "Keeps the lowest id per start, end, start coordinates and description", f"{thousands(dup)} removed"],
        ["city_normalized", "Five NY county-boroughs → New York; every other city as reported", "all New York rows"],
        ["event_type", "seasonal_closure when the description says so; else construction", f"{thousands(counts['seasonal closures'])} seasonal"],
        ["is_batch_start / end", "The exact timestamp is shared by 100+ rows: an administrative stamp, not an observed time", f"{thousands(con['batch_start'])} / {thousands(con['batch_end'])}  ({n(con['batch_start'])/n(con['events'])*100:.1f}% / {n(con['batch_end'])/n(con['events'])*100:.1f}%)"],
        ["is_open_at_extract", "end time equals the extract cutoff, 2022-01-01", f"{thousands(con['open_at_extract'])}"],
        ["duration_hours", "end minus start, in hours", f"mean {con['mean_hours']}, median {n(con['median_hours']):.0f}"],
    ], size=11.5, row_h=0.46, align_right_from=2)
    d.bullets(s, MARGIN, 4.9, 12.1, 1.7, [
        "Tests on the staged table: unique on the dedup key, not null on time, city and state, severity in 1–4, start before end. No negative durations exist in this extract.",
        "The mean of 398 hours against a median of 7 says the totals are carried by a long tail of multi-day advisories, not by the typical event. That is why Q1 shows events and hours side by side.",
    ], size=12.5, space_after=6)

    # 7 — Q1
    ratio_nb = n(nyc["hours_excl_batch"]) / n(phx["hours_excl_batch"])
    s = d.content_slide("Q1 — New York has the most construction hours, under this definition",
                        takeaway=f"New York averaged about {thousands(nyc['avg_concurrent'])} active construction advisories at any moment of the five years; Phoenix about {thousands(phx['avg_concurrent'])}.",
                        source="queries/02, int_city_month_hours")
    d.figure(s, "q1_ten_cities.png", MARGIN, BODY_Y - 0.05, w=7.9)
    d.caption(s, MARGIN, 4.75, 7.9, "Ten largest US cities, 2017–2021, deduplicated, seasonal closures excluded. Hours are allocated to the months each event was active.")
    d.text(s, 8.9, BODY_Y, 3.8, 0.4, ["Two things that change the answer"], size=14, bold=True)
    d.bullets(s, 8.9, BODY_Y + 0.5, 3.8, 3.2, [
        [("Manhattan alone would not lead. ", {"bold": True}), ("The five-borough rollup is what puts New York first.", {})],
        [("Drop the batch-stamped rows and it is a near tie: ", {"bold": True}),
         (f"{millions(nyc['hours_excl_batch'])} to {millions(phx['hours_excl_batch'])} ({ratio_nb:.2f}×).", {})],
        "Phoenix outranking Los Angeles and Chicago by this much is more plausibly a reporting effect than a construction one: the feeds aggregate what each state DOT publishes.",
    ], size=12.5, space_after=7)
    d.text(s, 8.9, 5.0, 3.8, 1.5, [[("Answer: ", {"bold": True}),
        ("New York, with Phoenix close behind and both far ahead of the rest. The order of those two depends on two definitional choices, both stated.", {})]], size=12.5)

    # 8 — Q2 small multiples
    jump = {r["city"]: {} for r in by_year}
    for r in by_year:
        jump[r["city"]][int(r["year"])] = n(r["hours"])
    ny_share = jump["New York"][2021] / sum(jump["New York"].values()) * 100
    s = d.content_slide("Q2 — every city jumped 3–10× in 2021: the source changed, not the roads",
                        takeaway=f"{ny_share:.0f}% of New York's five-year total is 2021 alone, so “the past five years” is mostly one year of a different feed.",
                        source="queries/03, int_city_month_hours")
    pic = d.figure(s, "q2_city_small_multiples.png", MARGIN + 0.6, BODY_Y - 0.1, h=4.75)
    d.caption(s, MARGIN, (pic.top + pic.height) / 914400 + 0.1, 12.1, "Ten cities in ten states under different DOTs do not all have an eight-fold construction boom in the same year. Presenting the 2021 line as “construction increased” would be wrong.")

    # 9 — Q2 three changes
    s = d.content_slide("Q2 — three changes in the feed, dated from the data itself",
                        takeaway="The trend is readable 2017 to about September 2021; after that the file is missing the events that were still open when it was cut.",
                        source="queries/04, queries/05")
    d.figure(s, "q2_national_monthly.png", MARGIN, BODY_Y - 0.1, w=7.6)
    d.text(s, 8.5, BODY_Y, 4.3, 0.4, ["By start year, construction events"], size=13, bold=True)
    d.table(s, 8.5, BODY_Y + 0.45, [0.7, 1.0, 0.85, 0.85, 0.9], [
        ["Year", "Events", "Median h", "% = 96 h", "% < 1 h"]] + [
        [r["year"], compact(r["events"]), f"{n(r['median_hours']):.0f}", r["pct_96h"], r["pct_sub_hour"]] for r in decomp
    ], size=10.5, row_h=0.3, header_size=10.5)
    d.bullets(s, 8.5, 4.05, 4.3, 2.7, [
        [("2018–19: a 96-hour template. ", {"bold": True}), ("Up to 28% of events carry a default four-day lifespan. Gone by 2021.", {})],
        [("Sep 2020: a short-event feed. ", {"bold": True}), ("Events ×1.8 in a month, hours flat; by 2021 one event in four is under an hour.", {})],
        [("Mar–Apr 2021: the hours step. ", {"bold": True}), ("Monthly hours double twice. Short events don't carry hours; this is a feed of long advisories, concentrated in big metros.", {})],
    ], size=11.5, space_after=5)

    # 10 — NYC decomposition
    ny21 = next(r for r in ny_year if r["year"] == "2021")
    ny19 = next(r for r in ny_year if r["year"] == "2019")
    s = d.content_slide("Q2 — in New York, 2021 brought twenty times the month-long advisories of 2019",
                        takeaway="Two feeds with two signatures arrived in the same year: one publishing long advisories that carry the hours, one publishing congestion pings that carry almost none.",
                        source="queries/06, stg_construction")
    d.table(s, MARGIN, BODY_Y, [0.9, 1.3, 1.2, 1.3, 1.5, 1.6], [
        ["Year", "Events", "Mean hours", "% under 1 h", "% over 30 days", "Events over 30 days"]] + [
        [r["year"], thousands(r["events"]), r["mean_hours"], r["pct_sub_hour"], r["pct_over_30_days"], thousands(r["events_over_30_days"])] for r in ny_year
    ], size=12, row_h=0.4, highlight={len(ny_year)})
    d.caption(s, MARGIN, BODY_Y + 0.4 * (len(ny_year) + 1) + 0.05, 7.8, "New York, five boroughs, construction events by start year.")
    d.stat(s, 9.0, BODY_Y + 0.1, 3.7, f"{thousands(ny19['events_over_30_days'])} → {thousands(ny21['events_over_30_days'])}",
           "advisories lasting 30+ days, 2019 → 2021. These carry the hours.", size=28)
    d.stat(s, 9.0, BODY_Y + 1.7, 3.7, f"{ny21['pct_sub_hour']}%",
           "of 2021 events are under an hour: congestion pings, almost no hours.", size=28)
    d.bullets(s, MARGIN, 4.75, 12.1, 1.9, [
        [("A conclusion corrected along the way. ", {"bold": True}),
         ("Only 60 rows end on the extract date, so right-censoring was first judged negligible. But November–December 2021 events stay high while hours fall 58% from the October peak, against a seasonal dip of about 20% in earlier years. The likelier reading: events still open at extraction are absent from the file, not truncated. The last two to three months are missing their long-running advisories.", {})],
    ], size=12, space_after=4)

    # 11 — Q3
    s = d.content_slide("Q3 — accounting for city size does not change the ranking",
                        takeaway="Normalizing moves one city one place. The spread is the finding, and the spread is about reporting, which this dataset cannot prove on its own.",
                        source="queries/07, fct_city_comparison")
    d.figure(s, "q3_rank_bump.png", MARGIN, BODY_Y - 0.1, h=4.6)
    tx = 6.75
    d.table(s, tx, BODY_Y, [1.55, 1.2, 1.4, 1.55], [
        ["City", "Hours", "per sq mile", "per 100k residents"]] + [
        [r["city"], millions(r["hours"]), compact(r["hours_per_sq_mi"]), compact(r["hours_per_100k"])] for r in cmp_rows
    ], size=10.5, row_h=0.285, header_size=10.5)
    d.rect(s, tx, 4.75, 5.95, 1.85, fill=LIGHT)
    d.text(s, tx + 0.2, 4.85, 5.6, 1.7, [
        [("Hypothesis, not shown by the table. ", {"bold": True}),
         ("New York has 81× San Diego's hours per square mile. No two large US cities plausibly differ 80-fold in roadwork; the likelier explanation is that feed coverage varies by state DOT. ", {}),
         ("What would test it: ", {"bold": True}),
         ("a provider fingerprint by state (two spellings of the wind column mark two feeds), description templates by state, and an outside benchmark such as FHWA state DOT outlay per lane-mile.", {})],
    ], size=11)

    # 12 — Q4
    rank_by_year = {}
    for r in routes_year:
        rank_by_year.setdefault(r["year"], {})[int(r["rank_hours_per_mile"])] = r["path_name"].replace("SF -> ", "").replace("Berkley", "Berkeley")
    top = routes_all[0]
    s = d.content_slide("Q4 — SF → Berkeley carries the most construction per mile, and the leader has changed every two years",
                        takeaway="Stable: the three bridge routes are always the top three and Pacifica is at or near the bottom every year. Unstable: which bridge route leads.",
                        source="queries/08, fct_route_exposure")
    d.figure(s, "q4_routes.png", MARGIN, BODY_Y - 0.1, w=8.3)
    d.text(s, 9.3, BODY_Y, 3.4, 0.4, ["Leader by year, hours per mile"], size=13, bold=True)
    d.table(s, 9.3, BODY_Y + 0.45, [0.7, 1.35, 1.35], [
        ["Year", "1st", "2nd"]] + [
        [y, rank_by_year[y][1], rank_by_year[y][2]] for y in sorted(rank_by_year)
    ], size=11, row_h=0.32, align_right_from=99, header_size=10.5)
    d.bullets(s, 9.3, 4.05, 3.4, 2.7, [
        f"Five-year: Berkeley {compact(top['hours_per_mile'])} hours per mile; severity-weighting gives the same order.",
        f"Berkeley's 2021 is {n(next(r for r in routes_year if r['path_name']==top['path_name'] and r['year']=='2021')['hours'])/n(top['hours'])*100:.0f}% of its five-year total: the same feed change as the cities.",
        "San Leandro has 334 long events to Berkeley's 126 and is the route most likely undercounted.",
    ], size=11.5, space_after=5)
    d.caption(s, MARGIN, 5.45, 8.3, "Hours per route-mile = construction hours of matched events ÷ route length. Berkeley and San Leandro share the Bay Bridge approach, so bridge work counts for both.")

    # 13 — Q4 validation
    desc = read("09_q4_berkeley_2021_descriptions")
    s = d.content_slide("Q4 — what the model matched: the Berkeley route, 2021",
                        takeaway="I-80 at Ashby, Cleveland St, the Bay Bridge piers, Treasure Island, the Yerba Buena tunnel: the events a person would expect, found without a spatial extension.",
                        source="queries/09, int_route_events")
    d.table(s, MARGIN, BODY_Y, [6.6, 0.9, 1.0], [
        ["Description (as published)", "Events", "Hours"]] + [
        [r["description"][:95], r["events"], compact(r["hours"])] for r in desc[:11]
    ], size=10.5, row_h=0.36, header_size=10.5)
    d.text(s, 9.5, BODY_Y, 3.2, 0.4, ["How “near the route” was decided"], size=13, bold=True)
    d.bullets(s, 9.5, BODY_Y + 0.5, 3.2, 4.4, [
        "Each route is ~700 points a few dozen metres apart. An event matches if any of its points is within 100 m of one.",
        f"An event is its start point, its end point, and points every 50 m along the straight line between them when it is 5 miles or shorter: {n(counts['bay area events']) - n(counts['bay area events over 5 miles']):,.0f} of {thousands(counts['bay area events'])} Bay Area events.",
        f"The {thousands(counts['bay area events over 5 miles'])} longer events are matched on endpoints only and counted per route, so the undercount is visible.",
        "Plain SQL: a 100 m grid join, no PostGIS.",
    ], size=11.5, space_after=6)

    # 14 — Q5
    s = d.content_slide("Q5 — the same finding, delivered two ways",
                        takeaway="The uncertainty does not go away for executives. It gets compressed into a confidence label instead of a table.")
    col_w = 5.85
    for i, (head, items) in enumerate([
        ("Engineering ICs: software, perception, planning", [
            "Lead with the method and its limits: the 100 m buffer, the straight-line approximation, the long-event undercount, the shared Bay Bridge approach.",
            "Show the year-by-year table. “The leader changed every two years” is the finding, not a caveat.",
            "Give the matched-event list so they can check it against roads they know.",
            "Name what would make it hold up: road-snapped geometry, a provider ID per event, re-published advisories chained into one, exposure per road segment rather than per route.",
            "Hand over the models. They will want to re-run it with their own buffer.",
        ]),
        ("Business and operations executives", [
            "Lead with the decision: if one route runs for a year, Pacifica minimizes construction exposure and Berkeley maximizes it, by about 2× per mile.",
            "State confidence in one line: high on the bottom of the ranking, moderate on the top, because the order among the three bridge routes shifts year to year.",
            "One chart (hours per mile by route), one number per route, no table of years.",
            "Translate hours into something operational: average concurrent advisories along the route, or expected work zones per trip.",
            "Assumptions and the data's provenance on one backup slide, offered, not presented.",
        ]),
    ]):
        x = MARGIN + i * (col_w + 0.4)
        d.rect(s, x, BODY_Y, col_w, 0.55, fill=LIGHT)
        d.text(s, x + 0.2, BODY_Y, col_w - 0.4, 0.55, [head], size=14, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        d.bullets(s, x + 0.2, BODY_Y + 0.75, col_w - 0.4, 4.4, items, size=12.5, space_after=8)

    # 15 — Q6
    s = d.content_slide("Q6 — how AI was used, and where it was wrong",
                        takeaway="AI wrote most of the code and none of the decisions. The log in the repo records which was which, including the three times it was wrong and how each was caught.",
                        source="process.md")
    d.text(s, MARGIN, BODY_Y, 5.9, 0.4, ["How"], size=15, bold=True)
    d.bullets(s, MARGIN, BODY_Y + 0.45, 5.9, 4.6, [
        [("ChatGPT ", {"bold": True}), ("walked me through the environment: a second Postgres instance, the clone, the venv, dbt. It said what to run; I ran it and read the output.", {})],
        [("Claude ", {"bold": True}), ("as consultant and code-writer. I set the rules (minimal intervention, no files unless asked, flags not filters) and made every call: the dedup key, the seasonal-closure words, the 2017–2021 window, the 100 m buffer, which year to lead with.", {})],
        [("What I did myself: ", {"bold": True}), ("ran every command and query, read every grid, pushed back when a claim outran the evidence, and kept the log.", {})],
        [("A typical ask: ", {"bold": True}), ("“We need to dedupe rows that are the same place with the same timestamps. I want to use the description to separate construction from winter closures. Thoughts?”", {"italic": True})],
    ], size=12.5, space_after=8)
    d.text(s, 7.0, BODY_Y, 5.7, 0.4, ["Where it was wrong, and caught"], size=15, bold=True)
    d.bullets(s, 7.0, BODY_Y + 0.45, 5.7, 4.6, [
        [("“This Mac has no Postgres.” ", {"bold": True}), ("Its shell runs in a Linux VM beside the Mac and could not see the Mac's tools. Postgres 17 was installed. Caught on the first exchange.", {})],
        [("A hypothesis written as a finding. ", {"bold": True}), ("“The spread is reporting coverage” was asserted; the table shows a spread, not its cause. Rewritten as a hypothesis with the tests that would settle it.", {})],
        [("The winter regex. ", {"bold": True}), ("My word list, its pattern; neither of us anticipated Winter St. Found by exporting the matches and reading them.", {})],
        [("Why this way: ", {"bold": True}), ("the brief allows AI and says the insight has to be mine. Keeping the judgment calls and the verification on my side, and logging them, is how that stays true.", {})],
    ], size=12.5, space_after=8)

    # 16 — assumptions and alternatives
    s = d.content_slide("Assumptions made, and what I would do with more time",
                        takeaway="Every assumption is a line someone at Aurora could confirm or overturn; each is logged with what would change if it fell.")
    d.text(s, MARGIN, BODY_Y, 6.3, 0.4, ["Assumptions"], size=15, bold=True)
    d.table(s, MARGIN, BODY_Y + 0.45, [0.45, 5.85], [
        ["A1", "“City” is the municipality; New York is its five county-boroughs."],
        ["A2", "Rows sharing start, end, start coordinates and description are one event."],
        ["A3", "“Past five years” is the five complete years 2017–2021."],
        ["A4", "Seasonal closures are not construction; descriptions identify them."],
        ["A5", "Hours of reported traffic impact stand in for hours of roadwork."],
        ["A6", "An event is located by its endpoints; the road between is unknown."],
        ["A7", "“Near a route” is within 100 m; events ≤ 5 miles follow a straight line."],
        ["A8", "Raw counts reflect how much each DOT publishes as much as how much work exists."],
    ], size=11.5, row_h=0.4, align_right_from=99, header=False)
    d.text(s, 7.4, BODY_Y, 5.3, 0.4, ["With more time"], size=15, bold=True)
    d.bullets(s, 7.4, BODY_Y + 0.45, 5.3, 4.8, [
        "Road miles as the Q3 denominator: OpenStreetMap drive-network length inside each city boundary, so hours per road-mile.",
        "Chain re-published advisories into one event, so a five-month closure is five months, not sixty five-hour rows.",
        "Separate the feeds: the two spellings in the wind column date the provider changes without a provider ID.",
        "Snap events to road geometry and score exposure per road segment, which is what a planner can act on.",
        "Simpler, not more sophisticated: the whole thing in one notebook with DuckDB reading the CSV directly, for a one-off.",
    ], size=12.5, space_after=8)

    # 17 — appendix: where every number comes from
    s = d.content_slide("Appendix — where every number comes from",
                        takeaway="reports/pull_deck_data.py runs these against the database and writes one CSV each; build_charts.py and build_deck.py read the CSVs and nothing else.")
    d.table(s, MARGIN, BODY_Y, [1.1, 3.6, 4.0, 3.4], [
        ["Slides", "Query", "Reads", "Shows"],
        ["3", "queries/12_row_counts", "raw, stg_construction", "row counts at each layer"],
        ["5–6", "queries/10_staging_flags", "stg_construction", "flag counts, mean and median hours"],
        ["7", "queries/02_q1_ten_cities", "int_city_month_hours", "Q1 totals, concurrency"],
        ["8", "queries/03_q2_ten_cities_by_year", "int_city_month_hours", "Q2 small multiples"],
        ["9", "queries/04, 05", "int_city_month_hours, stg_construction", "monthly totals; by-year decomposition"],
        ["10", "queries/06_q2_new_york_by_year", "stg_construction", "New York by year"],
        ["11", "queries/07_q3_city_comparison", "fct_city_comparison", "Q3 normalized ranking"],
        ["12", "queries/08_q4_route_exposure", "fct_route_exposure", "Q4 by route and year"],
        ["13", "queries/09_q4_berkeley_2021_descriptions", "int_route_events", "matched descriptions"],
        ["—", "queries/11_duration_distribution", "stg_construction", "the 96 h and sub-hour templates (log only)"],
    ], size=11, row_h=0.38, align_right_from=99, header_size=11)

    d.save()


if __name__ == "__main__":
    build()
