import asyncio

from langchain_core.messages import HumanMessage

from graph import graph
from graph.utilities.bcolors import bcolors

THREAD_ID = "1"


async def stream_graph(user_input: str):
    config = {"configurable": {"thread_id": THREAD_ID}}
    async for event in graph.astream_events({"messages": [HumanMessage(content=user_input)]}, config=config, version="v2"):
        if event.get("event") == "on_chat_model_stream":
            chunk = event["data"].get("chunk")
            content = getattr(chunk, "content", None)
            if isinstance(content, str):
                print(content, end="", flush=True)
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
