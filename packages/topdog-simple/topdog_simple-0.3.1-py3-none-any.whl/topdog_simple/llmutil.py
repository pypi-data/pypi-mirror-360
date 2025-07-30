# PSEUDOCODE: Claude Command Utilities
#
# FUNCTION run_claude(prompt, is_first_run):
#   IMPORT claude SDK
#   CALL SDK with prompt
#   STREAM results
# END FUNCTION

import anyio
from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock

def run_claude(prompt, is_first_run):
    """Run Claude using the Python SDK"""
    
    async def claude_query():
        options = ClaudeCodeOptions(
            allowed_tools=["*"],
            permission_mode='acceptEdits'
        )
        
        print(f"🚀 Running Claude with prompt: {prompt}")
        
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"CLAUDE: {block.text}")
            else:
                print(f"SDK: {message}")
                
        print(f"✓ Claude finished successfully")
        
    anyio.run(claude_query)