import re
import textwrap

import pandas as pd
import streamlit as st

from nlp import analyze_query
from recommendation import compare_hospitals, recommend_hospitals


# ============================================================
# HTML RENDER HELPER
# ============================================================
#
# Streamlit's Markdown renderer treats any line indented by
# 4+ spaces as a code block. Because HTML strings written
# inside indented Python functions inherit that indentation,
# passing them straight to st.markdown() causes Streamlit to
# print the raw tags as text instead of rendering them.
#
# _html() strips that leading indentation (via textwrap.dedent)
# before the string reaches st.markdown(), which fixes it.
# ALWAYS use this helper instead of calling st.markdown()
# directly with a hand-indented HTML string.

def _html(content: str) -> None:
    st.markdown(
        textwrap.dedent(content).strip(),
        unsafe_allow_html=True,
    )


# ============================================================
# HEALTHCARE TERMS
# ============================================================

HEALTHCARE_TERMS = [
    "hospital",
    "hospitals",
    "clinic",
    "doctor",
    "doctors",
    "treatment",
    "treatments",
    "patient",
    "care",
    "medical",
    "health",
    "healthcare",
    "surgery",
    "emergency",
    "recommend",
    "recommendation",
    "compare",
    "versus",
    "rating",
    "success",
    "beds",
    "specialist",
    "specialty",
    "speciality",
    "specialties",
    "nabh",
]


# ============================================================
# OFF-TOPIC TERMS
# ============================================================

OFF_TOPIC_TERMS = {
    "car",
    "cars",
    "vehicle",
    "vehicles",
    "bike",
    "bikes",
    "motorcycle",
    "bus",
    "train",
    "flight",
    "flights",
    "hotel",
    "hotels",
    "movie",
    "movies",
    "laptop",
    "phone",
    "mobile",
    "restaurant",
    "shopping",
    "clothes",
    "school",
    "college",
    "job",
    "jobs",
    "cricket",
    "football",
    "stock",
    "stocks",
}


# ============================================================
# INITIALIZE CHATBOT
# ============================================================

def initialize_chatbot():
    if "messages" not in st.session_state:
        st.session_state.messages = []


# ============================================================
# CHATBOT CSS
# ============================================================

def chatbot_styles():
    _html(
        """
        <style>

        /* =========================================
           CHATBOT HEADER
           ========================================= */

        .chatbot-title-box {
            background: #ffffff;
            border: 1px solid #d7e3e9;
            border-radius: 16px;
            padding: 18px 22px;
            margin-top: 10px;
            margin-bottom: 8px;
            box-shadow: 0 3px 12px rgba(22, 58, 95, 0.07);
        }

        .chatbot-title {
            color: #163A5F;
            font-size: 1.15rem;
            font-weight: 750;
            margin-bottom: 4px;
        }

        .chatbot-subtitle {
            color: #13A094;
            font-size: 0.78rem;
            font-weight: 600;
        }

        /* =========================================
           DESCRIPTION
           ========================================= */

        .chatbot-description {
            color: #63788a;
            font-size: 0.88rem;
            line-height: 1.5;
            padding: 6px 4px 12px 4px;
        }

        /* =========================================
           WELCOME BOX
           ========================================= */

        .chatbot-welcome {
            background: #ffffff;
            border: 1px solid #dce7ec;
            border-radius: 15px;
            padding: 18px 20px;
            margin: 4px 0 15px 0;
            color: #334e68;
            line-height: 1.6;
            box-shadow: 0 2px 8px rgba(22, 58, 95, 0.04);
        }

        .chatbot-welcome-title {
            color: #163A5F;
            font-weight: 700;
            font-size: 0.98rem;
        }

        .chatbot-example {
            color: #13A094;
            font-weight: 700;
        }

        /* =========================================
           CHAT MESSAGES
           ========================================= */

        [data-testid="stChatMessage"] {
            border-radius: 14px !important;
            margin: 8px 0 !important;
            padding: 10px 14px !important;
        }

        /* Assistant message */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
            background: #ffffff !important;
            border: 1px solid #dce7ec !important;
            box-shadow: 0 2px 8px rgba(22, 58, 95, 0.04);
        }

        /* User message */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: #e8f7f5 !important;
            border: 1px solid #c8e8e4 !important;
        }

        /* =========================================
           CHAT INPUT
           ========================================= */

        [data-testid="stChatInput"] {
            margin-top: 8px !important;
            margin-bottom: 5px !important;
        }

        [data-testid="stChatInput"] > div {
            background: #ffffff !important;
            border: 1px solid #cbdce4 !important;
            border-radius: 15px !important;
            box-shadow: 0 4px 14px rgba(22, 58, 95, 0.08) !important;
        }

        [data-testid="stChatInput"] textarea {
            color: #163A5F !important;
            font-size: 0.94rem !important;
        }

        [data-testid="stChatInput"] textarea::placeholder {
            color: #8aa0b2 !important;
            opacity: 1 !important;
        }

        [data-testid="stChatInput"] button {
            background: #13A094 !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
        }

        [data-testid="stChatInput"] button:hover {
            background: #0F857C !important;
        }

        /* =========================================
           CHAT MESSAGE TEXT
           ========================================= */

        [data-testid="stChatMessage"] p {
            color: #334e68;
        }

        [data-testid="stChatMessage"] strong {
            color: #163A5F;
        }

        [data-testid="stChatMessage"] h3 {
            color: #163A5F !important;
            font-size: 1.05rem !important;
        }

        /* =========================================
           SMALL SCREEN
           ========================================= */

        @media (max-width: 700px) {
            .chatbot-title-box {
                padding: 15px 16px;
            }
            .chatbot-description {
                padding-left: 2px;
                padding-right: 2px;
            }
            [data-testid="stChatMessage"] {
                margin-left: 0 !important;
                margin-right: 0 !important;
            }
        }

        </style>
        """
    )


