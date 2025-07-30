# PSEUDOCODE: Configuration Management
#
# CLASS Config:
#   CONSTANTS:
#     MAX_HISTORY_MESSAGES = 30
#     COMPRESSION_TARGET_SIZE = 5
#     COMPRESSION_SUMMARY_LENGTH = 3
#   END CONSTANTS
#
#   METHOD __init__(max_history=30, compression_target=5, summary_length=3):
#     SET self.max_history_messages = max_history
#     SET self.compression_target_size = compression_target  
#     SET self.compression_summary_length = summary_length
#   END METHOD
# END CLASS

class Config:
    """Configuration settings for topdog-simple"""
    
    def __init__(self, 
                 max_history_messages=30,
                 compression_target_size=5, 
                 compression_summary_length=3):
        """
        Initialize configuration
        
        Args:
            max_history_messages: Trigger compression after this many messages
            compression_target_size: Keep this many recent messages after compression
            compression_summary_length: Target sentences for history summary
        """
        self.max_history_messages = max_history_messages
        self.compression_target_size = compression_target_size
        self.compression_summary_length = compression_summary_length
    
    def should_compress_history(self, history_length):
        """Check if history needs compression"""
        return history_length >= self.max_history_messages
    
    def get_compression_info(self):
        """Get compression settings info"""
        return {
            'max_messages': self.max_history_messages,
            'keep_recent': self.compression_target_size,
            'summary_sentences': self.compression_summary_length
        }