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
import time

# Configuration constants - can be overridden by environment variables
DEFAULT_TIMEOUT = int(os.getenv('CLAUDE_TIMEOUT', '300'))  # 5 minutes default
HEARTBEAT_TIMEOUT = int(os.getenv('CLAUDE_HEARTBEAT_TIMEOUT', '60'))  # 1 minute without output
FORCE_CLI = os.getenv('CLAUDE_FORCE_CLI', 'false').lower() == 'true'  # Force CLI mode (disable SDK)

def check_sdk_availability():
    """Check what's needed for SDK mode"""
    missing = []
    
    try:
        import anyio
    except ImportError:
        missing.append("anyio (pip install anyio)")
    
    try:
        import claude_code_sdk
    except ImportError:
        missing.append("claude-code-sdk (pip install claude-code-sdk)")
    
    return missing

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
            
            print(f"\033[1;32m🚀 Using Claude SDK (reliable completion detection)\033[0m")
            
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"CLAUDE: {block.text}")
                else:
                    print(f"SDK: {message}")
                    
            print(f"\033[1;32m✓ SDK query completed successfully\033[0m")
            
        anyio.run(claude_query)
        return True
        
    except ImportError as e:
        missing = check_sdk_availability()
        # Extract just the package names
        packages = []
        for pkg in missing:
            if '(' in pkg:
                packages.append(pkg.split('(')[0].strip())
            else:
                packages.append(pkg)
        
        print(f"\033[1;33m⚠ SDK not available - missing: {', '.join(packages)}\033[0m")
        print(f"\033[1;33m  Install with: pip install {' '.join(packages)}\033[0m")
        print(f"\033[1;33m  Falling back to CLI mode...\033[0m")
        return False
    except Exception as e:
        print(f"\033[1;31m✗ SDK error: {e}\033[0m")
        print(f"\033[1;31m  Falling back to CLI mode...\033[0m")
        return False

def run_claude(prompt, is_first_run):
    # Try SDK first unless explicitly disabled
    if not FORCE_CLI:
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
    
    # Use JSON streaming to detect completion signals (requires --verbose)
    if is_first_run:
        command = ["claude", "-p", prompt, "--output-format=stream-json", "--verbose"]
    else:
        command = ["claude", "-p", prompt, "--continue", "--output-format=stream-json", "--verbose"]
    
    print(f"Running command: {' '.join(command)}")
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered for better real-time output
    )
    
    # Debug: Check if process started successfully
    if process.poll() is not None:
        print(f"\033[1;31mERROR: Process exited immediately with code {process.returncode}\033[0m")
        stdout, stderr = process.communicate()
        if stdout:
            print(f"STDOUT: {stdout}")
        if stderr:
            print(f"STDERR: {stderr}")
        return
    
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
        manual_skip = True
        # Don't print here to avoid reentrant calls - let the main loop handle it
    
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
        streams_closed = set()
        while True:
            # Check if process has finished first
            if process.poll() is not None:
                print(f"\033[1;32m✓ Process exited normally (return code: {process.returncode})\033[0m")
                break
                
            # Check for manual skip
            if manual_skip:
                print(f"\033[1;33m⚠ Manual skip - terminating process\033[0m")
                process.terminate()
                break
            
            ready, _, _ = select.select([process.stdout, process.stderr], [], [], 1.0)
            current_time = time.time()
            
            if not ready:
                # Check for various exit conditions
                if completion_detected:
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
                    # Stream closed - track which streams have closed
                    streams_closed.add(stream)
                    if len(streams_closed) >= 2:  # Both stdout and stderr closed
                        print(f"\033[1;32m✓ All streams closed, process finishing...\033[0m")
                        # Give process a moment to exit cleanly
                        try:
                            process.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            pass
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