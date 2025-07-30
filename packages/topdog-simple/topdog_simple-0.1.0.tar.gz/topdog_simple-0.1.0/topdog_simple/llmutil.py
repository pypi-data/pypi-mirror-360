# PSEUDOCODE: Claude Command Utilities
#
# FUNCTION run_claude(prompt, is_first_run):
#   IF is_first_run:
#     SET command = "claude -p prompt --output-format=stream-json"
#   ELSE:
#     SET command = "claude -p prompt --output-format=stream-json --continue"
#   END IF
#   
#   START subprocess with command
#   WHILE subprocess running:
#     READ line from output
#     IF line is JSON:
#       PARSE and PRINT JSON
#     ELSE:
#       PRINT raw line
#     END IF
#   END WHILE
# END FUNCTION

import subprocess
import json

def run_claude(prompt, is_first_run):
    if is_first_run:
        command = ["claude", "-p", prompt, "--output-format=stream-json"]
    else:
        command = ["claude", "-p", prompt, "--output-format=stream-json", "--continue"]
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    for line in process.stdout:
        if line.strip():
            try:
                data = json.loads(line)
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print(line.rstrip())
    
    process.wait()