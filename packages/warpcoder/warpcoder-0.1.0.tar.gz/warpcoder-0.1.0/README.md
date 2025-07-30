# WarpCoder

Universal BDD Project Generator for Claude Code - Automatically sets up Claude Code environment and manages BDD development lifecycle.

## Installation

```bash
pip install warpcoder
```

## Quick Start

After installation, you can use either `warp` or `warpclaude` command:

```bash
# Auto-run based on project state
warp

# Show interactive menu
warp --menu

# Check installation status
warp --check
```

## Features

- ✨ **Auto-Setup**: Automatically installs Claude Code, Node.js, and dependencies
- 🚀 **BDD Workflow**: Complete BDD project initialization and development loop
- 🧠 **Context7 Integration**: Enhanced memory management for Claude
- 🎮 **Interactive Menu**: User-friendly interface for all operations
- 📦 **Smart Detection**: Automatically detects and continues existing projects

## What It Does

WarpCoder automates the entire BDD (Behavior Driven Development) workflow:

1. **Environment Setup**: Ensures Claude Code, Node.js, and BDD frameworks are installed
2. **Project Initialization**: Creates domain models, state diagrams, and feature files
3. **Development Loop**: Iteratively implements code to pass BDD tests
4. **Full Stack**: Handles backend, frontend, and integration automatically

## Commands

### Default Behavior
```bash
warp
```
- If BDD project exists: Continues development (100 iterations)
- If no project: Starts interactive initialization

### Interactive Menu
```bash
warp --menu
```
Shows options for:
- Quick Start (Auto Init + Development)
- Initialize New Project
- Continue Existing Project
- Run Finished Project
- Setup Environment Only
- Create SDK Example
- Check Installation Status

### Check Status
```bash
warp --check
```
Verifies installation of all components.

## Project Structure

When you initialize a new project, WarpCoder creates:

```
your-project/
├── features/           # BDD feature files
│   └── steps/         # Step definitions
├── docs/              # Documentation
│   ├── ddd.md        # Domain model
│   ├── state-diagram.md
│   └── mission.md
├── pseudocode/        # Architecture planning
└── .claude/           # Claude configuration
    └── commands/      # Custom commands
```

## Requirements

- Python 3.8+
- Internet connection (for initial setup)
- macOS, Linux, or Windows

## How It Works

1. **Setup Phase**: Installs missing dependencies (Claude Code, Node.js via nvm)
2. **Init Phase**: Analyzes your app goal and creates minimal BDD structure
3. **Development Phase**: Runs tests, implements code, verifies full stack
4. **Delivery Phase**: Creates entry points (play.py/menu.py) for easy execution

## License

MIT License

## Contributing

Contributions welcome! Please submit issues and pull requests on GitHub.

## Support

For issues, questions, or suggestions, please visit our GitHub repository.