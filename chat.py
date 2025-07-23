import streamlit as st
import requests as r
import google.generativeai as ggai


sysprompt = "You are an assistant that helps people with American History. Only answer questions related to American History. Never answer anything unrelated to American History."

def use_gemini(api_key, context):
    st.title("American History Help")

    ggai.configure(api_key=api_key)
    model = ggai.GenerativeModel('gemini-2.5-pro')

    # Setup session state for chat and message history
    if context:
        if "chat" not in st.session_state:
            st.session_state.chat = model.start_chat(history=[
                {"role": "user", "parts": [sysprompt]}
            ])
        if "messages" not in st.session_state:
            st.session_state.messages = []
    else:
        chat = model.start_chat(history=[
            {"role": "user", "parts": [sysprompt]}
        ])

    # Display conversation history using st.chat_message
    if context and st.session_state.get("messages"):
        for m in st.session_state.messages:
            with st.chat_message("user"):
                st.write(m["You"])
            with st.chat_message("assistant"):
                st.write(m["AI"])

    # Input box at the bottom
    msg = st.chat_input("Ask a question about American History:")
    if msg:
        try:
            if context:
                response = st.session_state.chat.send_message(msg)
                st.session_state.messages.append({"You": msg, "AI": response.text})
                with st.chat_message("user"):
                    st.write(msg)
                with st.chat_message("assistant"):
                    st.write(response.text)
            else:
                response = chat.send_message(msg)
                with st.chat_message("user"):
                    st.write(msg)
                with st.chat_message("assistant"):
                    st.write(response.text)
        except Exception:
            st.error("Invalid API key")



def use_ollama():
    st.title("American History Help")

    if "omessages" not in st.session_state:
        st.session_state.omessages = [{"role": "system", "content": sysprompt}]

    for msg in st.session_state.omessages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        elif msg["role"] == "ai":
            with st.chat_message("assistant"):
                st.write(msg["content"])


    msg = st.chat_input("Question:")
    if msg:
        st.session_state.omessages.append({"role": "user", "content": msg})
        with st.chat_message("user"):
            st.write(msg)

        try:
            payload = {
                "model": "llama3.2:3b",
                "messages": st.session_state.omessages,
                "stream": False
            }
            response = r.post("http://localhost:11434/api/chat", json=payload, timeout=30)
            if response.status_code == 200:
                reply = response.json()["message"]["content"]
                st.session_state.omessages.append({"role": "ai", "content": reply})
                with st.chat_message("assistant"):
                    st.write(reply)
            else:
                st.error("Ollama server error.")
        except r.exceptions.ConnectionError:
            st.error("Ollama is not running.")
        except Exception as e:
            st.error(str(e))




with st.sidebar:
    api_choice = st.selectbox("Choose API Provider:",["Gemini", "Ollama"])
if api_choice == "Gemini":
    with st.sidebar:
        # default Gemini API key set (replace (API key) with actual API key)
        api_key=st.text_input("Gemini API key", value="(API key)", type="password")
        # api_key_2=st.text_input("HeyGen API key", type="password")
        # replace (API key) with actual API key
        if api_key=="(API key)":
            st.markdown("<p style='font-size:8px;'>(default API key [not set])</p>", unsafe_allow_html=True)
        # choose to retain context (remembers what you said before) or not
        context=st.toggle("retain context", value=True)
    use_gemini(api_key, context)
elif api_choice == "Ollama":
    with st.sidebar:
        st.write("Runs locally. Make sure you have Ollama installed.")
    use_ollama()