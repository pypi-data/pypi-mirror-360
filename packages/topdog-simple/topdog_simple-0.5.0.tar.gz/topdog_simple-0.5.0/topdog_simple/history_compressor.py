# PSEUDOCODE: History Compression Utility
#
# FUNCTION CompressHistory(conversation_history, config)
# BEGIN
#     IF length(conversation_history) >= config.max_history_messages THEN
#         old_messages = first (total - target) messages from conversation_history
#         recent_messages = last target messages from conversation_history
#         
#         summary_prompt = "Summarize this conversation history in " + config.summary_length + " sentences: " + old_messages
#         summary = CallClaude(summary_prompt)
#         
#         new_history = [{"role": "system", "content": "SUMMARY: " + summary}] + recent_messages
#         RETURN new_history
#     ELSE
#         RETURN conversation_history
#     ENDIF
# END

import anyio
from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock

class HistoryCompressor:
    """Handles conversation history compression"""
    
    def __init__(self, config):
        self.config = config
    
    async def _get_summary(self, old_messages):
        """Get summary of old messages using Claude"""
        # Build summary prompt
        history_text = ""
        for msg in old_messages:
            role = msg["role"].upper()
            content = msg["content"]
            history_text += f"{role}: {content}\n"
        
        summary_prompt = f"Summarize this conversation history in {self.config.compression_summary_length} sentences. Focus on key topics, decisions, and important information:\n\n{history_text}"
        
        options = ClaudeCodeOptions(
            allowed_tools=["*"],
            permission_mode='acceptEdits'
        )
        
        summary_text = ""
        async for message in query(prompt=summary_prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        summary_text += block.text
        
        return summary_text.strip()
    
    def compress_history(self, conversation_history):
        """Compress conversation history if needed"""
        if not self.config.should_compress_history(len(conversation_history)):
            return conversation_history
        
        print(f"🗜️  Compressing history: {len(conversation_history)} → {self.config.compression_target_size} + summary")
        
        # Split messages
        keep_count = self.config.compression_target_size
        old_messages = conversation_history[:-keep_count] if keep_count > 0 else conversation_history
        recent_messages = conversation_history[-keep_count:] if keep_count > 0 else []
        
        # Get summary
        try:
            summary = anyio.run(self._get_summary, old_messages)
            
            # Create new history with summary + recent messages
            compressed_history = [
                {"role": "system", "content": f"CONVERSATION SUMMARY: {summary}"}
            ] + recent_messages
            
            print(f"✅ History compressed: Summary + {len(recent_messages)} recent messages")
            return compressed_history
            
        except Exception as e:
            print(f"⚠️  Compression failed: {e}, keeping original history")
            return conversation_history