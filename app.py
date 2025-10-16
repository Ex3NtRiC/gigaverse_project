# app.py
import streamlit as st
import time
from backend import ask_ai, start_prompt, generate_roadmap_image
import re

# --- Page config ---
st.set_page_config(page_title="AI Career Path Guide", page_icon="🎯", layout="wide")

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = start_prompt()
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "awaiting_options" not in st.session_state:
    st.session_state.awaiting_options = False
if "processing" not in st.session_state:
    st.session_state.processing = False
if "answered" not in st.session_state:
    st.session_state.answered = False
if "session_start" not in st.session_state:
    st.session_state.session_start = time.time()
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "final_recommendation" not in st.session_state:
    st.session_state.final_recommendation = None
if "roadmap_image" not in st.session_state:
    st.session_state.roadmap_image = None

# --- Calculate session duration ---
elapsed = int(time.time() - st.session_state.session_start)
mins, secs = divmod(elapsed, 60)
session_duration = f"{mins:02d}:{secs:02d}"

# --- Theme styles (Dark theme only) ---
bg_color = "#1e1e1e"
text_color = "#ffffff"
nav_bg = "#2d2d2d"
card_bg = "#2d2d2d"
border_color = "#444"
button_bg = "#4a4a4a"
accent_color = "#64b5f6"
hero_text = "#ffffff"
secondary_text = "#cccccc"

