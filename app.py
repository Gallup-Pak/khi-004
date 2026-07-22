import os
import glob
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

# =========================================================================
# PAGE CONFIG
# =========================================================================
st.set_page_config(
    page_title="Pakistan Climate Dashboard",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================================
# THEME PALETTES (Light / Dark switch)
# =========================================================================
DARK = dict(
    BG="#0b1220", SURFACE="#111a2b", SURFACE_2="#16233a", BORDER="#223049",
    ACCENT="#22d3ee", ACCENT_2="#38bdf8", WARM="#f97316", RAIN="#38bdf8",
    TEXT="#f8fafc", SUBTEXT="#94a3b8", GRID="#1f2b40",
    LOGO_BG="#ffffff",
    CITY_COLORS={
        "Karachi": "#22d3ee", "Lahore": "#fb923c", "Islamabad": "#a3e635",
        "Peshawar": "#f472b6", "Quetta": "#facc15", "Muzaffarabad": "#818cf8",
    },
)
LIGHT = dict(
    BG="#f4f6fb", SURFACE="#ffffff", SURFACE_2="#eef2f9", BORDER="#dde3ee",
    ACCENT="#0891b2", ACCENT_2="#0369a1", WARM="#c2410c", RAIN="#0369a1",
    TEXT="#0f172a", SUBTEXT="#55617a", GRID="#e6eaf2",
    LOGO_BG="#ffffff",
    CITY_COLORS={
        "Karachi": "#0891b2", "Lahore": "#c2410c", "Islamabad": "#4d7c0f",
        "Peshawar": "#be185d", "Quetta": "#a16207", "Muzaffarabad": "#4338ca",
    },
)

if "theme_dark" not in st.session_state:
    st.session_state.theme_dark = True

PAL = DARK if st.session_state.theme_dark else LIGHT
BG, SURFACE, SURFACE_2, BORDER = PAL["BG"], PAL["SURFACE"], PAL["SURFACE_2"], PAL["BORDER"]
ACCENT, ACCENT_2, WARM, RAIN = PAL["ACCENT"], PAL["ACCENT_2"], PAL["WARM"], PAL["RAIN"]
TEXT, SUBTEXT, GRID, LOGO_BG = PAL["TEXT"], PAL["SUBTEXT"], PAL["GRID"], PAL["LOGO_BG"]
CITY_COLORS = PAL["CITY_COLORS"]

LOGO_BASE64 = (
    "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"
)

SEASON_ORDER = ["Winter", "Spring", "Summer", "Autumn"]
SEASON_MAP = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Autumn", 10: "Autumn", 11: "Autumn",
}
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# =========================================================================
# DATA LOADING (robust to launch directory, cached on file mtime)
# =========================================================================
def _find_data_file():
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = glob.glob(os.path.join(here, "**", "*weather*1947*.csv"), recursive=True)
    if not candidates:
        candidates = glob.glob(os.path.join(here, "**", "*weather_data_from_1947*.csv"), recursive=True)
    if not candidates:
        candidates = glob.glob(os.path.join(here, "**", "*.csv"), recursive=True)
    if not candidates:
        candidates = glob.glob("*weather*.csv") + glob.glob("*.csv")
    return candidates[0] if candidates else None


@st.cache_data
def load_data(path: str, mtime: float):
    df = pd.read_csv(path)
    df["DateObj"] = pd.to_datetime(df["Date"], format="%Y-%m")
    df["Season"] = df["Month"].map(SEASON_MAP)
    df["MonthName"] = df["Month"].map(lambda m: MONTH_NAMES[m - 1])
    df["Decade"] = (df["Year"] // 10 * 10).astype(str) + "s"
    return df


DATA_PATH = _find_data_file()
if DATA_PATH is None:
    st.error("Could not locate the weather CSV file. Please make sure it is uploaded alongside app.py.")
    st.stop()

df_all = load_data(DATA_PATH, os.path.getmtime(DATA_PATH))

# =========================================================================
# HELPERS
# =========================================================================
def hex_to_rgba(hex_color, alpha=0.2):
    h = hex_color.lstrip("#")
    r, g, b = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def fmt_compact(x, unit=""):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return str(x)
    a = abs(x)
    if a >= 1_000_000:
        s = f"{x/1_000_000:.2f}M"
    elif a >= 1_000:
        s = f"{x/1_000:.2f}K"
    else:
        s = f"{x:,.2f}" if a < 100 else f"{x:,.1f}"
    return f"{s}{unit}"


def style_fig(fig, height=430, legend=True):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT, size=12.5),
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(
            font=dict(color=TEXT, size=11.5),
            bgcolor="rgba(0,0,0,0)",
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
        ) if legend else dict(font=dict(color=TEXT)),
        showlegend=legend,
        hoverlabel=dict(bgcolor=SURFACE_2, font_color=TEXT, bordercolor=ACCENT),
        transition=dict(duration=350, easing="cubic-in-out"),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, color=SUBTEXT, linecolor=BORDER)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, color=SUBTEXT, linecolor=BORDER)
    fig.update_coloraxes(colorbar=dict(tickfont=dict(color=SUBTEXT), title_font=dict(color=SUBTEXT)))
    return fig


def chart_card_open(title, desc=""):
    st.markdown(f"""<div class="chart-card fade-in">
        <div class="chart-title">{title}</div>
        <div class="chart-desc">{desc}</div>""", unsafe_allow_html=True)


def chart_card_close():
    st.markdown("</div>", unsafe_allow_html=True)


def insights_box(title, points):
    items = "".join([f"<li>{p}</li>" for p in points if p])
    st.markdown(f"""<div class="insights-box fade-in">
        <div class="insights-title">💡 {title}</div>
        <ul>{items}</ul>
    </div>""", unsafe_allow_html=True)


def kpi_card(label, value, sub="", color=ACCENT, decimals=1, prefix="", suffix=""):
    """Self-contained animated count-up KPI card (own inline <style> since components.html is an isolated iframe)."""
    try:
        val = float(value)
    except (TypeError, ValueError):
        val = 0.0
    uid = f"kpi_{abs(hash(label + str(value) + sub)) % 10_000_000}"
    html = f"""
    <style>
      #{uid} {{
        background:{SURFACE}; border:1px solid {BORDER}; border-radius:16px;
        padding:16px 18px; font-family:'Inter',sans-serif; transition: all 0.25s ease;
        box-sizing:border-box; height:118px; display:flex; flex-direction:column; justify-content:center;
      }}
      #{uid}:hover {{ border-color:{color}; box-shadow:0 8px 22px {hex_to_rgba(color,0.18)}; transform:translateY(-2px); }}
      #{uid} .kpi-label {{ color:{SUBTEXT}; font-size:0.78rem; font-weight:600; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:6px; }}
      #{uid} .kpi-value {{ color:{color}; font-size:1.7rem; font-weight:800; line-height:1.1; font-family:'JetBrains Mono',monospace; }}
      #{uid} .kpi-sub {{ color:{SUBTEXT}; font-size:0.74rem; margin-top:4px; }}
    </style>
    <div id="{uid}" class="fade-in">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value"><span id="{uid}_num">0</span></div>
      <div class="kpi-sub">{sub}</div>
    </div>
    <script>
      (function() {{
        const target = {val};
        const el = document.getElementById("{uid}_num");
        const dur = 900;
        const start = performance.now();
        function frame(now) {{
          const p = Math.min((now - start) / dur, 1);
          const eased = 1 - Math.pow(1 - p, 3);
          const cur = target * eased;
          el.textContent = "{prefix}" + cur.toFixed({decimals}) + "{suffix}";
          if (p < 1) requestAnimationFrame(frame);
        }}
        requestAnimationFrame(frame);
      }})();
    </script>
    """
    components.html(html, height=126)


