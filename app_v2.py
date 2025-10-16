# app.py
import streamlit as st
import time
from backend import ask_ai, start_prompt
from streamlit_autorefresh import st_autorefresh
import re

# --- Page config ---
st.set_page_config(page_title="AI Career Path Guide", page_icon="🎯")

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

# --- Calculate session duration ---
elapsed = int(time.time() - st.session_state.session_start)
mins, secs = divmod(elapsed, 60)
session_duration = f"{mins:02d}:{secs:02d}"

# --- Calculate steps ---
total_steps = len(st.session_state.conversation) + 1
answered_steps = sum(1 for entry in st.session_state.conversation if entry.get("answer"))
current_step = answered_steps + 1

# --- Sticky navbar ---
st.markdown(
    """
    <style>
    .sticky-navbar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #f0f2f6;
        padding: 10px;
        z-index: 9999;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #ccc;
    }
    .sticky-navbar button {
        background-color: #e0e0e0;
        border: none;
        padding: 5px 10px;
        cursor: pointer;
        font-size: 14px;
        border-radius: 5px;
    }
    .content-padding {
        padding-top: 60px; /* adjust based on navbar height */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

nav_cols = st.columns([1,1,1])
with nav_cols[0]:
    st.markdown(f"Step: {current_step} / {total_steps}")
with nav_cols[1]:
    st.markdown(f"Session: {session_duration}")
with nav_cols[2]:
    if st.button("🔁 Restart"):
        for key in ["messages", "conversation", "awaiting_options", "processing", "answered", "session_start"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

st.write("Tell me about your passions, skills, or goals — I’ll guide you step by step!")

# --- Chat history (answered only) ---
if st.session_state.conversation:
    st.markdown("### 🕓 Conversation History")
    for idx, entry in enumerate(st.session_state.conversation, 1):
        if entry.get("answer"):
            st.markdown(f"**Q{idx}:** {entry['question']}")
            st.markdown(f"**A{idx}:** {entry['answer']}")
    st.markdown("---")

# Step 1: Start conversation
if not st.session_state.conversation:
    with st.form(key="start_form", clear_on_submit=False):
        user_input = st.text_area(
            "Describe yourself or your goals:",
            "",
            placeholder="Type your description here...",
            height=100
        )
        submit = st.form_submit_button("Start")  # ⚡ Always enabled

    if submit:
        if user_input.strip():  # Only proceed if text is not empty
            st.session_state.processing = True
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner("Thinking..."):
                reply = ask_ai(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.conversation.append({"question": reply, "answer": None})
            st.session_state.processing = False
            st.rerun()
        else:
            st.warning("Please enter something before pressing Start.")

# --- Step 2: Continue conversation ---
else:
    latest_reply = st.session_state.messages[-1]["content"]

    # --- Parse question and options ---
    lines = [line.strip() for line in latest_reply.split("\n") if line.strip()]
    question_lines, options = [], []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith(("-", "•")) or re.match(r"^\d+\.", stripped):
            option_text = re.sub(r"^(\d+\.|[-•])\s*", "", stripped)
            options.append(option_text)
        else:
            question_lines.append(line)

    question_text = "\n".join(question_lines).strip()
    if question_text:
        st.markdown(f"**{question_text}**")

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
            selected = st.multiselect("Select one or more:", options)
        else:
            selected = st.radio("Select one:", options)

    # --- Submit answer ---
    submit_disabled = st.session_state.processing or not selected
    if st.button("Submit Answer", disabled=submit_disabled):
        st.session_state.processing = True
        answer = ", ".join(selected) if isinstance(selected, list) else selected

        # Store answer in conversation
        if st.session_state.conversation:
            st.session_state.conversation[-1]["answer"] = answer

        st.session_state.messages.append({"role": "user", "content": answer})

        with st.spinner("Thinking..."):
            reply = ask_ai(st.session_state.messages)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.conversation.append({"question": reply, "answer": None})
        st.session_state.processing = False
        st.rerun()