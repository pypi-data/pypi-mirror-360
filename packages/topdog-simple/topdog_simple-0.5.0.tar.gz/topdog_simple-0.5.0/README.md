# Topdog Simple

Intelligent infinite loop driver for Claude Code with proper completion detection, configurable timeouts, and multiple execution modes.

## Installation

```bash
pip install topdog-simple
```

## Usage

```bash
topdogsimple
```

The tool will continuously cycle through three prompts:
1. "write helloworld.md and say hi and then stop"
2. "How can you prove it?" 
3. "Please run tests and fix"

## Configuration

Set environment variables to customize behavior:

```bash
export CLAUDE_TIMEOUT=600          # 10 minutes (default: 300s)
export CLAUDE_HEARTBEAT_TIMEOUT=120 # 2 minutes (default: 60s)  
export CLAUDE_USE_SDK=true          # Use Python SDK (default: false)
```

## Features

- **Intelligent Completion Detection**: JSON streaming analysis + process monitoring
- **Configurable Timeouts**: Environment variable control for long-running tasks
- **SDK Support**: Optional claude-code-sdk integration for better control
- **Heartbeat Monitoring**: Detects hung vs. working processes
- **Manual Override**: Ctrl+C to skip hung processes without stopping the loop
- **Automatic Configuration**: Creates `.claude/` files with full permissions
- **Persistent Context**: Maintains session state across prompts

## Manual Controls

- **Ctrl+C once**: Skip current prompt and continue to next
- **Ctrl+C twice**: Exit the entire loop

## SDK Mode

Install the SDK for enhanced reliability:

```bash
pip install claude-code-sdk
export CLAUDE_USE_SDK=true
topdogsimple
```