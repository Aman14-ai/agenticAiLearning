import os,requests,asyncio
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

tools=[calculator]

# make llm tool aware
llm_with_tools = llm.bind_tools(tools)

class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage], add_messages]

def build_graph():
    async def chat_node(state:ChatState):
        response=await llm_with_tools.ainvoke(state['messages'])
        return {'messages':[response]}

    tool_node=ToolNode(tools)

    graph=StateGraph(ChatState)

    graph.add_node('chat_node',chat_node)
    graph.add_node('tools',tool_node)

    graph.add_edge(START,'chat_node')
    graph.add_conditional_edges('chat_node',tools_condition)
    graph.add_edge('tools','chat_node')
    chatbot=graph.compile()
    return chatbot;



async def main():
    chatbot=build_graph()
    response=await chatbot.ainvoke({'messages':["multiply 5 and 3 use external tool and specify that it's a calculator tool"]})
    print(response['messages'][-1].content)

if __name__=="__main__":
    asyncio.run(main())