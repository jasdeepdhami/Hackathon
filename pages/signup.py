import base64
from pathlib import Path
import streamlit as st
from auth import signup_user
st.set_page_config(
    page_title="CareCompass - Sign Up",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)
ROOT = Path(__file__).resolve().parent.parent
bg_path = ROOT / "background.jpeg"
logo_path = ROOT / "logo.jpeg"
if not bg_path.exists():
    bg_path = Path("background.jpeg")
if not logo_path.exists():
    logo_path = Path("logo.jpeg")

img = ""
if bg_path.exists():
    img = base64.b64encode(bg_path.read_bytes()).decode()

logo_b64 = ""
if logo_path.exists():
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()

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
    background: #f4f9fc !important;
}}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stSidebar"],
[data-testid="stExpandSidebarButton"],
[data-testid="stElementToolbar"],
[data-testid="stHeaderActionElements"] {{
    display: none !important;
}}

[data-testid="stHorizontalBlock"]:has(.signup-hero),
[data-testid="stHorizontalBlock"]:has(.signup-panel-marker) {{
    gap: 0 !important;
    align-items: stretch !important;
    flex-wrap: nowrap !important;
    display: flex !important;
}}

div[data-testid="stColumn"]:has(.signup-hero) {{
    flex: 1.05 1 0 !important;
    min-width: 0 !important;
    max-width: 52% !important;
}}

div[data-testid="stColumn"]:has(.signup-panel-marker) {{
    flex: 0.95 1 0 !important;
    min-width: 0 !important;
    max-width: 48% !important;
    background: #f7fbfe !important;
    min-height: 100vh !important;
    padding: 28px 42px 24px 36px !important;
}}

div[data-testid="stColumn"]:has(.signup-panel-marker) [data-testid="stVerticalBlock"] {{
    gap: 0.28rem !important;
}}

div[data-testid="stColumn"]:has(.signup-panel-marker) [data-testid="stHorizontalBlock"] {{
    gap: 12px !important;
    flex-wrap: nowrap !important;
}}

div[data-testid="stTextInput"] [data-testid="stWidgetLabel"],
div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] {{
    display: none !important;
    min-height: 0 !important;
}}

.signup-hero {{
    min-height: 100vh;
    background-image: linear-gradient(
            90deg,
            rgba(247, 252, 255, 0.55) 0%,
            rgba(247, 252, 255, 0.08) 42%,
            rgba(0, 0, 0, 0) 100%
        ),
        url('data:image/jpeg;base64,{img}');
    background-size: cover;
    background-position: center;
    padding: 36px 40px 32px 44px;
    box-sizing: border-box;
}}

.signup-hero img {{
    height: 56px;
    width: auto;
    object-fit: contain;
    margin-bottom: 70px;
}}

.hero-title {{
    font-size: 2.7rem !important;
    line-height: 1.12 !important;
    color: {NAVY} !important;
    font-weight: 800 !important;
    margin: 0 0 16px 0 !important;
    max-width: 420px;
}}

.hero-kicker {{
    letter-spacing: 0.14em;
    font-size: 0.78rem;
    font-weight: 700;
    color: {NAVY};
    text-transform: uppercase;
}}

.panel-title {{
    color: {NAVY} !important;
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    margin: 0 0 6px 0 !important;
}}

.panel-sub {{
    color: #5b6b78;
    font-size: 0.92rem;
    margin: 0 0 14px 0;
    line-height: 1.45;
}}

[data-testid="stForm"] {{
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
}}

div[data-baseweb="input"],
div[data-baseweb="select"] {{
    width: 100% !important;
    background-color: white !important;
    border: 1px solid #d5dde3 !important;
    border-radius: 12px !important;
}}

div[data-baseweb="input"] input,
div[data-baseweb="select"] input {{
    background-color: white !important;
    color: #64748B !important;
}}

div[data-baseweb="select"],
div[data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] {{
    background-color: #ffffff !important;
    background: #ffffff !important;
    color: #333333 !important;
    border-radius: 12px !important;
}}

[data-testid="stSelectbox"] [data-baseweb="select"] * {{
    color: #333333 !important;
    background-color: transparent !important;
}}

[data-testid="stCheckbox"] {{
    padding-top: 4px !important;
    padding-bottom: 4px !important;
}}

[data-testid="stCheckbox"] label p {{
    color: {NAVY} !important;
    font-size: 0.86rem !important;
}}

[data-testid="stTextInputRootElement"],
[data-testid="stTextInputRootElement"] > div,
div[data-baseweb="input"] div {{
    background-color: #ffffff !important;
    background: #ffffff !important;
}}

