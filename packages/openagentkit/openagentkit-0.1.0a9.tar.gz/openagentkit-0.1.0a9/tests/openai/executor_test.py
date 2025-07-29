from openagentkit.modules.openai import OpenAIAgent
from openagentkit.core.tools.base_tool import Tool
from pydantic import BaseModel
import openai
import os

class ResponseSchema(BaseModel):
    reasoning: str
    """
    The reasoning behind the response.
    """
    response: str
    """
    The final response to the user.
    """

class GetWeather(Tool):
    """
    A tool to get the current weather of a city.
    """
    def __call__(self, city: str) -> str:
        """
        Get the current weather in a city.
        """
        # Simulate a weather API call
        return f"The current weather in {city} is sunny with a temperature of 25°C."
    
get_weather = GetWeather()

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

agent = OpenAIAgent(
    client=client,
    model="o4-mini",
    system_message="""
    You are a helpful assistant that can answer questions and help with tasks.
    You are also able to use tools to get information.
    """,
    tools=[get_weather],
    temperature=1.0,
    max_tokens=1000,
    top_p=1.0,
)

generator = agent.execute(
    messages=[
        {"role": "user", "content": "What's the weather like in New York? Can you try to think what the season currently is based on the weather?"}
    ],
    reasoning_effort="low",
    response_schema=ResponseSchema,  # Specify the response schema
)

for response in generator:
    if response.content:
        print(f"Response: {response.content}")