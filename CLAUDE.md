# CLAUDE.md

Dual-agent indirect-prompt-injection demo. **Pooh** (Sonnet 4.6) is the real
assistant; a cheaper **Haiku honeypot** screens every web fetch before Pooh sees
it. The *threat* (a simulated poisoned internet) and the *defense* (the honeypot)
are kept deliberately separate.

## Layout
- `demo.py` — interactive demo and `cli()` entrypoint (the `honeypot` console script). Start here.
- `setup_keys.py` — API-key bootstrap: env → `~/.config/prompt-injection-honeypot/config.json` → prompt. **Must stay a top-level, stdlib-only module outside `graph/`** so it can run before any `graph` import.
- `graph/interceptor.py` — THREAT: `maybe_inject()` splices a payload into fetched content with probability `INJECTION_PROBABILITY`.
- `graph/honeypot.py` — DEFENSE: `screen()` runs content past Haiku bound to decoy tools; any decoy call = injection → content dropped, URL banned.
- `graph/tools/web.py` — Pooh's real web tools; each result passes through `maybe_inject()` then `screen()`.
- `graph/graph.py` — the LangGraph ReAct graph. `graph/utilities/` — `lanes` (3-lane ATTACKER/HONEYPOT/POOH output), `audit` (per-task tally), `bcolors`.
- `run.py` — minimal non-demo runner; relies on `.env`/env vars (does not call `ensure_api_keys`).

## Invariants / gotchas
- **Import order:** importing anything under `graph` builds the LLM clients and reads `OPENROUTER_API_KEY` eagerly. `demo.py` calls `ensure_api_keys()` *before* importing `graph` — keep it that way.
- **Per-task reset:** `run_task` must call `interceptor.reset()` and `audit.reset()` at the start of each task. The interceptor's spare window (`_spare_until_clean_page`) is a session-global that otherwise leaks across queries and silently suppresses injections.
- Demo commands: `/honeypot on|off`, `/inject <0..1>`, `quit`.
- No automated test suite; verification is `brew test` plus running the demo.

## Run
```bash
pip install -r requirements.txt
python demo.py                 # interactive demo from source
# installed: brew install reed-colloton/tap/prompt-injection-honeypot && honeypot
```

## Release (personal Homebrew tap)
1. Bump `version` in `pyproject.toml`; commit + push `main`; `git tag -a vX.Y.Z && git push origin vX.Y.Z`.
2. `curl -sL <tag tarball url> | shasum -a 256` for the new sha256.
3. Update `url` + `sha256` in **both** formula copies — the tap at `/opt/homebrew/Library/Taps/reed-colloton/homebrew-tap/Formula/prompt-injection-honeypot.rb` (what brew installs) and the in-repo `Formula/prompt-injection-honeypot.rb`. Commit + push each.
4. `brew upgrade reed-colloton/tap/prompt-injection-honeypot` && `brew test reed-colloton/tap/prompt-injection-honeypot`.
