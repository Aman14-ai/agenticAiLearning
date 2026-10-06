import os,requests
import sqlite3
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv 
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver 
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun,tool
from langgraph.prebuilt import ToolNode,tools_condition

load_dotenv()

groq_api_key=os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=groq_api_key,
)

# first tool
search_tool = DuckDuckGoSearchRun()

# second tool
@tool
def calculator(first_number:float,second_number:float,operation:str)->dict:
    """
    Perform basic arithmetic operations on two numbers.
    Supported operations: add, subtract, multiply, divide.
    """
    try:
        if operation == "add":
            result = first_number + second_number
        elif operation == "subtract":
            result = first_number - second_number
        elif operation == "multiply":
            result = first_number * second_number
        elif operation == "divide":
            if second_number == 0:
                return {"error": "Division by zero is not allowed."}
            result = first_number / second_number
        else:
            return {"error": f"Unsupported operation: {operation}"}
        
        return {"first_number":first_number,"second_number":second_number,"operation":operation,"result": result}
    except Exception as e:
        return {"error": str(e)}

# third tool
@tool
def get_stock_price(symbol:str)->dict:
    """
    Get the current stock price for a given symbol (eg. "AAPL","TSLA")
    using alpha vantage with API key in url
    """
    try:
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&interval=5min&apikey=DLEODNO19HENL7IP'
        r=requests.get(url)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

tools=[search_tool,calculator,get_stock_price]

# make llm tool aware
llm_with_tools = llm.bind_tools(tools)




class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage], add_messages]

def chat_node(state:ChatState):
    response=llm_with_tools.invoke(state['messages'])
    return {'messages':[response]}

tool_node=ToolNode(tools)

graph=StateGraph(ChatState)

graph.add_node('chat_node',chat_node)
graph.add_node('tools',tool_node)

graph.add_edge(START,'chat_node')
graph.add_conditional_edges('chat_node',tools_condition)
graph.add_edge('tools','chat_node')

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

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)