# ============================================================
# GET VALUE FROM DATAFRAME ROW
# ============================================================

def _cell(row, *column_names):
    for column in column_names:
        if column in row.index:
            value = row[column]
            if pd.notna(value):
                return value
    return None


# ============================================================
# CHECK WHETHER QUERY IS RELEVANT
# ============================================================

def is_relevant_query(query, query_info):
    lowered = str(query).lower()

    tokens = set(re.findall(r"[a-z0-9]+", lowered))

    # Check for clearly unrelated topics
    if tokens & OFF_TOPIC_TERMS:
        return False

    # Check healthcare words
    has_medical_term = any(
        re.search(r"\b" + re.escape(term) + r"\b", lowered)
        for term in HEALTHCARE_TERMS
    )

    has_disease = bool(query_info.get("disease"))
    has_specialty = bool(query_info.get("specialty"))
    has_hospital = bool(
        query_info.get("hospital") or query_info.get("hospitals")
    )

    if has_medical_term or has_disease or has_specialty or has_hospital:
        return True

    return False


# ============================================================
# OFF-TOPIC RESPONSE
# ============================================================

def off_topic_response():
    return (
        "I can only help with **hospital recommendations "
        "and comparisons**. Queries like cars, shopping, "
        "or travel are outside what I can do.\n\n"
        "Try something like:\n"
        "- `dengue hospitals in Punjab`\n"
        "- `cardiology hospitals in Delhi under 50000`\n"
        "- `compare AIIMS Delhi and Sir Ganga Ram Hospital`"
    )


# ============================================================
# FORMAT HOSPITAL CARD
# ============================================================

def format_hospital_card(row, index):
    name = _cell(row, "hospital_name", "name") or "Unknown hospital"

    response = f"**{index}. {name}**\n\n"

    # Location
    city = _cell(row, "city")
    state = _cell(row, "state")

    if city or state:
        location = ", ".join(part for part in [city, state] if part)
        response += f"📍 **Location:** {location}\n\n"

    # Hospital type
    hospital_type = _cell(row, "hospital_type")
    if hospital_type:
        response += f"🏥 **Type:** {hospital_type}\n\n"

    # Rating
    rating = pd.to_numeric(_cell(row, "rating"), errors="coerce")
    if pd.notna(rating):
        response += f"⭐ **Rating:** {rating:.1f}\n\n"

    # Treatment cost
    cost = pd.to_numeric(_cell(row, "treatment_cost_inr"), errors="coerce")
    if pd.notna(cost):
        response += f"💰 **Treatment Cost:** ₹{cost:,.0f}\n\n"

    # Success rate
    success_rate = pd.to_numeric(_cell(row, "success_rate"), errors="coerce")
    if pd.notna(success_rate):
        response += f"📊 **Success Rate:** {success_rate:.2f}%\n\n"

    # Disease
    disease = _cell(row, "disease")
    if disease:
        response += f"🦠 **Disease:** {disease}\n\n"

    # Specialties
    specialties = _cell(row, "specialties")
    if specialties:
        response += f"🩺 **Specialties:** {specialties}\n\n"

    response += "---\n\n"

    return response


# ============================================================
# FORMAT HOSPITAL RESULTS
# ============================================================

def format_hospital_results(results, query_info):
    if results is None or results.empty:
        return (
            "I couldn't find any hospitals matching "
            "your requirements. Try another city, "
            "disease, specialty, or budget."
        )

    hints = []

    if query_info.get("disease"):
        hints.append(f"disease **{query_info['disease']}**")

    if query_info.get("specialty"):
        hints.append(f"specialty **{query_info['specialty']}**")

    if query_info.get("city"):
        hints.append(f"city **{query_info['city']}**")

    if query_info.get("state"):
        hints.append(f"state **{query_info['state']}**")

    if query_info.get("budget") is not None:
        hints.append(f"budget up to ₹{query_info['budget']:,.0f}")

    response = "### 🏥 Recommended Hospitals\n\n"
    response += "Sorted by **success rate** (highest first).\n\n"

    if hints:
        response += "Matching " + ", ".join(hints) + ":\n\n"

    for index, row in results.iterrows():
        response += format_hospital_card(row, index + 1)

    return response