# --- Custom CSS ---
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Inter', sans-serif;
    }}

    .sticky-navbar {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: {nav_bg};
        padding: 15px 20px;
        z-index: 9999;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid {accent_color};
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}

    .nav-item {{
        color: {text_color};
        font-weight: 600;
        font-size: 16px;
        margin: 0 15px;
    }}

    .content-padding {{
        padding-top: 80px;
    }}

    .conversation-card {{
        background: {card_bg};
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid {accent_color};
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}

    .question-text {{
        color: {accent_color};
        font-weight: 600;
        font-size: 18px;
        margin-bottom: 8px;
    }}

    .answer-text {{
        color: {text_color};
        font-size: 16px;
        padding-left: 10px;
    }}

    .hero-section {{
        text-align: center;
        padding: 40px 20px;
        background: linear-gradient(135deg, {accent_color}22 0%, {accent_color}11 100%);
        border-radius: 15px;
        margin-bottom: 30px;
    }}

    .hero-title {{
        font-size: 42px;
        font-weight: 700;
        color: {accent_color};
        margin-bottom: 10px;
    }}

    .hero-subtitle {{
        font-size: 20px;
        color: {hero_text};
        opacity: 0.9;
    }}

    .stButton > button {{
        background: {accent_color} !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        background: {accent_color} !important;
        color: white !important;
    }}

    .stButton > button:disabled {{
        background: {button_bg} !important;
        color: #999 !important;
        cursor: not-allowed;
        transform: none;
    }}

    /* Force form submit button styling */
    .stFormSubmitButton > button {{
        background: {accent_color} !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 16px;
    }}

    .stFormSubmitButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        background: {accent_color} !important;
        color: white !important;
    }}

    .stFormSubmitButton > button:disabled {{
        background: {button_bg} !important;
        color: #999 !important;
        cursor: not-allowed;
    }}

    /* Fix radio button and text visibility in light theme */
    .stRadio > label, .stTextArea > label {{
        color: {text_color} !important;
    }}

    .stMultiSelect > label {{
        color: white !important;
    }}

    .stRadio > div {{
        color: {text_color} !important;
    }}

    .stRadio label {{
        color: {text_color} !important;
    }}

    div[role="radiogroup"] label {{
        color: {text_color} !important;
    }}

    div[role="radiogroup"] label span {{
        color: {text_color} !important;
    }}

    .stRadio div[data-baseweb="radio"] > div {{
        color: {text_color} !important;
    }}

    .stMultiSelect div {{
        color: {text_color} !important;
    }}

    /* Force radio button text color */
    [data-testid="stMarkdownContainer"] p {{
        color: {text_color} !important;
    }}

    /* Balloon animation */
    @keyframes float {{
        0%, 100% {{ transform: translateY(0) rotate(0deg); }}
        50% {{ transform: translateY(-20px) rotate(5deg); }}
    }}

    @keyframes rise {{
        0% {{ opacity: 0; transform: translateY(100vh) scale(0); }}
        10% {{ opacity: 1; transform: translateY(80vh) scale(1); }}
        100% {{ opacity: 0; transform: translateY(-100vh) scale(1); }}
    }}

    .balloon {{
        position: fixed;
        font-size: 50px;
        animation: rise 8s ease-in infinite;
        z-index: 1000;
    }}

    .recommendation-box {{
        background: linear-gradient(135deg, {accent_color}22 0%, {accent_color}33 100%);
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        border: 2px solid {accent_color};
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        animation: slideIn 0.8s ease-out;
    }}

    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .recommendation-title {{
        font-size: 32px;
        font-weight: 700;
        color: {accent_color};
        margin-bottom: 20px;
        text-align: center;
    }}

    .recommendation-content {{
        font-size: 18px;
        line-height: 1.8;
        color: {secondary_text};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Navigation Bar ---
nav_html = f"""
<div class="sticky-navbar">
    <div class="nav-item">🎯 Career Path Guide</div>
    <div class="nav-item">⏱️ {session_duration}</div>
</div>
<div class="content-padding"></div>
"""
st.markdown(nav_html, unsafe_allow_html=True)

# --- Theme toggle and restart in columns ---
col1, col2 = st.columns([7, 1])
with col2:
    if st.button("🔄 Restart"):
        for key in ["messages", "conversation", "awaiting_options", "processing", "answered", "session_start",
                    "final_recommendation", "roadmap_image"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# --- Hero Section ---
if not st.session_state.conversation:
    st.markdown(
        f"""
        <div class="hero-section">
            <div class="hero-title">Discover Your Perfect Career Path</div>
            <div class="hero-subtitle">Share your passions, skills, and dreams — let AI guide you step by step</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Chat history (answered only) ---
if st.session_state.conversation:
    st.markdown("### 💬 Your Journey So Far")
    for idx, entry in enumerate(st.session_state.conversation, 1):
        if entry.get("answer"):
            st.markdown(
                f"""
                <div class="conversation-card">
                    <div class="question-text">Q{idx}: {entry['question']}</div>
                    <div class="answer-text">💡 {entry['answer']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("---")

# --- Check for final recommendation ---
if st.session_state.conversation:
    latest_reply = st.session_state.messages[-1]["content"]
    if "ready to give you a career recommendation" in latest_reply.lower() or "career recommendation" in latest_reply.lower():
        st.session_state.final_recommendation = latest_reply

# --- Display final recommendation with animation ---
if st.session_state.final_recommendation:
    # Balloons animation
    balloons_html = """
    <div>
        <div class="balloon" style="left: 10%; animation-delay: 0s;">🎈</div>
        <div class="balloon" style="left: 25%; animation-delay: 1s;">🎉</div>
        <div class="balloon" style="left: 40%; animation-delay: 2s;">🎊</div>
        <div class="balloon" style="left: 55%; animation-delay: 1.5s;">🎈</div>
        <div class="balloon" style="left: 70%; animation-delay: 0.5s;">🎉</div>
        <div class="balloon" style="left: 85%; animation-delay: 2.5s;">🎊</div>
    </div>
    """
    st.markdown(balloons_html, unsafe_allow_html=True)

    # Add header with anchor for linking
    st.markdown("### 🌟 Your Personalized Career Recommendation")

    # Recommendation box
    st.markdown(
        f"""
        <div class="recommendation-box">
            <div class="recommendation-content">{st.session_state.final_recommendation}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Generate roadmap image
    if not st.session_state.roadmap_image:
        with st.spinner("✨ Creating your personalized career roadmap..."):
            try:
                # Collect user answers for context
                user_profile = []
                for entry in st.session_state.conversation:
                    if entry.get("answer"):
                        user_profile.append(f"Q: {entry['question']}\nA: {entry['answer']}")

                profile_context = "\n\n".join(user_profile)

                image_url = generate_roadmap_image(
                    st.session_state.final_recommendation,
                    profile_context
                )
                st.session_state.roadmap_image = image_url
            except Exception as e:
                st.error(f"Could not generate roadmap image: {str(e)}")

    if st.session_state.roadmap_image:
        st.markdown("### 🗺️ Your Career Roadmap")
        st.image(st.session_state.roadmap_image, use_container_width=True)
        st.markdown(f"[🔗 Open Roadmap in New Tab]({st.session_state.roadmap_image})")

    st.stop()

# Step 1: Start conversation
if not st.session_state.conversation:
    # Check if we need to process a pending start
    if st.session_state.get("pending_start_input"):
        user_input = st.session_state.pending_start_input
        st.session_state.processing = True
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("🤔 Analyzing your profile..."):
            reply = ask_ai(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.conversation.append({"question": reply, "answer": None})
        st.session_state.processing = False
        del st.session_state.pending_start_input
        st.rerun()

    with st.form(key="start_form", clear_on_submit=False):
        user_input = st.text_area(
            "Tell us about yourself:",
            "",
            placeholder="e.g., I love solving problems, working with data, and helping people. I have a background in mathematics and enjoy creative projects...",
            height=150
        )
        submit = st.form_submit_button("🚀 Start My Journey", disabled=st.session_state.processing)

    if submit:
        if user_input.strip():
            st.session_state.pending_start_input = user_input
            st.rerun()
        else:
            st.warning("⚠️ Please tell us about yourself before starting.")

# --- Step 2: Continue conversation ---
else:
    latest_reply = st.session_state.messages[-1]["content"]

    # --- Parse question and options ---
    lines = [line.strip() for line in latest_reply.split("\n") if line.strip()]
    question_lines, options = [], []

    # First, identify where options start
    option_start_index = -1
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith(("-", "•")) or re.match(r"^\d+\.", stripped):
            option_start_index = i
            break

    # Separate question from options
    if option_start_index != -1:
        question_lines = lines[:option_start_index]
        option_lines = lines[option_start_index:]

        # Parse options
        for line in option_lines:
            stripped = line.lstrip()
            if stripped.startswith(("-", "•")) or re.match(r"^\d+\.", stripped):
                option_text = re.sub(r"^(\d+\.|[-•])\s*", "", stripped)
                if option_text:  # Only add non-empty options
                    options.append(option_text)
    else:
        # No options found, all is question
        question_lines = lines

    question_text = "\n".join(question_lines).strip()
    if question_text:
        st.markdown(f"### {question_text}")

    # --- Auto-detect multiple selection ---
    lower_reply = latest_reply.lower()
    multiple = any(
        phrase in lower_reply
        for phrase in [
            "select all that apply",
            "choose all that apply",
            "select multiple",
            "you can select multiple",
            "select one or more",
        ]
    )

    # --- Display selection widget ---
    selected = []
    if options:
        if multiple:
            selected = st.multiselect("Choose your answers:", options, key="multi_select")
        else:
            selected = st.radio("Choose your answer:", options, key="radio_select")

    # --- Submit answer ---
    submit_disabled = st.session_state.processing or not selected
    if st.button("✅ Submit Answer", disabled=submit_disabled, key="submit_answer"):
        st.session_state.processing = True
        st.rerun()  # Immediately rerun to show disabled state

    # Process the answer if we're in processing state
    if st.session_state.processing and selected:
        answer = ", ".join(selected) if isinstance(selected, list) else selected

        # Store answer in conversation
        if st.session_state.conversation:
            st.session_state.conversation[-1]["answer"] = answer

        st.session_state.messages.append({"role": "user", "content": answer})

        with st.spinner("🤔 Processing your answer..."):
            reply = ask_ai(st.session_state.messages)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.conversation.append({"question": reply, "answer": None})
        st.session_state.processing = False
        st.rerun()