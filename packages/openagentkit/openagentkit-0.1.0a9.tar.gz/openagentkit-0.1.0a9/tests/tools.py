from openagentkit.core.tools.base_tool import tool, Tool
from openagentkit.modules.openai import AsyncOpenAIAgent
from openai import AsyncOpenAI
import asyncio

@tool
async def search_google(query: str) -> str:
    """
    A simple tool to search Google and return the first result.
    This is a placeholder function and should be replaced with actual search logic.
    """
    # In a real implementation, you would use an API or web scraping to get results.
    # Here we just return a mock response.
    return f"Mock search result for query: {query}"

class GetWeather(Tool):
    async def __call__(self, city: str) -> str:
        """Get the current Weather of a city."""
        return f"The current weather in {city} is sunny with a temperature of 25°C."

get_weather = GetWeather()

client = AsyncOpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama"
)

agent = AsyncOpenAIAgent(
    client=client,
    model="qwen3:4b",
    system_message="You are a helpful assistant that can answer questions and help with tasks. ALWAYS use the GreetTool to greet users",
    tools=[get_weather, search_google],
    temperature=0.7,
    max_tokens=1000,
    top_p=1.0,
)

async def main():
    async for response in agent.stream_execute(messages=[{"role": "user", "content": "Hi! Search up the news on Bitcoin for me."}]):
        print(response.tool_calls) if response.tool_calls else None
        print(response.tool_results) if response.tool_results else None
        print(response.delta_content, end="", flush=True) if response.delta_content else None

if __name__ == "__main__":
    asyncio.run(main())