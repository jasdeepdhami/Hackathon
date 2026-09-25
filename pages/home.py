import os
import base64
import random
import streamlit as st
import pandas as pd
import html as html_lib
import folium
from chatbot import run_chatbot
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

st.set_page_config(
    page_title="CareCompass - Patient View",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)
df = pd.read_csv("data2.csv")
df["Success_Rate"] = df["patients_treated_well"] / df["patients_on_disease_beds"] * 100


if "locations" not in st.session_state:
    st.session_state.locations = "All States"
if "locationc" not in st.session_state:
    st.session_state.locationc = "All Cities"
if "Disease" not in st.session_state:
    st.session_state.Disease = "Dengue"
if "Treatment" not in st.session_state:
    st.session_state.Treatment = 200000
if "Hospital_Type" not in st.session_state:
    st.session_state.Hospital_Type = "All"
if "Sorting_Parameter" not in st.session_state:
    st.session_state.Sorting_Parameter = "Success Rate"
if "hospital_name_query" not in st.session_state:
    st.session_state.hospital_name_query = ""
if st.session_state.get("_clear_name_query"):
    st.session_state.hospital_name_query = ""
    st.session_state._clear_name_query = False


@st.cache_data
def load_hospital_photos():
    image_dir = os.path.join(os.path.dirname(__file__), "hospital_images")
    photos = []
    if os.path.isdir(image_dir):
        for name in sorted(os.listdir(image_dir)):
            if name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                path = os.path.join(image_dir, name)
                with open(path, "rb") as file:
                    encoded = base64.b64encode(file.read()).decode()
                photos.append(f"data:image/jpeg;base64,{encoded}")
    return photos


def unique_shuffled_photos(count, photos, seed):
    if not photos or count <= 0:
        return [None] * count
    rng = random.Random(seed)
    unused = photos[:]
    rng.shuffle(unused)
    assigned = unused[:count]
    if len(assigned) == count:
        return assigned
    # More hospitals than unique photos: keep using a shuffled deck,
    # avoiding the same image on two neighboring cards.
    while len(assigned) < count:
        unused = photos[:]
        rng.shuffle(unused)
        if assigned and len(unused) > 1 and unused[0] == assigned[-1]:
            unused[0], unused[1] = unused[1], unused[0]
        take = min(len(unused), count - len(assigned))
        assigned.extend(unused[:take])
    return assigned


HOSPITAL_PHOTOS = load_hospital_photos()


def load_logo_b64():
    for path in (
        os.path.join(os.path.dirname(__file__), "logo.jpeg"),
        "logo.jpeg",
        os.path.join(os.path.dirname(__file__), "..", "logo.jpeg"),
    ):
        if os.path.exists(path):
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode()
    return ""


LOGO_B64 = load_logo_b64()