def render_dark_table(data, max_rows=500):
    d = data.head(max_rows).copy()
    cols = "".join([f"<th>{c}</th>" for c in d.columns])
    rows = ""
    for _, r in d.iterrows():
        cells = "".join([f"<td>{v}</td>" for v in r.values])
        rows += f"<tr>{cells}</tr>"
    st.markdown(f"""<div class="dark-table-wrap fade-in">
        <table class="dark-table"><thead><tr>{cols}</tr></thead><tbody>{rows}</tbody></table>
    </div>""", unsafe_allow_html=True)


def city_color_map(cities):
    return {c: CITY_COLORS.get(c, ACCENT) for c in cities}


# =========================================================================
# GLOBAL CSS
# =========================================================================
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

.stApp {{ background: linear-gradient(160deg, {BG} 0%, {BG} 100%); color: {TEXT}; transition: background 0.3s ease; }}

#MainMenu, footer {{ visibility: hidden; }}
.stDeployButton {{ display: none !important; }}

/* keep the native header bar untouched in structure (it hosts the sidebar collapse/expand button) — only recolor it */
header[data-testid="stHeader"] {{ background: transparent !important; }}

/* cosmetic-only styling of the native sidebar toggle buttons — do NOT touch display/visibility,
   Streamlit itself toggles that between the two states; forcing it here is what breaks the "show" button */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"] {{
  background:{SURFACE} !important;
  border:1px solid {BORDER} !important;
  border-radius: 10px !important;
  box-shadow: 0 4px 14px rgba(0,0,0,0.25) !important;
}}
[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapsedControl"]:hover,
[data-testid="stSidebarCollapseButton"]:hover {{ background:{SURFACE_2} !important; }}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg {{ fill:{ACCENT} !important; color:{ACCENT} !important; }}

.block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1400px; }}

/* ============================= RESPONSIVENESS ============================= */
@media (max-width: 992px) {{
  .block-container {{ padding-left: 1rem !important; padding-right: 1rem !important; max-width: 100% !important; }}
  section[data-testid="stSidebar"] {{ width: 320px !important; }}
}}

@media (max-width: 768px) {{
  section[data-testid="stSidebar"] {{ min-width: 82vw !important; max-width: 82vw !important; }}
  .header-wrap {{ flex-wrap: wrap; gap: 10px; }}
  .header-logo-card {{ width: 92px !important; height: 52px !important; }}
  .header-title {{ font-size: 1.35rem !important; }}
  .header-sub {{ font-size: 0.82rem !important; }}
  .meta-pill {{ font-size: 0.68rem !important; padding: 3px 9px !important; }}
  .block-container {{ padding-left: 0.75rem !important; padding-right: 0.75rem !important; }}
  .chart-card {{ padding: 14px 14px 6px 14px !important; }}
  .chart-title {{ font-size: 0.95rem !important; }}
  .insights-box {{ padding: 14px 16px !important; }}
  [data-baseweb="tab"] * {{ font-size: 0.76rem !important; }}
}}

@media (max-width: 480px) {{
  .header-title {{ font-size: 1.1rem !important; }}
  .header-sub {{ font-size: 0.74rem !important; }}
  .header-logo-card {{ width: 72px !important; height: 40px !important; }}
  .meta-pills {{ gap: 5px !important; }}
  section[data-testid="stSidebar"] {{ min-width: 90vw !important; max-width: 90vw !important; }}
}}

@keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: translateY(0); }} }}
.fade-in {{ animation: fadeInUp 0.6s ease both; }}

/* header */
.header-wrap {{ display:flex; align-items:center; gap:18px; margin-bottom: 4px; }}
.header-logo-card {{
  background:{LOGO_BG}; border:1px solid {BORDER}; border-radius:16px; width:132px; height:72px;
  display:flex; align-items:center; justify-content:center; font-size:30px; padding:8px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.20);
  flex-shrink:0; box-sizing:border-box;
}}
.header-logo-card img {{ max-width:100%; max-height:100%; object-fit:contain; }}
.header-title {{ font-size:2rem; font-weight:800; color:{TEXT} !important; margin:0; letter-spacing:-0.02em; }}
.header-sub {{ color:{SUBTEXT} !important; font-size:0.95rem; margin-top:2px; }}
.meta-pills {{ display:flex; gap:8px; margin-top:8px; flex-wrap:wrap; }}
.meta-pill {{
  background:{SURFACE_2}; border:1px solid {BORDER}; color:{ACCENT} !important;
  font-size:0.75rem; font-weight:600; padding:4px 12px; border-radius:999px;
}}

/* theme toggle */
div[data-testid="stToggle"] {{ display:flex; justify-content:flex-end; }}

/* card */
.chart-card {{
  background:{SURFACE}; border:1px solid {BORDER}; border-radius:16px;
  padding:18px 20px 8px 20px; margin-bottom:22px; transition: all 0.25s ease;
}}
.chart-card:hover {{ border-color:{hex_to_rgba(ACCENT,0.35)}; box-shadow:0 8px 24px {hex_to_rgba(ACCENT,0.10)}; transform: translateY(-2px); }}
.chart-title {{ font-size:1.05rem; font-weight:700; color:{TEXT} !important; margin:0 0 2px 0; }}
.chart-desc {{ font-size:0.82rem; color:{SUBTEXT} !important; margin:0 0 10px 0; }}

/* insights box */
.insights-box {{
  background: linear-gradient(135deg, {SURFACE_2} 0%, {SURFACE} 100%);
  border:1px solid {hex_to_rgba(ACCENT,0.2)}; border-radius:16px; padding:18px 22px; margin: 6px 0 24px 0;
  transition: all 0.25s ease;
}}
.insights-box:hover {{ border-color:{hex_to_rgba(ACCENT,0.5)}; }}
.insights-title {{ color:{ACCENT} !important; font-weight:700; font-size:1rem; margin-bottom:10px; display:flex; align-items:center; gap:8px; }}
.insights-box ul {{ margin:0; padding-left:1.1rem; }}
.insights-box li {{ color:{TEXT} !important; font-size:0.9rem; margin-bottom:6px; line-height:1.5; }}
.insights-box li b {{ color:{ACCENT_2} !important; }}

