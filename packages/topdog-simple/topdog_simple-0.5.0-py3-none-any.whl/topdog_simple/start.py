#!/usr/bin/env python3

# PSEUDOCODE: Main Loop with Categorized Development Prompts
# 
# DEFINE prompt_categories = {
#   "validation_proof": ["Are you sure features completed?", "What should you work on next?", ...]
#   "api_data_integration": ["Did you connect UI to API?", "Is data real and correct?", ...]
#   "database_infrastructure": ["Did you do migrations?", "Did you model domain?", ...]
#   "testing_apis": ["What data model tests?", "Did you create correct APIs?", ...]
#   "config_environment": ["Need API keys?", "Any fake keys?", "Can you run app?", ...]
#   "status_progress": ["What's current status?"]
#   "bdd_testing": ["Do you see BDD features?", "Run behave commands?", "Fail fast until green?", ...]
# }
# FLATTEN all categories into prompts array
# SET index = 0
# SET conversation_history = []
# SET config = Config(max_history=30, compression_target=5, summary_length=3)
# 
# WHILE forever:
#   GET current_prompt from prompts[index]
#   CALL run_claude(current_prompt, conversation_history, config)
#   SET index = next index (wrap around)
#   WAIT 3 seconds or pause for debugging
# END WHILE

import time
import sys
import os
import json
from .llmutil import run_claude
from .config import Config
from .prompts import PROMPT_CATEGORIES
from .prompt_strategies import CategoryRoundRobinStrategy, RoundRobinStrategy, BDDFocusedStrategy, RandomStrategy, WeightedBDDStrategy
from .strategy_metrics import StrategyMetrics

def setup_claude_config():
    """Set up Claude Code configuration files with wide open permissions"""
    
    # Create .claude directory if it doesn't exist
    os.makedirs('.claude', exist_ok=True)
    
    # Create CLAUDE.md with project instructions
    claude_md_content = """# TopDog Simple Project

## Project Purpose
This is a test project for topdog-simple - an infinite loop that drives Claude Code.

## Permissions
- Full file system access granted
- All bash commands allowed
- All tools enabled

## Instructions
- Feel free to create, edit, and manage any files
- Run tests and builds as needed
- Make improvements and fix issues
- Work autonomously with full permissions
"""
    
    with open('.claude/CLAUDE.md', 'w') as f:
        f.write(claude_md_content)
    
    # Create settings.json with wide open permissions
    settings = {
        "permissions": {
            "allow": [
                "*",
                "Write(*)",
                "Edit(*)", 
                "Bash(*)",
                "Read(*)",
                "MultiEdit(*)",
                "Glob(*)",
                "Grep(*)",
                "LS(*)",
                "Task(*)"
            ]
        }
    }
    
    with open('.claude/settings.json', 'w') as f:
        json.dump(settings, f, indent=2)
    
    print(f"\033[1;36mClaude configuration files created:\033[0m")
    print(f"  📝 .claude/CLAUDE.md")
    print(f"  ⚙️  .claude/settings.json (wide open permissions)")

def main(strategy_name="CategoryRoundRobin"):
    # Set up Claude configuration on first run
    setup_claude_config()
    
    # Initialize configuration (can be customized here)
    config = Config(
        max_history_messages=30,    # Compress after 30 messages
        compression_target_size=5,  # Keep 5 recent messages
        compression_summary_length=3 # 3 sentence summary
    )
    
    # Initialize strategy (can be easily swapped)
    strategies = {
        "CategoryRoundRobin": CategoryRoundRobinStrategy(),
        "RoundRobin": RoundRobinStrategy(),
        "BDDFocused": BDDFocusedStrategy(),
        "Random": RandomStrategy(),
        "WeightedBDD": WeightedBDDStrategy()
    }
    
    strategy = strategies.get(strategy_name, CategoryRoundRobinStrategy())
    metrics = StrategyMetrics()
    
    print(f"\033[1;32m🚀 Using Claude Code SDK\033[0m")
    print(f"\033[1;36m⚙️  Config: Max history={config.max_history_messages}, Keep recent={config.compression_target_size}\033[0m")
    print(f"\033[1;35m🎯 Strategy: {strategy.get_strategy_name()}\033[0m")
    
    conversation_history = []  # Initialize conversation history
    
    try:
        prompt_count = 0
        while True:
            # Get next prompt from strategy
            current_prompt, context = strategy.get_next_prompt(PROMPT_CATEGORIES)
            
            # Extract category from context for metrics
            category = context.split(":")[0].strip() if ":" in context else context
            if category.startswith("CategoryRR"):
                category = context.split(": ")[1] if ": " in context else "unknown"
            elif category.startswith("Non-BDD"):
                category = context.split(": ")[1] if ": " in context else "non-bdd"
            elif category.startswith("Random"):
                category = context.split(": ")[1] if ": " in context else "random"
            elif category.startswith("Weighted"):
                category = context.split(": ")[1] if ": " in context else "weighted"
            
            prompt_count += 1
            
            print(f"\n\033[1;32m{'='*60}\033[0m")
            print(f"\033[1;34mPrompt #{prompt_count} [{context}]\033[0m")
            print(f"\033[1;37m{current_prompt}\033[0m")
            print(f"\033[1;32m{'='*60}\033[0m")
            
            # Track metrics
            metrics.track_prompt(strategy.get_strategy_name(), category, current_prompt)
            
            # Run Claude
            run_claude(current_prompt, conversation_history, config)
            
            # Show live stats every 5 prompts
            if prompt_count % 5 == 0:
                metrics.print_live_stats(strategy.get_strategy_name())
            
            # Add human pause every 10 prompts for debugging
            if prompt_count % 10 == 0:
                print(f"\033[1;33m\n🔍 Debugging pause (every 10 prompts): Press Enter to continue or Ctrl+C to stop...\033[0m")
                input()
            
            print(f"\033[1;33m\nClaude finished! Moving to next prompt in 3 seconds...\033[0m")
            time.sleep(3)
            
    except KeyboardInterrupt:
        print(f"\033[1;31m\nLoop stopped by user\033[0m")
        
        # Export final metrics
        print(f"\033[1;36m\n📊 Final Strategy Metrics:\033[0m")
        metrics.print_live_stats(strategy.get_strategy_name())
        
        # Export to file
        filename = metrics.export_metrics()
        print(f"\033[1;36m📄 Metrics exported to: {filename}\033[0m")
        
        sys.exit(0)

if __name__ == "__main__":
    main()