# PSEUDOCODE: Prompt Strategy Pattern
#
# CLASS PromptStrategy:
#   METHOD get_next_prompt(prompt_categories): ABSTRACT
#   METHOD get_strategy_name(): RETURN strategy name
#   METHOD reset(): RESET internal state
# END CLASS
#
# CLASS RoundRobinStrategy(PromptStrategy):
#   VARIABLE index = 0
#   METHOD get_next_prompt(): RETURN prompts[index], INCREMENT index
# END CLASS
#
# CLASS CategoryRoundRobinStrategy(PromptStrategy):
#   VARIABLE category_index = 0
#   METHOD get_next_prompt(): PICK random from current category, MOVE to next category
# END CLASS
#
# CLASS BDDFocusedStrategy(PromptStrategy):
#   VARIABLE counter = 0
#   METHOD get_next_prompt(): IF counter MOD 2 = 0 THEN BDD ELSE other category
# END CLASS

import random
from abc import ABC, abstractmethod

class PromptStrategy(ABC):
    """Abstract base class for prompt selection strategies"""
    
    @abstractmethod
    def get_next_prompt(self, prompt_categories):
        """Get the next prompt based on strategy"""
        pass
    
    @abstractmethod
    def get_strategy_name(self):
        """Return the name of this strategy"""
        pass
    
    def reset(self):
        """Reset strategy state"""
        pass

class RoundRobinStrategy(PromptStrategy):
    """Ask all prompts in order, cycling through"""
    
    def __init__(self):
        self.index = 0
        self.all_prompts = []
        self.initialized = False
    
    def _initialize(self, prompt_categories):
        if not self.initialized:
            # Flatten all prompts
            for category_prompts in prompt_categories.values():
                self.all_prompts.extend(category_prompts)
            self.initialized = True
    
    def get_next_prompt(self, prompt_categories):
        self._initialize(prompt_categories)
        
        current_prompt = self.all_prompts[self.index]
        self.index = (self.index + 1) % len(self.all_prompts)
        
        return current_prompt, f"RoundRobin ({self.index}/{len(self.all_prompts)})"
    
    def get_strategy_name(self):
        return "RoundRobin"
    
    def reset(self):
        self.index = 0

class CategoryRoundRobinStrategy(PromptStrategy):
    """Round robin through categories, random prompt within each category"""
    
    def __init__(self):
        self.category_index = 0
        self.category_names = []
        self.initialized = False
    
    def _initialize(self, prompt_categories):
        if not self.initialized:
            self.category_names = list(prompt_categories.keys())
            self.initialized = True
    
    def get_next_prompt(self, prompt_categories):
        self._initialize(prompt_categories)
        
        current_category = self.category_names[self.category_index]
        category_prompts = prompt_categories[current_category]
        selected_prompt = random.choice(category_prompts)
        
        # Move to next category
        self.category_index = (self.category_index + 1) % len(self.category_names)
        
        return selected_prompt, f"CategoryRR: {current_category}"
    
    def get_strategy_name(self):
        return "CategoryRoundRobin"
    
    def reset(self):
        self.category_index = 0

class BDDFocusedStrategy(PromptStrategy):
    """Every other prompt is BDD, others are random from non-BDD categories"""
    
    def __init__(self):
        self.counter = 0
        self.non_bdd_categories = []
        self.initialized = False
    
    def _initialize(self, prompt_categories):
        if not self.initialized:
            self.non_bdd_categories = [k for k in prompt_categories.keys() if k != 'bdd_testing']
            self.initialized = True
    
    def get_next_prompt(self, prompt_categories):
        self._initialize(prompt_categories)
        
        if self.counter % 2 == 0:
            # BDD turn
            selected_prompt = random.choice(prompt_categories['bdd_testing'])
            context = "BDD-Focus"
        else:
            # Non-BDD turn
            random_category = random.choice(self.non_bdd_categories)
            selected_prompt = random.choice(prompt_categories[random_category])
            context = f"Non-BDD: {random_category}"
        
        self.counter += 1
        return selected_prompt, context
    
    def get_strategy_name(self):
        return "BDDFocused"
    
    def reset(self):
        self.counter = 0

class RandomStrategy(PromptStrategy):
    """Completely random prompt selection from all categories"""
    
    def __init__(self):
        self.all_prompts_with_categories = []
        self.initialized = False
    
    def _initialize(self, prompt_categories):
        if not self.initialized:
            for category, prompts in prompt_categories.items():
                for prompt in prompts:
                    self.all_prompts_with_categories.append((prompt, category))
            self.initialized = True
    
    def get_next_prompt(self, prompt_categories):
        self._initialize(prompt_categories)
        
        selected_prompt, category = random.choice(self.all_prompts_with_categories)
        return selected_prompt, f"Random: {category}"
    
    def get_strategy_name(self):
        return "Random"

class WeightedBDDStrategy(PromptStrategy):
    """40% chance BDD, 60% chance other categories"""
    
    def __init__(self):
        self.non_bdd_categories = []
        self.initialized = False
    
    def _initialize(self, prompt_categories):
        if not self.initialized:
            self.non_bdd_categories = [k for k in prompt_categories.keys() if k != 'bdd_testing']
            self.initialized = True
    
    def get_next_prompt(self, prompt_categories):
        self._initialize(prompt_categories)
        
        if random.random() < 0.4:  # 40% chance BDD
            selected_prompt = random.choice(prompt_categories['bdd_testing'])
            context = "Weighted-BDD (40%)"
        else:
            random_category = random.choice(self.non_bdd_categories)
            selected_prompt = random.choice(prompt_categories[random_category])
            context = f"Weighted-Other (60%): {random_category}"
        
        return selected_prompt, context
    
    def get_strategy_name(self):
        return "WeightedBDD"