/* tabs */
.stTabs [data-baseweb="tab-list"], div[data-baseweb="tab-list"] {{
  background:{SURFACE} !important; border:1px solid {BORDER} !important;
  border-radius:14px !important; padding:6px !important; gap:4px !important;
  overflow-x:auto !important; flex-wrap:nowrap !important;
}}
.stTabs [data-baseweb="tab"], [data-baseweb="tab"] {{
  height:42px !important; border-radius:10px !important; color:{SUBTEXT} !important;
  transition: all 0.2s ease !important;
}}
[data-baseweb="tab"] * {{ color:{SUBTEXT} !important; font-weight:600 !important; font-size:0.86rem !important; }}
.stTabs [aria-selected="true"] {{ background:{hex_to_rgba(ACCENT,0.15)} !important; }}
.stTabs [aria-selected="true"] * {{ color:{ACCENT} !important; }}
.stTabs [data-baseweb="tab"]:hover {{ background:{SURFACE_2} !important; }}
.stTabs [data-baseweb="tab-highlight"] {{ background-color:{ACCENT} !important; }}
.stTabs [data-baseweb="tab-panel"] {{ animation: fadeInUp 0.4s ease both; }}

/* sidebar */
section[data-testid="stSidebar"] {{ background:{SURFACE} !important; border-right:1px solid {BORDER}; }}
section[data-testid="stSidebar"] * {{ color:{TEXT} !important; }}
section[data-testid="stSidebar"] .stSlider label, section[data-testid="stSidebar"] label {{ color:{TEXT} !important; font-weight:600 !important; }}
section[data-testid="stSidebar"] hr {{ border-color:{BORDER}; }}

/* slider accent (avoid default red) */
div[data-baseweb="slider"] div[role="slider"] {{ background-color:{ACCENT} !important; border-color:{ACCENT} !important; }}
div[data-baseweb="slider"] > div > div {{ background:{ACCENT} !important; }}
div[data-baseweb="slider"] > div:first-child {{ background:{BORDER} !important; }}

/* multiselect chips */
span[data-baseweb="tag"] {{ background-color:{hex_to_rgba(ACCENT,0.2)} !important; border:1px solid {hex_to_rgba(ACCENT,0.4)} !important; }}
span[data-baseweb="tag"] * {{ color:{ACCENT} !important; }}
div[data-baseweb="popover"], div[data-baseweb="menu"] {{ background:{SURFACE_2} !important; }}
div[role="listbox"], div[role="option"] {{ background:{SURFACE_2} !important; color:{TEXT} !important; }}
div[role="listbox"] * , div[role="option"] * {{ color:{TEXT} !important; }}
div[role="option"]:hover {{ background:{SURFACE} !important; }}

/* selectbox / dropdown readability (closed box + selected value + arrow icon) */
div[data-baseweb="select"] > div {{ background:{SURFACE_2} !important; border-color:{BORDER} !important; }}
div[data-baseweb="select"] div, div[data-baseweb="select"] span {{ color:{TEXT} !important; }}
div[data-baseweb="select"] svg {{ fill:{SUBTEXT} !important; }}
ul[data-baseweb="menu"] li {{ background:{SURFACE_2} !important; color:{TEXT} !important; }}
ul[data-baseweb="menu"] li:hover {{ background:{SURFACE} !important; }}

/* base markdown text color (default theme-following text, overridden by more specific !important rules above) */
[data-testid="stMarkdownContainer"] {{ color:{TEXT}; }}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] div,
[data-testid="stMarkdownContainer"] label {{ color:{TEXT}; }}

/* checkboxes / captions / buttons / toggle */
.stCheckbox label, .stCaptionContainer, .stMarkdown p {{ color:{TEXT} !important; }}
.stCaptionContainer, small, .stCaption {{ color:{SUBTEXT} !important; }}
.stDownloadButton button, .stButton button {{
  background:{hex_to_rgba(ACCENT,0.15)} !important; color:{ACCENT} !important; border:1px solid {hex_to_rgba(ACCENT,0.4)} !important;
  border-radius:10px !important; font-weight:600 !important; transition: all 0.2s ease !important;
}}
.stDownloadButton button:hover, .stButton button:hover {{ background:{hex_to_rgba(ACCENT,0.28)} !important; transform: translateY(-1px); }}
label[data-baseweb="checkbox"] div[aria-checked="true"] {{ background:{ACCENT} !important; border-color:{ACCENT} !important; }}

