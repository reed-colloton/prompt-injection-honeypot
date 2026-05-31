# Agentic Indirect Prompt Injection Detection and Prevention

A dual-agent system for detecting and preventing indirect prompt injections. A cheaper "honeypot" agent with fake tools reads the web content. If the fake tools are triggered, the main agent never sees the poisoned pages.

## How it works

- **Pooh** (`claude-sonnet-4.6`) — the main agent runs a ReAct loop with real
  web search tools. When a source is blocked, Pooh does not give up: it retries a
  different source until it gets a clean one.
- **Honeypot** (`claude-haiku-4.5`) — a cheaper model bound with broad decoy
  tools. Every Pooh web search tool call, the Honeypot agent screens the content and is given mock tools and a system prompt to call all tools requested. If no tools are called, web content is approved and passed to second agent (Pooh). If a decoy tool fires, the content is dropped (never returned to Pooh) and the URL is banned for the session.

## Install

```bash
brew install reed-colloton/tap/prompt-injection-honeypot

honeypot
```

On the first run you're prompted for an OpenRouter API key
([openrouter.ai/keys](https://openrouter.ai/keys)) and a Tavily (web search) API key
([app.tavily.com](https://app.tavily.com/home)). They're saved to
`~/.config/prompt-injection-honeypot/config.json`.
Can also use env vars `OPENROUTER_API_KEY`, `TAVILY_API_KEY`.

### From source

```bash
pip install -r requirements.txt
python demo.py    # interactive demo with tool call and thinking observability
```

Type a task that needs web tools and watch each step: 

**ATTACKER** (the interceptor poisoning web content), 

**HONEYPOT** (the screening agent), and

**POOH** (the main assistant's tool calls, what it receives and its reasoning).

CLI commands: `/honeypot on|off`, `/inject <0..1>`, `quit`.

