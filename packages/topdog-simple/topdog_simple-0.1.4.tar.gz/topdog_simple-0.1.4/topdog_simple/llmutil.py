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
    # First test if claude command exists
    test_process = subprocess.Popen(
        ["claude", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    test_stdout, test_stderr = test_process.communicate()
    
    if test_process.returncode != 0:
        print(f"ERROR: claude command not found or failed")
        print(f"Return code: {test_process.returncode}")
        print(f"Stderr: {test_stderr}")
        return
    
    print("Claude command found, proceeding...")
    
    # Try without --output-format first to see if that's the issue
    if is_first_run:
        command = ["claude", "-p", prompt]
    else:
        command = ["claude", "-p", prompt, "--continue"]
    
    print(f"Running command: {' '.join(command)}")
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0  # Unbuffered
    )
    
    print("Process started, waiting for output...")
    
    # Read both stdout and stderr
    import select
    import sys
    
    if hasattr(select, 'select'):
        # Unix-like systems
        timeout_count = 0
        max_timeout = 60  # 60 seconds total timeout
        while True:
            ready, _, _ = select.select([process.stdout, process.stderr], [], [], 1.0)
            if not ready:
                timeout_count += 1
                if timeout_count >= max_timeout:
                    print("TIMEOUT: Process took too long, terminating...")
                    process.terminate()
                    break
                if process.poll() is not None:
                    break
                continue
                
            timeout_count = 0  # Reset timeout if we get output
            for stream in ready:
                line = stream.readline()
                if line:
                    if stream == process.stdout:
                        print(f"STDOUT: {line.rstrip()}")
                    else:
                        print(f"STDERR: {line.rstrip()}")
    else:
        # Windows fallback
        try:
            stdout, stderr = process.communicate(timeout=30)
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
        except subprocess.TimeoutExpired:
            print("TIMEOUT: Process took too long, terminating...")
            process.terminate()
            stdout, stderr = process.communicate()
    
    return_code = process.wait()
    print(f"Process finished with return code: {return_code}")