/* dark table */
.dark-table-wrap {{ max-height:520px; overflow:auto; border:1px solid {BORDER}; border-radius:14px; }}
table.dark-table {{ width:100%; border-collapse:collapse; font-size:0.82rem; font-family:'JetBrains Mono', monospace; }}
table.dark-table thead th {{
  position:sticky; top:0; background:{SURFACE_2}; color:{ACCENT} !important; text-align:left;
  padding:10px 14px; border-bottom:2px solid {BORDER}; z-index:2;
}}
table.dark-table tbody td {{ padding:8px 14px; color:{TEXT} !important; border-bottom:1px solid {BORDER}; }}
table.dark-table tbody tr {{ transition: background 0.15s ease; }}
table.dark-table tbody tr:hover {{ background:{SURFACE_2}; }}
</style>""", unsafe_allow_html=True)

# =========================================================================
# HEADER (with Light / Dark toggle) — content filled in after filters are applied below,
# but the placeholder is created here so it stays visually at the top of the page.
# =========================================================================
header_slot = st.empty()

# =========================================================================
# SIDEBAR FILTERS (cascading Province -> City)
# =========================================================================
with st.sidebar:
    st.markdown("### 🔎 Filters")

    all_provinces = sorted(df_all["Province"].unique().tolist())
    sel_provinces = st.multiselect("Province / Region", all_provinces, default=all_provinces)
    if not sel_provinces:
        sel_provinces = all_provinces

    city_options = sorted(df_all[df_all["Province"].isin(sel_provinces)]["City"].unique().tolist())
    sel_cities = st.multiselect("Cities", city_options, default=city_options)
    if not sel_cities:
        sel_cities = city_options

    st.markdown("---")
    yr_min, yr_max = int(df_all["Year"].min()), int(df_all["Year"].max())
    yr_range = st.slider("Year Range", yr_min, yr_max, (yr_min, yr_max), step=1)

    decades = sorted(df_all["Decade"].unique().tolist())
    sel_decades = st.multiselect("Decade (optional refine)", decades, default=decades)
    if not sel_decades:
        sel_decades = decades

    st.markdown("---")
    sel_seasons = st.multiselect("Season", SEASON_ORDER, default=SEASON_ORDER)
    if not sel_seasons:
        sel_seasons = SEASON_ORDER

    sel_months = st.multiselect("Specific Months (optional refine)", MONTH_NAMES, default=MONTH_NAMES)
    if not sel_months:
        sel_months = MONTH_NAMES

    st.markdown("---")
    st.caption("Data source: monthly climate records, Pakistan Meteorological archive-style dataset (1947–2025).")

df = df_all[
    (df_all["Province"].isin(sel_provinces))
    & (df_all["City"].isin(sel_cities))
    & (df_all["Year"].between(yr_range[0], yr_range[1]))
    & (df_all["Decade"].isin(sel_decades))
    & (df_all["Season"].isin(sel_seasons))
    & (df_all["MonthName"].isin(sel_months))
].copy()

if df.empty:
    with header_slot.container():
        st.warning("No data matches the current filter selection. Please broaden your filters.")
    st.stop()

CMAP = city_color_map(sel_cities)
cap_years = f"{yr_range[0]}–{yr_range[1]}"

# --- render the header now, with pills reflecting the current filter selection ---
n_cities_sel = len(sel_cities)
n_records_sel = len(df)
n_years_sel = df["Year"].nunique()
cities_label = "City" if n_cities_sel == 1 else "Cities"
years_label = "Year" if n_years_sel == 1 else "Years"

with header_slot.container():
    h_left, h_right = st.columns([6, 1])
    with h_left:
        st.markdown(f"""
        <div class="header-wrap fade-in">
          <div class="header-logo-card"><img src="data:image/png;base64,{LOGO_BASE64}" alt="Gallup Pakistan"/></div>
          <div>
            <p class="header-title">Pakistan Climate & Weather Dashboard</p>
            <p class="header-sub">Monthly temperature &amp; precipitation records across {n_cities_sel} selected {cities_label.lower()}</p>
            <div class="meta-pills">
              <span class="meta-pill">{cap_years}</span>
              <span class="meta-pill">{n_cities_sel} {cities_label}</span>
              <span class="meta-pill">{n_records_sel:,} Monthly Records</span>
              <span class="meta-pill">{n_years_sel} {years_label} of Data</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with h_right:
        st.write("")
        st.toggle("🌙 Dark", value=st.session_state.theme_dark, key="theme_dark",
                  help="Switch between light and dark mode")


# =========================================================================
# TABS (Raw Data tab removed)
# =========================================================================
tabs = st.tabs([
    "🌡️ Temperature Trends",
    "🌧️ Precipitation",
    "🏙️ City Comparison",
    "📅 Seasonal Patterns",
    "📈 Climate Change",
    "⚠️ Extremes",
    "🗺️ Geographic",
])

