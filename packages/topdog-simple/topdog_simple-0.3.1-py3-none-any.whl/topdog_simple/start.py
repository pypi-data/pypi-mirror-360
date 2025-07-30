#!/usr/bin/env python3

# PSEUDOCODE: Main Loop
# 
# SET prompts = ["What was the last discussion all about?", "I'm thinking about pink elephants", "What did we just discuss?", "What file have we been writing to?", "Summary of conversation"]
# SET index = 0
# SET first_run = TRUE
# 
# WHILE forever:
#   GET current_prompt from prompts[index]
#   CALL run_claude(current_prompt, first_run)
#   SET index = next index (wrap around)
#   SET first_run = FALSE
#   WAIT 3 seconds
# END WHILE

import time
import sys
import os
import json
from .llmutil import run_claude

def setup_claude_config():
    """Set up Claude Code configuration files with wide open permissions"""
    
    # Create .claude directory if it doesn't exist
    os.makedirs('.claude', exist_ok=True)
    
    # Create CLAUDE.md with project instructions
    claude_md_content = """# TopDog Simple Project

## Project Purpose
This is a test project for topdog-simple - an infinite loop that drives Claude Code.

## Permissions
- Full file system access granted
- All bash commands allowed
- All tools enabled

## Instructions
- Feel free to create, edit, and manage any files
- Run tests and builds as needed
- Make improvements and fix issues
- Work autonomously with full permissions
"""
    
    with open('.claude/CLAUDE.md', 'w') as f:
        f.write(claude_md_content)
    
    # Create settings.json with wide open permissions
    settings = {
        "permissions": {
            "allow": [
                "*",
                "Write(*)",
                "Edit(*)", 
                "Bash(*)",
                "Read(*)",
                "MultiEdit(*)",
                "Glob(*)",
                "Grep(*)",
                "LS(*)",
                "Task(*)"
            ]
        }
    }
    
    with open('.claude/settings.json', 'w') as f:
        json.dump(settings, f, indent=2)
    
    print(f"\033[1;36mClaude configuration files created:\033[0m")
    print(f"  📝 .claude/CLAUDE.md")
    print(f"  ⚙️  .claude/settings.json (wide open permissions)")

def main():
    # Set up Claude configuration on first run
    setup_claude_config()
    
    print(f"\033[1;32m🚀 Using Claude Code SDK\033[0m")
    
    prompts = [
        "What was the last discussion all about? Write it into prompt0.md",
        "I'm thinking about pink elephants. Please just acknowledge that you understand and tell me what you think about them",
        "What did we just discuss? Write that into prompt2.md",
        "What file have we been writing things to? Put your answer in prompt3answer.md",
        "Please write a summary of our entire conversation into prompt4answer.md"
    ]
    index = 0
    first_run = True
    
    try:
        while True:
            current_prompt = prompts[index]
            print(f"\n\033[1;32m{'='*60}\033[0m")
            print(f"\033[1;34mPrompt {index + 1}: {current_prompt}\033[0m")
            print(f"\033[1;32m{'='*60}\033[0m")
            
            run_claude(current_prompt, first_run)
            
            # Add human pause after the last prompt (prompt 4) for debugging
            if index == 4:  # After prompt 4 (0-indexed, so prompt 4 is index 4)
                print(f"\033[1;33m\n🔍 Debugging pause: Check the output files, then press Enter to continue...\033[0m")
                input()
            
            index = (index + 1) % len(prompts)
            first_run = False
            
            if index != 0:  # Don't wait before starting the next cycle
                print(f"\033[1;33m\nClaude finished! Moving to next prompt in 3 seconds...\033[0m")
                time.sleep(3)
    except KeyboardInterrupt:
        print(f"\033[1;31m\nLoop stopped by user\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    main()