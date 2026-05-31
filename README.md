# prompt-injection-honeypot

A dual-agent system for detecting and preventing indirect prompt injections. A cheaper "honeypot" agent with fake tools reads the web content. If the fake tools are triggered, the main agent never sees the poisoned pages.

## How it works

- **Pooh** (`claude-sonnet-4.6`) — the main agent runs a ReAct loop with real
  web search tools.
- **Honeypot** (`claude-haiku-4.5`) — a cheaper model bound with broad decoy
  tools. Every Pooh web search tool call, the Honeypot agent screens the content and is given mock tools and a system prompt to call all tools requested. If no tools are called, web content is approved and passed to second agent (Pooh).

## Run

Needs `OPENROUTER_API_KEY` and `TAVILY_API_KEY` in `.env` file.

```bash
pip install -r requirements.txt
python demo.py    # interactive demo with tool call and thinking observability 
```

Type a task and watch each step: the tool Pooh calls, whether the interceptor
poisoned the response, the honeypot's verdict, what Pooh receives, its reasoning.

CLI commands: `/honeypot on|off`, `/inject <0..1>`, `quit`.