# -------------------------------------------------------------------------
# TAB 1 — TEMPERATURE TRENDS
# -------------------------------------------------------------------------
with tabs[0]:
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        kpi_card("Avg Mean Temp", df["tas"].mean(), sub="°C across filtered period", color=WARM, decimals=2, suffix="°C")
    with k2:
        kpi_card("Avg Max Temp", df["tasmax"].mean(), sub="mean of monthly highs", color=WARM, decimals=2, suffix="°C")
    with k3:
        kpi_card("Avg Min Temp", df["tasmin"].mean(), sub="mean of monthly lows", color=ACCENT_2, decimals=2, suffix="°C")
    with k4:
        kpi_card("Hottest Recorded", df["tasmax"].max(), sub=f"{df.loc[df['tasmax'].idxmax(),'City']} · {df.loc[df['tasmax'].idxmax(),'Date']}", color="#ef4444", decimals=1, suffix="°C")
    with k5:
        kpi_card("Coldest Recorded", df["tasmin"].min(), sub=f"{df.loc[df['tasmin'].idxmin(),'City']} · {df.loc[df['tasmin'].idxmin(),'Date']}", color=ACCENT_2, decimals=1, suffix="°C")

    hottest_city = df.groupby("City")["tas"].mean().idxmax()
    coldest_city = df.groupby("City")["tas"].mean().idxmin()
    widest_swing = (df.groupby("City")["tasmax"].mean() - df.groupby("City")["tasmin"].mean()).idxmax()
    insights_box("Key Findings", [
        f"<b>{hottest_city}</b> has the highest average temperature among the selected cities in this period.",
        f"<b>{coldest_city}</b> is consistently the coolest of the selected cities on average.",
        f"<b>{widest_swing}</b> shows the widest gap between average daily highs and lows, indicating more continental/arid conditions.",
        f"The overall dataset spans <b>{cap_years}</b>, covering {df['Year'].nunique()} distinct years of monthly observations.",
        f"Average monthly high across all filtered records is <b>{df['tasmax'].mean():.1f}°C</b>, and average monthly low is <b>{df['tasmin'].mean():.1f}°C</b>.",
        f"The overall average temperature across all selected cities is <b>{df['tas'].mean():.1f}°C</b>.",
    ])

    st.write("")
    chart_card_open("Monthly Mean Temperature Over Time", "Full monthly resolution time series, one line per city")
    fig1 = go.Figure()
    for c in sel_cities:
        sub = df[df["City"] == c].sort_values("DateObj")
        fig1.add_trace(go.Scatter(x=sub["DateObj"], y=sub["tas"], mode="lines", name=c,
                                   line=dict(color=CMAP[c], width=1.3), opacity=0.85))
    style_fig(fig1, height=440)
    st.plotly_chart(fig1, use_container_width=True, key="chart_monthly_temp_line")
    chart_card_close()

    chart_card_open("Temperature Range Band (Max / Mean / Min)", "Annual average of monthly high, mean, and low temperatures per city")
    annual_range = df.groupby(["City", "Year"], as_index=False)[["tasmax", "tas", "tasmin"]].mean()
    fig2 = go.Figure()
    for c in sel_cities:
        sub = annual_range[annual_range["City"] == c].sort_values("Year")
        fig2.add_trace(go.Scatter(x=sub["Year"], y=sub["tasmax"], line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig2.add_trace(go.Scatter(x=sub["Year"], y=sub["tasmin"], line=dict(width=0), fill="tonexty",
                                   fillcolor=hex_to_rgba(CMAP[c], 0.15), showlegend=False, hoverinfo="skip"))
        fig2.add_trace(go.Scatter(x=sub["Year"], y=sub["tas"], mode="lines", name=c,
                                   line=dict(color=CMAP[c], width=2)))
    style_fig(fig2, height=440)
    st.plotly_chart(fig2, use_container_width=True, key="chart_temp_range_band")
    chart_card_close()

    chart_card_open("Distribution of Monthly Mean Temperatures", "Histogram of all monthly readings, split by city")
    fig1b = px.histogram(df, x="tas", color="City", color_discrete_map=CMAP, barmode="overlay", nbins=40, opacity=0.6)
    style_fig(fig1b, height=400)
    st.plotly_chart(fig1b, use_container_width=True, key="chart_temp_histogram")
    chart_card_close()

    chart_card_open("Average Temperature by Decade", "Grouped comparison of decade-level average temperature per city")
    decade_city = df.groupby(["City", "Decade"], as_index=False)["tas"].mean().sort_values("Decade")
    fig1c = px.bar(decade_city, x="Decade", y="tas", color="City", color_discrete_map=CMAP, barmode="group")
    style_fig(fig1c, height=420)
    st.plotly_chart(fig1c, use_container_width=True, key="chart_decade_bar")
    chart_card_close()

# -------------------------------------------------------------------------
# TAB 2 — PRECIPITATION
# -------------------------------------------------------------------------
with tabs[1]:
    total_pr = df.groupby("City")["pr"].sum()
    wettest_city = total_pr.idxmax()
    driest_city = total_pr.idxmin()
    monsoon = df[df["Month"].isin([7, 8])]["pr"].sum()
    monsoon_share = monsoon / df["pr"].sum() * 100 if df["pr"].sum() > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card("Avg Monthly Rainfall", df["pr"].mean(), sub="mm, all filtered records", color=RAIN, decimals=1, suffix=" mm")
    with k2:
        kpi_card("Wettest City", total_pr.max(), sub=wettest_city, color=RAIN, decimals=0, suffix=" mm total")
    with k3:
        kpi_card("Driest City", total_pr.min(), sub=driest_city, color=WARM, decimals=0, suffix=" mm total")
    with k4:
        kpi_card("Jul–Aug Monsoon Share", monsoon_share, sub="of total filtered rainfall", color=ACCENT, decimals=1, suffix="%")

    insights_box("Key Findings", [
        f"<b>{wettest_city}</b> received the most cumulative rainfall of the selected cities in this window.",
        f"<b>{driest_city}</b> received the least, reflecting Pakistan's sharp east–west aridity gradient.",
        f"July–August (peak monsoon) accounts for roughly <b>{monsoon_share:.1f}%</b> of total rainfall across the selection.",
        f"Average monthly rainfall across all filtered records is <b>{df['pr'].mean():.1f} mm</b>.",
        "Coastal and northern cities generally show markedly different rainfall regimes than the arid interior/west.",
        f"Total cumulative rainfall across all selected cities in this window is <b>{fmt_compact(total_pr.sum())} mm</b>.",
    ])

    st.write("")
    chart_card_open("Precipitation Over Time", "Monthly rainfall (mm) per city, stacked area view")
    pr_pivot = df.pivot_table(index="DateObj", columns="City", values="pr", aggfunc="mean").fillna(0)
    fig3 = go.Figure()
    for c in sel_cities:
        if c in pr_pivot.columns:
            fig3.add_trace(go.Scatter(x=pr_pivot.index, y=pr_pivot[c], mode="lines", name=c,
                                       stackgroup="one", line=dict(width=0.5, color=CMAP[c]),
                                       fillcolor=hex_to_rgba(CMAP[c], 0.55)))
    style_fig(fig3, height=440)
    st.plotly_chart(fig3, use_container_width=True, key="chart_pr_area")
    chart_card_close()

    chart_card_open("Average Monthly Rainfall Climatology", "Mean precipitation by calendar month, colored by intensity")
    clim_pr = df.groupby("MonthName", as_index=False)["pr"].mean()
    clim_pr["MonthName"] = pd.Categorical(clim_pr["MonthName"], categories=MONTH_NAMES, ordered=True)
    clim_pr = clim_pr.sort_values("MonthName")
    fig4 = px.bar(clim_pr, x="MonthName", y="pr", color="pr", color_continuous_scale=["#0e2a44", "#22d3ee", "#67e8f9"])
    style_fig(fig4, height=400, legend=False)
    st.plotly_chart(fig4, use_container_width=True, key="chart_pr_climatology")
    chart_card_close()

    chart_card_open("Total Rainfall Share by City", "Treemap of cumulative rainfall over the filtered period")
    tree_df = total_pr.reset_index()
    tree_df.columns = ["City", "TotalRain"]
    fig5 = px.treemap(tree_df, path=["City"], values="TotalRain", color="TotalRain",
                       color_continuous_scale=["#0e2a44", "#22d3ee", "#a5f3fc"])
    fig5.update_traces(textfont=dict(color="#0b1220", size=15))
    style_fig(fig5, height=400, legend=False)
    st.plotly_chart(fig5, use_container_width=True, key="chart_pr_treemap")
    chart_card_close()

    chart_card_open("Monthly Rainfall Distribution by City", "Violin plot showing spread and density of monthly rainfall")
    fig5b = go.Figure()
    for c in sel_cities:
        sub = df[df["City"] == c]
        fig5b.add_trace(go.Violin(y=sub["pr"], name=c, line_color=CMAP[c], fillcolor=hex_to_rgba(CMAP[c], 0.4), meanline_visible=True))
    style_fig(fig5b, height=430, legend=False)
    st.plotly_chart(fig5b, use_container_width=True, key="chart_pr_violin")
    chart_card_close()

    chart_card_open("Annual Total Rainfall Trend", "Sum of rainfall per year across selected cities")
    annual_pr = df.groupby("Year", as_index=False)["pr"].sum()
    fig5c = px.bar(annual_pr, x="Year", y="pr", color="pr", color_continuous_scale=["#0e2a44", "#22d3ee", "#38bdf8"])
    style_fig(fig5c, height=400, legend=False)
    st.plotly_chart(fig5c, use_container_width=True, key="chart_annual_pr_bar")
    chart_card_close()

# -------------------------------------------------------------------------
# TAB 3 — CITY COMPARISON
# -------------------------------------------------------------------------
with tabs[2]:
    st.write("")
    rank_df = df.groupby("City", as_index=False)["tas"].mean().sort_values("tas", ascending=False)
    warmest = rank_df.iloc[0]["City"]
    coolest = rank_df.iloc[-1]["City"]
    insights_box("Key Findings", [
        f"<b>{warmest}</b> ranks as the warmest city on average across the selected filters.",
        f"<b>{coolest}</b> ranks as the coolest, likely reflecting elevation and latitude differences.",
        "The seasonal radar profile highlights how sharply Punjab and Sindh plains cities swing between winter and summer compared to hill cities.",
        "Box plots reveal which cities have the widest year-round temperature variability versus more stable climates.",
        "The bubble summary combines temperature, rainfall, and range in a single comparative view across cities.",
        f"The average temperature gap between the warmest and coolest selected city is <b>{(rank_df['tas'].max()-rank_df['tas'].min()):.1f}°C</b>.",
    ])

    chart_card_open("Seasonal Temperature Profile", "Average monthly temperature per city on a radial axis")
    clim_city = df.groupby(["City", "Month"], as_index=False)["tas"].mean()
    fig6 = go.Figure()
    for c in sel_cities:
        sub = clim_city[clim_city["City"] == c].sort_values("Month")
        theta = [MONTH_NAMES[m - 1] for m in sub["Month"]]
        fig6.add_trace(go.Scatterpolar(r=sub["tas"], theta=theta, fill="toself", name=c,
                                        line=dict(color=CMAP[c])))
    fig6.update_layout(polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(gridcolor=GRID, color=SUBTEXT),
        angularaxis=dict(gridcolor=GRID, color=SUBTEXT),
    ))
    style_fig(fig6, height=460)
    st.plotly_chart(fig6, use_container_width=True, key="chart_radar_seasonal")
    chart_card_close()

    chart_card_open("Temperature Distribution by City", "Spread of monthly mean temperature readings")
    fig7 = go.Figure()
    for c in sel_cities:
        sub = df[df["City"] == c]
        fig7.add_trace(go.Box(y=sub["tas"], name=c, marker_color=CMAP[c], boxmean=True))
    style_fig(fig7, height=430, legend=False)
    st.plotly_chart(fig7, use_container_width=True, key="chart_box_temp_city")
    chart_card_close()

    chart_card_open("City Ranking by Average Temperature", "Continuous color scale highlights relative warmth")
    fig8 = px.bar(rank_df, x="tas", y="City", orientation="h", color="tas",
                  color_continuous_scale=["#1e3a5f", "#22d3ee", "#f97316"])
    style_fig(fig8, height=380, legend=False)
    fig8.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig8, use_container_width=True, key="chart_city_rank_temp")
    chart_card_close()

    chart_card_open("Max Temperature vs Rainfall", "Do hotter months bring more or less rain? Each point is one city-month record")
    fig9 = px.scatter(df, x="tasmax", y="pr", color="City", color_discrete_map=CMAP, opacity=0.55)
    style_fig(fig9, height=430)
    st.plotly_chart(fig9, use_container_width=True, key="chart_scatter_tmax_pr")
    chart_card_close()

    chart_card_open("City Climate Bubble Summary", "Average temperature vs average rainfall, bubble size = temperature range (max−min)")
    bubble_df = df.groupby("City", as_index=False).agg(
        AvgTemp=("tas", "mean"), AvgRain=("pr", "mean"),
        TempRange=("tasmax", "mean"),
    )
    bubble_df["TempRange"] = bubble_df["TempRange"] - df.groupby("City")["tasmin"].mean().reindex(bubble_df["City"]).values
    fig9b = px.scatter(bubble_df, x="AvgTemp", y="AvgRain", size="TempRange", color="City",
                        color_discrete_map=CMAP, size_max=55, text="City")
    fig9b.update_traces(textposition="top center", textfont=dict(color=TEXT))
    style_fig(fig9b, height=440, legend=False)
    st.plotly_chart(fig9b, use_container_width=True, key="chart_bubble_city_summary")
    chart_card_close()

