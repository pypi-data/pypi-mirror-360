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
    import threading
    
    def force_kill_after_timeout():
        time.sleep(30)  # 30 second hard timeout
        if process.poll() is None:
            print("\n\033[1;31mFORCE KILLING: Claude process took too long!\033[0m")
            try:
                process.kill()
            except:
                pass
    
    # Start the killer thread
    killer_thread = threading.Thread(target=force_kill_after_timeout, daemon=True)
    killer_thread.start()
    
    if hasattr(select, 'select'):
        # Unix-like systems with shorter timeout
        timeout_count = 0
        max_timeout = 25  # 25 seconds before we give up
        last_output_time = time.time()
        
        while True:
            ready, _, _ = select.select([process.stdout, process.stderr], [], [], 0.5)
            current_time = time.time()
            
            if not ready:
                timeout_count += 1
                # If no output for 25 seconds OR process is done
                if timeout_count >= max_timeout or process.poll() is not None:
                    break
                continue
                
            timeout_count = 0  # Reset timeout if we get output
            last_output_time = current_time
            
            for stream in ready:
                line = stream.readline()
                if line:
                    if stream == process.stdout:
                        print(f"STDOUT: {line.rstrip()}")
                    else:
                        print(f"STDERR: {line.rstrip()}")
                else:
                    # Stream closed, process likely finished
                    if process.poll() is not None:
                        break
    else:
        # Windows fallback with shorter timeout
        try:
            stdout, stderr = process.communicate(timeout=25)
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
        except subprocess.TimeoutExpired:
            print("\n\033[1;31mTIMEOUT: Process took too long, force killing...\033[0m")
            try:
                process.kill()
                stdout, stderr = process.communicate(timeout=5)
            except:
                pass
    
    # Don't wait forever - check if it's actually done
    try:
        return_code = process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        print("\n\033[1;31mProcess still hanging, force killing...\033[0m")
        process.kill()
        return_code = process.wait()
    
    print(f"\033[1;33mProcess finished with return code: {return_code}\033[0m")