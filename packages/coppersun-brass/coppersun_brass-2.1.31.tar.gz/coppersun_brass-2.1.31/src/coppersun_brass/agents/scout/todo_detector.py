#!/usr/bin/env python3
"""
TODODetector - Core pattern detection for Scout Agent
Standalone implementation with confidence-tiered regex patterns
"""

import re
import os
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import mimetypes

@dataclass
class TODOFinding:
    """Represents a detected TODO item with metadata"""
    file_path: str
    line_number: int
    content: str
    todo_type: str  # TODO, FIXME, BUG, etc.
    confidence: float  # 0.0 - 1.0
    priority_score: int  # 0-100
    is_researchable: bool
    context_lines: List[str]
    content_hash: str
    created_at: datetime
    
    def __post_init__(self):
        """Generate content hash if not provided"""
        if not self.content_hash:
            key = f"{self.file_path}:{self.line_number}:{self.content.strip()}"
            self.content_hash = hashlib.sha256(key.encode()).hexdigest()[:16]

class TODODetector:
    """
    Standalone TODO detection with confidence-tiered patterns
    No dependencies on DCP or other Copper Alloy Brass components
    """
    
    def __init__(self):
        self.patterns = self._compile_patterns()
        self.supported_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h',
            '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala',
            '.md', '.rst', '.txt', '.json', '.yaml', '.yml', '.toml', '.ini',
            '.html', '.css', '.scss', '.vue', '.svelte', '.sql'
        }
        
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for different confidence tiers"""
        return {
            # High confidence patterns
            'high_confidence': re.compile(
                r'(?i)(?://|#|/\*|\*|<!--)\s*(TODO|FIXME|BUG)\s*[:\-]?\s*(.+?)(?:\*/|-->|$)',
                re.MULTILINE
            ),
            
            # Medium confidence patterns  
            'medium_confidence': re.compile(
                r'(?i)(?://|#|/\*|\*|<!--)\s*(HACK|XXX)\s*[:\-]?\s*(.+?)(?:\*/|-->|$)',
                re.MULTILINE
            ),
            
            # Low confidence patterns
            'low_confidence': re.compile(
                r'(?i)(?://|#|/\*|\*|<!--)\s*(NOTE)\s*[:\-]?\s*(.+?)(?:\*/|-->|$)',
                re.MULTILINE
            ),
            
            # Priority modifiers
            'priority_high': re.compile(
                r'(?i)(URGENT|CRITICAL|IMPORTANT|ASAP)',
                re.MULTILINE
            ),
            
            # Context keywords
            'priority_context': re.compile(
                r'(?i)(security|performance|bug|error|crash|vulnerability|leak)',
                re.MULTILINE
            ),
            
            # Researchable indicators
            'researchable': re.compile(
                r'(?i)(research|investigate|find|example|pattern|look\s+for|study|explore)',
                re.MULTILINE
            ),
            
            # False positive filters
            'false_positives': re.compile(
                r'(?i)(grocery|shopping|personal|".*todo.*"|\'.*todo.*\')',
                re.MULTILINE
            )
        }
    
    def scan_file(self, file_path: str) -> List[TODOFinding]:
        """
        Scan a single file for TODO items
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            List of TODOFinding objects
        """
        findings = []
        
        try:
            # Check if file type is supported
            if not self._is_supported_file(file_path):
                return findings
                
            # Read file content
            content = self._read_file_safely(file_path)
            if not content:
                return findings
                
            lines = content.split('\n')
            
            # Scan each line for patterns
            for line_num, line in enumerate(lines, 1):
                line_findings = self._scan_line(
                    line, file_path, line_num, lines
                )
                findings.extend(line_findings)
                
        except Exception as e:
            # Log error but don't fail entire scan
            print(f"Error scanning {file_path}: {e}")
            
        return findings
    
    def scan_directory(self, dir_path: str) -> List[TODOFinding]:
        """
        Recursively scan directory for TODO items
        
        Args:
            dir_path: Root directory to scan
            
        Returns:
            List of all TODOFinding objects found
        """
        all_findings = []
        
        for root, dirs, files in os.walk(dir_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_findings = self.scan_file(file_path)
                all_findings.extend(file_findings)
                
        return all_findings
    
    def _scan_line(self, line: str, file_path: str, line_num: int, all_lines: List[str]) -> List[TODOFinding]:
        """Scan a single line for TODO patterns"""
        findings = []
        
        # Skip if likely false positive
        if self.patterns['false_positives'].search(line):
            return findings
            
        # Check each confidence tier
        for tier, confidence_value in [
            ('high_confidence', 0.9),
            ('medium_confidence', 0.7), 
            ('low_confidence', 0.5)
        ]:
            pattern = self.patterns[tier]
            matches = pattern.findall(line)
            
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    todo_type, content = match[0], match[1]
                else:
                    continue
                    
                # Skip empty content
                if not content.strip():
                    continue
                    
                # Calculate priority score
                priority_score = self._calculate_priority_score(
                    todo_type, content, confidence_value
                )
                
                # Create finding
                finding = TODOFinding(
                    file_path=file_path,
                    line_number=line_num,
                    content=content.strip(),
                    todo_type=todo_type.upper(),
                    confidence=confidence_value,
                    priority_score=priority_score,
                    is_researchable=bool(self.patterns['researchable'].search(content)),
                    context_lines=self._get_context_lines(all_lines, line_num),
                    content_hash="",  # Will be generated in __post_init__
                    created_at=datetime.now()
                )
                
                findings.append(finding)
                
        return findings
    
    def _calculate_priority_score(self, todo_type: str, content: str, confidence: float) -> int:
        """
        Calculate priority score (0-100) based on multiple factors
        
        Scoring breakdown:
        - Base score from TODO type (0-40)
        - Priority modifiers (0-30)
        - Context keywords (0-20)
        - Confidence multiplier (0-10)
        """
        score = 0
        
        # Base score by type
        type_scores = {
            'BUG': 40,
            'FIXME': 35,
            'TODO': 25,
            'HACK': 20,
            'XXX': 15,
            'NOTE': 10
        }
        score += type_scores.get(todo_type.upper(), 25)
        
        # Priority modifiers (+30 max)
        if self.patterns['priority_high'].search(content):
            priority_words = self.patterns['priority_high'].findall(content)
            if any(word.upper() in ['URGENT', 'CRITICAL'] for word in priority_words):
                score += 30
            elif any(word.upper() in ['IMPORTANT', 'ASAP'] for word in priority_words):
                score += 20
        
        # Context keywords (+20 max)
        if self.patterns['priority_context'].search(content):
            context_words = self.patterns['priority_context'].findall(content)
            # Security issues get highest context score
            if any(word.lower() in ['security', 'vulnerability', 'injection'] for word in context_words):
                score += 20
            # Performance and crashes are also high priority
            elif any(word.lower() in ['crash', 'leak', 'performance'] for word in context_words):
                score += 15
            # General bugs and errors
            elif any(word.lower() in ['bug', 'error'] for word in context_words):
                score += 10
        
        # Confidence multiplier (up to +10)
        score += int(confidence * 10)
        
        # Cap at 100
        return min(score, 100)
    
    def _get_context_lines(self, all_lines: List[str], line_num: int, context: int = 1) -> List[str]:
        """Get surrounding lines for context"""
        start = max(0, line_num - context - 1)
        end = min(len(all_lines), line_num + context)
        return all_lines[start:end]
    
    def _is_supported_file(self, file_path: str) -> bool:
        """Check if file type should be scanned"""
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_extensions
    
    def _should_ignore_dir(self, dir_name: str) -> bool:
        """Check if directory should be ignored"""
        ignore_dirs = {
            'node_modules', '.git', '__pycache__', '.pytest_cache',
            'build', 'dist', '.venv', 'venv', '.env',
            'coverage', '.coverage', '.tox', '.idea', '.vscode'
        }
        return dir_name in ignore_dirs
    
    def _read_file_safely(self, file_path: str) -> Optional[str]:
        """Safely read file content with encoding detection"""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                # Fall back to latin-1
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                return None
        except Exception:
            return None

# Test runner for standalone validation
def run_detection_test(test_dir: str = "testdata") -> None:
    """Run detection tests on sample files"""
    detector = TODODetector()
    
    print("🔍 Scout Agent - TODO Detection Test")
    print("=" * 50)
    
    if not os.path.exists(test_dir):
        print(f"❌ Test directory '{test_dir}' not found")
        return
        
    all_findings = detector.scan_directory(test_dir)
    
    # Group findings by file
    by_file = {}
    for finding in all_findings:
        file_name = os.path.basename(finding.file_path)
        if file_name not in by_file:
            by_file[file_name] = []
        by_file[file_name].append(finding)
    
    # Report results
    total_findings = len(all_findings)
    print(f"📊 Total findings: {total_findings}")
    print()
    
    for file_name, findings in by_file.items():
        print(f"📁 {file_name} ({len(findings)} findings)")
        
        for finding in findings:
            confidence_emoji = "🔴" if finding.confidence >= 0.9 else "🟡" if finding.confidence >= 0.7 else "🟢"
            research_emoji = "🔬" if finding.is_researchable else ""
            
            print(f"  {confidence_emoji} Line {finding.line_number}: {finding.todo_type} (Priority: {finding.priority_score})")
            print(f"    Content: {finding.content}")
            print(f"    Confidence: {finding.confidence:.1f} {research_emoji}")
            print(f"    Hash: {finding.content_hash}")
            print()
    
    # Summary by type
    by_type = {}
    for finding in all_findings:
        todo_type = finding.todo_type
        if todo_type not in by_type:
            by_type[todo_type] = 0
        by_type[todo_type] += 1
    
    print("📈 Summary by type:")
    for todo_type, count in sorted(by_type.items()):
        print(f"  {todo_type}: {count}")
    
    researchable_count = sum(1 for f in all_findings if f.is_researchable)
    print(f"  Researchable: {researchable_count}")

if __name__ == "__main__":
    run_detection_test()