# -------------------------------------------------------------------------
# TAB 4 — SEASONAL PATTERNS
# -------------------------------------------------------------------------
with tabs[3]:
    st.write("")
    focus_city = st.selectbox("Focus city for heatmap", sel_cities, index=0, key="season_focus_city")

    hottest_month = df.groupby("MonthName")["tas"].mean().idxmax()
    wettest_month = df.groupby("MonthName")["pr"].mean().idxmax()
    insights_box("Key Findings", [
        f"<b>{hottest_month}</b> is on average the hottest month across the selected cities.",
        f"<b>{wettest_month}</b> is on average the wettest month, consistent with the monsoon season.",
        f"The heatmap for <b>{focus_city}</b> reveals long-run warming or cooling patterns visually as color shifts across decades.",
        "Summer consistently shows the highest temperatures across all cities, while Winter shows the largest spread between cities.",
        "Rainfall climatology and the seasonal stacked view both confirm the monsoon's dominant share of annual precipitation.",
        f"Winter and Summer show the sharpest seasonal contrast, while Spring and Autumn are transitional in both temperature and rainfall.",
    ])

    chart_card_open(f"Year × Month Temperature Heatmap — {focus_city}", "Darker/cooler cells indicate lower temperatures, brighter/warmer cells indicate higher")
    hm = df[df["City"] == focus_city].pivot_table(index="Year", columns="MonthName", values="tas", aggfunc="mean")
    hm = hm.reindex(columns=MONTH_NAMES)
    fig10 = px.imshow(hm, color_continuous_scale=["#0e2a44", "#22d3ee", "#f97316"], aspect="auto")
    style_fig(fig10, height=520, legend=False)
    st.plotly_chart(fig10, use_container_width=True, key="chart_heatmap_year_month")
    chart_card_close()

    chart_card_open("Average Rainfall by Month (Polar View)", "Monthly precipitation climatology across all selected cities")
    clim_pr_all = df.groupby("MonthName", as_index=False)["pr"].mean()
    clim_pr_all["MonthName"] = pd.Categorical(clim_pr_all["MonthName"], categories=MONTH_NAMES, ordered=True)
    clim_pr_all = clim_pr_all.sort_values("MonthName")
    fig11 = go.Figure(go.Barpolar(
        r=clim_pr_all["pr"], theta=clim_pr_all["MonthName"],
        marker=dict(color=clim_pr_all["pr"], colorscale=[[0, "#0e2a44"], [1, "#22d3ee"]]),
    ))
    fig11.update_layout(polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(gridcolor=GRID, color=SUBTEXT),
        angularaxis=dict(gridcolor=GRID, color=SUBTEXT),
    ))
    style_fig(fig11, height=460, legend=False)
    st.plotly_chart(fig11, use_container_width=True, key="chart_polar_rain_month")
    chart_card_close()

    chart_card_open("Seasonal Average Temperature by City", "Grouped comparison of Winter / Spring / Summer / Autumn means")
    season_city = df.groupby(["City", "Season"], as_index=False)["tas"].mean()
    season_city["Season"] = pd.Categorical(season_city["Season"], categories=SEASON_ORDER, ordered=True)
    fig12 = px.bar(season_city.sort_values("Season"), x="Season", y="tas", color="City",
                    color_discrete_map=CMAP, barmode="group")
    style_fig(fig12, height=420)
    st.plotly_chart(fig12, use_container_width=True, key="chart_season_group_bar")
    chart_card_close()

    chart_card_open("Seasonal Rainfall Contribution by City", "Stacked view of how much rainfall each season contributes per city")
    season_rain = df.groupby(["City", "Season"], as_index=False)["pr"].sum()
    season_rain["Season"] = pd.Categorical(season_rain["Season"], categories=SEASON_ORDER, ordered=True)
    fig12b = px.bar(season_rain.sort_values("Season"), x="City", y="pr", color="Season", barmode="stack",
                     color_discrete_sequence=[ACCENT, "#a3e635", WARM, ACCENT_2])
    style_fig(fig12b, height=420)
    st.plotly_chart(fig12b, use_container_width=True, key="chart_season_rain_stack")
    chart_card_close()

