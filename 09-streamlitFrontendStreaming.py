import streamlit as st

from chatbotBackend import workflow
from langchain_core.messages import HumanMessage,SystemMessage


# Initialize session state
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []


st.title("Chat with apna llm stream")


for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


user_input = st.chat_input("Your message")


if user_input:

    st.session_state["message_history"].append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)


    config = {"configurable": {"thread_id": "1"}}

    initial_state = {
        "messages": [
            HumanMessage(content=user_input)
        ]
    }

    stream = workflow.stream(
        initial_state,
        config=config,
        stream_mode="messages"
    )

    with st.chat_message("assistant"):
        ai_msg=st.write_stream(
            message_chunk.content for message_chunk , metadata in stream
        )




    st.session_state["message_history"].append({
        "role": "assistant",
        "content": ai_msg
    })