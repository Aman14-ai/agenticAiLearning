import uuid
from chatbotBackendTools import workflow,retrieve_all_threads
from langchain_core.messages import HumanMessage,AIMessage
import streamlit as st
from dotenv import load_dotenv

load_dotenv()






# utility functions

def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id:str):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)



def reset_chat():
    thread_id=generate_thread_id()
    st.session_state["thread_id"] = thread_id
    st.session_state["message_history"] = []
    add_thread(thread_id)   


def load_conversation(thread_id:str):
    st.session_state["thread_id"] = thread_id
    state = workflow.get_state(config={'configurable': {'thread_id': thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])

    

# session setup state
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id']=generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()



add_thread(st.session_state['thread_id'])




# UI
st.title("Chat with apna llm stream")

st.sidebar.title("MINI ChatAI")
if st.sidebar.button("New Chat", key="new_chat_btn"):
    reset_chat()
st.sidebar.header("My Conversations")



for thread_id in reversed(st.session_state['chat_threads']):
    if st.sidebar.button(thread_id,key=thread_id):
        messages=load_conversation(thread_id)
        # compatibility issue solver
        temp_messages=[]
        for msg in messages:
            if isinstance(msg,HumanMessage):
                temp_messages.append({"role":"user","content":msg.content})
            else:
                temp_messages.append({"role":"assistant","content":msg.content})

        st.session_state["message_history"] = temp_messages



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

    
    # config = {"configurable": {"thread_id": st.session_state["thread_id"]}}
    # to separate the conversation in langsmith use this config
    config={
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn"
    }

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

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    with st.chat_message("assistant"):
        def ai_only_stream():
            for message_chunk, metadata in workflow.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    # yield only assistant tokens
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())




    st.session_state["message_history"].append({
        "role": "assistant",
        "content": ai_message
    })
