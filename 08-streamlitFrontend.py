import streamlit as st

from chatbotBackend import workflow
from langchain_core.messages import HumanMessage,SystemMessage


# Initialize session state
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []


st.title("Chat with apna llm")


# Load conversation history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Get user input
user_input = st.chat_input("Your message")


if user_input:

    # Display user message
    st.session_state["message_history"].append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)


    # LangGraph configuration
    config = {
        "configurable": {
            "thread_id": "1"
        }
    }

    initial_state = {
        "messages": [
            HumanMessage(content=user_input)
        ]
    }


    # AI response
    with st.chat_message("assistant"):

        # Loading indicator
        with st.spinner("Thinking..."):

            response_state = workflow.invoke(
                initial_state,
                config=config
            )

            response = response_state["messages"][-1].content

        # Display response
        st.markdown(response)


    # Save AI response
    st.session_state["message_history"].append({
        "role": "assistant",
        "content": response
    })