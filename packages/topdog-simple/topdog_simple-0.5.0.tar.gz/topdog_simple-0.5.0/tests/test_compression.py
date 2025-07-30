#!/usr/bin/env python3
"""Test history compression functionality"""

import sys
sys.path.insert(0, '.')

from topdog_simple.config import Config
from topdog_simple.history_compressor import HistoryCompressor

def test_compression():
    # Create config with low threshold for testing
    config = Config(max_history_messages=5, compression_target_size=2, compression_summary_length=2)
    compressor = HistoryCompressor(config)
    
    # Create fake conversation history (6 messages = should trigger compression)
    conversation_history = [
        {"role": "user", "content": "Hello, my name is Alice"},
        {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
        {"role": "user", "content": "I like cats"},
        {"role": "assistant", "content": "Cats are wonderful pets!"},
        {"role": "user", "content": "What's 2+2?"},
        {"role": "assistant", "content": "2+2 equals 4."}
    ]
    
    print(f"Original history: {len(conversation_history)} messages")
    for i, msg in enumerate(conversation_history):
        print(f"  {i+1}. {msg['role']}: {msg['content']}")
    
    # Test compression
    print(f"\nTesting compression (max={config.max_history_messages}, keep={config.compression_target_size})...")
    compressed = compressor.compress_history(conversation_history)
    
    print(f"\nCompressed history: {len(compressed)} messages")
    for i, msg in enumerate(compressed):
        print(f"  {i+1}. {msg['role']}: {msg['content']}")

if __name__ == "__main__":
    test_compression()