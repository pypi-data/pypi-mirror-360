from openagentkit.modules.openai import AsyncOpenAIAgent
from openagentkit.core.interfaces import AsyncBaseAgent
from openagentkit.core.models.responses import OpenAgentStreamingResponse
from openai import AsyncOpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client
import os
from typing import AsyncGenerator, Any
from dotenv import load_dotenv
from contextlib import AsyncExitStack
from mem0 import MemoryClient # type: ignore
import logging

logging.basicConfig(level=logging.ERROR)

load_dotenv()

class MCPAgent:
    def __init__(self, 
                 sse_urls: list[str], 
                 agent: AsyncBaseAgent,
                 user_id: str = "keith"):
        self.sse_urls = sse_urls
        self.sessions = []
        self.agent = agent
        self.exit_stack = AsyncExitStack()
        self._sse_contexts: list[Any] = []
        #self.memory = MemoryClient(api_key=os.getenv("MEM0_API_KEY"),)
        self.base_system_message = agent.system_message
        self.user_id = user_id

    async def __aenter__(self):
        # Use 'async with' inside a coroutine to keep context scoped
        self._sse_contexts = []
        for url in self.sse_urls:
            ctx = sse_client(url)
            self._sse_contexts.append(ctx)
        
        self.sessions: list[ClientSession] = []
        for ctx in self._sse_contexts:
            # each ctx here is an async context manager
            read, write = await ctx.__aenter__()
            session = ClientSession(read, write)

            await session.__aenter__()

            await session.initialize()

            self.sessions.append(session)

        await self.agent.connect_to_mcp(self.sessions)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb): # type: ignore
        for session in self.sessions:
            await session.__aexit__(exc_type, exc_val, exc_tb) # type: ignore

        for ctx in reversed(self._sse_contexts):
            await ctx.__aexit__(exc_type, exc_val, exc_tb)

    async def stream_execute(self, message: str) -> AsyncGenerator[OpenAgentStreamingResponse, None]:
        #relevant_memories = self.memory.search( # type: ignore
        #    
        # 
        # query=message,
        #    user_id=self.user_id,
        #    limit=5,  # Adjust the limit as needed
        #)
        #modified_system_message = self.agent.system_message
        #if relevant_memories:
        #    memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories)
        #    modified_system_message = f"{self.base_system_message}\n\nMemories:\n{memories_str}"
        #
        #self.agent.system_message = modified_system_message

        async for event in self.agent.stream_execute(messages=[{"role": "user", "content": message}]):
            #if event.finish_reason == "stop":
            #    context = await self.agent.get_history()
            #    if context:
            #        self.memory.add(context, user_id=self.user_id) # type: ignore

            yield event
        
        

if __name__ == "__main__":
    import asyncio

    async def main():
        agent = AsyncOpenAIAgent(
            client=AsyncOpenAI(
                base_url="http://localhost:11434/v1/",
                api_key=os.getenv("OPENAI_API_KEY"),
            ),
            #model="gpt-4o-mini",
            model="qwen3:4b"
        )
        async with MCPAgent(
            sse_urls=[
                "http://localhost:8088/sse",
            ],
            agent=agent,
        ) as agent:
            while True:
                user_input = input("You: ").strip()
                if user_input.lower() in {"exit", "quit"}:
                    break

                async for response in agent.stream_execute(user_input):
                    print(f"{response.tool_calls}") if response.tool_calls else None
                    print(f"{response.tool_results}") if response.tool_results else None
                    print(f"{response.delta_content}", end="", flush=True) if response.delta_content else None

                print()  # New line after response

    asyncio.run(main())
