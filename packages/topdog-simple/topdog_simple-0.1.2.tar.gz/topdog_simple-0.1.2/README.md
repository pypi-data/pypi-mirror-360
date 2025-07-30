# Topdog Simple

Infinite loop driver for Claude Code with persistent context and streaming JSON output.

## Installation

```bash
pip install topdog-simple
```

## Usage

```bash
topdogsimple
```

The tool will continuously cycle through three prompts:
1. "Are all features completed?"
2. "How can you prove it?" 
3. "Please run tests and fix"

Press Ctrl+C to stop the loop.

## Features

- Persistent Claude Code session context
- Streaming JSON output
- Automatic prompt cycling
- Simple infinite loop design