st.markdown(
    """
<style>
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    header[data-testid="stHeader"] {
        display: none !important;
    }
    .stApp {
        background: #eef6fb;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 12px;
    }
    .cc-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
    }
    .cc-logo {
        height: 54px;
        width: auto;
        object-fit: contain;
        display: block;
    }
    div[data-testid="stPopover"] button {
        border-radius: 50% !important;
        width: 46px !important;
        height: 46px !important;
        min-height: 46px !important;
        background: #e8f1fb !important;
        color: #163a66 !important;
        border: 1px solid #d5e4f2 !important;
        padding: 0 !important;
        font-size: 20px !important;
    }
    div[data-testid="stTextInput"] input {
        border-radius: 999px !important;
        min-height: 46px !important;
        background: #ffffff !important;
    }
    .profile-pop h4 {
        margin: 0 0 4px 0;
        color: #163a66;
    }
    .profile-pop p {
        margin: 0;
        color: #64748b;
        font-size: 13px;
    }
    .cc-hero {
        background: linear-gradient(90deg, #f4fbff 0%, #d9eefc 42%, rgba(255,255,255,0) 58%),
                    url("https://images.unsplash.com/photo-1586773860418-d37222d8fce3?auto=format&fit=crop&w=1400&q=80");
        background-size: cover;
        background-position: right center;
        border-radius: 18px;
        min-height: 210px;
        padding: 36px 40px;
        margin-bottom: 8px;
        box-shadow: 0 8px 24px rgba(23, 74, 124, 0.08);
        overflow: hidden;
        position: relative;
    }
    .cc-hero h1 {
        margin: 0;
        color: #163a66;
        font-size: 34px;
        line-height: 1.2;
        max-width: 420px;
        font-weight: 800;
    }
    .cc-hero p {
        margin: 12px 0 0 0;
        color: #4b6b88;
        max-width: 420px;
        font-size: 15px;
    }
    .filter-caption {
        font-size: 13px;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 2px;
    }
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stNumberInput"] > div {
        border-radius: 12px !important;
    }
    /* Force light styling so dropdowns/number inputs don't fall back to a
       dark theme's default (black tile, white text) */
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] span {
        color: #111827 !important;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] svg {
        fill: #111827 !important;
        color: #111827 !important;
    }
    div[data-testid="stNumberInput"] input {
        background-color: #ffffff !important;
        color: #111827 !important;
        caret-color: #111827 !important;
    }
    div[data-testid="stNumberInput"] button {
        background-color: #ffffff !important;
        color: #111827 !important;
    }
    div[data-testid="stNumberInput"] button svg {
        fill: #111827 !important;
    }
    div[data-testid="stTextInput"] input {
        background-color: #ffffff !important;
        color: #111827 !important;
        caret-color: #111827 !important;
    }
    /* Dropdown option list (the open menu) */
    ul[role="listbox"] li {
        background-color: #ffffff !important;
        color: #111827 !important;
    }
    ul[role="listbox"] li:hover,
    ul[role="listbox"] li[aria-selected="true"] {
        background: #eaf4ff !important;
        color: #123F73 !important;
    }
    div[data-testid="stButton"] > button {
        width: 100%;
        height: 46px;
        border-radius: 10px;
        border: none;
        background-color: #2563eb;
        color: white;
        font-size: 16px;
        font-weight: 600;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #1d4ed8;
        color: white;
    }
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: #e2e8f0;
        color: #334155;
    }
    .section-title {
        color: #1e3a5f;
        font-size: 22px;
        font-weight: 700;
        margin: 8px 0 4px 0;
    }
    .hospital-card {
        border: 1px solid #e6eef5;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        background: #ffffff;
        box-shadow: 0 4px 14px rgba(15, 76, 129, 0.05);
    }
    .card-row {
        display: flex;
        gap: 16px;
        align-items: stretch;
    }
    .thumb {
        width: 148px;
        min-width: 148px;
        height: 112px;
        border-radius: 12px;
        background: #dbeaf5;
        position: relative;
        overflow: hidden;
    }
    .thumb img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    .badge {
        position: absolute;
        top: 8px;
        left: 8px;
        background: #f59e0b;
        color: white;
        font-size: 10px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 999px;
        z-index: 1;
    }
    .card-body { flex: 1; min-width: 0; }
    .card-body h3 {
        margin: 0 0 6px 0;
        color: #163a66;
        font-size: 18px;
    }
    .meta { margin: 4px 0; color: #64748b; font-size: 13px; }
    .chips { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px; }
    .chip {
        background: #eef6ff;
        color: #2563eb;
        font-size: 11px;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 999px;
    }
    .card-side {
        width: 170px;
        min-width: 150px;
        text-align: right;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        justify-content: space-between;
    }
    .emergency { color: #e11d48; font-weight: 700; font-size: 13px; margin: 0; }
    .side-stat { color: #3b82b6; font-size: 12px; margin: 4px 0; }
    .map-title {
        color: #1e3a5f;
        font-size: 20px;
        font-weight: 700;
        margin: 8px 0 10px 0;
    }
    .cta-card {
        margin-top: 14px;
        background: linear-gradient(90deg, #e8fff6, #dff7ee);
        border-radius: 14px;
        padding: 16px 18px;
        color: #0f766e;
        font-weight: 600;
    }
    /* SEARCH BUTTON */
    div[data-testid="stButton"] button[kind="secondary"] {
    background-color: #123F73 !important;
    color: white !important;
    border: 1px solid #123F73 !important;
    border-radius: 10px !important;
    }

    div[data-testid="stButton"] button[kind="secondary"]:hover {
    background-color: #0D315C !important;
    color: white !important;
    }

    /* ---------- Hospital card: professional layout (ported from v2) ---------- */
    .hospital-card {
        position: relative;
        overflow: hidden;
        padding: 18px 20px 18px 22px !important;
        border-radius: 18px !important;
        border: 1px solid #e3edf6 !important;
    }
    .hospital-card::before {                 /* accent bar on the left edge */
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 5px;
        background: linear-gradient(180deg, #1c4f8a 0%, #14b8a6 100%);
    }
    .hc-row { display: flex; gap: 22px; align-items: stretch; flex-wrap: wrap; }

    /* photo */
    .hc-thumb {
        width: 170px; min-width: 170px; height: 130px;
        border-radius: 14px;
        overflow: hidden;
        position: relative;
        background: #dbeaf5;
        align-self: flex-start;
    }
    .hc-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .hc-top-badge {
        position: absolute; top: 8px; left: 8px; z-index: 1;
        background: linear-gradient(135deg, #f59e0b, #f97316);
        color: #fff;
        font-size: 10px; font-weight: 700; letter-spacing: 0.04em;
        padding: 3px 10px;
        border-radius: 999px;
    }

    /* main info */
    .hc-main { flex: 1; min-width: 250px; }
    .hc-name {
        color: #0f2d52;
        font-size: 20px; font-weight: 800; line-height: 1.25;
        margin: 0 0 8px 0;
    }
    .hc-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
    .hc-tag {
        font-size: 12px; font-weight: 700;
        padding: 4px 11px;
        border-radius: 8px;
    }
    .hc-tag-type   { background: #eef3fb; color: #1c4f8a; }
    .hc-tag-rating { background: #fff7e0; color: #a16207; }

    .hc-facts {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px 24px;
        margin-bottom: 14px;
    }
    .hc-label {
        font-size: 11px; font-weight: 700;
        letter-spacing: 0.08em; text-transform: uppercase;
        color: #8094aa;
        margin-bottom: 2px;
    }
    .hc-value { font-size: 15px; font-weight: 700; color: #163a66; }

    .hc-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
    .hc-chip {
        background: #eef6ff; color: #2563eb;
        font-size: 11px; font-weight: 600;
        padding: 4px 10px;
        border-radius: 999px;
        border: 1px solid #dbeafe;
    }

    /* right-hand panel */
    .hc-side {
        width: 200px; min-width: 180px;
        display: flex; flex-direction: column;
        justify-content: space-between;
        gap: 14px;
        padding-left: 20px;
        border-left: 1px dashed #d5e2ee;
    }
    .hc-emerg {
        align-self: flex-end;
        display: inline-flex; align-items: center; gap: 8px;
        background: #fff1f3; color: #be123c;
        font-size: 12px; font-weight: 800;
        padding: 5px 12px;
        border-radius: 999px;
    }
    .hc-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #e11d48;
        animation: hc-pulse 1.6s infinite;
    }
    @keyframes hc-pulse {
        0%   { box-shadow: 0 0 0 0 rgba(225, 29, 72, 0.5); }
        70%  { box-shadow: 0 0 0 7px rgba(225, 29, 72, 0); }
        100% { box-shadow: 0 0 0 0 rgba(225, 29, 72, 0); }
    }
    .hc-rate { font-size: 30px; font-weight: 800; line-height: 1.1; }
    .hc-bar {
        height: 8px;
        background: #e8eff6;
        border-radius: 999px;
        overflow: hidden;
        margin-top: 6px;
    }
    .hc-bar-fill { height: 100%; border-radius: 999px; }
    .hc-patients { font-size: 13px; color: #3b5878; }
    .hc-patients b { color: #163a66; font-size: 15px; }
</style>
""",
    unsafe_allow_html=True,
)

