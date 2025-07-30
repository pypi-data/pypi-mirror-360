"""Evolution tracker for monitoring persistent code issues over time.

General Staff Role: G2 Intelligence - Historical Analysis
Tracks how code issues, especially TODOs and technical debt, evolve
across sprints to identify areas needing strategic intervention.

Persistent Value: Creates historical record of technical debt accumulation
that helps AI identify chronic problems requiring attention.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
import hashlib
import logging

from .base_analyzer import CodeIssue

logger = logging.getLogger(__name__)


@dataclass
class IssueEvolution:
    """Tracks how an issue has evolved over time.
    
    Optimized for AI understanding of technical debt trends.
    """
    
    issue_id: str  # Hash of issue type + location + core content
    issue_type: str
    file_path: str
    line_number: int  # May change over time
    first_seen: datetime
    last_seen: datetime
    occurrences: int = 1
    sprint_count: int = 1  # Number of sprints this has persisted
    severity_changes: List[Tuple[datetime, str]] = field(default_factory=list)
    line_number_changes: List[Tuple[datetime, int]] = field(default_factory=list)
    resolution_attempts: int = 0
    is_resolved: bool = False
    resolved_date: Optional[datetime] = None
    
    def to_dcp_observation(self) -> Dict[str, Any]:
        """Convert to DCP observation for AI strategic planning."""
        persistence_days = (self.last_seen - self.first_seen).days
        
        # Determine strategic importance based on persistence
        if persistence_days > 90:
            strategic_importance = 'critical'
        elif persistence_days > 30:
            strategic_importance = 'high'
        elif persistence_days > 14:
            strategic_importance = 'medium'
        else:
            strategic_importance = 'low'
            
        return {
            "type": "persistent_issue",
            "subtype": self.issue_type,
            "issue_id": self.issue_id,
            "location": {
                "file": self.file_path,
                "current_line": self.line_number
            },
            "persistence": {
                "first_seen": self.first_seen.isoformat(),
                "days_old": persistence_days,
                "sprint_count": self.sprint_count,
                "occurrences": self.occurrences
            },
            "strategic_importance": strategic_importance,
            "ai_assessment": self._generate_ai_assessment(persistence_days),
            "movement_pattern": self._analyze_movement_pattern()
        }
        
    def _generate_ai_assessment(self, persistence_days: int) -> str:
        """Generate strategic assessment for AI commander."""
        if self.issue_type == 'todo_comment' and persistence_days > 60:
            return "Long-standing TODO indicates deferred work that may be blocking progress. Consider prioritizing or removing if obsolete."
        elif self.issue_type == 'fixme_comment' and persistence_days > 30:
            return "Persistent FIXME suggests known bug or hack. Technical debt is accumulating - plan refactoring sprint."
        elif self.issue_type == 'high_complexity' and self.sprint_count > 3:
            return "Complex code surviving multiple sprints increases maintenance risk. Schedule dedicated refactoring."
        elif self.resolution_attempts > 2:
            return "Multiple failed resolution attempts indicate deeper architectural issues. Consider broader refactoring."
        else:
            return "Monitor for further persistence. May become strategic concern if not addressed soon."
            
    def _analyze_movement_pattern(self) -> str:
        """Analyze how the issue has moved through the codebase."""
        if not self.line_number_changes:
            return "static"
        
        # Calculate line number drift
        movements = [change[1] for change in self.line_number_changes]
        if len(movements) > 1:
            total_drift = abs(movements[-1] - movements[0])
            if total_drift > 50:
                return "significant_movement"
            elif total_drift > 10:
                return "moderate_movement"
        
        return "minor_movement"


class EvolutionTracker:
    """Tracks evolution of code issues across time for strategic intelligence.
    
    General Staff Role: Provides historical perspective on technical debt
    to inform AI strategic planning and prioritization.
    """
    
    def __init__(self, db_path: Optional[str] = None, dcp_path: Optional[str] = None):
        """Initialize evolution tracker with persistence.
        
        Args:
            db_path: Path to SQLite database for historical data
            dcp_path: Path to DCP for coordination
        """
        self.dcp_path = dcp_path
        self.db_path = db_path or "evolution_tracker.db"
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for tracking evolution."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enable WAL mode for better concurrent access
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        
        # Optimize SQLite performance
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS issue_evolution (
                issue_id TEXT PRIMARY KEY,
                issue_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                current_line INTEGER NOT NULL,
                first_seen TIMESTAMP NOT NULL,
                last_seen TIMESTAMP NOT NULL,
                occurrences INTEGER DEFAULT 1,
                sprint_count INTEGER DEFAULT 1,
                severity_history TEXT,  -- JSON array
                line_history TEXT,      -- JSON array
                resolution_attempts INTEGER DEFAULT 0,
                is_resolved BOOLEAN DEFAULT FALSE,
                resolved_date TIMESTAMP,
                issue_content TEXT,     -- For generating consistent IDs
                metadata TEXT          -- JSON for extensibility
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_file_path ON issue_evolution(file_path);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issue_type ON issue_evolution(issue_type);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_resolved ON issue_evolution(is_resolved);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_persistence ON issue_evolution(
                first_seen, last_seen, sprint_count
            );
        """)
        
        conn.commit()
        conn.close()
        
    def track_issues(self, issues: List[CodeIssue], sprint_id: Optional[str] = None):
        """Track a batch of issues, updating evolution history.
        
        Args:
            issues: List of current issues found
            sprint_id: Current sprint identifier
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_time = datetime.now()
        current_sprint = sprint_id or self._estimate_sprint_id()
        
        # Track which issues we've seen this run
        seen_issue_ids = set()
        
        for issue in issues:
            issue_id = self._generate_issue_id(issue)
            seen_issue_ids.add(issue_id)
            
            # Check if we've seen this issue before
            cursor.execute("""
                SELECT issue_id, occurrences, sprint_count, severity_history, 
                       line_history, first_seen
                FROM issue_evolution 
                WHERE issue_id = ?
            """, (issue_id,))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing issue
                occurrences = existing[1] + 1
                sprint_count = existing[2]
                severity_history = json.loads(existing[3])
                line_history = json.loads(existing[4])
                first_seen = datetime.fromisoformat(existing[5])
                
                # Check if this is a new sprint
                days_since_first = (current_time - first_seen).days
                estimated_sprints = max(1, days_since_first // 14)  # 2-week sprints
                if estimated_sprints > sprint_count:
                    sprint_count = estimated_sprints
                
                # Track severity changes
                if not severity_history or severity_history[-1][1] != issue.severity:
                    severity_history.append([current_time.isoformat(), issue.severity])
                    
                # Track line number changes
                if not line_history or line_history[-1][1] != issue.line_number:
                    line_history.append([current_time.isoformat(), issue.line_number])
                
                cursor.execute("""
                    UPDATE issue_evolution 
                    SET current_line = ?, last_seen = ?, occurrences = ?, 
                        sprint_count = ?, severity_history = ?, line_history = ?
                    WHERE issue_id = ?
                """, (
                    issue.line_number, current_time, occurrences, sprint_count,
                    json.dumps(severity_history), json.dumps(line_history),
                    issue_id
                ))
            else:
                # New issue
                severity_history = [[current_time.isoformat(), issue.severity]]
                line_history = [[current_time.isoformat(), issue.line_number]]
                
                cursor.execute("""
                    INSERT INTO issue_evolution (
                        issue_id, issue_type, file_path, current_line, first_seen, 
                        last_seen, occurrences, sprint_count, severity_history, 
                        line_history, issue_content, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    issue_id, issue.issue_type, issue.file_path, issue.line_number,
                    current_time, current_time, 1, 1,
                    json.dumps(severity_history), json.dumps(line_history),
                    issue.description, json.dumps(issue.metadata)
                ))
        
        # Mark resolved issues (not seen in this run but were active)
        if seen_issue_ids:
            self._mark_resolved_in_chunks(cursor, seen_issue_ids, current_time)
        
        conn.commit()
        conn.close()
    
    def _mark_resolved_in_chunks(self, cursor: sqlite3.Cursor, seen_issue_ids: Set[str], current_time: datetime):
        """Mark resolved issues in chunks to avoid SQLite parameter limits.
        
        SQLite has a limit of 999 parameters per query, so we chunk large sets.
        
        Args:
            cursor: Database cursor
            seen_issue_ids: Set of issue IDs that are still active
            current_time: Current timestamp
        """
        chunk_size = 400  # Stay well under SQLite's 999 limit (need 2x for the query)
        issue_list = list(seen_issue_ids)
        
        for i in range(0, len(issue_list), chunk_size):
            chunk = issue_list[i:i + chunk_size]
            placeholders = ','.join('?' * len(chunk))
            
            cursor.execute(f"""
                UPDATE issue_evolution 
                SET is_resolved = TRUE, resolved_date = ?
                WHERE file_path IN (
                    SELECT DISTINCT file_path FROM issue_evolution 
                    WHERE issue_id IN ({placeholders})
                ) AND issue_id NOT IN ({placeholders})
                AND is_resolved = FALSE
            """, [current_time] + chunk + chunk)
        
    def get_persistent_issues(self, min_days: int = 14, 
                            min_sprints: int = 2) -> List[IssueEvolution]:
        """Get issues that have persisted beyond thresholds.
        
        Args:
            min_days: Minimum days of persistence
            min_sprints: Minimum number of sprints
            
        Returns:
            List of persistent issues for AI strategic planning
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=min_days)
        
        cursor.execute("""
            SELECT issue_id, issue_type, file_path, current_line, first_seen,
                   last_seen, occurrences, sprint_count, severity_history,
                   line_history, resolution_attempts, is_resolved, resolved_date
            FROM issue_evolution
            WHERE first_seen <= ? 
            AND sprint_count >= ?
            AND is_resolved = FALSE
            ORDER BY sprint_count DESC, occurrences DESC
        """, (cutoff_date, min_sprints))
        
        persistent_issues = []
        for row in cursor.fetchall():
            evolution = IssueEvolution(
                issue_id=row[0],
                issue_type=row[1],
                file_path=row[2],
                line_number=row[3],
                first_seen=datetime.fromisoformat(row[4]),
                last_seen=datetime.fromisoformat(row[5]),
                occurrences=row[6],
                sprint_count=row[7],
                severity_changes=[(datetime.fromisoformat(t), s) 
                                for t, s in json.loads(row[8])],
                line_number_changes=[(datetime.fromisoformat(t), l) 
                                   for t, l in json.loads(row[9])],
                resolution_attempts=row[10],
                is_resolved=bool(row[11]),
                resolved_date=datetime.fromisoformat(row[12]) if row[12] else None
            )
            persistent_issues.append(evolution)
        
        conn.close()
        return persistent_issues
        
    def get_evolution_report(self) -> Dict[str, Any]:
        """Generate comprehensive evolution report for AI assessment.
        
        Returns:
            Report optimized for AI strategic planning
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get summary statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_tracked,
                COUNT(CASE WHEN is_resolved = FALSE THEN 1 END) as active_issues,
                COUNT(CASE WHEN sprint_count >= 3 AND is_resolved = FALSE THEN 1 END) as chronic_issues,
                AVG(CASE WHEN is_resolved = FALSE THEN sprint_count END) as avg_persistence,
                MAX(sprint_count) as max_persistence
            FROM issue_evolution
        """)
        
        stats = cursor.fetchone()
        
        # Get issues by type
        cursor.execute("""
            SELECT issue_type, COUNT(*) as count, AVG(sprint_count) as avg_sprints
            FROM issue_evolution
            WHERE is_resolved = FALSE
            GROUP BY issue_type
            ORDER BY count DESC
        """)
        
        issues_by_type = [
            {"type": row[0], "count": row[1], "avg_persistence": row[2]}
            for row in cursor.fetchall()
        ]
        
        # Get most persistent issues
        persistent_issues = self.get_persistent_issues(min_days=30, min_sprints=3)
        
        conn.close()
        
        return {
            "summary": {
                "total_tracked": stats[0],
                "active_issues": stats[1],
                "chronic_issues": stats[2],
                "average_persistence_sprints": stats[3],
                "max_persistence_sprints": stats[4]
            },
            "issues_by_type": issues_by_type,
            "most_persistent": [
                {
                    "file": issue.file_path,
                    "type": issue.issue_type,
                    "sprints": issue.sprint_count,
                    "days": (issue.last_seen - issue.first_seen).days
                }
                for issue in persistent_issues[:10]
            ],
            "ai_recommendations": self._generate_strategic_recommendations(
                stats, issues_by_type, persistent_issues
            )
        }
        
    def _generate_issue_id(self, issue: CodeIssue) -> str:
        """Generate consistent ID for tracking issues across time.
        
        Args:
            issue: Code issue to generate ID for
            
        Returns:
            Unique identifier based on issue characteristics
        """
        # Create ID from stable characteristics
        id_components = [
            issue.issue_type,
            issue.file_path,
            issue.entity_name,
            # Use first 50 chars of description to handle minor changes
            issue.description[:50] if len(issue.description) > 50 else issue.description
        ]
        
        id_string = '|'.join(id_components)
        return hashlib.sha256(id_string.encode()).hexdigest()[:16]
        
    def _estimate_sprint_id(self) -> str:
        """Estimate current sprint based on date.
        
        Returns:
            Sprint identifier
        """
        # Simple 2-week sprint estimation
        base_date = datetime(2024, 1, 1)  # Arbitrary sprint 1 start
        days_since = (datetime.now() - base_date).days
        sprint_number = (days_since // 14) + 1
        return f"sprint_{sprint_number}"
        
    def _generate_strategic_recommendations(self, stats: Tuple, 
                                          issues_by_type: List[Dict],
                                          persistent_issues: List[IssueEvolution]) -> List[str]:
        """Generate AI-focused strategic recommendations.
        
        Args:
            stats: Summary statistics
            issues_by_type: Breakdown by issue type
            persistent_issues: Most persistent issues
            
        Returns:
            Strategic recommendations for AI commander
        """
        recommendations = []
        
        # Check for chronic technical debt
        if stats[2] > 10:  # chronic_issues
            recommendations.append(
                f"TECHNICAL DEBT ALERT: {stats[2]} issues have persisted for 3+ sprints. "
                "Schedule a dedicated debt reduction sprint to prevent compound interest."
            )
        
        # Check for TODO accumulation
        todo_stats = next((t for t in issues_by_type if t['type'] == 'todo_comment'), None)
        if todo_stats and todo_stats['count'] > 20:
            recommendations.append(
                f"TODO OVERFLOW: {todo_stats['count']} unresolved TODOs averaging "
                f"{todo_stats['avg_persistence']:.1f} sprints old. Review and either "
                "implement or remove obsolete items."
            )
        
        # Check for complexity debt
        complexity_issues = [p for p in persistent_issues if p.issue_type == 'high_complexity']
        if len(complexity_issues) > 5:
            recommendations.append(
                f"COMPLEXITY CRISIS: {len(complexity_issues)} high-complexity functions "
                "persisting across sprints. Prioritize refactoring to improve maintainability."
            )
        
        # Check for security debt
        security_issues = [p for p in persistent_issues if 'security' in p.issue_type]
        if security_issues:
            recommendations.append(
                f"SECURITY RISK: {len(security_issues)} security issues persisting. "
                "These should be highest priority for immediate resolution."
            )
        
        return recommendations