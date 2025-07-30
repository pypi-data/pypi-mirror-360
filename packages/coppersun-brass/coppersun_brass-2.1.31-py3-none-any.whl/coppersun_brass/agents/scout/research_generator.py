#!/usr/bin/env python3
"""
Research Query Generator for Scout Agent
Generates structured research queries for AI agents to execute
"""

import re
import json
import hashlib
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum

from .todo_detector import TODOFinding

class ResearchType(Enum):
    """Types of research that can be requested"""
    API_INTEGRATION = "api_integration"
    ALGORITHM_OPTIMIZATION = "algorithm_optimization"
    SECURITY_PATTERNS = "security_patterns"
    PERFORMANCE_TUNING = "performance_tuning"
    ARCHITECTURE_PATTERNS = "architecture_patterns"
    LIBRARY_COMPARISON = "library_comparison"
    CODE_EXAMPLES = "code_examples"
    BEST_PRACTICES = "best_practices"
    DEBUGGING_SOLUTIONS = "debugging_solutions"
    DEPLOYMENT_STRATEGIES = "deployment_strategies"

@dataclass
class ResearchQuery:
    """Structured research query for AI agents"""
    query_id: str
    type: str  # "research_query"
    priority: int  # 0-100 priority score
    query: str  # Human-readable research question
    source: str  # "scout"
    linked_todo: str  # Reference to original TODO finding
    confidence: float  # 0.0-1.0 confidence in research relevance
    research_type: ResearchType
    tags: List[str]
    metadata: Dict
    created_at: str
    
    def to_dcp_observation(self) -> Dict:
        """Convert to DCP observation format"""
        return {
            "id": f"scout/research-{self.query_id}",
            "type": "research_query",
            "priority": self.priority,
            "summary": f"Research: {self.query} [Linked: {self.linked_todo}, Source: scout]",
            "confidence": self.confidence,
            "metadata": {
                "research_type": self.research_type.value,
                "query": self.query,
                "tags": self.tags,
                "linked_todo": self.linked_todo,
                "context": self.metadata.get("context", ""),
                "file_context": self.metadata.get("file_context", {}),
                "created_at": self.created_at,
                "ai_instructions": self.metadata.get("ai_instructions", "")
            }
        }

