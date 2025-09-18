import os

from typing import Annotated
from typing_extensions import TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode, tools_condition


from graph.models import Models
from graph.tools.bank import get_balance, transfer_funds
from graph.tools.local_scraper import localhost_scrape
from graph.prompts import Prompts


load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)
checkpointer = InMemorySaver()
current_model = Models.gemini_2_5_pro

llm = ChatOpenAI(
    model=current_model,
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    streaming=True,
)
web_search = TavilySearch(max_results=2)
bank_tools = [get_balance, transfer_funds]
local_tools = [localhost_scrape]
tools = [web_search, *bank_tools, *local_tools]
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    messages = [Prompts.SYSTEM_PROMPT] + state["messages"]
    return {"messages": [llm_with_tools.invoke(messages)]}


graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile(checkpointer=checkpointer)
