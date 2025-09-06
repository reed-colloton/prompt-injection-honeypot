# prompt-injection-honeypot

## Architecture:
- ReAct agent with tools, protected against idirect prompt injection
- before using tool, runs web content through honeypot llm
- If no tool call with honeypot, tool call runs
- Ideally honepot llm is faster/cheaper so it shouldn't cause latency


## Proof of concept:
- First run with two tools: web search and mock bank account transfer
- Then add more tools
- Should be able to catch any tool being run, not just bank account, in the future
- And then maybe move on to other injections besides tool calling

