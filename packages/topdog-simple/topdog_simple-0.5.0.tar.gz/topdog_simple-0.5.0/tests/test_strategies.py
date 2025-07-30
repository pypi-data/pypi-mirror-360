#!/usr/bin/env python3
"""Test all prompt strategies"""

import sys
sys.path.insert(0, '.')

from topdog_simple.prompts import PROMPT_CATEGORIES
from topdog_simple.prompt_strategies import (
    CategoryRoundRobinStrategy, 
    RoundRobinStrategy, 
    BDDFocusedStrategy, 
    RandomStrategy, 
    WeightedBDDStrategy
)
from topdog_simple.strategy_metrics import StrategyMetrics

def test_all_strategies():
    """Test all strategies work and produce different distributions"""
    
    strategies = {
        "CategoryRoundRobin": CategoryRoundRobinStrategy(),
        "RoundRobin": RoundRobinStrategy(),
        "BDDFocused": BDDFocusedStrategy(),
        "Random": RandomStrategy(),
        "WeightedBDD": WeightedBDDStrategy()
    }
    
    metrics = StrategyMetrics()
    
    print("🧪 Testing All Prompt Strategies")
    print("=" * 50)
    
    # Test each strategy
    for name, strategy in strategies.items():
        print(f"\n🎯 Testing {name} Strategy:")
        
        # Run 14 prompts (2 full cycles for CategoryRoundRobin)
        for i in range(14):
            prompt, context = strategy.get_next_prompt(PROMPT_CATEGORIES)
            
            # Extract category for metrics
            category = "unknown"
            if ":" in context:
                parts = context.split(": ")
                if len(parts) > 1:
                    category = parts[1]
            elif context in PROMPT_CATEGORIES:
                category = context
            elif "BDD" in context:
                category = "bdd_testing"
            
            metrics.track_prompt(name, category, prompt)
            print(f"  {i+1:2d}. [{context}] {prompt[:50]}...")
        
        # Show strategy stats
        print(f"\n📊 {name} Results:")
        metrics.print_live_stats(name)
        
        distribution = metrics.get_category_distribution(name)
        print(f"   Category Distribution:")
        for cat, pct in distribution.items():
            print(f"     {cat}: {pct:.1f}%")
    
    print("\n" + "=" * 50)
    print("🏆 Strategy Comparison:")
    comparison = metrics.compare_strategies()
    
    if 'comparison_summary' in comparison:
        summary = comparison['comparison_summary']
        if 'highest_bdd_coverage' in summary:
            name, coverage = summary['highest_bdd_coverage']
            print(f"   Highest BDD Coverage: {name} ({coverage:.1f}%)")
        if 'average_bdd_coverage' in summary:
            print(f"   Average BDD Coverage: {summary['average_bdd_coverage']:.1f}%")

if __name__ == "__main__":
    test_all_strategies()