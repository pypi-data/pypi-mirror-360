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
import os

# Configuration constants - can be overridden by environment variables
DEFAULT_TIMEOUT = int(os.getenv('CLAUDE_TIMEOUT', '300'))  # 5 minutes default
HEARTBEAT_TIMEOUT = int(os.getenv('CLAUDE_HEARTBEAT_TIMEOUT', '60'))  # 1 minute without output
USE_SDK = os.getenv('CLAUDE_USE_SDK', 'false').lower() == 'true'

def run_claude_with_sdk(prompt, is_first_run):
    """Run Claude using the Python SDK for better control"""
    try:
        import anyio
        from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock
        
        async def claude_query():
            options = ClaudeCodeOptions(
                allowed_tools=["*"],
                permission_mode='acceptEdits'
            )
            
            print(f"\033[1;36mUsing Claude SDK...\033[0m")
            
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"CLAUDE: {block.text}")
                else:
                    print(f"SDK: {message}")
                    
            print(f"\033[1;32m✓ SDK query completed\033[0m")
            
        anyio.run(claude_query)
        return True
        
    except ImportError:
        print(f"\033[1;33m⚠ claude-code-sdk not installed, falling back to CLI\033[0m")
        return False
    except Exception as e:
        print(f"\033[1;31m✗ SDK error: {e}, falling back to CLI\033[0m")
        return False

def run_claude(prompt, is_first_run):
    # Try SDK first if enabled
    if USE_SDK:
        if run_claude_with_sdk(prompt, is_first_run):
            return
    
    # Fallback to CLI approach
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
    
    # Use JSON streaming to detect completion signals
    if is_first_run:
        command = ["claude", "-p", prompt, "--output-format=stream-json"]
    else:
        command = ["claude", "-p", prompt, "--continue", "--output-format=stream-json"]
    
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
    
    # Use configurable timeouts
    completion_detected = False
    last_heartbeat = time.time()
    manual_skip = False
    
    def signal_handler(signum, frame):
        nonlocal manual_skip
        print(f"\n\033[1;33m⚠ Manual skip requested (Ctrl+C)\033[0m")
        manual_skip = True
    
    # Set up signal handler for manual override
    import signal
    original_handler = signal.signal(signal.SIGINT, signal_handler)
    
    def emergency_kill_after_timeout():
        time.sleep(DEFAULT_TIMEOUT)  # Emergency backstop
        if process.poll() is None:
            print(f"\n\033[1;31mEMERGENCY KILL: Process exceeded {DEFAULT_TIMEOUT}s limit!\033[0m")
            try:
                process.kill()
            except:
                pass
    
    # Start the emergency killer thread
    killer_thread = threading.Thread(target=emergency_kill_after_timeout, daemon=True)
    killer_thread.start()
    
    def parse_json_for_completion(line):
        """Parse JSON line and check for completion signals"""
        nonlocal completion_detected
        try:
            data = json.loads(line.strip())
            
            # Look for completion indicators in the JSON structure
            if isinstance(data, dict):
                # Check various completion signals
                if data.get('type') == 'completion' or data.get('finished', False):
                    completion_detected = True
                    print(f"\033[1;32m✓ COMPLETION DETECTED: {data}\033[0m")
                    return True
                    
                # Check for message structure with content
                if 'messages' in data:
                    for msg in data.get('messages', []):
                        if msg.get('role') == 'assistant' and 'content' in msg:
                            print(f"CLAUDE: {msg['content']}")
                            
                # Generic JSON output
                elif 'content' in data:
                    print(f"CLAUDE: {data['content']}")
                else:
                    print(f"JSON: {json.dumps(data, indent=2)}")
                    
            return False
        except json.JSONDecodeError:
            # Not JSON, treat as regular output
            print(f"OUTPUT: {line.rstrip()}")
            return False
    
    if hasattr(select, 'select'):
        # Unix-like systems with intelligent detection
        while True:
            ready, _, _ = select.select([process.stdout, process.stderr], [], [], 1.0)
            current_time = time.time()
            
            if not ready:
                # Check for various exit conditions
                if manual_skip:
                    print(f"\033[1;33m⚠ Manual skip - terminating process\033[0m")
                    process.terminate()
                    break
                elif process.poll() is not None:
                    print(f"\033[1;32m✓ Process exited normally\033[0m")
                    break
                elif completion_detected:
                    print(f"\033[1;32m✓ Completion detected, waiting for process exit...\033[0m")
                    # Give it a few seconds to clean up after completion
                    try:
                        process.wait(timeout=5)
                        break
                    except subprocess.TimeoutExpired:
                        print(f"\033[1;33m⚠ Process didn't exit after completion, force closing\033[0m")
                        process.terminate()
                        break
                elif current_time - last_heartbeat > HEARTBEAT_TIMEOUT:
                    print(f"\n\033[1;33m⚠ No output for {HEARTBEAT_TIMEOUT}s - possible hang detected\033[0m")
                    print(f"Press Ctrl+C to skip, or wait for emergency timeout...")
                    last_heartbeat = current_time  # Reset to avoid spam
                continue
                
            last_heartbeat = current_time  # Reset heartbeat on any output
            
            for stream in ready:
                line = stream.readline()
                if line:
                    if stream == process.stdout:
                        if parse_json_for_completion(line):
                            completion_detected = True
                    else:
                        print(f"STDERR: {line.rstrip()}")
                else:
                    # Stream closed
                    if process.poll() is not None:
                        print(f"\033[1;32m✓ Stream closed, process finished\033[0m")
                        break
    else:
        # Windows fallback
        try:
            stdout, stderr = process.communicate(timeout=DEFAULT_TIMEOUT)
            if stdout:
                for line in stdout.split('\n'):
                    if line.strip():
                        parse_json_for_completion(line)
            if stderr:
                print(f"STDERR: {stderr}")
        except subprocess.TimeoutExpired:
            print(f"\n\033[1;31mTIMEOUT: Process exceeded {DEFAULT_TIMEOUT}s, force killing...\033[0m")
            try:
                process.kill()
                stdout, stderr = process.communicate(timeout=5)
            except:
                pass
    
    # Restore original signal handler
    signal.signal(signal.SIGINT, original_handler)
    
    # Don't wait forever - check if it's actually done
    try:
        return_code = process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        print("\n\033[1;31mProcess still hanging, force killing...\033[0m")
        process.kill()
        return_code = process.wait()
    
    print(f"\033[1;33mProcess finished with return code: {return_code}\033[0m")