# PSEUDOCODE: Claude Command Utilities
#
# FUNCTION run_claude(prompt, is_first_run):
#   IMPORT claude SDK
#   CALL SDK with prompt
#   STREAM results
# END FUNCTION

import anyio
from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock
from .response_formatter import ResponseFormatter
from .history_compressor import HistoryCompressor

def run_claude(prompt, conversation_history, config=None):
    """Run Claude using the Python SDK with conversation history"""
    
    async def claude_query():
        # Compress history if needed
        if config:
            compressor = HistoryCompressor(config)
            working_history = compressor.compress_history(conversation_history)
        else:
            working_history = conversation_history
        
        # Build conversation history for context
        history_text = ""
        if working_history:
            history_text = "\n\nPrevious conversation history:\n"
            for msg in working_history:
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
        
        print(f"🚀 Running Claude with prompt: {prompt}")
        print(f"📚 Conversation history: {len(conversation_history)} messages")
        if config and len(conversation_history) != len(working_history):
            print(f"🗜️  Using compressed history: {len(working_history)} messages")
        
        formatter = ResponseFormatter()
        response_text = ""
        sdk_messages = []
        
        async for message in query(prompt=full_prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_text += block.text
            else:
                sdk_messages.append(message)
        
        # Format and display the output cleanly
        formatter.format_output(prompt, response_text, sdk_messages)
        
        # Add user prompt and assistant response to history
        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": response_text})
        
        print(f"✓ Claude finished successfully")
        return response_text
        
    return anyio.run(claude_query)