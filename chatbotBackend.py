import os
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv 
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
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

checkpointer=InMemorySaver()

workflow=graph.compile(checkpointer=checkpointer)