# ============================================================
# FORMAT HOSPITAL COMPARISON
# ============================================================

def format_comparison(results, hospital_names):
    if results is None or results.empty:
        names = " and ".join(f"**{name}**" for name in hospital_names)
        return (
            f"I couldn't compare {names}. "
            "Please use hospital names from the dataset."
        )

    response = "### ⚖️ Hospital Comparison\n\n"
    response += "Sorted by **success rate** (highest first).\n\n"

    if len(results) == 1:
        found = _cell(results.iloc[0], "hospital_name") or "one hospital"
        response += f"I only found **{found}**. Name two hospitals to compare.\n\n"

    for index, row in results.iterrows():
        response += format_hospital_card(row, index + 1)

    if len(results) >= 2:
        top = _cell(results.iloc[0], "hospital_name") or "the first hospital"
        top_rate = pd.to_numeric(
            _cell(results.iloc[0], "success_rate"), errors="coerce"
        )

        if pd.notna(top_rate):
            response += f"**{top}** has the higher success rate ({top_rate:.2f}%)."
        else:
            response += f"**{top}** ranks first in this comparison."

    return response


# ============================================================
# PROCESS USER QUERY
# ============================================================

def process_query(query, hospital_data):
    query_info = analyze_query(query, hospital_data)

    # Always sort by success rate
    query_info["sort_by"] = "success_rate"

    # Check relevance
    if not is_relevant_query(query, query_info):
        return off_topic_response()

    # ========================================================
    # HOSPITAL COMPARISON
    # ========================================================
    if query_info.get("intent") == "compare":
        hospital_names = query_info.get("hospitals") or []

        if len(hospital_names) < 2:
            return (
                "To compare hospitals, name **two hospitals**, for example:\n\n"
                "`compare AIIMS Delhi and Sir Ganga Ram Hospital`."
            )

        results = compare_hospitals(hospital_data, hospital_names[:2])

        return format_comparison(results, hospital_names[:2])

    # ========================================================
    # HOSPITAL RECOMMENDATION
    # ========================================================
    results = recommend_hospitals(hospital_data, query_info)

    return format_hospital_results(results, query_info)


# ============================================================
# MAIN CHATBOT
# ============================================================

def run_chatbot(hospital_data):
    initialize_chatbot()
    chatbot_styles()

    # ========================================================
    # CHATBOT HEADER
    # ========================================================
    _html(
        """
        <div class="chatbot-title-box">
            <div class="chatbot-title">
                🤖 &nbsp; CareCompass Hospital Assistant
            </div>
            <div class="chatbot-subtitle">
                🟢 Online • Hospital recommendations
            </div>
        </div>
        """
    )

    # ========================================================
    # DESCRIPTION
    # ========================================================
    _html(
        """
        <div class="chatbot-description">
            Ask about hospitals by
            <b>disease</b>,
            <b>location</b>, or
            <b>specialty</b>.
            You can also compare two hospitals.
            Results are ranked by success rate.
        </div>
        """
    )

    # ========================================================
    # WELCOME MESSAGE
    # ========================================================
    if not st.session_state.messages:
        _html(
            """
            <div class="chatbot-welcome">
                <div class="chatbot-welcome-title">
                    👋 Hi! I'm your CareCompass Hospital Assistant.
                </div>
                <br>
                I can help you find hospitals based on
                disease, city, specialty, treatment cost,
                or compare two hospitals.
                <br><br>
                <span class="chatbot-example">Try asking:</span>
                <br><br>
                🏥 &nbsp; <b>Dengue hospitals in Punjab</b>
                <br><br>
                📍 &nbsp; <b>Cardiology hospitals in Delhi</b>
                <br><br>
                ⚖️ &nbsp; <b>Compare AIIMS Delhi and Sir Ganga Ram Hospital</b>
            </div>
            """
        )

    # ========================================================
    # CHAT HISTORY
    # ========================================================
    else:
        for message in st.session_state.messages:
            avatar = "🤖" if message["role"] == "assistant" else "👤"

            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    # ========================================================
    # CHAT INPUT
    # ========================================================
    user_query = st.chat_input(
        "Ask me about hospitals, diseases, locations or specialties..."
    )

    if not user_query:
        return

    # ========================================================
    # SAVE USER MESSAGE
    # ========================================================
    st.session_state.messages.append(
        {"role": "user", "content": user_query}
    )

    # ========================================================
    # PROCESS QUERY
    # ========================================================
    try:
        response = process_query(user_query, hospital_data)
    except Exception as e:
        # Keep the actual error in the terminal
        # while showing a friendly message to the user.
        print("Chatbot error:", e)

        response = (
            "Something went wrong while searching "
            "hospitals. Please try a hospital-related "
            "query such as:\n\n"
            "- `dengue hospitals in Delhi`\n"
            "- `cardiology hospitals in Punjab`\n"
            "- `compare two hospitals`"
        )

    # ========================================================
    # SAVE ASSISTANT RESPONSE
    # ========================================================
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    # ========================================================
    # REFRESH
    # ========================================================
    st.rerun()