# -------------------------------------------------------------------------
# TAB 5 — CLIMATE CHANGE
# -------------------------------------------------------------------------
with tabs[4]:
    annual_city = df.groupby(["City", "Year"], as_index=False)["tas"].mean()
    trend_rows = []
    for c in sel_cities:
        sub = annual_city[annual_city["City"] == c]
        if len(sub) >= 2:
            slope, intercept = np.polyfit(sub["Year"], sub["tas"], 1)
            trend_rows.append({"City": c, "SlopePerDecade": slope * 10, "Intercept": intercept})
    trend_df = pd.DataFrame(trend_rows)

    overall_annual_series = df.groupby("Year")["tas"].mean()
    overall_slope = np.polyfit(overall_annual_series.index, overall_annual_series.values, 1)[0]

    k1, k2, k3 = st.columns(3)
    with k1:
        kpi_card("Overall Warming Rate", overall_slope * 10, sub="°C per decade, all selected cities", color=WARM, decimals=3, suffix="°C/decade")
    with k2:
        fastest = trend_df.loc[trend_df["SlopePerDecade"].idxmax()] if not trend_df.empty else None
        kpi_card("Fastest Warming City", fastest["SlopePerDecade"] if fastest is not None else 0, sub=fastest["City"] if fastest is not None else "", color="#ef4444", decimals=3, suffix="°C/decade")
    with k3:
        slowest = trend_df.loc[trend_df["SlopePerDecade"].idxmin()] if not trend_df.empty else None
        kpi_card("Slowest / Cooling City", slowest["SlopePerDecade"] if slowest is not None else 0, sub=slowest["City"] if slowest is not None else "", color=ACCENT_2, decimals=3, suffix="°C/decade")

    insights_box("Key Findings", [
        f"The combined warming rate across selected cities is approximately <b>{overall_slope*10:.3f}°C per decade</b>.",
        (f"<b>{fastest['City']}</b> shows the fastest warming trend at <b>{fastest['SlopePerDecade']:.3f}°C/decade</b>." if fastest is not None else ""),
        (f"<b>{slowest['City']}</b> shows the slowest warming or slight cooling at <b>{slowest['SlopePerDecade']:.3f}°C/decade</b>." if slowest is not None else ""),
        "The 10-year rolling average smooths out year-to-year noise and makes the underlying long-term trend easier to see.",
        "The anomaly chart highlights which years ran hotter or cooler than the long-run average — useful for spotting warming acceleration.",
        f"Over the full filtered period ({cap_years}), the average annual temperature is <b>{overall_annual_series.mean():.2f}°C</b>.",
    ])

    st.write("")
    chart_card_open("Annual Mean Temperature with Linear Trend", "Yearly average temperature per city plus fitted linear trend line")
    fig13 = go.Figure()
    for c in sel_cities:
        sub = annual_city[annual_city["City"] == c].sort_values("Year")
        fig13.add_trace(go.Scatter(x=sub["Year"], y=sub["tas"], mode="markers", name=f"{c} (obs)",
                                    marker=dict(color=CMAP[c], size=5, opacity=0.5), showlegend=False))
        if len(sub) >= 2:
            slope, intercept = np.polyfit(sub["Year"], sub["tas"], 1)
            trend_y = slope * sub["Year"] + intercept
            fig13.add_trace(go.Scatter(x=sub["Year"], y=trend_y, mode="lines", name=c,
                                        line=dict(color=CMAP[c], width=2.5)))
    style_fig(fig13, height=460)
    st.plotly_chart(fig13, use_container_width=True, key="chart_trend_line")
    chart_card_close()

    chart_card_open("Warming Rate by City", "Slope of linear trend in °C per decade — positive bars indicate warming")
    if not trend_df.empty:
        fig14 = px.bar(trend_df.sort_values("SlopePerDecade"), x="SlopePerDecade", y="City", orientation="h",
                        color="SlopePerDecade", color_continuous_scale=["#38bdf8", "#94a3b8", "#f97316"])
        style_fig(fig14, height=380, legend=False)
        st.plotly_chart(fig14, use_container_width=True, key="chart_warming_bar")
    chart_card_close()

    chart_card_open("10-Year Rolling Average Temperature", "Smoothed multi-year trend across all selected cities combined")
    overall_annual = df.groupby("Year", as_index=False)["tas"].mean().sort_values("Year")
    overall_annual["Rolling10yr"] = overall_annual["tas"].rolling(10, min_periods=3).mean()
    fig15 = go.Figure()
    fig15.add_trace(go.Scatter(x=overall_annual["Year"], y=overall_annual["tas"], mode="lines",
                                name="Annual Mean", line=dict(color=GRID, width=1)))
    fig15.add_trace(go.Scatter(x=overall_annual["Year"], y=overall_annual["Rolling10yr"], mode="lines",
                                name="10-yr Rolling Avg", line=dict(color=WARM, width=3)))
    style_fig(fig15, height=420)
    st.plotly_chart(fig15, use_container_width=True, key="chart_rolling10")
    chart_card_close()

    chart_card_open("Temperature Anomaly by Year", "Deviation from the full-period average — orange bars are above average (warmer), blue bars are below average (cooler)")
    baseline_mean = df["tas"].mean()
    anomaly_df = overall_annual[["Year", "tas"]].copy()
    anomaly_df["Anomaly"] = anomaly_df["tas"] - baseline_mean
    fig15b = go.Figure(go.Bar(
        x=anomaly_df["Year"], y=anomaly_df["Anomaly"],
        marker_color=[WARM if v >= 0 else ACCENT_2 for v in anomaly_df["Anomaly"]],
    ))
    style_fig(fig15b, height=400, legend=False)
    st.plotly_chart(fig15b, use_container_width=True, key="chart_anomaly_bar")
    chart_card_close()

