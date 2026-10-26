#!/usr/bin/env python
"""
Draw the deck's figures from the CSVs in reports/data/ into reports/figures/.

Usage, from the repo root:

    python reports/build_charts.py

Needs matplotlib only. Reads the grids written by pull_deck_data.py; never touches the
database. Every figure names the query it was drawn from in its filename and caption.

Chart conventions (kept the same on every figure so the deck reads as one system):
one hue for a single measure, a fixed five-colour set for the five routes, thin marks,
quiet grid, direct labels where they help and a legend wherever there is more than one
series, and no chart with two y-axes — two measures get two panels.
"""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGURES = HERE / "figures"

# --- palette -----------------------------------------------------------------
BLUE = "#1368E5"          # Aurora blue, sampled from the wordmark
BLUE_LIGHT = "#9DC2F5"
INK = "#1F2937"
MUTED = "#6B7B8C"
GRID = "#DCE3EA"
ROUTE_COLOURS = {        # validated for colour-vision separation and contrast
    "SF -> Berkley": "#1368E5",
    "SF -> San Rafael": "#D9480F",
    "SF -> San Leandro": "#2E8B57",
    "SF -> San Mateo": "#8E44AD",
    "SF -> Pacifica": "#B8860B",
}
ROUTE_LABELS = {k: k.replace("SF -> ", "").replace("Berkley", "Berkeley") for k in ROUTE_COLOURS}

plt.rcParams.update({
    "font.family": ["Arial", "Liberation Sans", "DejaVu Sans"],
    "font.size": 11,
    "text.color": INK,
    "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED,
    "axes.titlecolor": INK,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "legend.frameon": False,
    "legend.fontsize": 10,
    "savefig.dpi": 200,
    "savefig.facecolor": "white",
})


# --- helpers -----------------------------------------------------------------
def read(name: str) -> list[dict]:
    with open(DATA / f"{name}.csv", newline="") as f:
        return list(csv.DictReader(f))


def num(s: str) -> float:
    return float(s) if s not in ("", None) else 0.0


def fmt_compact(x, _pos=None) -> str:
    """107684891 -> '108M', 29390 -> '29k', 586 -> '586'."""
    x = float(x)
    if abs(x) >= 1e6:
        v = x / 1e6
        return f"{v:.0f}M" if v >= 10 else f"{v:.1f}M"
    if abs(x) >= 1e3:
        v = x / 1e3
        return f"{v:.0f}k" if v >= 10 else f"{v:.1f}k"
    return f"{x:.0f}"


def tidy(ax, left=True, bottom=True):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_visible(left)
    ax.spines["bottom"].set_visible(bottom)
    ax.tick_params(length=0)


