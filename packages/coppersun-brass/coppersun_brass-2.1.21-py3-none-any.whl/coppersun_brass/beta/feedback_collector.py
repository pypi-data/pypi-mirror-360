#!/usr/bin/env python3
"""
Beta Feedback Collection System for Copper Alloy Brass v1.0
Collects, stores, and analyzes beta tester feedback.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from coppersun_brass.core.security import validate_string, InputValidationError


class FeedbackType(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    PERFORMANCE = "performance"
    USABILITY = "usability"
    DOCUMENTATION = "documentation"
    OTHER = "other"


class FeedbackPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackStatus(str, Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    WONT_FIX = "wont_fix"


class FeedbackSubmission(BaseModel):
    type: FeedbackType
    priority: FeedbackPriority = FeedbackPriority.MEDIUM
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    steps_to_reproduce: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    environment: Optional[Dict[str, str]] = None
    user_email: Optional[EmailStr] = None
    api_version: str = "1.0.0-beta"


class FeedbackResponse(BaseModel):
    id: str
    status: FeedbackStatus
    message: str
    created_at: str


class FeedbackCollector:
    """Manages beta feedback collection and storage."""
    
    def __init__(self, db_path: Path = Path("beta_feedback.db")):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize feedback database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                steps_to_reproduce TEXT,
                expected_behavior TEXT,
                actual_behavior TEXT,
                environment TEXT,
                user_email TEXT,
                api_version TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                resolution_notes TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_id TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feedback_id) REFERENCES feedback(id)
            )
        """)
        
        conn.commit()
        conn.close()
        
    def submit_feedback(self, feedback: FeedbackSubmission) -> FeedbackResponse:
        """Submit new feedback."""
        feedback_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO feedback (
                    id, type, priority, title, description,
                    steps_to_reproduce, expected_behavior, actual_behavior,
                    environment, user_email, api_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback_id,
                feedback.type.value,
                feedback.priority.value,
                feedback.title,
                feedback.description,
                feedback.steps_to_reproduce,
                feedback.expected_behavior,
                feedback.actual_behavior,
                json.dumps(feedback.environment) if feedback.environment else None,
                feedback.user_email,
                feedback.api_version
            ))
            
            conn.commit()
            
            # Send notification for high priority items
            if feedback.priority in [FeedbackPriority.HIGH, FeedbackPriority.CRITICAL]:
                self._send_notification(feedback_id, feedback)
            
            return FeedbackResponse(
                id=feedback_id,
                status=FeedbackStatus.NEW,
                message="Thank you for your feedback! We'll review it shortly.",
                created_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {e}")
        finally:
            conn.close()
            
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {
            'total': 0,
            'by_type': {},
            'by_priority': {},
            'by_status': {},
            'response_times': []
        }
        
        # Total feedback
        cursor.execute("SELECT COUNT(*) FROM feedback")
        stats['total'] = cursor.fetchone()[0]
        
        # By type
        cursor.execute("""
            SELECT type, COUNT(*) FROM feedback 
            GROUP BY type
        """)
        stats['by_type'] = dict(cursor.fetchall())
        
        # By priority
        cursor.execute("""
            SELECT priority, COUNT(*) FROM feedback 
            GROUP BY priority
        """)
        stats['by_priority'] = dict(cursor.fetchall())
        
        # By status
        cursor.execute("""
            SELECT status, COUNT(*) FROM feedback 
            GROUP BY status
        """)
        stats['by_status'] = dict(cursor.fetchall())
        
        # Average resolution time
        cursor.execute("""
            SELECT AVG(julianday(resolved_at) - julianday(created_at)) * 24
            FROM feedback
            WHERE resolved_at IS NOT NULL
        """)
        avg_resolution = cursor.fetchone()[0]
        stats['avg_resolution_hours'] = avg_resolution if avg_resolution else 0
        
        conn.close()
        return stats
        
    def get_recent_feedback(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent feedback submissions."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM feedback
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        feedback = []
        for row in cursor.fetchall():
            item = dict(row)
            if item['environment']:
                item['environment'] = json.loads(item['environment'])
            feedback.append(item)
            
        conn.close()
        return feedback
        
    def update_feedback_status(self, 
                             feedback_id: str, 
                             status: FeedbackStatus,
                             notes: Optional[str] = None):
        """Update feedback status."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE feedback 
                SET status = ?, 
                    updated_at = CURRENT_TIMESTAMP,
                    resolved_at = CASE WHEN ? = 'resolved' THEN CURRENT_TIMESTAMP ELSE resolved_at END,
                    resolution_notes = COALESCE(?, resolution_notes)
                WHERE id = ?
            """, (status.value, status.value, notes, feedback_id))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Feedback not found")
                
            conn.commit()
        finally:
            conn.close()
            
    def _send_notification(self, feedback_id: str, feedback: FeedbackSubmission):
        """Send notification for high priority feedback."""
        # This would integrate with Slack, email, etc.
        # For now, just log
        print(f"HIGH PRIORITY FEEDBACK: {feedback_id}")
        print(f"Type: {feedback.type}, Priority: {feedback.priority}")
        print(f"Title: {feedback.title}")


class FeedbackAnalyzer:
    """Analyzes feedback patterns and trends."""
    
    def __init__(self, collector: FeedbackCollector):
        self.collector = collector
        
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze feedback trends."""
        stats = self.collector.get_feedback_stats()
        recent = self.collector.get_recent_feedback(100)
        
        analysis = {
            'summary': stats,
            'trends': {},
            'common_issues': [],
            'recommendations': []
        }
        
        # Identify trends
        if stats['total'] > 0:
            # High bug rate
            bug_rate = stats['by_type'].get('bug', 0) / stats['total']
            if bug_rate > 0.4:
                analysis['trends']['high_bug_rate'] = bug_rate
                analysis['recommendations'].append(
                    "High bug rate detected. Consider additional testing."
                )
            
            # Many performance issues
            perf_issues = stats['by_type'].get('performance', 0)
            if perf_issues > 5:
                analysis['trends']['performance_concerns'] = perf_issues
                analysis['recommendations'].append(
                    "Multiple performance issues reported. Review optimization."
                )
            
            # Critical issues
            critical = stats['by_priority'].get('critical', 0)
            if critical > 0:
                analysis['trends']['critical_issues'] = critical
                analysis['recommendations'].append(
                    f"{critical} critical issues need immediate attention."
                )
        
        # Find common themes
        titles = [f['title'].lower() for f in recent]
        common_words = {}
        for title in titles:
            for word in title.split():
                if len(word) > 4:  # Skip short words
                    common_words[word] = common_words.get(word, 0) + 1
        
        # Top issues
        analysis['common_issues'] = sorted(
            common_words.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return analysis


# FastAPI app for feedback API
app = FastAPI(title="Copper Alloy Brass Beta Feedback API")
collector = FeedbackCollector()
analyzer = FeedbackAnalyzer(collector)


@app.post("/api/v1/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackSubmission):
    """Submit beta feedback."""
    return collector.submit_feedback(feedback)


@app.get("/api/v1/feedback/stats")
async def get_feedback_stats():
    """Get feedback statistics."""
    return collector.get_feedback_stats()


@app.get("/api/v1/feedback/recent")
async def get_recent_feedback(limit: int = 10):
    """Get recent feedback."""
    return collector.get_recent_feedback(limit)


@app.get("/api/v1/feedback/analysis")
async def analyze_feedback():
    """Analyze feedback trends."""
    return analyzer.analyze_trends()


@app.put("/api/v1/feedback/{feedback_id}/status")
async def update_feedback_status(
    feedback_id: str,
    status: FeedbackStatus,
    notes: Optional[str] = None
):
    """Update feedback status."""
    collector.update_feedback_status(feedback_id, status, notes)
    return {"message": "Status updated successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)