# -------------------------------------------------------------------------
# TAB 6 — EXTREMES
# -------------------------------------------------------------------------
with tabs[5]:
    st.write("")
    bins = [-100, 10, 20, 30, 40, 100]
    labels = ["Cold (<10°C)", "Cool (10–20°C)", "Warm (20–30°C)", "Hot (30–40°C)", "Extreme (>40°C)"]
    df_binned = df.copy()
    df_binned["TempBand"] = pd.cut(df_binned["tas"], bins=bins, labels=labels)
    band_counts = df_binned["TempBand"].value_counts().reindex(labels).fillna(0).reset_index()
    band_counts.columns = ["TempBand", "Count"]
    band_counts = band_counts.sort_values("Count", ascending=False)

    hottest_row = df.loc[df["tasmax"].idxmax()]
    wettest_row = df.loc[df["pr"].idxmax()]
    dominant_band = band_counts.iloc[0]["TempBand"]
    extreme_heat_total = int((df["tasmax"] > 35).sum())
    insights_box("Key Findings", [
        f"The single hottest month on record in this selection is <b>{hottest_row['City']}, {hottest_row['Date']}</b> at <b>{hottest_row['tasmax']:.1f}°C</b>.",
        f"The single wettest month on record is <b>{wettest_row['City']}, {wettest_row['Date']}</b> with <b>{wettest_row['pr']:.1f} mm</b>.",
        f"The most common temperature band across all filtered records is <b>{dominant_band}</b>.",
        "Extreme heat events (above 40°C) are concentrated in specific plains cities during peak summer months.",
        "Extreme rainfall events cluster heavily around the July–August monsoon window.",
        f"There are <b>{extreme_heat_total}</b> monthly records in this selection where the high exceeded 35°C.",
    ])

    chart_card_open("Top 10 Hottest Months on Record", "Highest single monthly maximum temperatures in the filtered data")
    hot10 = df.nlargest(10, "tasmax")[["City", "Date", "tasmax"]].sort_values("tasmax")
    fig16 = px.bar(hot10, x="tasmax", y=hot10["City"] + " · " + hot10["Date"], orientation="h",
                    color="tasmax", color_continuous_scale=["#f97316", "#ef4444"])
    style_fig(fig16, height=440, legend=False)
    fig16.update_yaxes(title="")
    st.plotly_chart(fig16, use_container_width=True, key="chart_top10_hot")
    chart_card_close()

    chart_card_open("Top 10 Wettest Months on Record", "Highest single monthly rainfall totals in the filtered data")
    wet10 = df.nlargest(10, "pr")[["City", "Date", "pr"]].sort_values("pr")
    fig17 = px.bar(wet10, x="pr", y=wet10["City"] + " · " + wet10["Date"], orientation="h",
                    color="pr", color_continuous_scale=["#0e2a44", "#22d3ee", "#38bdf8"])
    style_fig(fig17, height=440, legend=False)
    fig17.update_yaxes(title="")
    st.plotly_chart(fig17, use_container_width=True, key="chart_top10_wet")
    chart_card_close()

    chart_card_open("Distribution of Monthly Temperature Categories", "Records bucketed into climate comfort bands, ordered by frequency")
    fig18 = go.Figure(go.Funnel(
        y=band_counts["TempBand"], x=band_counts["Count"],
        marker=dict(color=[WARM, "#fb923c", "#facc15", ACCENT_2, "#818cf8"]),
        textinfo="value+percent initial",
    ))
    style_fig(fig18, height=420, legend=False)
    st.plotly_chart(fig18, use_container_width=True, key="chart_funnel_temp_band")
    chart_card_close()

    chart_card_open("Extreme Heat Months per Year", "Count of months where the monthly high exceeded 35°C, across selected cities")
    extreme_heat = df[df["tasmax"] > 35].groupby("Year").size().reset_index(name="Count")
    fig18b = px.bar(extreme_heat, x="Year", y="Count", color="Count",
                     color_continuous_scale=["#1e3a5f", "#f97316", "#ef4444"])
    style_fig(fig18b, height=400, legend=False)
    st.plotly_chart(fig18b, use_container_width=True, key="chart_extreme_heat_year")
    chart_card_close()

# -------------------------------------------------------------------------
# TAB 7 — GEOGRAPHIC
# -------------------------------------------------------------------------
with tabs[6]:
    st.write("")
    geo_metric = st.radio("Map metric", ["Avg Temperature (°C)", "Avg Rainfall (mm)"], horizontal=True, key="geo_metric")
    geo_df = df.groupby(["City", "Province", "Latitude", "Longitude"], as_index=False).agg(
        AvgTemp=("tas", "mean"), AvgRain=("pr", "mean")
    )
    value_col = "AvgTemp" if geo_metric.startswith("Avg Temp") else "AvgRain"
    scale = ["#38bdf8", "#22d3ee", "#f97316"] if value_col == "AvgTemp" else ["#0e2a44", "#22d3ee", "#38bdf8"]

    northmost_city = geo_df.loc[geo_df["Latitude"].idxmax(), "City"]
    southmost_city = geo_df.loc[geo_df["Latitude"].idxmin(), "City"]
    insights_box("Key Findings", [
        "Southern coastal cities (e.g. Karachi) show moderated temperature swings due to maritime influence.",
        "Northern and hill-adjacent cities (e.g. Muzaffarabad) show cooler averages, consistent with elevation.",
        "Western/interior cities (e.g. Quetta) show the sharpest seasonal temperature contrast typical of arid highland climates.",
        "Rainfall is markedly higher in northern cities compared to the arid west and south.",
        f"<b>{northmost_city}</b> is the northernmost of the selected cities, while <b>{southmost_city}</b> is the southernmost.",
        "The province snapshot table below lets you compare every selected city's average temperature and rainfall side by side.",
    ])

    chart_card_open("City Locations on the Map", "Bubble size and color reflect the selected climate metric")
    fig19 = px.scatter_geo(geo_df, lat="Latitude", lon="Longitude", size=value_col, color=value_col,
                           color_continuous_scale=scale, hover_name="City",
                           hover_data={"Province": True, "Latitude": False, "Longitude": False,
                                       "AvgTemp": ":.1f", "AvgRain": ":.1f"},
                           scope="asia")
    fig19.update_geos(
        showcountries=True, countrycolor=BORDER, showland=True, landcolor=SURFACE_2,
        showocean=True, oceancolor=BG, showlakes=False, bgcolor="rgba(0,0,0,0)",
        center=dict(lat=30.5, lon=69.5), projection_scale=5.2, resolution=50,
    )
    style_fig(fig19, height=520, legend=False)
    st.plotly_chart(fig19, use_container_width=True, key="chart_geo_map")
    chart_card_close()

    chart_card_open("Latitude vs. Average Temperature", "Does elevation/northness correlate with average temperature across cities?")
    fig19b = px.scatter(geo_df, x="Latitude", y="AvgTemp", color="City", color_discrete_map=CMAP,
                         size="AvgRain", size_max=40, text="City")
    fig19b.update_traces(textposition="top center", textfont=dict(color=TEXT))
    style_fig(fig19b, height=420, legend=False)
    st.plotly_chart(fig19b, use_container_width=True, key="chart_lat_vs_temp")
    chart_card_close()

    chart_card_open("Province Snapshot Table", "Average climate metrics per city / province in the current selection")
    render_dark_table(geo_df.round(2).sort_values("AvgTemp", ascending=False))
    chart_card_close()
