import streamlit as st
import requests
import uuid


def fetch_streamed_response(api_url, payload):
    with requests.post(api_url, json=payload, stream=True) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                yield chunk.decode("utf-8")


def main(api_url):
    st.set_page_config(page_title="AI Travel Companion", page_icon="✈️")
    st.title("Super Travel Companion")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = str(uuid.uuid4())

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask me about travel!")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)


        for chunk in fetch_streamed_response(api_url, {"user_input": user_input, "thread": st.session_state["thread_id"]}):
            with st.chat_message("assistant"):
                st.markdown(chunk)
            st.session_state.messages.append({"role": "assistant", "content": chunk})


if __name__ == "__main__":
    API_URL = "http://fastapi:8000/agent"
    main(API_URL)
