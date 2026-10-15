# Tools are the things that the LLM/agent can use to interact with the world. They can be APIs, databases, or even other LLMs. The agent can use these tools to get information, perform actions, or generate content.
# we can get write this tool either ourself or use the tools provided by langchain. The tools provided by langchain are wrappers around APIs and other services that make it easy to use them in our agents.
# how to add three diff tools:
# 1.. wikipedia search tool  ->  free, doesnot need api key
# 2.. duckduckgo search tool --> free, doesnot need api key
# 3.. python function tool --> we can write our own python function and use it as a tool. The agent can call this function to perform some action or get some information.




from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_classic.tools import Tool
from datetime import datetime

search = DuckDuckGoSearchRun()
search_tool = Tool(
    name = "search",
    func = search.run,
    description = "searches the web for information. Input should be a search query string."
)




