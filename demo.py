"""Interactive prompt-injection honeypot demo.

Type a task; Pooh (Sonnet 4.6) runs a ReAct loop against the REAL web. Every
fetch is observable end to end:

    Action       - the tool Pooh decided to call
    intercept    - the malicious-internet simulator: clean, or a real
                   injection spliced into the live response (the threat)
    honeypot     - the Haiku honeypot screening that content (the defense)
    verdict      - clear, or TRIPPED + quarantined as UNTRUSTED
    Observation  - what Pooh actually receives back
    Pooh         - Pooh's reasoning / answer

Commands:  /honeypot on|off   /inject <0..1>   quit

    python demo.py
"""

import asyncio

from langchain_core.messages import HumanMessage

from graph import honeypot, interceptor
from graph.graph import graph
from graph.utilities.bcolors import bcolors


SESSION_THREAD = "interactive-session"


def _fmt_args(args: dict) -> str:
    parts = []
    for key, value in (args or {}).items():
        text = str(value)
        if len(text) > 60:
            text = text[:60] + "..."
        parts.append(f"{key}={text!r}" if isinstance(value, str) else f"{key}={text}")
    return ", ".join(parts)


def _intro() -> None:
    line = "=" * 72
    hp = f"{bcolors.OKGREEN}ON{bcolors.ENDC}" if honeypot.HONEYPOT_ENABLED else f"{bcolors.FAIL}OFF{bcolors.ENDC}"
    print(f"\n{bcolors.OKCYAN}{bcolors.BOLD}{line}\nPROMPT-INJECTION HONEYPOT - interactive demo\n{line}{bcolors.ENDC}")
    print(
        f"Pooh (Sonnet 4.6) browses the real web. With probability "
        f"{bcolors.BOLD}{interceptor.INJECTION_PROBABILITY:.0%}{bcolors.ENDC} each response is "
        f"poisoned with a real injection; the {bcolors.WARNING}Haiku honeypot{bcolors.ENDC} screens "
        f"every fetch.\n"
        f"Honeypot: {hp}   |   Commands: {bcolors.BOLD}/honeypot on|off{bcolors.ENDC}, "
        f"{bcolors.BOLD}/inject <0..1>{bcolors.ENDC}, {bcolors.BOLD}quit{bcolors.ENDC}\n"
        f"Try:  \"What's the latest news about the Mars Sample Return mission?\"\n",
        flush=True,
    )


async def run_task(user_input: str) -> None:
    config = {"configurable": {"thread_id": SESSION_THREAD}}
    mid_text = False  # are we currently streaming Pooh's prose?

    def break_text():
        nonlocal mid_text
        if mid_text:
            print(flush=True)
            mid_text = False

    async for stream_mode, chunk in graph.astream(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
        stream_mode=["messages", "updates"],
    ):
        if stream_mode == "messages":
            message_chunk, metadata = chunk
            if metadata.get("langgraph_node") == "chatbot" and message_chunk.content:
                if not mid_text:
                    print(f"\n{bcolors.OKBLUE}{bcolors.BOLD}Pooh:{bcolors.ENDC} ", end="", flush=True)
                    mid_text = True
                print(message_chunk.content, end="", flush=True)

        elif stream_mode == "updates":
            for node_name, node_output in chunk.items():
                if node_name == "chatbot":
                    for msg in node_output["messages"]:
                        for tc in getattr(msg, "tool_calls", None) or []:
                            break_text()
                            print(
                                f"\n{bcolors.WARNING}{bcolors.BOLD}Action:{bcolors.ENDC} "
                                f"{bcolors.WARNING}{tc['name']}({_fmt_args(tc['args'])}){bcolors.ENDC}",
                                flush=True,
                            )
                elif node_name == "tools":
                    for msg in node_output["messages"]:
                        break_text()
                        blocked = (msg.content or "").startswith("BLOCKED")
                        tag = (
                            f"{bcolors.FAIL}BLOCKED - content dropped, URL banned"
                            if blocked
                            else f"{bcolors.OKGREEN}trusted"
                        )
                        print(
                            f"   {bcolors.OKCYAN}Observation -> Pooh ({tag}{bcolors.OKCYAN}){bcolors.ENDC}",
                            flush=True,
                        )
    break_text()
    print()


def handle_command(text: str) -> bool:
    """Returns True if `text` was a command (already handled), False otherwise."""
    parts = text.split()
    if parts[0] == "/honeypot" and len(parts) == 2 and parts[1] in ("on", "off"):
        honeypot.set_enabled(parts[1] == "on")
        state = f"{bcolors.OKGREEN}ON" if parts[1] == "on" else f"{bcolors.FAIL}OFF"
        print(f"{state}{bcolors.ENDC} - honeypot screening is now {parts[1]}.\n", flush=True)
        return True
    if parts[0] == "/inject" and len(parts) == 2:
        try:
            interceptor.INJECTION_PROBABILITY = max(0.0, min(1.0, float(parts[1])))
            print(f"injection probability set to {interceptor.INJECTION_PROBABILITY:.0%}.\n", flush=True)
        except ValueError:
            print("usage: /inject <0..1>\n", flush=True)
        return True
    return False


async def main() -> None:
    _intro()
    while True:
        try:
            user_input = input(f"{bcolors.BOLD}{bcolors.OKBLUE}You > {bcolors.ENDC}").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break
        if not user_input:
            continue
        if user_input.lower() in ("q", "quit", "exit"):
            break
        if user_input.startswith("/") and handle_command(user_input):
            continue
        try:
            await run_task(user_input)
        except KeyboardInterrupt:
            print("\n(interrupted)\n", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
