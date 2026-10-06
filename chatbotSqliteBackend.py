import os
import sqlite3
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv 
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver 
from langchain_groq import ChatGroq

load_dotenv()

groq_api_key=os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=groq_api_key,
)



class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage], add_messages]

def chat_node(state:ChatState):
    response=llm.invoke(state['messages'])
    return {'messages':[response]}

graph=StateGraph(ChatState)

graph.add_node('chat_node',chat_node)

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

# checkpointer=InMemorySaver()
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)   

workflow=graph.compile(checkpointer=checkpointer)

config={
    'configurable':{
        'thread_id':1
    }
}
res=workflow.invoke({'messages':['who is her family members']},config=config)
print(res['messages'][-1].content)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)