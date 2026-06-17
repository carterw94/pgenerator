"""PGenerator - A beautiful terminal password generator"""

import random
import string
import sys
import subprocess
import math
import time


def _install(package):
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", package],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


# Auto-install so users can just run `python pgenerator.py` without any setup step
for _pkg in ["pyfiglet", "rich", "pyperclip"]:
    try:
        __import__(_pkg)
    except ImportError:
        print(f"Installing {_pkg}...")
        _install(_pkg)

import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich import box
from rich.align import Align
import pyperclip

# highlight=False stops rich from randomly coloring numbers/strings in our output
console = Console(highlight=False, emoji=False)

# Keeping symbols to a sensible subset — some sites reject chars like ` ~ \ ' "
SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"


# --- Display -----------------------------------------------------------------

def show_title():
    console.clear()
    try:
        art = pyfiglet.figlet_format("PGenerator", font="slant")
    except Exception:
        # "slant" isn't bundled with every pyfiglet install, fall back to default
        art = pyfiglet.figlet_format("PGenerator")

    lines = art.splitlines()
    styled = Text()
    colors = ["bold cyan", "bold blue", "bold magenta", "bold cyan", "bold blue"]
    for i, line in enumerate(lines):
        styled.append(line + "\n", style=colors[i % len(colors)])

    console.print()
    console.print(Align.center(styled))
    console.print(
        Align.center(Text("--- Secure Password Generator ---", style="dim white"))
    )
    console.print()


def display_password(password, opts):
    console.print()

    strength_label, strength_color = _strength(password, opts)

    # Color-code each character type so the output is easy to read at a glance
    pwd_text = Text()
    for ch in password:
        if ch.isupper():
            pwd_text.append(ch, style="bold cyan")
        elif ch.islower():
            pwd_text.append(ch, style="white")
        elif ch.isdigit():
            pwd_text.append(ch, style="bold yellow")
        else:
            pwd_text.append(ch, style="bold magenta")

    console.print(
        Panel(
            Align.center(pwd_text),
            title="[bold white] Generated Password [/bold white]",
            border_style="cyan",
            box=box.DOUBLE_EDGE,
            padding=(1, 3),
        )
    )

    tbl = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    tbl.add_column("k", style="dim")
    tbl.add_column("v", style="bold")
    tbl.add_row("Length", f"{len(password)} characters")
    tbl.add_row("Strength", f"[{strength_color}]{strength_label}[/{strength_color}]")
    console.print(Align.center(tbl))
    console.print()


# --- Logic -------------------------------------------------------------------

def _strength(password: str, opts: dict):
    # Shannon entropy: bits = length * log2(charset_size)
    # Thresholds (<40 / <60 / <80 / 80+) roughly match NIST guidelines
    size = 0
    if opts["use_upper"]:   size += 26
    if opts["use_lower"]:   size += 26
    if opts["use_digits"]:  size += 10
    if opts["use_symbols"]: size += len(SYMBOLS)
    entropy = len(password) * math.log2(size) if size > 1 else 0
    if entropy < 40:  return "Weak",        "red"
    if entropy < 60:  return "Fair",        "yellow"
    if entropy < 80:  return "Strong",      "green"
    return             "Very Strong",        "bold green"


def _filter(chars: str, exclude_ambiguous: bool, custom_exc: set) -> str:
    ambiguous = set("0O1lI")
    result = set(chars) - custom_exc
    if exclude_ambiguous:
        result -= ambiguous
    return "".join(sorted(result))


def generate_password(opts: dict):
    custom_exc = set(opts["custom_exclude"])
    pools = []
    required = []

    for flag, src in [
        ("use_upper",   string.ascii_uppercase),
        ("use_lower",   string.ascii_lowercase),
        ("use_digits",  string.digits),
        ("use_symbols", SYMBOLS),
    ]:
        if opts[flag]:
            pool = _filter(src, opts["exclude_ambiguous"], custom_exc)
            if pool:
                pools.append(pool)
                # Pull one guaranteed character from each enabled type
                required.append(random.choice(pool))

    if not pools:
        return None, "No character types selected - enable at least one."

    full_charset = "".join(pools)

    # Never go shorter than the number of required chars, even if the user asked for fewer
    length = max(opts["length"], len(required))
    extra = [random.choice(full_charset) for _ in range(length - len(required))]

    chars = required + extra
    random.shuffle(chars)  # Shuffle so the required chars don't all land at the front
    return "".join(chars), None


# --- Prompts -----------------------------------------------------------------

def ask_options() -> dict:
    console.print(
        Panel("[bold white]Configure your password[/bold white]", style="cyan", box=box.ROUNDED)
    )
    console.print()

    length = IntPrompt.ask(
        "  [bold cyan]Minimum length[/bold cyan]", default=16, show_default=True
    )
    length = max(1, length)
    console.print()

    use_upper   = Confirm.ask("  [bold cyan]Uppercase letters[/bold cyan] [dim](A-Z)[/dim]",       default=True)
    use_lower   = Confirm.ask("  [bold cyan]Lowercase letters[/bold cyan] [dim](a-z)[/dim]",       default=True)
    use_digits  = Confirm.ask("  [bold cyan]Numbers          [/bold cyan] [dim](0-9)[/dim]",       default=True)
    use_symbols = Confirm.ask("  [bold cyan]Symbols          [/bold cyan] [dim](!@#$%...)[/dim]",  default=True)
    console.print()

    exclude_ambiguous = Confirm.ask(
        "  [bold cyan]Exclude ambiguous chars[/bold cyan] [dim](0 O 1 l I)[/dim]", default=False
    )
    custom_exclude = Prompt.ask(
        "  [bold cyan]Exclude specific chars[/bold cyan]  [dim](blank to skip)[/dim]", default=""
    )

    return dict(
        length=length,
        use_upper=use_upper,
        use_lower=use_lower,
        use_digits=use_digits,
        use_symbols=use_symbols,
        exclude_ambiguous=exclude_ambiguous,
        custom_exclude=custom_exclude,
    )


# --- Main loop ---------------------------------------------------------------

def main():
    while True:
        show_title()

        try:
            opts = ask_options()
        except (KeyboardInterrupt, EOFError):
            console.print("\n\n[dim]  Goodbye! Stay secure.[/dim]\n")
            break

        console.print()

        with console.status("[bold cyan]  Generating password...[/bold cyan]", spinner="dots"):
            time.sleep(0.4)  # Small pause — makes the generation feel intentional
            password, error = generate_password(opts)

        if error:
            console.print(f"\n  [bold red]Error: {error}[/bold red]\n")
            time.sleep(1.5)
            continue

        display_password(password, opts)

        try:
            if Confirm.ask("  [bold cyan]Copy to clipboard?[/bold cyan]", default=True):
                pyperclip.copy(password)
                console.print("  [bold green]>> Copied![/bold green]")
        except Exception:
            # pyperclip silently fails on headless Linux without xclip/xsel
            console.print("  [dim](Clipboard unavailable on this system)[/dim]")

        console.print()

        try:
            again = Confirm.ask("  [bold cyan]Generate another?[/bold cyan]", default=True)
        except (KeyboardInterrupt, EOFError):
            again = False

        if not again:
            console.print("\n  [dim]Goodbye! Stay secure.[/dim]\n")
            break


if __name__ == "__main__":
    main()
