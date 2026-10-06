import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

load_dotenv()

groq_api_key=os.getenv("GROQ_API_KEY")

os.environ["LANGCHAIN_PROJECT"]="langsmithSequentialChain"

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=groq_api_key,
)

prompt1 = PromptTemplate(
    template='Generate a detailed report on {topic}',
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template='Generate a 5 pointer summary from the following text \n {text}',
    input_variables=['text']
)

parser = StrOutputParser()

chain=prompt1 | llm | parser | prompt2 | llm | parser

config={
    'run_name':"sequential chain",
    "tags":['llm_app','report generation','report summarisation'],
    'metadata':{
        'model':'openai/gpt-oss-20b',
        'created_by':'aman choudhary'
    }
}

response = chain.invoke({"topic":"capital of india"},config=config)

print(response)