[data-testid="stTextInput"] button,
[data-testid="stTextInput"] [data-testid="stBaseButton-secondary"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    width: 2rem !important;
    height: 2rem !important;
    min-height: 2rem !important;
    color: #5b6b78 !important;
}}

div[data-baseweb="input"] input,
div[data-baseweb="select"] input {{
    background-color: white !important;
    color: #64748B !important;;
}}

div[data-baseweb="input"] input::placeholder {{
    color: #64748B !important;
    opacity: 1 !important;
}}

div[data-testid="stFormSubmitButton"] {{
    width: 100% !important;
    margin-top: 8px !important;
}}

div[data-testid="stFormSubmitButton"] button,
button[data-testid="stBaseButton-secondaryFormSubmit"] {{
    width: 100% !important;
    height: 46px !important;
    background: {TEAL} !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    white-space: nowrap !important;
}}

div[data-testid="stCheckbox"] label {{
    color: {NAVY} !important;
    font-size: 0.86rem !important;
}}

div[data-testid="stColumn"]:has(.signup-panel-marker) [data-testid="stButton"] button {{
    background: #ffffff !important;
    color: {NAVY} !important;
    border: 1px solid #d5dde3 !important;
    border-radius: 12px !important;
    width: 100% !important;
    height: 46px !important;
    font-weight: 700 !important;
    white-space: nowrap !important;
}}

div[data-testid="stColumn"]:has(.signup-panel-marker) [data-testid="stPageLink-NavLink"],
div[data-testid="stColumn"]:has(.signup-panel-marker) a {{
    color: {TEAL} !important;
    justify-content: center !important;
    font-weight: 700 !important;
    text-decoration: none !important;
}}

.or-row {{
    text-align: center;
    color: #8a97a3;
    font-size: 0.82rem;
    letter-spacing: 0.08em;
    margin: 8px 0 4px 0;
}}

.signin-row {{
    text-align: center;
    color: #5b6b78;
    font-size: 0.9rem;
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
        <div class="signup-hero">
            {logo_html}
            <div class="hero-title">Better Health<br>Starts Here</div>
            <div class="hero-kicker">Find Hospitals  •  Compare  •  Make Informed Decisions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_space:
    st.markdown('<div class="signup-panel-marker"></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Create Your Account</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="panel-sub">Join CareCompass to explore hospitals, compare '
        "facilities, and make better healthcare decisions.</p>",
        unsafe_allow_html=True,
    )

    with st.form("signup_form"):
        col_fn, col_ln = st.columns(2)
        with col_fn:
            first_name = st.text_input(
                "First Name",
                placeholder="First Name",
                icon=":material/person:",
                label_visibility="collapsed",
            )
        with col_ln:
            last_name = st.text_input(
                "Last Name",
                placeholder="Last Name",
                icon=":material/person:",
                label_visibility="collapsed",
            )
        username = st.text_input(
        "Username",
        placeholder="Username",
        icon=":material/person:",
        label_visibility="collapsed",
    )
        email = st.text_input(
            "Email",
            placeholder="Email address",
            icon=":material/mail:",
            label_visibility="collapsed",
        )
        phone = st.text_input(
            "Phone",
            placeholder="Phone number",
            icon=":material/call:",
            label_visibility="collapsed",
        )
        
        password = st.text_input(
            "Password",
            placeholder="Password",
            type="password",
            icon=":material/lock:",
            label_visibility="collapsed",
        )
        confirm = st.text_input(
            "Confirm password",
            placeholder="Confirm password",
            type="password",
            icon=":material/lock:",
            label_visibility="collapsed",
        )
        
        created = st.form_submit_button(
            "Create Account :material/arrow_forward:",
            use_container_width=True,
        )

        if created:
            missing = not all([
        first_name,
        last_name,
        username,
        email,
        phone,
        password,
        confirm
    ])

            if missing:
                st.error("Please fill in all fields.")

            elif password != confirm:
                st.error("Passwords do not match.")

            else:

                success, result = signup_user(
            username=username.strip(),
            password=password,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            phone_number=phone.strip(),
            email=email.strip(),
        )

                if success:
                    st.success("Account created successfully!")

                    st.switch_page("title.py")

                else:
                    st.error(result)

    st.markdown('<p class="or-row">OR</p>', unsafe_allow_html=True)
    
    col1,col2,col4= st.columns(3)
    with col1:
        st.markdown(
        '<p class="signin-row">Already have an account?</p>',
        unsafe_allow_html=True,
        )
    with col2:
        st.page_link("title.py", label="*:blue[Sign in]*")