def save(fig, name: str):
    FIGURES.mkdir(exist_ok=True)
    path = FIGURES / name
    fig.savefig(path, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print(f"  wrote {path.relative_to(HERE.parent)}")


# --- figure 1: Q1, the ten cities --------------------------------------------
def fig_q1_ten_cities():
    rows = read("02_q1_ten_cities")
    rows.sort(key=lambda r: num(r["hours"]))              # ascending so the top city is at the top
    cities = [r["city"] for r in rows]
    hours = [num(r["hours"]) for r in rows]
    events = [num(r["events"]) for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True,
                                   gridspec_kw={"wspace": 0.12})
    for ax, values, title in ((ax1, hours, "Construction hours, 2017–2021"),
                              (ax2, events, "Construction events, 2017–2021")):
        bars = ax.barh(cities, values, color=BLUE, height=0.62)
        ax.set_title(title, loc="left")
        ax.xaxis.set_major_formatter(FuncFormatter(fmt_compact))
        ax.grid(axis="y", visible=False)
        tidy(ax, left=False)
        xmax = max(values)
        ax.set_xlim(0, xmax * 1.18)
        for bar, v in zip(bars, values):
            ax.text(bar.get_width() + xmax * 0.015, bar.get_y() + bar.get_height() / 2,
                    fmt_compact(v), va="center", ha="left", fontsize=10, color=INK)
    ax1.tick_params(axis="y", labelsize=11, colors=INK)
    save(fig, "q1_ten_cities.png")


# --- figure 2: Q2, small multiples by year -----------------------------------
def fig_q2_small_multiples():
    rows = read("03_q2_ten_cities_by_year")
    order = [r["city"] for r in read("02_q1_ten_cities")]     # same order as Q1, by hours
    by_city = {c: {} for c in order}
    for r in rows:
        by_city[r["city"]][int(r["year"])] = num(r["hours"])
    years = [2017, 2018, 2019, 2020, 2021]

    fig, axes = plt.subplots(2, 5, figsize=(11, 4.6), sharey=True,
                             gridspec_kw={"wspace": 0.08, "hspace": 0.55})
    for ax, city in zip(axes.flat, order):
        vals = [by_city[city].get(y, 0) for y in years]
        colours = [BLUE_LIGHT] * 4 + [BLUE]
        ax.bar([str(y)[2:] for y in years], vals, color=colours, width=0.7)
        ax.set_yscale("log")
        ax.set_ylim(5e4, 2e8)
        ax.yaxis.set_major_formatter(FuncFormatter(fmt_compact))
        ax.set_title(city, loc="left", fontsize=11)
        ax.grid(axis="x", visible=False)
        tidy(ax, left=False)
        ax.tick_params(axis="x", labelsize=9)
        ratio = vals[4] / vals[3] if vals[3] else 0
        ax.text(0.04, 0.95, f"{ratio:.0f}× in 2021", transform=ax.transAxes,
                ha="left", va="top", fontsize=9.5, color=INK, fontweight="bold")
        ax.tick_params(axis="y", which="minor", left=False)
    for ax in axes[:, 0]:
        ax.tick_params(axis="y", labelsize=9)
    fig.suptitle("Construction hours by year, ten largest cities (log scale; 2021 in dark blue)",
                 x=0.125, y=0.99, ha="left", fontsize=12, fontweight="bold", color=INK)
    save(fig, "q2_city_small_multiples.png")


# --- figure 3: Q2, national monthly ------------------------------------------
def fig_q2_national_monthly():
    rows = read("04_q2_national_monthly")
    months = [r["month"][:7] for r in rows]
    events = [num(r["events"]) for r in rows]
    hours = [num(r["hours"]) for r in rows]
    x = list(range(len(months)))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 4.9), sharex=True,
                                   gridspec_kw={"hspace": 0.35})
    for ax, vals, title in ((ax1, events, "Construction events per month, all cities"),
                            (ax2, hours, "Construction hours per month, all cities")):
        ax.plot(x, vals, color=BLUE, linewidth=2)
        ax.set_title(title, loc="left")
        ax.yaxis.set_major_formatter(FuncFormatter(fmt_compact))
        ax.set_ylim(0, max(vals) * 1.25)
        ax.grid(axis="x", visible=False)
        tidy(ax, left=False)
    ticks = [i for i, m in enumerate(months) if m.endswith("-01")]
    ax2.set_xticks(ticks)
    ax2.set_xticklabels([months[i][:4] for i in ticks])

    def note(ax, vals, label, text, text_x_label, frac_y, ha="center"):
        i = months.index(label)
        tx = months.index(text_x_label)
        ax.annotate(text, xy=(i, vals[i]), xytext=(tx, ax.get_ylim()[1] * frac_y),
                    ha=ha, va="top", fontsize=9.5, color=INK,
                    arrowprops={"arrowstyle": "->", "color": MUTED, "linewidth": 0.9,
                                "shrinkB": 4})

    note(ax1, events, "2020-09", "Sep 2020: a short-event feed starts\n(events ×1.8, hours flat)",
         "2019-06", 0.95)
    note(ax2, hours, "2021-04", "Mar–Apr 2021: hours double\ntwo months running",
         "2019-11", 0.95)
    note(ax2, hours, "2021-12", "Nov–Dec 2021: still-open\nevents absent from the extract",
         "2021-12", 0.995, ha="right")
    save(fig, "q2_national_monthly.png")


