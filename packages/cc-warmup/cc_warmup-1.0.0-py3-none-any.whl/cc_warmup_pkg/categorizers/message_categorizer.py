"""Message categorizer for Claude Code usage patterns."""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime
from dataclasses import dataclass

@dataclass
class CategoryResult:
    """Result of message categorization."""
    category: str
    confidence: float
    keywords_matched: List[str]
    context_clues: List[str]


class MessageCategorizer:
    """Categorizes messages into development workflow categories using rule-based keyword matching."""
    
    # Category definitions with keywords and patterns
    CATEGORIES = {
        'planning': {
            'keywords': [
                'plan', 'planning', 'roadmap', 'outline', 'strategy', 'approach',
                'design', 'architecture', 'structure', 'organize', 'workflow',
                'requirements', 'spec', 'specification', 'feature', 'milestone',
                'scope', 'timeline', 'priority', 'task', 'todo', 'backlog',
                'brainstorm', 'idea', 'concept', 'draft', 'proposal'
            ],
            'context_patterns': [
                'how should', 'what if', 'let me think', 'i need to', 'we should',
                'the plan is', 'my approach', 'i want to', 'considering', 'thinking about'
            ],
            'weight_multipliers': {
                'high': ['plan', 'planning', 'roadmap', 'architecture', 'design', 'strategy'],
                'medium': ['approach', 'workflow', 'structure', 'requirements', 'feature'],
                'low': ['idea', 'concept', 'thinking', 'considering']
            }
        },
        'development': {
            'keywords': [
                'code', 'coding', 'implement', 'implementation', 'function', 'method',
                'class', 'module', 'library', 'framework', 'api', 'endpoint',
                'refactor', 'refactoring', 'optimize', 'performance', 'algorithm',
                'variable', 'parameter', 'return', 'import', 'export', 'package',
                'syntax', 'compile', 'build', 'deploy', 'version', 'commit',
                'merge', 'branch', 'repository', 'git', 'github',
                # Additional common programming terms
                'python', 'javascript', 'typescript', 'java', 'cpp', 'c++',
                'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'cloud',
                'database', 'sql', 'nosql', 'mongodb', 'postgres', 'mysql',
                'react', 'vue', 'angular', 'node', 'nodejs', 'npm', 'yarn',
                'webpack', 'babel', 'eslint', 'prettier', 'typescript',
                'express', 'fastapi', 'django', 'flask', 'spring', 'rails',
                'microservice', 'microservices', 'serverless', 'lambda',
                'config', 'configuration', 'environment', 'env', 'production'
            ],
            'context_patterns': [
                'let me code', 'i\'ll implement', 'the code', 'this function',
                'def ', 'class ', 'import ', 'from ', 'return ', 'if __name__',
                'git commit', 'git push', 'npm install', 'pip install'
            ],
            'weight_multipliers': {
                'high': ['implement', 'code', 'function', 'class', 'refactor', 'commit', 'python', 'javascript', 'docker'],
                'medium': ['module', 'library', 'api', 'algorithm', 'syntax', 'build', 'database', 'react', 'node', 'config'],
                'low': ['performance', 'optimize', 'version', 'package', 'environment', 'cloud']
            }
        },
        'debugging': {
            'keywords': [
                'debug', 'debugging', 'bug', 'error', 'exception', 'issue', 'problem',
                'fix', 'fixing', 'broken', 'crash', 'fail', 'failure', 'stack trace',
                'traceback', 'log', 'logging', 'console', 'output', 'stderr', 'stdout',
                'investigate', 'troubleshoot', 'diagnose', 'analyze', 'check',
                'warning', 'alert', 'critical', 'fatal', 'panic'
            ],
            'context_patterns': [
                'what\'s wrong', 'something\'s broken', 'not working', 'throws error',
                'getting error', 'stack trace', 'error message', 'exception occurred',
                'let me debug', 'i\'ll investigate', 'checking logs', 'found the issue'
            ],
            'weight_multipliers': {
                'high': ['debug', 'error', 'bug', 'exception', 'crash', 'fix'],
                'medium': ['issue', 'problem', 'broken', 'failure', 'investigate'],
                'low': ['warning', 'check', 'analyze', 'log']
            }
        },
        'testing': {
            'keywords': [
                'test', 'testing', 'tests', 'unit test', 'integration test', 'e2e',
                'assert', 'assertion', 'mock', 'mocking', 'stub', 'spy', 'fixture',
                'pytest', 'jest', 'mocha', 'jasmine', 'selenium', 'coverage',
                'tdd', 'bdd', 'scenario', 'spec', 'validate', 'validation',
                'verify', 'verification', 'benchmark', 'performance test'
            ],
            'context_patterns': [
                'write test', 'test case', 'test suite', 'running tests',
                'test passes', 'test fails', 'assert that', 'should return',
                'expect to', 'testing whether', 'let me test', 'i\'ll verify'
            ],
            'weight_multipliers': {
                'high': ['test', 'testing', 'assert', 'verify', 'validate'],
                'medium': ['mock', 'coverage', 'scenario', 'benchmark'],
                'low': ['spec', 'fixture', 'stub']
            }
        }
    }
    
    MIN_CONFIDENCE_THRESHOLD = 0.3
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the message categorizer."""
        self.logger = logger or logging.getLogger(__name__)
        
        # Pre-compile keyword sets for faster lookup
        self._compiled_keywords = {}
        self._keyword_to_categories = {}  # For O(1) keyword lookups
        self._weight_map = {}  # For O(1) weight lookups
        
        for category, config in self.CATEGORIES.items():
            self._compiled_keywords[category] = {
                'keywords': set(config['keywords']),
                'context_patterns': config['context_patterns'],
                'weight_multipliers': config['weight_multipliers']
            }
            
            # Build reverse keyword lookup map
            for keyword in config['keywords']:
                if keyword not in self._keyword_to_categories:
                    self._keyword_to_categories[keyword] = []
                self._keyword_to_categories[keyword].append(category)
                
                # Build weight lookup map
                weight = 1.0
                for weight_level, weight_keywords in config['weight_multipliers'].items():
                    if keyword in weight_keywords:
                        if weight_level == 'high':
                            weight = 2.0
                        elif weight_level == 'medium':
                            weight = 1.5
                        elif weight_level == 'low':
                            weight = 0.8
                        break
                self._weight_map[(category, keyword)] = weight
    
    def categorize_message(self, message_data: Dict[str, Any]) -> Optional[CategoryResult]:
        """
        Categorize a single message based on its content.
        
        Args:
            message_data: JSONL message entry with content and metadata
            
        Returns:
            CategoryResult if confidence >= threshold, None otherwise
        """
        # Extract text content from message
        content = self._extract_message_content(message_data)
        if not content:
            return None
        
        # Normalize content for analysis
        normalized_content = content.lower()
        
        # Score each category
        category_scores = {}
        for category in self.CATEGORIES.keys():
            score_result = self._calculate_category_score(category, normalized_content)
            if score_result[0] > 0:  # Only include categories with positive scores
                category_scores[category] = score_result
        
        # Find best category
        if not category_scores:
            return None
        
        best_category = max(category_scores.keys(), key=lambda cat: category_scores[cat][0])
        confidence, keywords_matched, context_clues = category_scores[best_category]
        
        # Check minimum confidence threshold
        if confidence < self.MIN_CONFIDENCE_THRESHOLD:
            return None
        
        return CategoryResult(
            category=best_category,
            confidence=confidence,
            keywords_matched=keywords_matched,
            context_clues=context_clues
        )
    
    def categorize_messages_batch(self, messages: List[Dict[str, Any]]) -> Dict[str, List[CategoryResult]]:
        """
        Categorize multiple messages efficiently.
        
        Args:
            messages: List of JSONL message entries
            
        Returns:
            Dict mapping category names to lists of CategoryResult objects
        """
        results = {category: [] for category in self.CATEGORIES.keys()}
        
        for message in messages:
            category_result = self.categorize_message(message)
            if category_result:
                results[category_result.category].append(category_result)
        
        return results
    
    def _extract_message_content(self, message_data: Dict[str, Any]) -> str:
        """Extract text content from message data."""
        content_parts = []
        
        # Check for Claude Code JSONL format first (has 'message' field)
        if 'message' in message_data:
            message_content = message_data['message']
            if isinstance(message_content, str):
                content_parts.append(message_content)
            elif isinstance(message_content, dict):
                # Handle nested message structure
                if 'content' in message_content:
                    if isinstance(message_content['content'], str):
                        content_parts.append(message_content['content'])
                    elif isinstance(message_content['content'], list):
                        for item in message_content['content']:
                            if isinstance(item, dict) and 'text' in item:
                                content_parts.append(item['text'])
                            elif isinstance(item, str):
                                content_parts.append(item)
                # Also check for direct text in message dict
                for text_field in ['text', 'body']:
                    if text_field in message_content and isinstance(message_content[text_field], str):
                        content_parts.append(message_content[text_field])
        
        # Try standard content field (for other formats)
        if 'content' in message_data:
            if isinstance(message_data['content'], str):
                content_parts.append(message_data['content'])
            elif isinstance(message_data['content'], list):
                for item in message_data['content']:
                    if isinstance(item, dict) and 'text' in item:
                        content_parts.append(item['text'])
                    elif isinstance(item, str):
                        content_parts.append(item)
        
        # Check for any other text fields
        for key in ['text', 'body']:
            if key in message_data and isinstance(message_data[key], str):
                content_parts.append(message_data[key])
        
        return ' '.join(content_parts)
    
    def _calculate_category_score(self, category: str, content: str) -> Tuple[float, List[str], List[str]]:
        """Calculate score for a specific category using optimized set operations."""
        config = self._compiled_keywords[category]
        
        # Extract words from content for set intersection
        content_words = set(content.split())
        
        # Find keyword matches using set intersection (O(1) lookups)
        matched_keywords = config['keywords'].intersection(content_words)
        keywords_matched = list(matched_keywords)
        
        # Calculate keyword score using pre-computed weights
        keyword_score = 0.0
        for keyword in matched_keywords:
            weight = self._weight_map.get((category, keyword), 1.0)
            keyword_score += weight
        
        # Find context pattern matches
        context_clues = []
        context_score = 0.0
        
        for pattern in config['context_patterns']:
            if pattern in content:
                context_clues.append(pattern)
                context_score += 1.0
        
        # Calculate final confidence score
        total_score = keyword_score + (context_score * 0.5)  # Context patterns worth half
        
        # Calculate keyword density with sub-linear scaling to avoid penalizing short messages
        word_count = len(content.split())
        if word_count > 0:
            keyword_density = len(keywords_matched) / word_count
            # Use square root scaling to boost confidence for keyword-dense short messages
            density_factor = min(1.0, (keyword_density * 10) ** 0.5)
            confidence = total_score * density_factor
        else:
            confidence = total_score
        
        # Cap confidence at 1.0
        confidence = min(1.0, confidence)
        
        return confidence, keywords_matched, context_clues
    
    def get_category_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics about the categorization system."""
        stats = {}
        
        for category, config in self.CATEGORIES.items():
            stats[category] = {
                'total_keywords': len(config['keywords']),
                'total_context_patterns': len(config['context_patterns']),
                'weight_distribution': {
                    level: len(keywords) 
                    for level, keywords in config['weight_multipliers'].items()
                }
            }
        
        return stats