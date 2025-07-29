#!/usr/bin/env python3
"""
ScoutDCPIntegrator - Staging system for Scout Agent findings
Provides stage → review → commit workflow for DCP integration
"""

import json
import os
from typing import List, Dict, Optional, Set
from datetime import datetime, timezone
from pathlib import Path

try:
    from .todo_detector import TODOFinding
    from .research_generator import ResearchQueryGenerator, ResearchQuery, ResearchType
except ImportError:
    # For standalone testing
    from todo_detector import TODOFinding
    from research_generator import ResearchQueryGenerator, ResearchQuery, ResearchType

class ScoutDCPIntegrator:
    """
    Manages staging and committing Scout findings to DCP
    Implements safe batch operations with human/AI oversight
    """
    
    def __init__(self, staging_file: str = "scout_findings.json", dcp_manager=None):
        self.staging_file = staging_file
        self.dcp_manager = dcp_manager  # Will be None for standalone testing
        self.staged_findings: List[TODOFinding] = []
        self.staged_research_queries: List[ResearchQuery] = []
        self.research_generator = ResearchQueryGenerator()
        self._load_staged_findings()
    
    def stage_findings(self, findings: List[TODOFinding], deduplicate: bool = True) -> Dict[str, int]:
        """
        Stage TODO findings for later review and commit
        
        Args:
            findings: List of TODOFinding objects to stage
            deduplicate: Remove duplicates from existing staged items
            
        Returns:
            Dict with staging statistics
        """
        if not findings:
            return {"staged": 0, "duplicates": 0, "total_staged": len(self.staged_findings)}
        
        original_count = len(self.staged_findings)
        duplicates = 0
        staged = 0
        
        # Get existing hashes for deduplication
        existing_hashes = {f.content_hash for f in self.staged_findings} if deduplicate else set()
        
        for finding in findings:
            if deduplicate and finding.content_hash in existing_hashes:
                duplicates += 1
                continue
                
            # Validate finding before staging
            if self._validate_finding(finding):
                self.staged_findings.append(finding)
                existing_hashes.add(finding.content_hash)
                staged += 1
        
        # Save to staging file
        self._save_staged_findings()
        
        return {
            "staged": staged,
            "duplicates": duplicates,
            "total_staged": len(self.staged_findings),
            "previous_count": original_count
        }
    
    def review_staged(self, filter_criteria: Optional[Dict] = None) -> Dict[str, any]:
        """
        Review staged findings with optional filtering
        
        Args:
            filter_criteria: Dict with keys like 'min_priority', 'confidence', 'todo_type'
            
        Returns:
            Dict with review statistics and grouped findings
        """
        filtered_findings = self._filter_findings(self.staged_findings, filter_criteria)
        
        # Group by various categories for review
        by_priority = self._group_by_priority(filtered_findings)
        by_confidence = self._group_by_confidence(filtered_findings)
        by_type = self._group_by_type(filtered_findings)
        by_file = self._group_by_file(filtered_findings)
        
        researchable_count = sum(1 for f in filtered_findings if f.is_researchable)
        
        return {
            "total_staged": len(self.staged_findings),
            "filtered_count": len(filtered_findings),
            "by_priority": by_priority,
            "by_confidence": by_confidence,
            "by_type": by_type,
            "by_file": by_file,
            "researchable_count": researchable_count,
            "findings": filtered_findings
        }
    
    def commit_staged(self, filter_criteria: Optional[Dict] = None, dry_run: bool = False) -> Dict[str, any]:
        """
        Commit staged findings to DCP with optional filtering
        
        Args:
            filter_criteria: Only commit findings matching criteria
            dry_run: Show what would be committed without actually doing it
            
        Returns:
            Dict with commit results
        """
        if not self.staged_findings:
            return {"error": "No staged findings to commit"}
        
        # Filter findings for commit
        to_commit = self._filter_findings(self.staged_findings, filter_criteria)
        
        if not to_commit:
            return {"error": "No findings match filter criteria"}
        
        if dry_run:
            return {
                "dry_run": True,
                "would_commit": len(to_commit),
                "would_remain_staged": len(self.staged_findings) - len(to_commit),
                "findings_preview": [self._finding_to_summary(f) for f in to_commit[:5]]
            }
        
        # Convert to DCP observations
        observations = [self._finding_to_dcp_observation(f) for f in to_commit]
        
        # Commit to DCP (if manager available)
        if self.dcp_manager:
            try:
                # Use thread-safe batch update
                with self.dcp_manager.lock():
                    result = self.dcp_manager.add_observations(observations, source_agent="scout")
                
                # Remove committed findings from staging
                committed_hashes = {f.content_hash for f in to_commit}
                self.staged_findings = [
                    f for f in self.staged_findings 
                    if f.content_hash not in committed_hashes
                ]
                self._save_staged_findings()
                
                # Check if any failed
                if result['failed'] > 0:
                    print(f"Warning: {result['failed']} observations failed validation")
                    for error in result['errors']:
                        print(f"  - {error['error']}")
                
                return {
                    "committed": result['succeeded'],
                    "failed": result['failed'],
                    "remaining_staged": len(self.staged_findings),
                    "observations_added": result['succeeded'],
                    "errors": result['errors']
                }
                
            except Exception as e:
                return {"error": f"DCP commit failed: {str(e)}"}
        else:
            # Standalone mode - just show what would be committed
            return {
                "standalone_mode": True,
                "would_commit": len(observations),
                "observations_preview": observations[:3]
            }
    
    def clear_staged(self, filter_criteria: Optional[Dict] = None) -> Dict[str, int]:
        """
        Clear staged findings with optional filtering
        
        Args:
            filter_criteria: Only clear findings matching criteria (None = clear all)
            
        Returns:
            Dict with clear statistics
        """
        original_count = len(self.staged_findings)
        
        if filter_criteria:
            to_clear = self._filter_findings(self.staged_findings, filter_criteria)
            clear_hashes = {f.content_hash for f in to_clear}
            self.staged_findings = [
                f for f in self.staged_findings 
                if f.content_hash not in clear_hashes
            ]
        else:
            self.staged_findings = []
        
        self._save_staged_findings()
        
        return {
            "cleared": original_count - len(self.staged_findings),
            "remaining": len(self.staged_findings),
            "original_count": original_count
        }
    
    def _finding_to_dcp_observation(self, finding: TODOFinding) -> Dict:
        """Convert TODOFinding to DCP observation format"""
        return {
            "id": f"scout/{finding.content_hash}-{int(finding.created_at.timestamp())}",
            "type": "todo_item",
            "priority": finding.priority_score,
            "summary": f"{finding.todo_type}: {finding.content} [Location: {os.path.basename(finding.file_path)}:{finding.line_number}, Source: scout]",
            "confidence": finding.confidence,
            "metadata": {
                "todo_type": finding.todo_type,
                "file_path": finding.file_path,
                "line_number": finding.line_number,
                "content_hash": finding.content_hash,
                "is_researchable": finding.is_researchable,
                "context_lines": finding.context_lines,
                "created_at": finding.created_at.isoformat(),
                "last_seen": datetime.now(timezone.utc).isoformat()
            }
        }
    
    def _finding_to_summary(self, finding: TODOFinding) -> Dict:
        """Create summary dict for finding"""
        return {
            "type": finding.todo_type,
            "priority": finding.priority_score,
            "confidence": finding.confidence,
            "content": finding.content[:50] + "..." if len(finding.content) > 50 else finding.content,
            "file": os.path.basename(finding.file_path),
            "line": finding.line_number,
            "researchable": finding.is_researchable
        }
    
    def _filter_findings(self, findings: List[TODOFinding], criteria: Optional[Dict]) -> List[TODOFinding]:
        """Filter findings based on criteria"""
        if not criteria:
            return findings
        
        filtered = findings
        
        if "min_priority" in criteria:
            filtered = [f for f in filtered if f.priority_score >= criteria["min_priority"]]
        
        if "min_confidence" in criteria:
            filtered = [f for f in filtered if f.confidence >= criteria["min_confidence"]]
        
        if "todo_type" in criteria:
            types = criteria["todo_type"]
            if isinstance(types, str):
                types = [types]
            filtered = [f for f in filtered if f.todo_type in types]
        
        if "researchable_only" in criteria and criteria["researchable_only"]:
            filtered = [f for f in filtered if f.is_researchable]
        
        if "file_pattern" in criteria:
            pattern = criteria["file_pattern"].lower()
            filtered = [f for f in filtered if pattern in f.file_path.lower()]
        
        return filtered
    
    def _group_by_priority(self, findings: List[TODOFinding]) -> Dict[str, int]:
        """Group findings by priority ranges"""
        ranges = {"Critical (90+)": 0, "High (70-89)": 0, "Medium (50-69)": 0, "Low (<50)": 0}
        
        for finding in findings:
            if finding.priority_score >= 90:
                ranges["Critical (90+)"] += 1
            elif finding.priority_score >= 70:
                ranges["High (70-89)"] += 1
            elif finding.priority_score >= 50:
                ranges["Medium (50-69)"] += 1
            else:
                ranges["Low (<50)"] += 1
        
        return ranges
    
    def _group_by_confidence(self, findings: List[TODOFinding]) -> Dict[str, int]:
        """Group findings by confidence tiers"""
        tiers = {"High (0.9+)": 0, "Medium (0.7-0.8)": 0, "Low (<0.7)": 0}
        
        for finding in findings:
            if finding.confidence >= 0.9:
                tiers["High (0.9+)"] += 1
            elif finding.confidence >= 0.7:
                tiers["Medium (0.7-0.8)"] += 1
            else:
                tiers["Low (<0.7)"] += 1
        
        return tiers
    
    def _group_by_type(self, findings: List[TODOFinding]) -> Dict[str, int]:
        """Group findings by TODO type"""
        by_type = {}
        for finding in findings:
            todo_type = finding.todo_type
            by_type[todo_type] = by_type.get(todo_type, 0) + 1
        return by_type
    
    def _group_by_file(self, findings: List[TODOFinding]) -> Dict[str, int]:
        """Group findings by file"""
        by_file = {}
        for finding in findings:
            file_name = os.path.basename(finding.file_path)
            by_file[file_name] = by_file.get(file_name, 0) + 1
        return by_file
    
    def _validate_finding(self, finding: TODOFinding) -> bool:
        """Validate finding before staging"""
        if not finding.content.strip():
            return False
        if not finding.todo_type:
            return False
        if finding.priority_score < 0 or finding.priority_score > 100:
            return False
        if finding.confidence < 0.0 or finding.confidence > 1.0:
            return False
        return True
    
    def generate_research_queries(self, auto_stage: bool = False) -> Dict[str, any]:
        """
        Generate research queries from researchable staged findings
        
        Args:
            auto_stage: If True, automatically stage generated queries
            
        Returns:
            Dict with generation statistics and queries
        """
        # Filter researchable findings
        researchable_findings = [f for f in self.staged_findings if f.is_researchable]
        
        if not researchable_findings:
            return {
                "generated": 0,
                "researchable_findings": 0,
                "queries": []
            }
        
        # Generate research queries
        queries = self.research_generator.generate_queries(researchable_findings)
        
        # Optionally stage the queries
        if auto_stage:
            self.staged_research_queries.extend(queries)
            self._save_staged_findings()
        
        return {
            "generated": len(queries),
            "researchable_findings": len(researchable_findings),
            "queries": queries,
            "auto_staged": auto_stage
        }
    
    def review_research_queries(self) -> Dict[str, any]:
        """Review staged research queries"""
        if not self.staged_research_queries:
            return {
                "total_queries": 0,
                "by_type": {},
                "by_priority": {},
                "queries": []
            }
        
        # Group by research type
        by_type = {}
        for query in self.staged_research_queries:
            research_type = query.research_type.value
            by_type[research_type] = by_type.get(research_type, 0) + 1
        
        # Group by priority
        by_priority = {"high": 0, "medium": 0, "low": 0}
        for query in self.staged_research_queries:
            if query.priority >= 80:
                by_priority["high"] += 1
            elif query.priority >= 60:
                by_priority["medium"] += 1
            else:
                by_priority["low"] += 1
        
        return {
            "total_queries": len(self.staged_research_queries),
            "by_type": by_type,
            "by_priority": by_priority,
            "queries": self.staged_research_queries
        }
    
    def _load_staged_findings(self) -> None:
        """Load staged findings and research queries from file"""
        if not os.path.exists(self.staging_file):
            self.staged_findings = []
            self.staged_research_queries = []
            return
        
        try:
            with open(self.staging_file, 'r') as f:
                data = json.load(f)
                
            # Load TODO findings
            self.staged_findings = []
            for item in data.get("findings", []):
                finding = TODOFinding(
                    file_path=item["file_path"],
                    line_number=item["line_number"],
                    content=item["content"],
                    todo_type=item["todo_type"],
                    confidence=item["confidence"],
                    priority_score=item["priority_score"],
                    is_researchable=item["is_researchable"],
                    context_lines=item["context_lines"],
                    content_hash=item["content_hash"],
                    created_at=datetime.fromisoformat(item["created_at"])
                )
                self.staged_findings.append(finding)
            
            # Load research queries
            self.staged_research_queries = []
            for item in data.get("research_queries", []):
                query = ResearchQuery(
                    query_id=item["query_id"],
                    type=item["type"],
                    priority=item["priority"],
                    query=item["query"],
                    source=item["source"],
                    linked_todo=item["linked_todo"],
                    confidence=item["confidence"],
                    research_type=ResearchType(item["research_type"]),
                    tags=item["tags"],
                    metadata=item["metadata"],
                    created_at=item["created_at"]
                )
                self.staged_research_queries.append(query)
                
        except Exception as e:
            print(f"Error loading staged findings: {e}")
            self.staged_findings = []
            self.staged_research_queries = []
    
    def _save_staged_findings(self) -> None:
        """Save staged findings and research queries to file"""
        try:
            data = {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "count": len(self.staged_findings),
                "research_count": len(self.staged_research_queries),
                "findings": [],
                "research_queries": []
            }
            
            # Save TODO findings
            for finding in self.staged_findings:
                data["findings"].append({
                    "file_path": finding.file_path,
                    "line_number": finding.line_number,
                    "content": finding.content,
                    "todo_type": finding.todo_type,
                    "confidence": finding.confidence,
                    "priority_score": finding.priority_score,
                    "is_researchable": finding.is_researchable,
                    "context_lines": finding.context_lines,
                    "content_hash": finding.content_hash,
                    "created_at": finding.created_at.isoformat()
                })
            
            # Save research queries
            for query in self.staged_research_queries:
                data["research_queries"].append({
                    "query_id": query.query_id,
                    "type": query.type,
                    "priority": query.priority,
                    "query": query.query,
                    "source": query.source,
                    "linked_todo": query.linked_todo,
                    "confidence": query.confidence,
                    "research_type": query.research_type.value,
                    "tags": query.tags,
                    "metadata": query.metadata,
                    "created_at": query.created_at
                })
            
            with open(self.staging_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving staged findings: {e}")

# Standalone test function
def test_staging_system():
    """Test the staging system with sample data"""
    try:
        from .todo_detector import TODODetector
    except ImportError:
        from todo_detector import TODODetector
    
    print("🧪 Testing Scout DCP Integration - Staging System")
    print("=" * 55)
    
    # Create detector and integrator
    detector = TODODetector()
    integrator = ScoutDCPIntegrator(staging_file="test_scout_findings.json")
    
    # Clear any existing staged findings
    integrator.clear_staged()
    
    # Scan test directory
    findings = detector.scan_directory("testdata")
    
    if not findings:
        print("❌ No findings to test with")
        return
    
    print(f"📊 Found {len(findings)} TODO items")
    
    # Stage findings
    stage_result = integrator.stage_findings(findings)
    print(f"📦 Staged: {stage_result['staged']}, Duplicates: {stage_result['duplicates']}")
    
    # Review staged findings
    review = integrator.review_staged()
    print(f"\n📋 Review Summary:")
    print(f"  Total staged: {review['total_staged']}")
    print(f"  By priority: {review['by_priority']}")
    print(f"  By confidence: {review['by_confidence']}")
    print(f"  Researchable: {review['researchable_count']}")
    
    # Test filtering
    high_priority_review = integrator.review_staged({"min_priority": 70})
    print(f"\n🔥 High Priority Items (70+): {high_priority_review['filtered_count']}")
    
    # Test dry run commit
    dry_run = integrator.commit_staged({"min_priority": 70}, dry_run=True)
    print(f"\n🧪 Dry Run Commit: Would commit {dry_run.get('would_commit', 0)} items")
    
    # Show a few sample observations
    if "findings_preview" in dry_run:
        print("\n📝 Sample findings that would be committed:")
        for i, finding in enumerate(dry_run["findings_preview"][:3], 1):
            print(f"  {i}. {finding['type']} (Priority: {finding['priority']}): {finding['content']}")
    
    print(f"\n✅ Staging system test complete!")
    print(f"📁 Staged findings saved to: test_scout_findings.json")

if __name__ == "__main__":
    test_staging_system()