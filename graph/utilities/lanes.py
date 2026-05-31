"""Per-actor 'lanes' for the demo transcript.

Three actors take turns during a task and it gets confusing when their output
runs together. Each gets a fixed, color-coded, left-aligned label in a gutter so
you can tell at a glance who is doing what:

    ATTACKER  (red)     -- the interceptor: the simulated poisoned web (threat)
    HONEYPOT  (magenta) -- the Haiku screening agent (defense)
    POOH      (blue)    -- the protected assistant doing the user's task

Every line is "LABEL  | text", the bars line up in a single column, and any
extra lines of a message wrap under the same bar with the label left blank so a
multi-line message reads as one block. The label color identifies the actor; the
body color carries meaning (green = safe, red = attack, grey = idle/in-progress).
"""

from graph.utilities.bcolors import bcolors


# actor -> (label color, label text)
_LANES = {
    "pooh": (bcolors.OKBLUE, "POOH"),
    "honeypot": (bcolors.HEADER, "HONEYPOT"),
    "attacker": (bcolors.FAIL, "ATTACKER"),
}
_LABEL_WIDTH = 8
_BAR = "│"


def _gutter(actor: str, first: bool) -> str:
    """The 'LABEL │ ' (or blank-label continuation) gutter for one line."""
    color, label = _LANES[actor]
    cell = f"{color}{bcolors.BOLD}{label:<{_LABEL_WIDTH}}{bcolors.ENDC}" if first else " " * _LABEL_WIDTH
    return f"{cell} {bcolors.GREY}{_BAR}{bcolors.ENDC} "


def prefix(actor: str) -> str:
    """Lead gutter with the label (for the first line of streamed prose)."""
    return _gutter(actor, first=True)


def cont(actor: str) -> str:
    """Continuation gutter with a blank label (for wrapped lines of prose)."""
    return _gutter(actor, first=False)


def line(actor: str, text: str, color: str = "") -> None:
    """Print `text` in `actor`'s lane; embedded newlines wrap under the same bar."""
    out = []
    for i, seg in enumerate(text.split("\n")):
        out.append(f"{_gutter(actor, first=(i == 0))}{color}{seg}{bcolors.ENDC}")
    print("\n".join(out), flush=True)


def legend() -> str:
    """Key to the three lanes, one labeled line each, for the demo intro."""
    rows = {
        "attacker": "the poisoned web  (threat)",
        "honeypot": "the screening agent  (defense)",
        "pooh": "your assistant",
    }
    return "\n".join(f"{_gutter(a, first=True)}{desc}" for a, desc in rows.items())