class ResearchQueryGenerator:
    """
    Generates research queries from researchable TODO findings
    Focuses on creating Claude-optimized research prompts
    """
    
    def __init__(self):
        self.research_patterns = self._compile_research_patterns()
        self.query_templates = self._load_query_templates()
        
    def _compile_research_patterns(self) -> Dict[ResearchType, List[re.Pattern]]:
        """Compile regex patterns for different research types"""
        return {
            ResearchType.API_INTEGRATION: [
                re.compile(r'(?i)(api|integration|webhook|endpoint|rest|graphql)', re.MULTILINE),
                re.compile(r'(?i)(stripe|paypal|twitter|github|slack|oauth)', re.MULTILINE),
                re.compile(r'(?i)(authenticate|authorization|token|jwt)', re.MULTILINE),
            ],
            ResearchType.ALGORITHM_OPTIMIZATION: [
                re.compile(r'(?i)(algorithm|optimize|performance|speed|efficient)', re.MULTILINE),
                re.compile(r'(?i)(sort|search|hash|cache|index)', re.MULTILINE),
                re.compile(r'(?i)(o\(n\)|complexity|bottleneck|slow)', re.MULTILINE),
            ],
            ResearchType.SECURITY_PATTERNS: [
                re.compile(r'(?i)(security|secure|vulnerability|xss|sql.injection)', re.MULTILINE),
                re.compile(r'(?i)(sanitize|validate|escape|encrypt|hash)', re.MULTILINE),
                re.compile(r'(?i)(csrf|authentication|authorization|permission)', re.MULTILINE),
            ],
            ResearchType.PERFORMANCE_TUNING: [
                re.compile(r'(?i)(performance|optimize|speed|memory|cpu)', re.MULTILINE),
                re.compile(r'(?i)(cache|lazy.load|pagination|batch)', re.MULTILINE),
                re.compile(r'(?i)(database|query|index|n\+1)', re.MULTILINE),
            ],
            ResearchType.ARCHITECTURE_PATTERNS: [
                re.compile(r'(?i)(architecture|pattern|design|structure)', re.MULTILINE),
                re.compile(r'(?i)(microservice|monolith|mvc|mvp|clean)', re.MULTILINE),
                re.compile(r'(?i)(factory|singleton|observer|decorator)', re.MULTILINE),
            ],
            ResearchType.LIBRARY_COMPARISON: [
                re.compile(r'(?i)(library|framework|package|module|dependency)', re.MULTILINE),
                re.compile(r'(?i)(compare|alternative|vs|versus|between)', re.MULTILINE),
                re.compile(r'(?i)(react|vue|angular|django|flask|fastapi)', re.MULTILINE),
            ],
            ResearchType.CODE_EXAMPLES: [
                re.compile(r'(?i)(example|sample|demo|snippet|template)', re.MULTILINE),
                re.compile(r'(?i)(implement|usage|how.to|tutorial)', re.MULTILINE),
                re.compile(r'(?i)(boilerplate|starter|scaffold)', re.MULTILINE),
            ],
            ResearchType.BEST_PRACTICES: [
                re.compile(r'(?i)(best.practice|convention|standard|guideline)', re.MULTILINE),
                re.compile(r'(?i)(clean.code|solid|dry|kiss|yagni)', re.MULTILINE),
                re.compile(r'(?i)(naming|style|format|lint)', re.MULTILINE),
            ],
            ResearchType.DEBUGGING_SOLUTIONS: [
                re.compile(r'(?i)(debug|troubleshoot|fix|resolve|issue)', re.MULTILINE),
                re.compile(r'(?i)(error|exception|bug|crash|fail)', re.MULTILINE),
                re.compile(r'(?i)(stack.trace|breakpoint|log|trace)', re.MULTILINE),
            ],
            ResearchType.DEPLOYMENT_STRATEGIES: [
                re.compile(r'(?i)(deploy|deployment|ci/cd|pipeline|release)', re.MULTILINE),
                re.compile(r'(?i)(docker|kubernetes|container|orchestration)', re.MULTILINE),
                re.compile(r'(?i)(aws|azure|gcp|cloud|serverless)', re.MULTILINE),
            ]
        }
    
    def _load_query_templates(self) -> Dict[ResearchType, List[str]]:
        """Load query templates for each research type"""
        return {
            ResearchType.API_INTEGRATION: [
                "What are the best practices for integrating {api_name} API in {language}?",
                "Show examples of {api_name} authentication and error handling patterns",
                "Compare different approaches for implementing {api_name} webhooks"
            ],
            ResearchType.ALGORITHM_OPTIMIZATION: [
                "What are efficient algorithms for {problem_description}?",
                "How to optimize {algorithm_name} for better time/space complexity?",
                "Compare different data structures for {use_case}"
            ],
            ResearchType.SECURITY_PATTERNS: [
                "What are the security best practices for {vulnerability_type}?",
                "How to properly implement {security_feature} in {framework}?",
                "Show secure patterns for handling {sensitive_data}"
            ],
            ResearchType.PERFORMANCE_TUNING: [
                "How to optimize {performance_issue} in {technology}?",
                "What are caching strategies for {use_case}?",
                "Best practices for database query optimization in {context}"
            ],
            ResearchType.ARCHITECTURE_PATTERNS: [
                "When to use {pattern_name} pattern vs alternatives?",
                "How to implement {architecture_style} for {use_case}?",
                "Compare architectural approaches for {system_requirement}"
            ],
            ResearchType.LIBRARY_COMPARISON: [
                "Compare {library1} vs {library2} for {use_case}",
                "What are the pros/cons of using {library_name}?",
                "Migration guide from {old_library} to {new_library}"
            ],
            ResearchType.CODE_EXAMPLES: [
                "Show implementation examples of {feature} in {language}",
                "Provide code snippets for {use_case} using {framework}",
                "Create a minimal example demonstrating {concept}"
            ],
            ResearchType.BEST_PRACTICES: [
                "What are the {language} best practices for {topic}?",
                "How to follow {principle} principle in {context}?",
                "Style guide recommendations for {code_element}"
            ],
            ResearchType.DEBUGGING_SOLUTIONS: [
                "How to debug {error_type} in {technology}?",
                "Common causes and fixes for {error_message}",
                "Troubleshooting guide for {issue_description}"
            ],
            ResearchType.DEPLOYMENT_STRATEGIES: [
                "Best practices for deploying {app_type} to {platform}",
                "How to set up CI/CD pipeline for {technology_stack}?",
                "Compare deployment strategies for {use_case}"
            ]
        }
    
    def generate_queries(self, findings: List[TODOFinding]) -> List[ResearchQuery]:
        """Generate research queries from researchable TODO findings"""
        queries = []
        
        for finding in findings:
            if not finding.is_researchable:
                continue
                
            # Detect research type
            research_type = self._detect_research_type(finding)
            
            # Generate query
            query = self._generate_query(finding, research_type)
            
            if query:
                queries.append(query)
        
        return queries
    
    def _detect_research_type(self, finding: TODOFinding) -> ResearchType:
        """Detect the most appropriate research type for a finding"""
        content = finding.content.lower()
        context = " ".join(finding.context_lines).lower()
        full_text = f"{content} {context}"
        
        # Score each research type
        type_scores = {}
        for research_type, patterns in self.research_patterns.items():
            score = sum(1 for pattern in patterns if pattern.search(full_text))
            if score > 0:
                type_scores[research_type] = score
        
        # Return the highest scoring type, or default to CODE_EXAMPLES
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        return ResearchType.CODE_EXAMPLES
    
    def _generate_query(self, finding: TODOFinding, research_type: ResearchType) -> Optional[ResearchQuery]:
        """Generate a research query from a finding"""
        # Extract key terms from the finding
        terms = self._extract_key_terms(finding.content)
        
        # Build the research question
        query_text = self._build_query_text(finding, research_type, terms)
        
        # Generate AI instructions
        ai_instructions = self._generate_ai_instructions(finding, research_type)
        
        # Create unique query ID
        query_id = hashlib.sha256(
            f"{finding.content_hash}-{research_type.value}-{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        return ResearchQuery(
            query_id=query_id,
            type="research_query",
            priority=finding.priority_score,
            query=query_text,
            source="scout",
            linked_todo=finding.content_hash,
            confidence=finding.confidence * 0.8,  # Slight reduction for research confidence
            research_type=research_type,
            tags=self._generate_tags(finding, research_type),
            metadata={
                "context": " ".join(finding.context_lines),
                "file_context": {
                    "file_path": finding.file_path,
                    "line_number": finding.line_number,
                    "file_type": finding.file_path.split('.')[-1] if '.' in finding.file_path else 'unknown'
                },
                "ai_instructions": ai_instructions,
                "original_todo": {
                    "type": finding.todo_type,
                    "content": finding.content
                }
            },
            created_at=datetime.now(timezone.utc).isoformat()
        )
    
    def _extract_key_terms(self, content: str) -> List[str]:
        """Extract key terms from TODO content"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                     'how', 'when', 'where', 'what', 'which', 'who', 'why'}
        
        # Extract words (alphanumeric + common programming chars)
        words = re.findall(r'[\w\-_\.]+', content.lower())
        
        # Filter out stop words and very short words
        terms = [w for w in words if w not in stop_words and len(w) > 2]
        
        return terms[:5]  # Return top 5 terms
    
    def _build_query_text(self, finding: TODOFinding, research_type: ResearchType, terms: List[str]) -> str:
        """Build a human-readable research query"""
        # Start with the original TODO content as context
        base_query = f"Research needed for: {finding.content}"
        
        # Add specific research focus based on type
        type_specific = {
            ResearchType.API_INTEGRATION: f"Find best practices for API integration involving {', '.join(terms[:2])}",
            ResearchType.ALGORITHM_OPTIMIZATION: f"Explore optimization techniques for {', '.join(terms[:2])}",
            ResearchType.SECURITY_PATTERNS: f"Investigate security patterns for {', '.join(terms[:2])}",
            ResearchType.PERFORMANCE_TUNING: f"Analyze performance optimization for {', '.join(terms[:2])}",
            ResearchType.ARCHITECTURE_PATTERNS: f"Research architectural patterns for {', '.join(terms[:2])}",
            ResearchType.LIBRARY_COMPARISON: f"Compare libraries/frameworks for {', '.join(terms[:2])}",
            ResearchType.CODE_EXAMPLES: f"Find code examples demonstrating {', '.join(terms[:2])}",
            ResearchType.BEST_PRACTICES: f"Identify best practices for {', '.join(terms[:2])}",
            ResearchType.DEBUGGING_SOLUTIONS: f"Find debugging solutions for {', '.join(terms[:2])}",
            ResearchType.DEPLOYMENT_STRATEGIES: f"Research deployment strategies for {', '.join(terms[:2])}"
        }
        
        specific_query = type_specific.get(research_type, base_query)
        
        # Add file context if relevant
        file_ext = finding.file_path.split('.')[-1] if '.' in finding.file_path else None
        if file_ext in ['py', 'js', 'ts', 'java', 'cpp', 'go', 'rs']:
            specific_query += f" in {file_ext} context"
        
        return specific_query
    
    def _generate_ai_instructions(self, finding: TODOFinding, research_type: ResearchType) -> str:
        """Generate specific instructions for AI agents"""
        instructions = [
            f"Research Type: {research_type.value}",
            f"Original TODO: {finding.todo_type} - {finding.content}",
            f"File Context: {finding.file_path}:{finding.line_number}",
            "",
            "Please provide:",
        ]
        
        # Type-specific instructions
        type_instructions = {
            ResearchType.API_INTEGRATION: [
                "1. Authentication methods and best practices",
                "2. Error handling patterns",
                "3. Rate limiting considerations",
                "4. Example implementation code",
                "5. Common pitfalls to avoid"
            ],
            ResearchType.ALGORITHM_OPTIMIZATION: [
                "1. Time and space complexity analysis",
                "2. Alternative algorithms comparison",
                "3. Implementation examples",
                "4. Benchmark results if available",
                "5. Trade-offs and considerations"
            ],
            ResearchType.SECURITY_PATTERNS: [
                "1. Vulnerability description and impact",
                "2. Secure implementation patterns",
                "3. Code examples (secure vs insecure)",
                "4. Testing approaches",
                "5. Industry standards and compliance"
            ],
            ResearchType.PERFORMANCE_TUNING: [
                "1. Performance bottleneck analysis",
                "2. Optimization techniques",
                "3. Benchmarking methods",
                "4. Before/after code examples",
                "5. Monitoring recommendations"
            ],
            ResearchType.ARCHITECTURE_PATTERNS: [
                "1. Pattern description and use cases",
                "2. Implementation guidelines",
                "3. Pros and cons analysis",
                "4. Code structure examples",
                "5. Migration strategies"
            ],
            ResearchType.LIBRARY_COMPARISON: [
                "1. Feature comparison matrix",
                "2. Performance benchmarks",
                "3. Community and maintenance status",
                "4. Migration effort assessment",
                "5. Code examples for each option"
            ],
            ResearchType.CODE_EXAMPLES: [
                "1. Minimal working example",
                "2. Production-ready implementation",
                "3. Error handling and edge cases",
                "4. Unit test examples",
                "5. Documentation snippets"
            ],
            ResearchType.BEST_PRACTICES: [
                "1. Industry standard guidelines",
                "2. Code style examples",
                "3. Anti-patterns to avoid",
                "4. Tooling recommendations",
                "5. Team adoption strategies"
            ],
            ResearchType.DEBUGGING_SOLUTIONS: [
                "1. Root cause analysis",
                "2. Step-by-step debugging approach",
                "3. Common fixes and workarounds",
                "4. Prevention strategies",
                "5. Logging and monitoring setup"
            ],
            ResearchType.DEPLOYMENT_STRATEGIES: [
                "1. Infrastructure requirements",
                "2. CI/CD pipeline configuration",
                "3. Environment-specific considerations",
                "4. Rollback strategies",
                "5. Monitoring and alerting setup"
            ]
        }
        
        instructions.extend(type_instructions.get(research_type, [
            "1. Relevant background information",
            "2. Implementation examples",
            "3. Best practices",
            "4. Common pitfalls",
            "5. Additional resources"
        ]))
        
        instructions.extend([
            "",
            "Focus on practical, actionable insights that can be directly applied to the codebase.",
            "Include code snippets where relevant.",
            "Cite sources and provide links to documentation when available."
        ])
        
        return "\n".join(instructions)
    
    def _generate_tags(self, finding: TODOFinding, research_type: ResearchType) -> List[str]:
        """Generate relevant tags for the research query"""
        tags = [research_type.value, finding.todo_type.lower()]
        
        # Add language/framework tags based on file extension
        file_ext = finding.file_path.split('.')[-1] if '.' in finding.file_path else None
        ext_to_tags = {
            'py': ['python'],
            'js': ['javascript'],
            'ts': ['typescript'],
            'java': ['java'],
            'cpp': ['c++'],
            'go': ['golang'],
            'rs': ['rust'],
            'rb': ['ruby'],
            'php': ['php'],
            'swift': ['swift'],
            'kt': ['kotlin']
        }
        
        if file_ext in ext_to_tags:
            tags.extend(ext_to_tags[file_ext])
        
        # Add priority tag
        if finding.priority_score >= 80:
            tags.append('high-priority')
        elif finding.priority_score >= 60:
            tags.append('medium-priority')
        else:
            tags.append('low-priority')
        
        # Add specific technology tags based on content
        content_lower = finding.content.lower()
        tech_keywords = {
            'react': 'react',
            'vue': 'vue',
            'angular': 'angular',
            'django': 'django',
            'flask': 'flask',
            'fastapi': 'fastapi',
            'express': 'express',
            'spring': 'spring',
            'docker': 'docker',
            'kubernetes': 'kubernetes',
            'aws': 'aws',
            'azure': 'azure',
            'gcp': 'gcp',
            'postgres': 'postgresql',
            'mysql': 'mysql',
            'mongodb': 'mongodb',
            'redis': 'redis'
        }
        
        for keyword, tag in tech_keywords.items():
            if keyword in content_lower:
                tags.append(tag)
        
        return list(set(tags))  # Remove duplicates