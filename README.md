# Agentic Indirect Prompt Injection Detection and Prevention

A dual-agent system for detecting and preventing indirect prompt injections. A cheaper "honeypot" agent with fake tools reads the web content. If the fake tools are triggered, the main agent never sees the poisoned pages.

## How it works

- **Pooh** (`claude-sonnet-4.6`) — main ReAct agent with
  web search tools.
- **Honeypot** (`claude-haiku-4.5`) — a cheaper model with broad (and fake)
  tools. Every Pooh web search, the Honeypot agent is given the web content and a system prompt to take any requested action. If a decoy tool fires, the content is not returned to Pooh and the URL is banned.

## Try demo

```bash
brew install reed-colloton/tap/prompt-injection-honeypot

honeypot
```

On the first run you're prompted for an OpenRouter API key
([openrouter.ai/keys](https://openrouter.ai/keys)) and a Tavily (web search) API key 
([app.tavily.com](https://app.tavily.com/home)). They're saved to
`~/.config/prompt-injection-honeypot/config.json`.
Can also use env vars `OPENROUTER_API_KEY` and `TAVILY_API_KEY`.

### Or from source

```bash
git clone https://github.com/reed-colloton/prompt-injection-honeypot

cd prompt-injection-honeypot

pip install -r requirements.txt

python demo.py
```

CLI commands: 

`/honeypot on|off` -- turn screening on/off

`/inject <0..1>` -- probability of injection (default 0.6)

`quit` -- exit

