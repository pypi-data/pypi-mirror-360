from openagentkit.modules.openai import AsyncOpenAIAgent
from openagentkit.modules.context.valkey_context_store import ValkeyContextStore
from openagentkit.core.tools.base_tool import tool
from pydantic import BaseModel
import logging
import asyncio
import valkey
import openai
import os
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class ResponseSchema(BaseModel):
    reasoning: str
    """
    The reasoning behind the response.
    """
    response: str
    """
    The final response to the user.
    """

# Define a tool
@tool # Wrap the function in a tool decorator to automatically create a schema
async def get_weather(city: str):
    """Get the weather of a city"""

    # Actual implementation here...
    # ...

    return f"Weather in {city}: sunny, 20°C, feels like 22°C, humidity: 50%"

# Initialize OpenAI client
client = openai.AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

redis_client = valkey.Valkey(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True,  # Ensure responses are decoded to strings
)

context = ValkeyContextStore(
    client=redis_client,
)

async def main():
    # Initialize LLM service
    agent = AsyncOpenAIAgent(
        client=client,
        model="o4-mini",
        system_message="""
        You are a helpful assistant that can answer questions and help with tasks.
        You are also able to use tools to get information.
        """,
        tools=[],
        context_store=context,
        max_tokens=1000,
    )

    start_time = time.time()

    stop = False

    async for response in agent.execute(
        messages=[
            {"role": "user", "content": "What're your thoughts on the impact of AI on society?"}
        ],
    ):
        if response.tool_calls:
            logger.info(f"Tool calls: {response.tool_calls}")
        if response.tool_results:
            logger.info(f"Tool results: {response.tool_results}")
        if response.content:
            print(response.content)
        #if response.delta_content:
        #    if not stop:
        #        # Stop after the first response
        #        stop = True
        #        elapsed_time = time.time() - start_time
        #        logger.info(f"First response delta received after {elapsed_time:.2f} seconds")
        #    print(response.delta_content, end="", flush=True)

    #async for response in agent.stream_execute(
    #    messages=[
    #        {"role": "user", "content": "What's my name?"}
    #    ],
    #):
    #    if response.tool_calls:
    #        logger.info(f"Tool calls: {response.tool_calls}")
    #    if response.tool_results:
    #        logger.info(f"Tool results: {response.tool_results}")
    #    if response.delta_content:
    #        print(response.delta_content, end="", flush=True)

    print()  # New line after the response

    print(context.get_agent_context(agent.agent_id))
if __name__ == "__main__":
    asyncio.run(main())