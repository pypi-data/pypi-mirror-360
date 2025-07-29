"""
Slack Message Formatter

General Staff G6 Role: Message Composition
Formats Copper Alloy Brass insights into clear, actionable Slack messages
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class MessageFormatter:
    """
    Formats Copper Alloy Brass data into Slack Block Kit messages
    
    General Staff G6 Function: Translates complex AI analysis
    into human-readable strategic communications.
    """
    
    def __init__(self):
        """Initialize formatter with style preferences"""
        self.max_text_length = 3000
        self.max_blocks = 50
        
        # Emoji mappings for visual clarity
        self.priority_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        self.type_emoji = {
            'BUG': '🐛',
            'TODO': '📝',
            'FIXME': '🔧',
            'HACK': '⚡',
            'OPTIMIZE': '⚙️',
            'SECURITY': '🔒',
            'DEPRECATED': '⚠️'
        }
    
    def format_analysis_results(self, 
                              analysis_type: str,
                              results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format analysis results into Slack blocks"""
        blocks = []
        
        # Header
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{analysis_type.title()} Analysis Complete"
            }
        })
        
        # Summary section
        summary = results.get('summary', {})
        if summary:
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Files Analyzed:*\n{summary.get('files_analyzed', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Issues Found:*\n{summary.get('issues_found', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Patterns Detected:*\n{summary.get('patterns_detected', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Confidence:*\n{summary.get('confidence', 0):.1%}"
                    }
                ]
            })
        
        # Key findings
        findings = results.get('findings', [])[:5]  # Top 5
        if findings:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Key Findings:*"
                }
            })
            
            for finding in findings:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• {finding.get('description', 'Unknown finding')}"
                    }
                })
        
        # Recommendations
        recommendations = results.get('recommendations', [])[:3]
        if recommendations:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Recommended Actions:*"
                }
            })
            
            for i, rec in enumerate(recommendations, 1):
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{i}. {rec.get('action', 'Unknown action')}"
                    }
                })
        
        # Context
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        })
        
        return blocks[:self.max_blocks]
    
    def format_todo_alert(self, todo: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format high-priority TODO as alert"""
        priority = todo.get('priority_label', 'high')
        todo_type = todo.get('type', 'TODO')
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{self.priority_emoji.get(priority, '🟠')} *High Priority {todo_type}*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*File:*\n`{todo.get('file', 'Unknown')}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Line:*\n{todo.get('line', 'Unknown')}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{todo.get('description', 'No description')}"
                }
            }
        ]
        
        # Add context if available
        if todo.get('context'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Context:*\n```{todo['context']}```"
                }
            })
        
        # Add metadata
        metadata = []
        if todo.get('assignee'):
            metadata.append(f"Assigned to: {todo['assignee']}")
        if todo.get('tags'):
            metadata.append(f"Tags: {', '.join(todo['tags'])}")
        
        if metadata:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": " | ".join(metadata)
                    }
                ]
            })
        
        return blocks
    
    def format_todo_batch(self, todos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format multiple TODOs in a batch"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📋 {len(todos)} TODOs Found"
                }
            }
        ]
        
        # Group by priority
        by_priority = {}
        for todo in todos:
            priority = todo.get('priority_label', 'medium')
            if priority not in by_priority:
                by_priority[priority] = []
            by_priority[priority].append(todo)
        
        # Format each priority group
        for priority in ['critical', 'high', 'medium', 'low']:
            if priority not in by_priority:
                continue
                
            priority_todos = by_priority[priority]
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{self.priority_emoji[priority]} *{priority.title()} Priority ({len(priority_todos)})*"
                }
            })
            
            # Show first 3 from each priority
            for todo in priority_todos[:3]:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• `{todo.get('file', 'Unknown')}:{todo.get('line', '?')}` - {todo.get('description', 'No description')[:100]}"
                    }
                })
            
            if len(priority_todos) > 3:
                blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"_...and {len(priority_todos) - 3} more_"
                        }
                    ]
                })
        
        return blocks[:self.max_blocks]
    
    def format_test_failure(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format test failure notification"""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "❌ *Test Suite Failed*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Tests:*\n{results.get('total_count', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Failed:*\n{results.get('failed_count', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Passed:*\n{results.get('passed_count', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Duration:*\n{results.get('duration', 'Unknown')}"
                    }
                ]
            }
        ]
        
        # Show failed tests
        failures = results.get('failures', [])[:5]
        if failures:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Failed Tests:*"
                }
            })
            
            for test in failures:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• `{test.get('name', 'Unknown')}` - {test.get('error', 'No error message')[:100]}"
                    }
                })
        
        return blocks
    
    def format_test_success(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format test success notification"""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "✅ *All Tests Passed!*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Tests:*\n{results.get('total_count', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Duration:*\n{results.get('duration', 'Unknown')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Coverage:*\n{results.get('coverage', 'Unknown')}"
                    }
                ]
            }
        ]
        
        return blocks
    
    def format_recommendation(self, 
                            recommendation: Dict[str, Any],
                            context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format strategic recommendation"""
        confidence = recommendation.get('confidence', 0)
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"💡 *Strategic Recommendation*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{recommendation.get('title', 'Recommendation')}*\n\n{recommendation.get('description', 'No description provided')}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Confidence:*\n{confidence:.1%}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Impact:*\n{recommendation.get('impact', 'Unknown')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Effort:*\n{recommendation.get('effort', 'Unknown')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Priority:*\n{recommendation.get('priority', 'Medium')}"
                    }
                ]
            }
        ]
        
        # Add reasoning
        if recommendation.get('reasoning'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Reasoning:*\n{recommendation['reasoning']}"
                }
            })
        
        # Add next steps
        steps = recommendation.get('next_steps', [])
        if steps:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Suggested Next Steps:*"
                }
            })
            
            for i, step in enumerate(steps[:3], 1):
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{i}. {step}"
                    }
                })
        
        # Add voting actions
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Accept"
                    },
                    "style": "primary",
                    "value": f"accept_{recommendation.get('id', 'unknown')}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Reject"
                    },
                    "style": "danger",
                    "value": f"reject_{recommendation.get('id', 'unknown')}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "More Info"
                    },
                    "value": f"info_{recommendation.get('id', 'unknown')}"
                }
            ]
        })
        
        return blocks
    
    def format_daily_report(self, 
                          stats: Dict[str, Any],
                          performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format daily report summary"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Daily Copper Alloy Brass Report"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Date:* {datetime.now().strftime('%Y-%m-%d')}"
                }
            },
            {"type": "divider"}
        ]
        
        # Activity summary
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📈 Activity Summary*"
            }
        })
        
        blocks.append({
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Total Events:*\n{stats.get('total_observations', 0)}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*High Priority:*\n{stats.get('high_priority', 0)}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Errors:*\n{stats.get('errors', 0)}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Active Agents:*\n{len(stats.get('by_agent', {}))}"
                }
            ]
        })
        
        # Top agents
        if stats.get('by_agent'):
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🤖 Most Active Agents*"
                }
            })
            
            top_agents = sorted(
                stats['by_agent'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            for agent, count in top_agents:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• *{agent}*: {count} events"
                    }
                })
        
        # Performance metrics
        if performance:
            cache_stats = performance.get('cache', {}).get('statistics', {})
            if cache_stats:
                blocks.append({"type": "divider"})
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*⚡ Performance*"
                    }
                })
                
                blocks.append({
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Cache Hit Rate:*\n{cache_stats.get('hit_rate', 0):.1%}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Hits:*\n{cache_stats.get('total_hits', 0)}"
                        }
                    ]
                })
        
        # Footer
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "Generated by Copper Alloy Brass General Staff | View detailed report in thread"
                }
            ]
        })
        
        return blocks[:self.max_blocks]