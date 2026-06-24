# PGenerator

A colorful, interactive terminal password generator written in Python.

```
               ____  ______                           __
              / __ \/ ____/__  ____  ___  _________ _/ /_____  _____
             / /_/ / / __/ _ \/ __ \/ _ \/ ___/ __ `/ __/ __ \/ ___/
            / ____/ /_/ /  __/ / / /  __/ /  / /_/ / /_/ /_/ / /
           /_/    \____/\___/_/ /_/\___/_/   \__,_/\__/\____/_/

                    --- Secure Password Generator ---
```

## Features

- Configurable length, character sets, and exclusions
- Guarantees at least one character from every enabled type
- Entropy-based strength rating (Weak / Fair / Strong / Very Strong)
- Color-coded output — uppercase, lowercase, digits, and symbols each get their own color
- One-keystroke clipboard copy via `pyperclip`
- Loops so you can generate multiple passwords in one session
- Zero-config first run — missing dependencies install themselves automatically

## Requirements

- Python 3.8+
- Dependencies install automatically on first run: `pyfiglet`, `rich`, `pyperclip`

On Linux without a desktop environment, clipboard support requires `xclip` or `xsel`:
```bash
sudo apt install xclip
```

## Usage

```bash
python pgenerator.py
```

| Prompt | Default | Description |
|---|---|---|
| Minimum length | 16 | Shortest acceptable password |
| Uppercase (A-Z) | Yes | Include capital letters |
| Lowercase (a-z) | Yes | Include small letters |
| Numbers (0-9) | Yes | Include digits |
| Symbols | Yes | `!@#$%^&*()_+-=[]{}|;:,.<>?` |
| Exclude ambiguous | No | Removes `0 O 1 l I` |
| Exclude specific chars | (none) | Type any characters you want excluded |

After generating, you can copy to clipboard and optionally generate another without restarting.

## How the strength rating works

Strength is calculated from [Shannon entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory)):

```
entropy (bits) = length × log₂(charset_size)
```

| Rating | Entropy |
|---|---|
| Weak | < 40 bits |
| Fair | 40 – 59 bits |
| Strong | 60 – 79 bits |
| Very Strong | 80+ bits |

A 16-character password using all four character types sits at ~104 bits — well into Very Strong.

## License

MIT
