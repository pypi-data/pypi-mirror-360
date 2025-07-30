# PSEUDOCODE: Strategy Metrics and Measurement
#
# CLASS StrategyMetrics:
#   VARIABLE strategy_stats = {}
#   
#   METHOD track_prompt(strategy_name, category, prompt):
#     INCREMENT category count for strategy
#     LOG prompt usage
#   END METHOD
#   
#   METHOD get_category_distribution(strategy_name):
#     RETURN percentage breakdown by category
#   END METHOD
#   
#   METHOD get_bdd_coverage(strategy_name):
#     RETURN percentage of BDD prompts used
#   END METHOD
#   
#   METHOD compare_strategies():
#     RETURN comparison report
#   END METHOD
# END CLASS

import time
import json
from collections import defaultdict, Counter
from typing import Dict, List, Tuple

class StrategyMetrics:
    """Track and measure effectiveness of different prompt strategies"""
    
    def __init__(self):
        self.strategy_stats = defaultdict(lambda: {
            'prompts_used': [],
            'categories_count': defaultdict(int),
            'start_time': time.time(),
            'total_prompts': 0,
            'session_data': []
        })
    
    def track_prompt(self, strategy_name: str, category: str, prompt: str):
        """Track a prompt usage for a strategy"""
        stats = self.strategy_stats[strategy_name]
        
        # Record the prompt usage
        timestamp = time.time()
        stats['prompts_used'].append({
            'prompt': prompt,
            'category': category,
            'timestamp': timestamp
        })
        
        # Update counters
        stats['categories_count'][category] += 1
        stats['total_prompts'] += 1
        
        # Track session data
        stats['session_data'].append({
            'prompt_number': stats['total_prompts'],
            'category': category,
            'timestamp': timestamp
        })
    
    def get_category_distribution(self, strategy_name: str) -> Dict[str, float]:
        """Get percentage distribution of categories for a strategy"""
        stats = self.strategy_stats[strategy_name]
        total = stats['total_prompts']
        
        if total == 0:
            return {}
        
        distribution = {}
        for category, count in stats['categories_count'].items():
            distribution[category] = (count / total) * 100
        
        return distribution
    
    def get_bdd_coverage(self, strategy_name: str) -> float:
        """Get percentage of BDD prompts used"""
        stats = self.strategy_stats[strategy_name]
        total = stats['total_prompts']
        bdd_count = stats['categories_count']['bdd_testing']
        
        if total == 0:
            return 0.0
        
        return (bdd_count / total) * 100
    
    def get_strategy_summary(self, strategy_name: str) -> Dict:
        """Get comprehensive summary for a strategy"""
        stats = self.strategy_stats[strategy_name]
        
        if stats['total_prompts'] == 0:
            return {'error': 'No data recorded for this strategy'}
        
        runtime = time.time() - stats['start_time']
        distribution = self.get_category_distribution(strategy_name)
        bdd_coverage = self.get_bdd_coverage(strategy_name)
        
        return {
            'strategy_name': strategy_name,
            'total_prompts': stats['total_prompts'],
            'runtime_seconds': runtime,
            'prompts_per_minute': (stats['total_prompts'] / runtime) * 60 if runtime > 0 else 0,
            'category_distribution': distribution,
            'bdd_coverage_percent': bdd_coverage,
            'categories_hit': len(stats['categories_count']),
            'most_used_category': max(stats['categories_count'].items(), key=lambda x: x[1])[0] if stats['categories_count'] else None
        }
    
    def compare_strategies(self) -> Dict:
        """Compare all tracked strategies"""
        comparison = {
            'strategies': {},
            'comparison_summary': {}
        }
        
        # Get summary for each strategy
        for strategy_name in self.strategy_stats.keys():
            comparison['strategies'][strategy_name] = self.get_strategy_summary(strategy_name)
        
        # Calculate comparison metrics
        if len(comparison['strategies']) > 1:
            bdd_coverages = {name: data['bdd_coverage_percent'] 
                           for name, data in comparison['strategies'].items() 
                           if 'bdd_coverage_percent' in data}
            
            if bdd_coverages:
                comparison['comparison_summary'] = {
                    'highest_bdd_coverage': max(bdd_coverages.items(), key=lambda x: x[1]),
                    'lowest_bdd_coverage': min(bdd_coverages.items(), key=lambda x: x[1]),
                    'average_bdd_coverage': sum(bdd_coverages.values()) / len(bdd_coverages)
                }
        
        return comparison
    
    def export_metrics(self, filename: str = None):
        """Export metrics to JSON file"""
        if filename is None:
            filename = f"strategy_metrics_{int(time.time())}.json"
        
        export_data = {
            'export_timestamp': time.time(),
            'strategies': {}
        }
        
        for strategy_name in self.strategy_stats.keys():
            export_data['strategies'][strategy_name] = self.get_strategy_summary(strategy_name)
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename
    
    def print_live_stats(self, strategy_name: str):
        """Print live statistics for a strategy"""
        summary = self.get_strategy_summary(strategy_name)
        
        if 'error' in summary:
            print(f"📊 {strategy_name}: {summary['error']}")
            return
        
        print(f"📊 {strategy_name} Stats:")
        print(f"   Prompts: {summary['total_prompts']}")
        print(f"   BDD Coverage: {summary['bdd_coverage_percent']:.1f}%")
        print(f"   Categories Hit: {summary['categories_hit']}")
        if summary['most_used_category']:
            print(f"   Most Used: {summary['most_used_category']}")
    
    def reset_strategy(self, strategy_name: str):
        """Reset metrics for a specific strategy"""
        if strategy_name in self.strategy_stats:
            del self.strategy_stats[strategy_name]
    
    def reset_all(self):
        """Reset all metrics"""
        self.strategy_stats.clear()