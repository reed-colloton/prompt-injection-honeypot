import asyncio

from langchain_core.messages import HumanMessage

from graph import graph
from graph.utilities.bcolors import bcolors

THREAD_ID = "1"


async def stream_graph(user_input: str):
    config = {"configurable": {"thread_id": THREAD_ID}}
    async for stream_mode, chunk in graph.astream(
        {"messages": [HumanMessage(content=user_input)]}, 
        config=config,
        stream_mode=["messages", "updates"]
    ):
        if stream_mode == "messages":
            message_chunk, metadata = chunk
            if message_chunk.content:
                print(message_chunk.content, end="", flush=True)
            if hasattr(message_chunk, "tool_calls") and message_chunk.tool_calls:
                for tool_call in message_chunk.tool_calls:
                    print(f"\n{bcolors.WARNING}[Tool Call: {tool_call['name']}]{bcolors.ENDC}", flush=True)
                    print(f"{bcolors.OKGREEN}{tool_call['args']}{bcolors.ENDC}", flush=True)
        elif stream_mode == "updates":
            for node_name, node_output in chunk.items():
                if node_name == "tools":
                    print(f"\n{bcolors.OKBLUE}[Tool Result]{bcolors.ENDC}", flush=True)
    print()


if __name__ == "__main__":
    while True:
        try:
            user_input = input(f"{bcolors.BOLD+bcolors.OKBLUE}Ask anything: {bcolors.BOLD+bcolors.ENDC}")
        except (KeyboardInterrupt, EOFError):
            print()
            break
        if user_input.lower() in ["q", "quit", "exit"]:
            break
        try:
            asyncio.run(stream_graph(user_input))
        except KeyboardInterrupt:
            print()
            continue
