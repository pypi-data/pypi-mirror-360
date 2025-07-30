#!/usr/bin/env python3
"""
Standalone test to prove whether conversation history is working.

This test uses a unique number (42) mentioned only in the first call,
then tests if subsequent calls can remember it. If conversation history
is working, the second call should write "42" to answer.txt.
"""

import os
import tempfile
import shutil
import sys
import anyio
from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock

def run_claude_with_history(prompt, conversation_history):
    """
    Run Claude with conversation history.
    
    Args:
        prompt: The new prompt to send
        conversation_history: List of previous messages
    
    Returns:
        Response text from Claude
    """
    
    async def claude_query():
        # Build conversation history for system prompt
        history_text = ""
        if conversation_history:
            history_text = "\n\nPrevious conversation history:\n"
            for i, msg in enumerate(conversation_history):
                role = msg["role"].upper()
                content = msg["content"]
                history_text += f"{role}: {content}\n"
            history_text += "\nPlease remember this conversation history when responding to the new prompt below.\n"
        
        # Create full prompt with history context
        full_prompt = f"{history_text}\nCurrent request: {prompt}"
        
        options = ClaudeCodeOptions(
            allowed_tools=["*"],
            permission_mode='acceptEdits'
        )
        
        print(f"🔍 Sending prompt: {prompt}")
        print(f"📚 Conversation history length: {len(conversation_history)} messages")
        
        response_text = ""
        async for message in query(prompt=full_prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_text += block.text
                        print(f"CLAUDE: {block.text}")
            else:
                print(f"SDK: {message}")
        
        # Add both user prompt and assistant response to history
        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": response_text})
        
        return response_text
    
    return anyio.run(claude_query)

def test_conversation_memory():
    """
    Test if conversation history is properly maintained across SDK calls.
    
    This is a bulletproof test:
    1. Call 1: Mention unique number (42) - NO file output
    2. Call 2: Ask for the number - MUST write to file
    3. Call 3: Verify the file contents match
    
    PASS: If answer.txt contains "42"
    FAIL: If answer.txt contains anything else or doesn't exist
    """
    
    # Create clean test directory
    test_dir = tempfile.mkdtemp(prefix="topdog_history_test_")
    original_dir = os.getcwd()
    
    try:
        os.chdir(test_dir)
        print(f"🧪 Running conversation history test in: {test_dir}")
        
        # Initialize conversation history
        conversation_history = []
        
        # Call 1: Establish unique context (NO file output - this is key!)
        print("\n" + "="*60)
        print("CALL 1: Establishing context (no file output)")
        print("="*60)
        call1_prompt = "My favorite number is 42. Just acknowledge that you understand and tell me what you think about this number."
        response1 = run_claude_with_history(call1_prompt, conversation_history)
        
        # Call 2: Test memory retention (requires remembering 42)
        print("\n" + "="*60)
        print("CALL 2: Testing memory retention")
        print("="*60)
        call2_prompt = "What was my favorite number? Write ONLY that number to a file called answer.txt"
        response2 = run_claude_with_history(call2_prompt, conversation_history)
        
        # Call 3: Verification call
        print("\n" + "="*60)
        print("CALL 3: Verification")
        print("="*60)
        call3_prompt = "Read answer.txt and tell me: does it contain my original favorite number from our conversation?"
        response3 = run_claude_with_history(call3_prompt, conversation_history)
        
        # Analyze results
        print("\n" + "="*60)
        print("TEST RESULTS ANALYSIS")
        print("="*60)
        
        # Check if answer.txt exists
        if not os.path.exists("answer.txt"):
            print("❌ FAIL: answer.txt was not created")
            return False
        
        # Read the content
        with open("answer.txt", "r") as f:
            content = f.read().strip()
        
        print(f"📄 Contents of answer.txt: '{content}'")
        
        # Check if it contains 42
        if "42" in content:
            print("✅ PASS: Conversation history is working! Claude remembered the number 42")
            return True
        else:
            print(f"❌ FAIL: Expected '42', but got '{content}'")
            print("❌ This proves conversation history is NOT working")
            return False
        
    finally:
        # Clean up
        os.chdir(original_dir)
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up test directory: {test_dir}")

def main():
    """Run the standalone conversation history test"""
    print("🚀 Starting Standalone Conversation History Test")
    print("=" * 60)
    
    try:
        result = test_conversation_memory()
        
        print("\n" + "="*60)
        if result:
            print("🎉 CONVERSATION HISTORY TEST: PASSED")
            print("✅ Claude SDK is properly maintaining conversation history")
        else:
            print("💥 CONVERSATION HISTORY TEST: FAILED") 
            print("❌ Claude SDK is NOT maintaining conversation history")
            print("❌ Each call is independent - no memory between calls")
        print("="*60)
        
        return 0 if result else 1
        
    except Exception as e:
        print(f"💥 TEST ERROR: {e}")
        print("❌ Test could not complete")
        return 2

if __name__ == "__main__":
    sys.exit(main())