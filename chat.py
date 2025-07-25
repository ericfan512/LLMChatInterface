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

# def generate_heygen_video(api_key, text):
#     headers = {
#         "Accept": "application/json",
#         "Content-Type": "application/json",
#         "X-Api-Key": api_key
#     }
#     payload = {
#         "video_inputs": [
#             {
#                 "avatar_id": "avatar-0f3f7008-eacc-4c73-b335-e48f43f82c4e",
#                 "voice": {
#                     "type": "text",
#                     "voice_id": "6be73833ef9a4eb0aeee399b8fe9d62b",
#                     "input_text": text
#                 },
#                 "script": {
#                     "type": "text",
#                     "input": text
#                 }
#             }
#         ],
#         "test": True
#     }

#     try:
#         res = r.post("https://api.heygen.com/v2/video/generate", json=payload, headers=headers)
#         st.write(f"Generate status: {res.status_code}")
#         st.write(f"Generate response: {res.text}")

#         if res.status_code == 200:
#             data = res.json().get("data", {})
#             video_id = data.get("video_id") or data.get("id") or data.get("videoId")
#             st.write(f"Extracted video_id: {video_id}")

#             if not video_id:
#                 st.error("Failed to get video ID.")
#                 return

#             import time
#             time.sleep(2)  # small delay before polling

#             status = "processing"
#             max_wait = 60  # max wait time in seconds
#             waited = 0
#             interval = 5

#             while status == "processing" and waited < max_wait:
#                 poll_url = f"https://api.heygen.com/v2/videos/{video_id}/status"
#                 poll = r.get(poll_url, headers=headers)

#                 st.write(f"Polling status: {poll.status_code}, response: {poll.text}")

#                 if poll.status_code == 200 and poll.text.strip():
#                     poll_data = poll.json()
#                     status = poll_data.get("data", {}).get("status")
#                     if status == "done":
#                         video_url = poll_data["data"]["video_url"]
#                         st.video(video_url)
#                         return
#                     elif status == "failed":
#                         st.error("Video generation failed.")
#                         return
#                 else:
#                     st.error(f"Polling failed with status {poll.status_code}")
#                     return

#                 time.sleep(interval)
#                 waited += interval

#             if status == "processing":
#                 st.warning("Video generation still in progress. Please wait a moment.")
#         else:
#             st.error(f"Error from HeyGen: {res.text}")

#     except Exception as e:
#         st.error(f"HeyGen request failed: {str(e)}")



with st.sidebar:
    api_choice = st.selectbox("Choose API Provider", ["Gemini", "Ollama"])

    choices = ["General", "Mathematics", "Science", "English", "History"]
    chat_choice = st.selectbox("Subject Choice", choices, index=0)
    # heygen_api_key = st.text_input("HeyGen API key", type="password", value="(API key)")

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

    if st.button("Clear History"):
        st.session_state.messages = []
        if "chat" in st.session_state:
            del st.session_state.chat
        if "omessages" in st.session_state:
            del st.session_state.omessages
    # if st.button("Generate HeyGen Video"):
    #     last_response = None
    #     if api_choice == "Gemini" and st.session_state.get("messages"):
    #         last_response = st.session_state.messages[-1]["AI"]
    #     elif api_choice == "Ollama":
    #         for msg in reversed(st.session_state.get("omessages", [])):
    #             if msg["role"] == "ai":
    #                 last_response = msg["content"]
    #                 break

    #     if last_response:
    #         generate_heygen_video(heygen_api_key, last_response)
    #     else:
    #         st.warning("No AI response found to generate video.")


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