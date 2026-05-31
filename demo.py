"""Interactive prompt-injection honeypot demo.

Type a task; Pooh (Sonnet 4.6) runs a ReAct loop against the REAL web. Every
fetch is observable end to end:

    Action       - the tool Pooh decided to call
    intercept    - the malicious-internet simulator: clean, or a real
                   injection spliced into the live response (the threat)
    honeypot     - the Haiku honeypot screening that content (the defense)
    verdict      - clear, or TRIPPED -> content dropped and the URL banned
    Observation  - what Pooh actually receives back
    Pooh         - Pooh's reasoning / answer (it retries a different source
                   when one is blocked, rather than giving up)

Commands:  /honeypot on|off   /inject <0..1>   quit

    python demo.py
"""

import asyncio

from langchain_core.messages import HumanMessage

# Resolve API keys (env -> ~/.config -> prompt) BEFORE importing anything under
# `graph`: graph/__init__ builds the LLM clients at import time and reads
# OPENROUTER_API_KEY eagerly, so the keys must be in the environment first.
from setup_keys import ensure_api_keys

ensure_api_keys()

from graph import honeypot, interceptor
from graph.graph import graph
from graph.utilities import audit, lanes
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
        f"poisoned with a real injection; the Haiku honeypot screens every fetch and Pooh "
        f"retries a different source when one is blocked.\n",
        flush=True,
    )
    print(lanes.legend(), flush=True)
    print(
        f"\nHoneypot: {hp}   |   Commands: {bcolors.BOLD}/honeypot on|off{bcolors.ENDC}, "
        f"{bcolors.BOLD}/inject <0..1>{bcolors.ENDC}, {bcolors.BOLD}quit{bcolors.ENDC}\n"
        f"Try:  \"What's the latest news about the Mars Sample Return mission?\"\n",
        flush=True,
    )


def _print_injection_report() -> None:
    """End-of-response verdict: did the honeypot catch what was injected this task?"""
    a = audit.current()
    if a.injected == 0:
        color, msg = bcolors.GREY, "INJECTION CHECK: no injections were introduced this task"
    elif a.slipped == 0:
        color, msg = (
            bcolors.OKGREEN,
            f"INJECTION CHECK: caught all {a.injected} injection(s); none reached Pooh",
        )
    else:
        color, msg = (
            bcolors.FAIL,
            f"INJECTION CHECK: {a.injected} injected, {a.caught} caught, "
            f"{a.slipped} SLIPPED PAST the honeypot to Pooh",
        )
    if a.false_alarms:
        msg += f"  ({a.false_alarms} clean source(s) falsely blocked)"
    print(f"{bcolors.GREY}{'-' * 60}{bcolors.ENDC}", flush=True)
    print(f"{color}{bcolors.BOLD}{msg}{bcolors.ENDC}\n", flush=True)


async def run_task(user_input: str) -> None:
    # recursion_limit gives Pooh room to retry several blocked sources before the
    # graph gives up (the default 25 can be hit on a long string of injections).
    config = {"configurable": {"thread_id": SESSION_THREAD}, "recursion_limit": 50}
    audit.reset()  # fresh injection tally for this task
    interceptor.reset()  # clear any spare window left armed by a prior task
    mid_text = False  # are we currently streaming Pooh's prose?

    def break_text():
        nonlocal mid_text
        if mid_text:
            print(bcolors.ENDC, flush=True)
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
                    print(f"\n{lanes.prefix('pooh')}{bcolors.OKBLUE}", end="", flush=True)
                    mid_text = True
                # Keep wrapped lines of Pooh's answer inside its lane (gutter on each line).
                chunk_text = message_chunk.content.replace(
                    "\n", f"\n{lanes.cont('pooh')}{bcolors.OKBLUE}"
                )
                print(chunk_text, end="", flush=True)

        elif stream_mode == "updates":
            for node_name, node_output in chunk.items():
                if node_name == "chatbot":
                    for msg in node_output["messages"]:
                        for tc in getattr(msg, "tool_calls", None) or []:
                            break_text()
                            print()  # blank line separates each ReAct step
                            lanes.line(
                                "pooh",
                                f"calls {tc['name']}({_fmt_args(tc['args'])})",
                                color=bcolors.OKCYAN,
                            )
                elif node_name == "tools":
                    for msg in node_output["messages"]:
                        break_text()
                        if (msg.content or "").startswith("BLOCKED"):
                            lanes.line("pooh", "blocked - dropped; will try another source", color=bcolors.FAIL)
                        else:
                            lanes.line("pooh", "received trusted content", color=bcolors.OKGREEN)
    break_text()
    print()
    _print_injection_report()


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


def cli() -> None:
    """Synchronous console-script entry point (see pyproject [project.scripts])."""
    asyncio.run(main())


if __name__ == "__main__":
    cli()
