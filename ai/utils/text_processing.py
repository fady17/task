# ai/utils/text_processing.py
"""
Utility classes for text processing, including fuzzy matching and intent extraction.
These are pure functions and classes with no external dependencies besides standard libraries.
"""

import re
from typing import List, Optional, Dict
from difflib import SequenceMatcher

class FuzzyMatcher:
    @staticmethod
    def similarity(a: str, b: str) -> float:
        """Calculate similarity between two strings (0.0 to 1.0)"""
        return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()
    
    @staticmethod
    def find_best_list_match(query: str, all_lists: List[Dict], threshold: float = 0.5) -> Optional[Dict]:
        """Find the best matching list using fuzzy search"""
        if not query or not all_lists:
            return None
        
        query = query.strip().lower()
        best_match = None
        best_score = 0.0
        
        for lst in all_lists:
            title = lst.get('title', '').strip().lower()
            
            if query == title or query in title or title in query:
                return lst
            
            score = FuzzyMatcher.similarity(query, title)
            if score >= threshold and score > best_score:
                best_match = lst
                best_score = score
        
        return best_match
    
    @staticmethod
    def find_best_item_match(query: str, all_lists: List[Dict], threshold: float = 0.5) -> Optional[tuple]:
        """Find best matching item. Returns (list_dict, item_dict) or None"""
        if not query or not all_lists:
            return None
        
        query = query.strip().lower()
        best_match = None
        best_score = 0.0
        
        for lst in all_lists:
            for item in lst.get('items', []):
                title = item.get('title', '').strip().lower()
                
                if query == title or query in title or title in query:
                    return (lst, item)
                
                score = FuzzyMatcher.similarity(query, title)
                if score >= threshold and score > best_score:
                    best_match = (lst, item)
                    best_score = score
        
        return best_match

class IntentAnalyzer:
    @staticmethod
    def extract_list_name(prompt: str) -> Optional[str]:
        """Extract list name from various prompt patterns"""
        patterns = [
            r"(?:create|make).*?(?:list|todo).*?(?:called|named)\s+['\"]([^'\"]+)['\"]",
            r"(?:create|make).*?(?:list|todo).*?(?:called|named)\s+(\w+(?:\s+\w+)*)",
            r"(?:delete|remove).*?(?:list|todo).*?['\"]([^'\"]+)['\"]",
            r"(?:delete|remove).*?(?:the\s+)?(\w+(?:\s+\w+)*?)(?:\s+list|\s+todo|\s*$)",
            r"(?:in|on|from|to)(?:\s+the)?\s+['\"]([^'\"]+)['\"]",
            r"(?:in|on|from|to)(?:\s+the)?\s+(\w+(?:\s+\w+)*?)(?:\s+list|\s+todo|\s*$)",
            r"(?:the\s+)?(\w+(?:\s+\w+)*)\s+list",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if name.lower() not in ['new', 'this', 'that', 'my', 'the', 'a', 'an']:
                    return name
        return None
    
    @staticmethod
    def extract_item_name(prompt: str) -> Optional[str]:
        """Extract item name from various prompt patterns"""
        patterns = [
            r"(?:add|create).*?['\"]([^'\"]+)['\"]",
            r"(?:add|create)\s+(.+?)(?:\s+to|\s+in|\s*$)",
            r"(?:mark|complete|done).*?['\"]([^'\"]+)['\"]",
            r"(?:mark|complete|done)\s+(.+?)(?:\s+as|\s+to|\s*$)",
            r"(?:delete|remove).*?(?:item|todo).*?['\"]([^'\"]+)['\"]",
            r"(?:delete|remove).*?(?:item|todo)\s+(.+?)(?:\s+from|\s*$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 0:
                    return name
        return None