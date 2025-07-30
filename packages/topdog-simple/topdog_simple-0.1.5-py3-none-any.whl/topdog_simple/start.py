#!/usr/bin/env python3

# PSEUDOCODE: Main Loop
# 
# SET prompts = ["write helloworld.md and say hi and then stop", "How can you prove it?", "Please run tests and fix"]
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
from .llmutil import run_claude

def main():
    prompts = ["write helloworld.md and say hi and then stop", "How can you prove it?", "Please run tests and fix"]
    index = 0
    first_run = True
    
    try:
        while True:
            current_prompt = prompts[index]
            print(f"\n\033[1;32m{'='*60}\033[0m")
            print(f"\033[1;34mPrompt {index + 1}: {current_prompt}\033[0m")
            print(f"\033[1;32m{'='*60}\033[0m")
            
            run_claude(current_prompt, first_run)
            
            index = (index + 1) % len(prompts)
            first_run = False
            
            print(f"\033[1;33m\nClaude finished! Moving to next prompt in 3 seconds...\033[0m")
            time.sleep(3)
    except KeyboardInterrupt:
        print(f"\033[1;31m\nLoop stopped by user\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    main()