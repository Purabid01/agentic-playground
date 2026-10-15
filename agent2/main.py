from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser as pydantic_output_parser
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool

load_dotenv()

class ResponseModel(BaseModel):
    poem: str
    summary: str
    sources: list[str]
    tools_used: list[str]

llm = chat = ChatGoogleGenerativeAI(model="gemini-3.8-flash")
parser = pydantic_output_parser(pydantic_object=ResponseModel)

prompt = chat_prompt = ChatPromptTemplate.from_messages(
    [
    ("system", "You are a helpful assistant that writes poems about nature."),
    ("user", "Write a short poem about the beauty of nature, and provide a summary, sources, and tools used."
     "wrap the output in this format and provide no other text\n{format_instructions}"),
    ("placeholder", "{chat_history}"),
    ("human", "{query}"),
    ("ai", "{agent_scratchpad}"),
    ("human", "{agent_scratchpad}"),
]).partial(format_instructions=parser.get_format_instructions())


tools = [search_tool]

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
query = input("Enter your query: ")
raw_response = agent_executor.invoke({"query": query})

try:
    structured_response = parser.parse(raw_response.get("output")[0]["text"])
    print(structured_response)
except Exception as e:
    print("Error parsing response:", e, "Raw response:", raw_response)

