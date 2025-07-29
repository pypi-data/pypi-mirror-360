# go-ssh

🚀 A smart SSH connector with fuzzy search, auto key upload, and secure password storage.

## Features

- 🔍 Fuzzy match SSH hosts from `~/.ssh/config`
- ✅ Checks reachability before connecting
- 🔐 Securely store passwords with `keyring`
- 🛠️ Automatically generate and upload SSH keys via `paramiko`
- 📋 List mode for host reachability summary
- 💡 Pick interactively from matched hosts

## Installation

```bash
pip install go-ssh
```

## Usage

```bash
gossh <query>
```

### Examples

```bash
gossh beacon               # Connect to first reachable host that matches "beacon"
gossh beacon --list        # List all matches with reachability info
gossh beacon --pick        # Pick manually from matched entries
gossh --save-pass          # Save global SSH password securely
gossh beacon --pass        # Save password for this specific host
gossh beacon --user        # Save username for this specific host
```

## Requirements

- Python 3.6+
- `paramiko`, `keyring`

## License

MIT License – see [LICENSE](LICENSE) file.
