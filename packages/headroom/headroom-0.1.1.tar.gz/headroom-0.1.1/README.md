# Max Headroom

<p align="center">
  <img src="headroom/assets/Max_Logo.png" alt="Max Logo" width="800"/>
</p>

**Max> A Command-line AI Agent**

---

## Overview

**Max** is a powerful, extensible command-line AI assistant. It can:
- Connect to local or cloud based LLMs
- Interpret natural language commands
- Run system tools and shell commands safely (with confirmation)
- Manage files, directories, packages, and more
- Provide interactive chat and planning features

---

## Installation

```sh
pip install headroom
```

---

## Usage

Start Max from your terminal:

```sh
max
```

Type natural language requests or commands, for example:
- `create a new directory called test`
- `copy file.txt to backup/`
- `install package requests`
- `help`
- `exit`

Max will confirm actions before running anything that changes your system and remeber your preferences.

---

## Features

- **Natural Language Understanding:** Ask for actions in plain English.
- **Safe Execution:** Confirmation prompts for system changes.
- **Always Allow/Revocation:** Mark commands as always allowed or revoke them.
- **Tab Completion:** Quickly find available commands.
- **Extensible:** Add your own tools and commands.

---

## Configuration & Customization

- **Config:** Edit `config.yaml` to customize commands and behavior.
- **User Preferences:** Preferences are stored and managed automatically.

---

## Development

Clone the repo and install dependencies:

```sh
git clone https://github.com/SUNKENDREAMS/headroom.git
cd headroom
pip install -e .
```

Run locally:

```sh
python -m headroom.max
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

James Bridges

---

## Contributing

Pull requests and issues are welcome!

---

## Acknowledgements

- [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)
- [pyyaml](https://github.com/yaml/pyyaml)
- [requests](https://github.com/psf/requests)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

---
