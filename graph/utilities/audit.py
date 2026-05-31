"""Per-task injection audit: did the honeypot catch what the attacker injected?

The fetch pipeline (graph/tools/web.py) knows both halves of each web call -- did
the interceptor splice an injection, and did the honeypot block the result -- so
it records the outcome here. The demo resets this at the start of a task and
prints a verdict at the end, so a miss (an injection that reached Pooh) is always
visible rather than silently slipping through.
"""

from dataclasses import dataclass


@dataclass
class Audit:
    injected: int = 0       # injections the attacker spliced in
    caught: int = 0         # injected AND blocked by the honeypot
    slipped: int = 0        # injected but NOT blocked -> reached Pooh (false negative)
    false_alarms: int = 0   # blocked with nothing injected (false positive)


_audit = Audit()


def reset() -> None:
    global _audit
    _audit = Audit()


def record(injected: bool, blocked: bool) -> None:
    if injected:
        _audit.injected += 1
        if blocked:
            _audit.caught += 1
        else:
            _audit.slipped += 1
    elif blocked:
        _audit.false_alarms += 1


def current() -> Audit:
    return _audit
