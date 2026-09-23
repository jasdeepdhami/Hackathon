import os
import base64
import streamlit as st
from auth import login_user
st.set_page_config(
    page_title="CareCompass - Sign In",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

with open("background.jpeg", "rb") as file:
    img = base64.b64encode(file.read()).decode()

logo_b64 = ""
if os.path.exists("logo.jpeg"):
    with open("logo.jpeg", "rb") as file:
        logo_b64 = base64.b64encode(file.read()).decode()

NAVY = "#163A5F"
TEAL = "#13A094"

st.markdown(
    f"""
<style>
.block-container,
[data-testid="stMainBlockContainer"] {{
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}}

[data-testid="stAppViewContainer"],
[data-testid="stApp"] {{
    padding: 0 !important;
    background-image: url('data:image/jpeg;base64,{img}');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stSidebar"],
[data-testid="stExpandSidebarButton"],
[data-testid="stElementToolbar"] {{
    display: none !important;
}}

[data-testid="stHorizontalBlock"]:has(.left-copy),
[data-testid="stHorizontalBlock"]:has(.login-card-marker) {{
    gap: 0 !important;
    align-items: stretch !important;
    flex-wrap: nowrap !important;
    display: flex !important;
}}

div[data-testid="stColumn"]:has(.left-copy) {{
    background: transparent !important;
    flex: 1.15 1 0 !important;
    min-width: 0 !important;
    max-width: 58% !important;
}}

div[data-testid="stColumn"]:has(.login-card-marker) {{
    background: transparent !important;
    flex: 0.85 1 0 !important;
    min-width: 0 !important;
    max-width: 48% !important;
}}

.left-copy {{
    min-height: 100vh;
    padding: 28px 20px 24px 36px;
    box-sizing: border-box;
    background: linear-gradient(
        90deg,
        rgba(247, 252, 255, 0.94) 0%,
        rgba(247, 252, 255, 0.72) 46%,
        rgba(247, 252, 255, 0.12) 100%
    );
}}

.left-copy img {{
    height: 58px;
    width: auto;
    object-fit: contain;
    margin-bottom: 56px;
}}

.hero-title {{
    font-size: 2.55rem !important;
    line-height: 1.15 !important;
    margin: 0 0 16px 0 !important;
    color: {NAVY} !important;
    font-weight: 800 !important;
}}

.hero-title span {{
    color: {TEAL} !important;
}}

.left-copy .lead {{
    max-width: 420px;
    color: #4a5b6b;
    font-size: 1.02rem;
    line-height: 1.55;
    margin: 0 0 28px 0;
}}

.feature {{
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 18px;
    max-width: 420px;
}}

.feature-icon {{
    width: 42px;
    height: 42px;
    min-width: 42px;
    border-radius: 50%;
    background: rgba(19, 160, 148, 0.12);
    color: {TEAL};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}}

.feature strong {{
    display: block;
    color: {NAVY};
    font-size: 0.98rem;
}}

.feature span {{
    color: #5b6b78;
    font-size: 0.88rem;
}}

.left-footer {{
    margin-top: 54px;
    color: {TEAL};
    font-style: italic;
    font-size: 1.05rem;
}}

div[data-testid="stColumn"]:has(.login-card-marker) {{
    background: #ffffff !important;
    border-radius: 22px !important;
    box-shadow: 0 18px 50px rgba(22, 58, 95, 0.16) !important;
    margin: 40px 32px 40px 8px !important;
    padding: 24px 24px 16px 24px !important;
}}

div[data-testid="stColumn"]:has(.login-card-marker) > div {{
    background: transparent !important;
    padding: 0 !important;
    box-shadow: none !important;
}}

div[data-testid="stColumn"]:has(.login-card-marker) [data-testid="stVerticalBlock"] {{
    gap: 0.4rem !important;
    background: transparent !important;
}}

div[data-testid="stColumn"]:has(.login-card-marker) img {{
    max-height: 72px !important;
    width: auto !important;
    object-fit: contain !important;
    margin: 4px auto 8px auto !important;
    display: block !important;
}}

div[data-testid="stColumn"]:has(.login-card-marker) [data-testid="stWidgetLabel"] {{
    display: none !important;
    min-height: 0 !important;
}}

[data-testid="stForm"] {{
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
}}

div[data-baseweb="input"] {{
    width: 100% !important;
    background-color: white !important;
    border: 1px solid #d5dde3 !important;
    border-radius: 12px !important;
}}

div[data-baseweb="input"] input {{
    background-color: white !important;
    color: #333333 !important;
}}

div[data-baseweb="input"] input::placeholder {{
    color: #7a8792 !important;
    opacity: 1 !important;
}}

[data-testid="stTextInput"] button,
[data-testid="stTextInput"] [data-testid="stBaseButton-secondary"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    width: 2rem !important;
    height: 2rem !important;
    min-height: 2rem !important;
    padding: 0 !important;
    color: #5b6b78 !important;
}}

[data-testid="stTextInputRootElement"],
[data-testid="stTextInputRootElement"] > div,
div[data-baseweb="input"],
div[data-baseweb="input"] div {{
    background-color: #ffffff !important;
    background: #ffffff !important;
}}

div[data-baseweb="input"] [data-testid="stIconMaterial"],
div[data-baseweb="input"] .material-symbols-outlined {{
    color: #5b6b78 !important;
}}

div[data-testid="stFormSubmitButton"] {{
    margin-top: 10px !important;
}}

div[data-testid="stFormSubmitButton"] {{
    width: 100% !important;
}}

div[data-testid="stFormSubmitButton"] button,
button[data-testid="stBaseButton-secondaryFormSubmit"] {{
    width: 100% !important;
    height: 48px !important;
    background-color: {TEAL} !important;
    background-image: none !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    white-space: nowrap !important;
}}

div[data-testid="stColumn"]:has(.login-card-marker) [data-testid="stHorizontalBlock"] {{
    gap: 12px !important;
}}

div[data-testid="stColumn"]:has(.register-btn-wrap):not(:has(.login-card-marker)) button {{
    background: {NAVY} !important;
    background-image: none !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    width: 100% !important;
    height: 46px !important;
    font-weight: 700 !important;
    white-space: nowrap !important;
}}

div[data-testid="stColumn"]:has(.skip-btn-wrap):not(:has(.login-card-marker)) button {{
    background: #ffffff !important;
    background-image: none !important;
    color: {NAVY} !important;
    border: 1px solid #d5dde3 !important;
    border-radius: 12px !important;
    width: 100% !important;
    height: 46px !important;
    font-weight: 700 !important;
    white-space: nowrap !important;
}}

.trust-row {{
    text-align: center;
    color: {TEAL};
    font-size: 0.82rem;
    margin-top: 10px;
}}
</style>
""",
    unsafe_allow_html=True,
)

left_space, right_space = st.columns([1.08, 1])

with left_space:
    logo_html = (
        f'<img src="data:image/jpeg;base64,{logo_b64}" alt="CareCompass" />'
        if logo_b64
        else "<h3>CareCompass</h3>"
    )
    st.markdown(
        f"""
        <div class="left-copy">
            {logo_html}
            <div class="hero-title">Better Care.<br><span>Smarter Decisions.</span></div>
            <p class="lead">
                CareCompass helps you find the right hospital,
                understand treatment costs and make informed
                healthcare decisions — all in one place.
            </p>
            <div class="feature">
                <div class="feature-icon">🏥</div>
                <div>
                    <strong>Find Hospitals</strong>
                    <span>Explore trusted hospitals near you.</span>
                </div>
            </div>
            <div class="feature">
                <div class="feature-icon">₹</div>
                <div>
                    <strong>Compare Costs</strong>
                    <span>Get treatment cost estimates easily.</span>
                </div>
            </div>
            <div class="feature">
                <div class="feature-icon">🛡️</div>
                <div>
                    <strong>Make Informed Choices</strong>
                    <span>Better information. Healthier tomorrow.</span>
                </div>
            </div>
            <div class="left-footer">♡ Your Health, Our Priority</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_space:
    st.markdown('<div class="login-card-marker"></div>', unsafe_allow_html=True)

    if logo_b64:
        st.markdown(
            f"""
            <div style="display:flex;justify-content:center;">
                <img src="data:image/jpeg;base64,{logo_b64}" alt="CareCompass" />
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<p style="color:#4a5b6b;text-align:center;margin:0 0 12px 0;">'
        "Sign in to your Care Compass account to continue</p>",
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        username = st.text_input(
            "",
            placeholder="Username",
            icon=":material/person:",
            label_visibility="collapsed",
        )
        password = st.text_input(
            "",
            type="password",
            placeholder="Password",
            icon=":material/lock:",
            label_visibility="collapsed",
        )
        login = st.form_submit_button(
            "Sign In :material/arrow_forward:",
            use_container_width=True,
        )
    if login:

        if not username or not password:
            st.error("Please enter username and password.")

        else:
            user = login_user(
            username=username.strip(),
            password=password
        )

            if user is not None:

            # Store logged-in user in session
                st.session_state.logged_in = True
                st.session_state.user = user
                st.session_state.user_id = user["user_id"]

                st.success("Login successful!")

                st.switch_page("pages/home.py")

            else:
                st.error("Invalid username or password.")

    st.markdown(
        '<p style="color:#5b6b78;text-align:center;margin:14px 0 8px 0;">'
        "Don't have an account?</p>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="register-btn-wrap"></div>', unsafe_allow_html=True)
        if st.button("Register", icon=":material/person_add:", use_container_width=True):
            st.switch_page("pages/signup.py")
    with col2:
        st.markdown('<div class="skip-btn-wrap"></div>', unsafe_allow_html=True)
        if st.button("Skip", icon=":material/arrow_forward:", use_container_width=True):
            st.switch_page("pages/home.py")

    st.markdown(
        '<p class="trust-row">🛡️ Secure  •  Trusted  •  For a Healthier You</p>',
        unsafe_allow_html=True,
    )
