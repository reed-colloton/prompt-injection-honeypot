from langchain_core.messages import HumanMessage

from graph import graph

THREAD_ID = "reed's-session"


def stream_graph(user_input: str):
    for event in graph.stream({"messages": [HumanMessage(content=user_input)]}, config={"configurable": {"thread_id": THREAD_ID}}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


while True:
    user_input = input("Ask anything: ")
    if user_input.lower() in ["q", "quit", "exit"]:
        break
    stream_graph(user_input)