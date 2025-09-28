import streamlit as st
from backend import ask_ai, start_prompt

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = start_prompt()
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "awaiting_options" not in st.session_state:
    st.session_state.awaiting_options = False
if "processing" not in st.session_state:
    st.session_state.processing = False  # New flag

st.title("🎯 AI Career Path Guide")
st.write("Tell me about your passions, skills, or what you want to achieve. I’ll guide you step by step!")

# Step 1: Initial user input
if not st.session_state.conversation:
    user_input = st.text_area("Describe yourself or your goals:", "")
    if st.button("Start") and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.processing = True  # Set processing flag
        reply = ask_ai(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.conversation.append(reply)
        st.session_state.awaiting_options = True
        st.session_state.processing = False  # Reset flag
        st.rerun()

# Step 2: Display AI questions + clickable options
else:
    latest_reply = st.session_state.messages[-1]["content"]

    # Show the AI's last message
    st.markdown(latest_reply)

    # Extract options (AI should format as list items: "-", "•", or "1.")
    options = [line.strip("•-1234567890. ")
               for line in latest_reply.split("\n")
               if line.strip().startswith(("-", "•", "1", "2"))]

    if options:
        multiple = "multiple" in latest_reply.lower()

        if multiple:
            selected = st.multiselect("Select one or more:", options)
        else:
            selected = st.radio("Select one:", options)

        # Initialize state for the button
        if "answered" not in st.session_state:
            st.session_state.answered = False

        # Disable button if already answered OR if processing
        submit_disabled = st.session_state.answered or st.session_state.processing

        if st.button("Submit Answer", disabled=submit_disabled):
            if selected:
                st.session_state.answered = True  # prevent multiple presses
                st.session_state.processing = True  # Start processing

                # Convert answer into string
                answer = ", ".join(selected) if isinstance(selected, list) else selected
                st.session_state.messages.append({"role": "user", "content": answer})
                reply = ask_ai(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state.conversation.append(reply)
                st.session_state.awaiting_options = True

                st.session_state.processing = False  # End processing
                st.session_state.answered = False  # Reset for next question
                st.rerun()
