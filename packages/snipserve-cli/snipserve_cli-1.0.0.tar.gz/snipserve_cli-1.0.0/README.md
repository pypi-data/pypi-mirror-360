# README.md
# SnipServe CLI

A command-line interface for SnipServe, allowing you to manage pastes from your terminal.

## Installation

```bash
pip install snipserve-cli
```

## Quick Start

1. **Configure your API key:**
   ```bash
   snipserve config set-key YOUR_API_KEY
   ```

2. **Set your instance URL (if not using default):**
   ```bash
   snipserve config set-url https://snipserve.spkal01.me
   ```

3. **Create a paste:**
   ```bash
   # From command line
   snipserve create "My Title" --content "Hello, world!"
   
   # From file
   snipserve create "Config File" --file config.json
   
   # Using editor
   snipserve create "My Script" --editor
   
   # From stdin
   echo "Hello, world!" | snipserve create "Piped Content"
   ```

## Commands

### Configuration
- `snipserve config set-key <api-key>` - Set your API key
- `snipserve config set-url <url>` - Set instance URL
- `snipserve config show` - Show current configuration

### Paste Management
- `snipserve create <title>` - Create a new paste
- `snipserve get <paste-id>` - View a paste
- `snipserve list` - List your pastes
- `snipserve update <paste-id>` - Update a paste
- `snipserve delete <paste-id>` - Delete a paste

### User Information
- `snipserve whoami` - Show current user info

## Examples

```bash
# Create from file with hidden flag
snipserve create "Secret Config" --file ~/.ssh/config --hidden

# Update paste content using editor
snipserve update abc123def --editor

# Create from command output
ls -la | snipserve create "Directory Listing"

# Quick paste from clipboard (macOS)
pbpaste | snipserve create "Clipboard Content"
```

## Environment Variables

- `SNIPSERVE_API_KEY` - Your API key
- `SNIPSERVE_URL` - Instance URL
- `EDITOR` - Preferred editor for `--editor` flag

## License

MIT License