profile_col, logo_col, search_col = st.columns([0.5, 1.5, 4.2], vertical_alignment="center")

with profile_col:
    with st.popover("👤"):
        signed_in = st.session_state.get("logged_in", False)

        if signed_in:
            user = st.session_state.get("user", {})
            display_name = (
                f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                or user.get("username", "Patient")
            )
            st.markdown(
                f"""
                <div class="profile-pop">
                    <h4>{html_lib.escape(display_name)}</h4>
                    <p>Signed in to CareCompass</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.divider()
            st.caption("Manage your account")
            
            if st.button("Sign out", use_container_width=True, key="profile_signout"):
                st.session_state.clear()
                st.switch_page("title.py")
        else:
            st.markdown(
                """
                <div class="profile-pop">
                    <h4>Guest User</h4>
                    <p>Please login to access your account</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.divider()
            if st.button("Sign In", use_container_width=True, key="profile_signin"):
                st.switch_page("title.py")

with logo_col:
    if LOGO_B64:
        st.markdown(
            f'<img class="cc-logo" src="data:image/jpeg;base64,{LOGO_B64}" alt="CareCompass" />',
            unsafe_allow_html=True,
        )
    else:
        st.markdown("**CareCompass**")

hospital_names = sorted(
    df["hospital_name"].dropna().unique().tolist()
)

with search_col:

    name_query = st.text_input(
        "Search hospitals",
        placeholder="🔍︎   Search by hospital name...",
        label_visibility="collapsed",
        key="hospital_name_query",
    )

    if name_query:
        suggestions = [
            name for name in hospital_names
            if name_query.lower() in name.lower()
        ]

        if suggestions:
            st.caption("Suggestions")

            selected_hospital = st.selectbox(
                "Hospital suggestions",
                suggestions,
                label_visibility="collapsed",
                key="hospital_suggestion"
            )

st.markdown(
    """
<div class="cc-hero">
  <h1>Find the Right Hospital<br>for Your Needs</h1>
  <p>Compare hospitals, explore facilities, and make informed decisions for a healthier tomorrow.</p>
</div>
""",
    unsafe_allow_html=True,
)
# Separate chatbot block
with st.container(border=True):
    run_chatbot(df)
#Manual Filtering
st.header("Filter Hospitals (Manually)")
disease = sorted(df["disease"].dropna().unique().tolist())
new_df=df[df["disease"].isin(disease)]
col1, col2, col3, col4, col5, col6,col7 = st.columns([1,1,1, 1, 1, 0.45, 0.45])
with col1:
    
    with st.container(border=True):
        st.markdown('<div class="filter-caption">🩺 Disease</div>', unsafe_allow_html=True)
        dis_index = disease.index(st.session_state.Disease) if st.session_state.Disease in disease else 0
        dis = st.selectbox(
            "Disease",
            disease,
            index=dis_index,
            label_visibility="collapsed",
        )   
# =========================================================
# STATE FILTER
# =========================================================

# Data for selected disease
states_df = new_df[new_df["disease"] == dis]

# Get all states available for this disease
states = sorted(
    states_df["state"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

# Add All States
state_options = ["All States"] + states


with col2:
    with st.container(border=True):

        st.markdown(
            '<div class="filter-caption">📍 Location (States)</div>',
            unsafe_allow_html=True
        )

        loc_index = (
            state_options.index(st.session_state.locations)
            if st.session_state.locations in state_options
            else 0
        )

        loc = st.selectbox(
            "Location",
            state_options,
            index=loc_index,
            label_visibility="collapsed",
        )


# =========================================================
# CITY FILTER
# =========================================================

if loc == "All States":

    # All cities available for this disease
    cities_df = states_df

else:

    # Cities only from selected state
    cities_df = states_df[
        states_df["state"] == loc
    ]


cities = sorted(
    cities_df["city"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

# Add All Cities
city_options = ["All Cities"] + cities


with col3:
    with st.container(border=True):

        st.markdown(
            '<div class="filter-caption">📍 Location (Cities)</div>',
            unsafe_allow_html=True
        )

        loc1_index = (
            city_options.index(st.session_state.locationc)
            if st.session_state.locationc in city_options
            else 0
        )

        loc1 = st.selectbox(
            "Location",
            city_options,
            index=loc1_index,
            label_visibility="collapsed",
        )
  # fallback to all cities
hos_type_options = ["All"] + sorted(cities_df["hospital_type"].dropna().astype(str).unique().tolist())
with col4:
    with st.container(border=True):
        st.markdown('<div class="filter-caption">🏥 Hospital Type</div>', unsafe_allow_html=True)
        type_index = (
            hos_type_options.index(st.session_state.Hospital_Type)
            if st.session_state.Hospital_Type in hos_type_options
            else 0
        )
        radio1 = st.selectbox(
            "Hospital Type",
            hos_type_options,
            index=type_index,
            label_visibility="collapsed",
        )

with col5:
    with st.container(border=True):
        st.markdown('<div class="filter-caption">💰 Treatment Cost</div>', unsafe_allow_html=True)
        cost = st.number_input(
            "Treatment Cost",
            min_value=1000,
            max_value=100000000,
            value=int(st.session_state.Treatment),
            step=1000,
            label_visibility="collapsed",
        )

with col6:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    reset = st.button("Reset", use_container_width=True)

with col7:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    submit = st.button("Search", use_container_width=True)

if submit:
    st.session_state.locations = loc
    st.session_state.locationc = loc1
    st.session_state.Disease = dis
    st.session_state.Treatment = cost
    st.session_state.Hospital_Type = radio1
    st.success("Search submitted successfully!")
    st.rerun()
elif reset:
    st.session_state.locations = "All States"
    st.session_state.locationc = "All Cities"
    st.session_state.Disease = "Dengue"
    st.session_state.Treatment = 200000
    st.session_state.Hospital_Type = "All"
    st.session_state.Sorting_Parameter = "Treatment Cost"
    st.session_state._clear_name_query = True
    st.success("Search reset successfully!")
    st.rerun()

# =========================================================
# FINAL HOSPITAL FILTER
# =========================================================

# Start with disease + treatment cost
filter_df = df[
    (df["disease"] == st.session_state.Disease)
    & (df["treatment_cost_inr"] <= st.session_state.Treatment)
]


# ---------------------------------------------------------
# STATE FILTER
# ---------------------------------------------------------

if st.session_state.locations != "All States":

    filter_df = filter_df[
        filter_df["state"] == st.session_state.locations
    ]


# ---------------------------------------------------------
# CITY FILTER
# ---------------------------------------------------------

if st.session_state.locationc != "All Cities":

    filter_df = filter_df[
        filter_df["city"] == st.session_state.locationc
    ]


# ---------------------------------------------------------
# HOSPITAL TYPE FILTER
# ---------------------------------------------------------

active_hospital_type = st.session_state.Hospital_Type

if active_hospital_type != "All":

    filter_df = filter_df[
        filter_df["hospital_type"] == active_hospital_type
    ]


if name_query and str(name_query).strip():

    needle = str(name_query).strip()

    filter_df = filter_df[
        filter_df["hospital_name"]
        .astype(str)
        .str.contains(
            needle,
            case=False,
            na=False
        )
    ]

col1, col2 = st.columns([2, 1])
with col1:
    title_col,button_col, sort_col = st.columns([1,1, 1])
    with title_col:
        st.markdown('<div class="section-title">Recommended Hospitals</div>', unsafe_allow_html=True)
    with button_col:
        show=st.button("Show all recommended hospitals", use_container_width=True)
    with sort_col:
        sort_options = [ "Success Rate","Treatment Cost"]
        sort_index = (
            sort_options.index(st.session_state.Sorting_Parameter)
            if st.session_state.Sorting_Parameter in sort_options
            else 0
        )
        radio2 = st.selectbox(
            "Sort by",
            sort_options,
            index=sort_index,
        )
        st.session_state.Sorting_Parameter = radio2
        

    if radio2 == "Success Rate":
        filter_df = filter_df.sort_values(by="Success_Rate", ascending=False)
    else:
        filter_df = filter_df.sort_values(by="treatment_cost_inr", ascending=False)

    if filter_df.empty:
        st.info("No hospitals match the selected filters. Try another type, cost, or search again.")

    photo_seed = "|".join(
        [
            str(st.session_state.locations),
            str(st.session_state.locationc),
            str(st.session_state.Disease),
            str(st.session_state.Treatment),
            str(active_hospital_type),
        ]
    )
    hospital_names = [str(name) for name in filter_df["hospital_name"].tolist()]
    unique_names = list(dict.fromkeys(hospital_names))
    shuffled = unique_shuffled_photos(len(unique_names), HOSPITAL_PHOTOS, photo_seed)
    photo_by_hospital = dict(zip(unique_names, shuffled))
    if not show:
        filter_df = filter_df.head(3)

    # ---------------------------------------------------------
    # HOSPITAL CARDS (upgraded layout, ported from v2)
    # ---------------------------------------------------------
    for index, hospital in filter_df.iterrows():
        photo_uri = photo_by_hospital.get(str(hospital["hospital_name"]))
        name = html_lib.escape(str(hospital["hospital_name"]))
        city = html_lib.escape(str(hospital["city"]))
        htype = html_lib.escape(str(hospital["hospital_type"]))
        rating = float(hospital["rating"])

        # Success-rate colour: green >= 90, amber >= 75, red below.
        # Guards against NaN/inf when patients_on_disease_beds is 0.
        rate = hospital["Success_Rate"]
        if pd.isna(rate) or abs(rate) == float("inf"):
            rate_txt, rate_width, rate_color = "N/A", 0, "#94a3b8"
        else:
            rate_txt = f"{rate:.1f}%"
            rate_width = max(0, min(100, rate))
            rate_color = "#16a34a" if rate >= 90 else "#f59e0b" if rate >= 75 else "#e11d48"

        badge = '<div class="hc-top-badge">★ Top Rated</div>' if rating >= 4.6 else ""
        thumb_inner = f'{badge}<img src="{photo_uri}" alt="{name}" />' if photo_uri else badge

        chips = "".join(
            f'<span class="hc-chip">{html_lib.escape(s.strip())}</span>'
            for s in str(hospital["specialties"]).split("|")
            if s.strip()
        )
        specialties_block = (
            f'<div class="hc-label">Specialties</div><div class="hc-chips">{chips}</div>'
            if chips else ""
        )

        html = f"""<div class="hospital-card">
<div class="hc-row">
<div class="hc-thumb">{thumb_inner}</div>
<div class="hc-main">
<div class="hc-name">{name}</div>
<div class="hc-tags">
<span class="hc-tag hc-tag-type">{htype}</span>
<span class="hc-tag hc-tag-rating">★ {rating:.1f} Rating</span>
</div>
<div class="hc-facts">
<div><div class="hc-label">Location</div><div class="hc-value">{city}</div></div>
<div><div class="hc-label">Treatment Cost</div><div class="hc-value">₹{hospital['treatment_cost_inr']:,}</div></div>
</div>
{specialties_block}
</div>
<div class="hc-side">
<div class="hc-emerg"><span class="hc-dot"></span>24/7 Emergency</div>
<div>
<div class="hc-label">Success Rate</div>
<div class="hc-rate" style="color:{rate_color}">{rate_txt}</div>
<div class="hc-bar"><div class="hc-bar-fill" style="width:{rate_width}%;background:{rate_color}"></div></div>
</div>
<div class="hc-patients">Patients in treatment: <b>{hospital['patients_on_disease_beds']}</b></div>
</div>
</div>
</div>"""
        st.markdown(html, unsafe_allow_html=True)

geolocator = Nominatim(user_agent="care_compass")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def get_city_coordinates(city):
    location = geolocator.geocode(f"{city}, India", timeout=10)
    if location:
        return location.latitude, location.longitude
    return None, None


with col2:
    st.markdown(
        '<div class="map-title">Hospitals Near You</div>',
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------
    # FIND MAP CENTER
    # ---------------------------------------------------------

    if not filter_df.empty:

        # If All States or All Cities is selected,
        # calculate the center from hospital coordinates
        if (
            st.session_state.locations == "All States"
            or st.session_state.locationc == "All Cities"
        ):

            valid_coordinates = filter_df[
                filter_df["latitude"].notna()
                & filter_df["longitude"].notna()
            ]

            if not valid_coordinates.empty:

                latitude = valid_coordinates["latitude"].mean()
                longitude = valid_coordinates["longitude"].mean()

            else:

                # Center of India as fallback
                latitude = 20.5937
                longitude = 78.9629

        else:

            # If a specific city is selected,
            # get its coordinates using Nominatim
            map_city = st.session_state.locationc

            latitude, longitude = get_city_coordinates(map_city)


        # -----------------------------------------------------
        # CREATE MAP
        # -----------------------------------------------------

        if latitude is not None and longitude is not None:

            # Use wider zoom when all states are selected
            if st.session_state.locations == "All States":
                zoom_level = 5
            else:
                zoom_level = 11

            map_object = folium.Map(
                location=[latitude, longitude],
                zoom_start=zoom_level
            )


            # -------------------------------------------------
            # ADD HOSPITAL MARKERS
            # -------------------------------------------------

            for _, row in filter_df.iterrows():

                # Make sure latitude and longitude exist
                if (
                    pd.notna(row["latitude"])
                    and pd.notna(row["longitude"])
                ):

                    folium.Marker(
                        location=[
                            row["latitude"],
                            row["longitude"]
                        ],
                        popup=row["hospital_name"],
                        tooltip=row["hospital_name"],
                        icon=folium.Icon(
                            color="red",
                            icon="info-sign"
                        )
                    ).add_to(map_object)


            # -------------------------------------------------
            # DISPLAY MAP
            # -------------------------------------------------

            map_data = st_folium(
                map_object,
                width=None,
                height=500,
                returned_objects=["last_clicked"],
            )

        else:

            st.error(
                f"Could not find the location: {st.session_state.locationc}"
            )

    else:

        st.info(
            "No hospitals available for the selected filters."
        )


    # ---------------------------------------------------------
    # CTA CARD
    # ---------------------------------------------------------

    st.markdown(
        """
        <div class="cta-card">
            Your health matters.<br>
            Compare. Choose. Get better care.
        </div>
        """,
        unsafe_allow_html=True,
    )

