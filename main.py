from langchain_community.tools.tavily_search import TavilySearchResults
from src.agent import LLM
import os

os.environ["TAVILY_API_KEY"] = "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"


def search_flow():
    tools = TavilySearchResults()
    result = tools.invoke("What is the weather in Tokyo?")


if __name__ == "__main__":
    search_flow()
