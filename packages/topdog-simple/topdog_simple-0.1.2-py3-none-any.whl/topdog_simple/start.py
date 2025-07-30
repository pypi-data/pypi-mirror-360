#!/usr/bin/env python3

# PSEUDOCODE: Main Loop
# 
# SET prompts = ["Are all features completed?", "How can you prove it?", "Please run tests and fix"]
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
    prompts = ["Are all features completed?", "How can you prove it?", "Please run tests and fix"]
    index = 0
    first_run = True
    
    try:
        while True:
            current_prompt = prompts[index]
            run_claude(current_prompt, first_run)
            index = (index + 1) % len(prompts)
            first_run = False
            time.sleep(3)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()