import streamlit as st
from cli_voice import *

# Streamlit UI setup
st.set_page_config(page_title="PAI", layout="centered")
st.title("PAI")
voice_toggle = st.toggle("Voice Mode", value=False, key=None, help=None, on_change=None, args=None, disabled=False, label_visibility="visible")
# CSS for pulsing orb animation
st.markdown(
    """
    <style>
    @keyframes pulse {
        0% { box-shadow: 0 0 10px rgba(0, 150, 255, 0.7); }
        50% { box-shadow: 0 0 20px rgba(0, 150, 255, 1); }
        100% { box-shadow: 0 0 10px rgba(0, 150, 255, 0.7); }
    }
    .pulsing-orb {
        width: 20px;
        height: 20px;
        background-color: #0096FF;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
        display: block;
        margin: 10px auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if not voice_toggle:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User input field
    user_input = st.chat_input("Type your message...")

    if user_input:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        # Call the chat function (Replace with your actual function call)
        assistant_output = chat(user_input, voice_mode=False)  # Replace with your function call
        
        # Display assistant response
        st.session_state.messages.append({"role": "assistant", "content": assistant_output})
        with st.chat_message("assistant"):
            st.write(assistant_output)

else:
    # if "messages" not in st.session_state:
    #     st.session_state.messages = []

    # # Display chat history
    # for message in st.session_state.messages:
    #     with st.chat_message(message["role"]):
    #         st.write(message["content"])

    # # User input field
    # user_input = st.chat_input("Type your message...")

    # if user_input:
    #     # Display user message
    #     st.session_state.messages.append({"role": "user", "content": user_input})
    #     with st.chat_message("user"):
    #         st.write(user_input)
        
    #     # Call the chat function (Replace with your actual function call)
    #     assistant_output = chat(user_input, voice_mode=True)  # Replace with your function call
        
    #     # send audio playing to a different thread??

    #     # Display assistant response
    #     st.session_state.messages.append({"role": "assistant", "content": assistant_output})
    #     with st.chat_message("assistant"):
    #         st.write(assistant_output)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User input field
    user_input = st.chat_input("Type your message...")

    if user_input:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        # Show pulsing orb while processing response
        with st.container():
            st.markdown("<div class='pulsing-orb'></div>", unsafe_allow_html=True)
            # time.sleep(2)  # Simulating processing time
        
        # Call the chat function (Replace with your actual function call)
        assistant_output = chat(user_input, voice_mode=True)   # Replace with your function call
        
        # Display assistant response
        st.session_state.messages.append({"role": "assistant", "content": assistant_output})
        # with st.chat_message("assistant"):
        #     st.write(assistant_output)                                                      

## skip ahead when playing voice




