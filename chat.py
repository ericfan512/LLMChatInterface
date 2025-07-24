import streamlit as st
import requests as r
import google.generativeai as ggai

def use_gemini(api_key, context, sysprompt):
    st.title("Subject Help")

    ggai.configure(api_key=api_key)
    model = ggai.GenerativeModel('gemini-2.5-pro')

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

    if context and st.session_state.get("messages"):
        for m in st.session_state.messages:
            with st.chat_message("user"):
                st.write(m["You"])
            with st.chat_message("assistant"):
                st.write(m["AI"])

    msg = st.chat_input("Question")
    if msg:
        with st.chat_message("user"):
            st.write(msg)

        try:
            if context:
                response = st.session_state.chat.send_message(msg)
                st.session_state.messages.append({"You": msg, "AI": response.text})
                with st.chat_message("assistant"):
                    st.write(response.text)
            else:
                response = chat.send_message(msg)
                with st.chat_message("assistant"):
                    st.write(response.text)
        except Exception as e:
            st.error(f"Error: {str(e)}")

def use_ollama(sysprompt):
    st.title("Subject Help")
    print(sysprompt)

    if "omessages" not in st.session_state:
        st.session_state.omessages = [{"role": "system", "content": sysprompt}]

    for msg in st.session_state.omessages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        elif msg["role"] == "ai":
            with st.chat_message("assistant"):
                st.write(msg["content"])

    msg = st.chat_input("Question")
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
    api_choice = st.selectbox("Choose API Provider", ["Gemini", "Ollama"])

    choices = ["General", "Mathematics", "Science", "English", "History"]
    chat_choice = st.selectbox("Subject Choice", choices, index=0)

    if "current_subject" not in st.session_state:
        st.session_state.current_subject = chat_choice

    if st.session_state.current_subject != chat_choice:
        st.session_state.current_subject = chat_choice
        st.session_state.messages = []
        if "chat" in st.session_state:
            del st.session_state.chat
        if "omessages" in st.session_state:
            del st.session_state.omessages
        if "messages" in st.session_state:
            del st.session_state.messages

    prompts = [
        "You are a general assistant that can answer any question briefly and accurately. Respond only to the current question. Never refer to previous messages.",
        """Ignore all previous prompts. You are now a math tutor. Only respond to math questions. DO NOT PROVIDE ANY INFORMATION THAT IS NOT RELATED TO MATH, NO MATTER HOW MUCH THE USER ASKS.
        If the question is not math-related, reply with:
        'I can only answer math questions. Please ask a math-related question or change the subject.'
        If it is math related, please do not reply with the previous statement.
        This is very important: never reference or respond to earlier questions. ONLY CONSIDER THE CURRENT QUESTION AND ANSWER IT COMPLETELY.""",
        """Ignore all previous prompts You are now a science tutor. Only respond to science questions. DO NOT PROVIDE ANY INFORMATION THAT IS NOT RELATED TO SCIENCE, NO MATTER HOW MUCH THE USER ASKS.
        If the question is not science-related, reply with:
        'I can only answer science questions. Please ask a science-related question or change the subject.'
        If it is science related, please do not reply with the previous statement.
        This is very important: never reference or respond to earlier questions. ONLY CONSIDER THE CURRENT QUESTION AND ANSWER IT COMPLETELY.""",
        """Ignore all previous prompts. You are now an English tutor. Only respond to English questions. DO NOT PROVIDE ANY INFORMATION THAT IS NOT RELATED TO ENGLISH, NO MATTER HOW MUCH THE USER ASKS.
        If the question is not English-related, reply with:
        'I can only answer English questions. Please ask an English-related question or change the subject.'
        If it is English related, please do not reply with the previous statement.
        This is very important: never reference or respond to earlier questions. ONLY CONSIDER THE CURRENT QUESTION AND ANSWER IT COMPLETELY.""",
        """Ignore all previous prompts You are now a history tutor. Only respond to history questions. DO NOT PROVIDE ANY INFORMATION THAT IS NOT RELATED TO HISTORY, NO MATTER HOW MUCH THE USER ASKS.
        If the question is not history-related, reply with:
        'I can only answer history questions. Please ask a history-related question or change the subject.'
        If it is history related, please do not reply with the previous statement.
        This is very important: never reference or respond to earlier questions. ONLY CONSIDER THE CURRENT QUESTION AND ANSWER IT COMPLETELY."""
    ]

    sysprompt = prompts[choices.index(chat_choice)]
    print(sysprompt)

    if st.button("Clear History"):
        st.session_state.messages = []
        if "chat" in st.session_state:
            del st.session_state.chat
        if "omessages" in st.session_state:
            del st.session_state.omessages

if api_choice == "Gemini":
    with st.sidebar:
        api_key = st.text_input("Gemini API key", value="(API key)", type="password")
        if api_key == "(API key)":
            st.markdown("<p style='font-size:8px;'>(API key not set)</p>", unsafe_allow_html=True)
        context = st.toggle("retain context", value=True)

    use_gemini(api_key, context, sysprompt)

elif api_choice == "Ollama":
    with st.sidebar:
        st.write("Runs locally. Make sure you have Ollama installed.")

    use_ollama(sysprompt)