# --- figure 4: Q3, rank under three definitions ------------------------------
def fig_q3_rank_bump():
    rows = read("07_q3_city_comparison")
    metrics = [("rank_raw_hours", "Raw hours"),
               ("rank_per_sq_mi", "Per square mile"),
               ("rank_per_capita", "Per 100k residents")]
    highlight = {"Phoenix": "#D9480F", "New York": BLUE}

    fig, ax = plt.subplots(figsize=(6.2, 4.8))
    for r in rows:
        ranks = [int(r[m]) for m, _ in metrics]
        colour = highlight.get(r["city"], "#B9C2CC")
        width = 2.4 if r["city"] in highlight else 1.6
        ax.plot([0, 1, 2], ranks, color=colour, linewidth=width, marker="o", markersize=6,
                markerfacecolor="white", markeredgewidth=1.6, zorder=3 if r["city"] in highlight else 2)
        ax.text(-0.08, ranks[0], r["city"], ha="right", va="center", fontsize=10,
                color=INK if r["city"] in highlight else MUTED)
        ax.text(2.08, ranks[2], r["city"], ha="left", va="center", fontsize=10,
                color=INK if r["city"] in highlight else MUTED)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([t for _, t in metrics], fontsize=10.5, color=INK)
    ax.set_yticks(range(1, 11))
    ax.set_yticklabels([f"{i}" for i in range(1, 11)], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(-0.9, 2.9)
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("Rank among the ten", color=MUTED)
    tidy(ax, left=False, bottom=False)
    ax.set_title("Where each city ranks under three definitions", loc="left")
    save(fig, "q3_rank_bump.png")


# --- figure 5: Q4, routes -----------------------------------------------------
def fig_q4_routes():
    rows = read("08_q4_route_exposure")
    years = [2017, 2018, 2019, 2020, 2021]
    by_route = {}
    totals = {}
    for r in rows:
        if r["year"] == "all":
            totals[r["path_name"]] = num(r["hours_per_mile"])
        else:
            by_route.setdefault(r["path_name"], {})[int(r["year"])] = num(r["hours_per_mile"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4),
                                   gridspec_kw={"width_ratios": [1.5, 1], "wspace": 0.3})
    for route, colour in ROUTE_COLOURS.items():
        vals = [by_route[route].get(y, 0) for y in years]
        ax1.plot(years, vals, color=colour, linewidth=2, marker="o", markersize=5,
                 markerfacecolor="white", markeredgewidth=1.6, label=ROUTE_LABELS[route])
    ax1.set_title("Construction hours per route-mile, by year (log scale)", loc="left")
    ax1.set_yscale("log")
    ax1.set_yticks([500, 1000, 2000, 5000, 10000, 20000])
    ax1.yaxis.set_major_formatter(FuncFormatter(fmt_compact))
    ax1.tick_params(axis="y", which="minor", left=False)
    ax1.set_xticks(years)
    ax1.set_xlim(2016.8, 2021.2)
    ax1.grid(axis="x", visible=False)
    ax1.legend(loc="upper left", ncol=1)
    tidy(ax1, left=False)

    order = sorted(totals, key=totals.get)
    bars = ax2.barh([ROUTE_LABELS[r] for r in order], [totals[r] for r in order],
                    color=[ROUTE_COLOURS[r] for r in order], height=0.62)
    ax2.set_title("Hours per route-mile, 2017–2021", loc="left")
    ax2.xaxis.set_major_formatter(FuncFormatter(fmt_compact))
    ax2.grid(axis="y", visible=False)
    xmax = max(totals.values())
    ax2.set_xlim(0, xmax * 1.2)
    for bar, r in zip(bars, order):
        ax2.text(bar.get_width() + xmax * 0.02, bar.get_y() + bar.get_height() / 2,
                 fmt_compact(totals[r]), va="center", fontsize=10, color=INK)
    tidy(ax2, left=False)
    ax2.tick_params(axis="y", colors=INK, labelsize=10.5)
    save(fig, "q4_routes.png")


if __name__ == "__main__":
    print("building figures from reports/data/")
    fig_q1_ten_cities()
    fig_q2_small_multiples()
    fig_q2_national_monthly()
    fig_q3_rank_bump()
    fig_q4_routes()
