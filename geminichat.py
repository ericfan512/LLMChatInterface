import streamlit as st
import google.generativeai as ggai

with st.sidebar:
    # default Gemini API key set (replace (API key) with actual API key)
    api_key=st.text_input("Gemini API key", value="(API key)", type="password")
    # replace (API key) with actual API key
    if api_key=="(API key)":
        st.markdown("<p style='font-size:8px;'>(default API key)</p>", unsafe_allow_html=True)
    # choose to retain context (remembers what you said before) or not
    context=st.toggle("retain context", value=True)

st.title("American History Help")

# set API key and model type (2.5 pro, 2.5 flash, etc.)
ggai.configure(api_key=api_key)
model = ggai.GenerativeModel('gemini-2.5-pro')

# puts chat in session_state if maintaining context is desired - allows for the chat data to be stored as long as program is running
# tell chat what its purpose is - in this case, it can only talk about American History
if context:
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[
            {
                "role": "user",
                "parts": [
                    "You are an assistant that helps people with American History. Only answer questions related to American History. Never answer anything unrelated to American History."
                ]
            }
        ])
    # keep track of previous messages (also with session_state) to maintain visible conversation history
    if "messages" not in st.session_state:
        st.session_state.messages = []
# don't keep track of previous chat (don't use session_state) if maintaining context is not desired
else:
    chat = model.start_chat(history=[
            {
                "role": "user",
                "parts": [
                    "You are an assistant that helps people with American History. Only answer questions related to American History. Never answer anything unrelated to American History."
                ]
            }
        ])

# message input
msg=st.text_input("Message: ")

# if message is not empty and send is clicked
if st.button("Send") and msg:
    # try-except returns "Invalid API key" if response cannot be attained
    try:
        # send message to chat (which is connected to the model)
        if context:
            response = st.session_state.chat.send_message(msg)
            # add user message and response to messages in session_state to keep track of entire chat
            st.session_state.messages.append({"You":msg, "AI":response.text})
        else:
            response = chat.send_message(msg)
        st.write(response.text)
    except Exception:
        st.write("Invalid API key")

# if maintaining context desired and chat has started
if context and st.session_state.get("messages"):
    st.markdown("### Conversation History")
    # print out each message and response in reverse chronological order (top is most recent)
    for i in reversed(st.session_state.messages):
        st.markdown(f"**You:** {i['You']}")
        st.markdown(f"**AI:** {i['AI']}")
        st.markdown("---")