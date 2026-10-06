import uuid
from chatbotBackend import workflow
from langchain_core.messages import HumanMessage
import streamlit as st






# utility functions

def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id:str):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

    if thread_id not in st.session_state["thread_id_title_mapping"]:
        st.session_state["thread_id_title_mapping"][thread_id] = "start conversation"


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
    st.session_state['chat_threads'] = []

if 'thread_id_title_mapping' not in st.session_state:
    st.session_state['thread_id_title_mapping'] = {}

add_thread(st.session_state['thread_id'])




# UI
st.title("Chat with apna llm stream")

st.sidebar.title("MINI ChatAI")
if st.sidebar.button("New Chat", key="new_chat_btn"):
    reset_chat()
st.sidebar.header("My Conversations")



for thread_id in reversed(st.session_state['chat_threads']):
    if st.sidebar.button(st.session_state['thread_id_title_mapping'][thread_id],key=thread_id):
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

    current_thread_id = st.session_state["thread_id"]

    if st.session_state["thread_id_title_mapping"][current_thread_id] == "start conversation":
        st.session_state["thread_id_title_mapping"][current_thread_id] = user_input[:30]

    with st.chat_message("user"):
        st.markdown(user_input)

    
    config = {"configurable": {"thread_id": st.session_state["thread_id"]}}

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
