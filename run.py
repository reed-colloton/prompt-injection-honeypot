import asyncio
from langchain_core.messages import HumanMessage

from graph import graph

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


while True:
    user_input = input("Ask anything: ")
    if user_input.lower() in ["q", "quit", "exit"]:
        break
    asyncio.run(stream_graph(user_input))
