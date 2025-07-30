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
    
    print(f"Running command: {' '.join(command)}")
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    print("Process started, waiting for output...")
    
    for line in process.stdout:
        if line.strip():
            print(f"Raw line: {repr(line)}")
            try:
                data = json.loads(line)
                print("JSON parsed successfully:")
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print(f"Raw output: {line.rstrip()}")
    
    stderr_output = process.stderr.read()
    if stderr_output:
        print(f"Error output: {stderr_output}")
    
    return_code = process.wait()
    print(f"Process finished with return code: {return_code}")