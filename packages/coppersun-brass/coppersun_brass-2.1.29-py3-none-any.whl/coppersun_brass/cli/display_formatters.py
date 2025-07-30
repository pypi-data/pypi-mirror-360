#!/usr/bin/env python3
"""
Display Formatters for Scout CLI Commands

Rich formatting classes for displaying Scout analysis results with progressive disclosure,
security issue highlighting, and comprehensive code quality insights.
"""

import json
from typing import List, Dict, Any, Optional, Union
from pathlib import Path


class ScoutResultsFormatter:
    """Format Scout analysis results for CLI display with progressive disclosure."""
    
    def __init__(self, detail_level: str = 'normal', limit: int = 20):
        """Initialize formatter with display preferences.
        
        Args:
            detail_level: Display mode - 'summary', 'normal', or 'verbose'
            limit: Maximum number of items to display per category
        """
        self.detail_level = detail_level
        self.limit = limit
        
    def format_results(self, results, format_type: str = 'table') -> str:
        """Format complete Scout results for display.
        
        Args:
            results: Scout analysis results object
            format_type: Output format - 'table', 'json', or 'markdown'
            
        Returns:
            Formatted string for display
        """
        if format_type == 'json':
            return self._format_json(results)
        elif format_type == 'markdown':
            return self._format_markdown(results)
        else:
            return self._format_table(results)
    
    def _format_table(self, results) -> str:
        """Format results as rich table display."""
        output = []
        
        # Summary header
        total_findings = len(results.todo_findings) + len(results.ast_results) + len(results.pattern_results)
        output.append(f"✅ Scout Analysis Complete - {total_findings} findings")
        
        if self.detail_level == 'summary':
            return self._format_summary_only(results)
        
        # TODO findings
        if results.todo_findings:
            output.append("\n📝 TODO Findings:")
            output.extend(self._format_todo_findings(results.todo_findings))
        
        # Security/Pattern findings
        if results.pattern_results:
            output.append("\n🚨 Security & Pattern Issues:")
            output.extend(self._format_pattern_results(results.pattern_results))
        
        # Code analysis findings
        if results.ast_results:
            output.append("\n🔍 Code Analysis:")
            output.extend(self._format_ast_results(results.ast_results))
        
        return "\n".join(output)
    
    def _format_summary_only(self, results) -> str:
        """Format minimal summary display (current behavior)."""
        output = [f"✅ Scan complete - found {len(results.todo_findings) + len(results.ast_results) + len(results.pattern_results)} findings"]
        
        # Show first 5 TODOs with basic display
        for finding in results.todo_findings[:5]:
            content = finding.content[:50] + ('...' if len(finding.content) > 50 else '')
            output.append(f"  📝 TODO: {content}")
        
        return "\n".join(output)
    
    def _format_todo_findings(self, findings) -> List[str]:
        """Format TODO findings with rich details."""
        output = []
        display_count = min(self.limit, len(findings))
        
        for i, finding in enumerate(findings[:display_count]):
            if self.detail_level == 'verbose':
                output.extend(self._format_todo_verbose(finding, i + 1))
            else:
                output.append(self._format_todo_normal(finding, i + 1))
        
        if len(findings) > display_count:
            output.append(f"  ... and {len(findings) - display_count} more TODO items")
        
        return output
    
    def _format_todo_normal(self, finding, index: int) -> str:
        """Format single TODO with normal detail level."""
        # Get attributes with safe defaults
        file_path = getattr(finding, 'file_path', 'unknown')
        line_number = getattr(finding, 'line_number', 0)
        content = getattr(finding, 'content', 'No content')
        confidence = getattr(finding, 'confidence', 0.0)
        security_risk = getattr(finding, 'security_risk', 'unknown')
        
        # Format file path
        if hasattr(file_path, 'name'):
            file_display = f"{file_path.name}:{line_number}"
        else:
            file_display = f"{Path(str(file_path)).name}:{line_number}"
        
        # Priority indicator based on confidence
        if confidence > 0.8:
            priority = "🔴 HIGH"
        elif confidence > 0.6:
            priority = "🟡 MEDIUM"
        else:
            priority = "🟢 LOW"
        
        # Security risk indicator
        risk_indicator = ""
        if security_risk and security_risk.lower() in ['critical', 'high']:
            risk_indicator = " 🚨"
        
        return f"  {index:2d}. {priority} {file_display} - {content[:60]}{'...' if len(content) > 60 else ''}{risk_indicator}"
    
    def _format_todo_verbose(self, finding, index: int) -> List[str]:
        """Format single TODO with verbose detail level."""
        output = []
        
        # Get attributes with safe defaults
        file_path = getattr(finding, 'file_path', 'unknown')
        line_number = getattr(finding, 'line_number', 0)
        content = getattr(finding, 'content', 'No content')
        confidence = getattr(finding, 'confidence', 0.0)
        security_risk = getattr(finding, 'security_risk', 'unknown')
        performance_impact = getattr(finding, 'performance_impact', 'unknown')
        classification = getattr(finding, 'classification', 'unclassified')
        
        # Priority based on confidence
        if confidence > 0.8:
            priority_display = "🔴 HIGH PRIORITY"
        elif confidence > 0.6:
            priority_display = "🟡 MEDIUM PRIORITY"
        else:
            priority_display = "🟢 LOW PRIORITY"
        
        # Header
        output.append(f"  {index:2d}. {priority_display} (Confidence: {confidence:.1%})")
        
        # File location
        if hasattr(file_path, 'name'):
            output.append(f"      📁 File: {file_path}")
        else:
            output.append(f"      📁 File: {file_path}")
        
        if line_number > 0:
            output.append(f"      📍 Line: {line_number}")
        
        # Content
        output.append(f"      📝 Content: {content}")
        
        # Metadata
        if classification != 'unclassified':
            output.append(f"      🏷️  Type: {classification}")
        
        if security_risk and security_risk != 'unknown':
            output.append(f"      🔒 Security Risk: {security_risk}")
        
        if performance_impact and performance_impact != 'unknown':
            output.append(f"      ⚡ Performance Impact: {performance_impact}")
        
        output.append("")  # Blank line separator
        
        return output
    
    def _format_pattern_results(self, results) -> List[str]:
        """Format security and pattern analysis results."""
        output = []
        display_count = min(self.limit, len(results))
        
        for i, result in enumerate(results[:display_count]):
            if self.detail_level == 'verbose':
                output.extend(self._format_pattern_verbose(result, i + 1))
            else:
                output.append(self._format_pattern_normal(result, i + 1))
        
        if len(results) > display_count:
            output.append(f"  ... and {len(results) - display_count} more pattern issues")
        
        return output
    
    def _format_pattern_normal(self, result, index: int) -> str:
        """Format single pattern result with normal detail level."""
        # Get attributes with safe defaults
        result_type = getattr(result, 'type', 'unknown')
        file_path = getattr(result, 'file_path', 'unknown')
        severity = getattr(result, 'severity', 'unknown')
        
        # Format file path
        if hasattr(file_path, 'name'):
            file_display = file_path.name
        else:
            file_display = Path(str(file_path)).name
        
        # Severity indicator
        if severity and severity.lower() == 'critical':
            severity_icon = "🚨"
        elif severity and severity.lower() == 'high':
            severity_icon = "🔴"
        elif severity and severity.lower() == 'medium':
            severity_icon = "🟡"
        else:
            severity_icon = "🟢"
        
        return f"  {index:2d}. {severity_icon} {result_type} in {file_display}"
    
    def _format_pattern_verbose(self, result, index: int) -> List[str]:
        """Format single pattern result with verbose detail level."""
        output = []
        
        # Get attributes with safe defaults
        result_type = getattr(result, 'type', 'unknown')
        file_path = getattr(result, 'file_path', 'unknown')
        line_number = getattr(result, 'line_number', 0)
        severity = getattr(result, 'severity', 'unknown')
        description = getattr(result, 'description', 'No description')
        
        # Severity display
        if severity and severity.lower() == 'critical':
            severity_display = "🚨 CRITICAL"
        elif severity and severity.lower() == 'high':
            severity_display = "🔴 HIGH"
        elif severity and severity.lower() == 'medium':
            severity_display = "🟡 MEDIUM"
        else:
            severity_display = "🟢 LOW"
        
        # Header
        output.append(f"  {index:2d}. {severity_display} - {result_type}")
        
        # File location
        if hasattr(file_path, 'name'):
            output.append(f"      📁 File: {file_path}")
        else:
            output.append(f"      📁 File: {file_path}")
        
        if line_number and line_number > 0:
            output.append(f"      📍 Line: {line_number}")
        
        # Description
        if description and description != 'No description':
            output.append(f"      📋 Issue: {description}")
        
        # Additional metadata if available
        if hasattr(result, 'metadata') and result.metadata:
            for key, value in result.metadata.items():
                if key in ['cwe', 'owasp', 'pattern_name']:
                    output.append(f"      🏷️  {key.upper()}: {value}")
        
        output.append("")  # Blank line separator
        
        return output
    
    def _format_ast_results(self, results) -> List[str]:
        """Format AST analysis results."""
        output = []
        display_count = min(self.limit, len(results))
        
        for i, result in enumerate(results[:display_count]):
            if self.detail_level == 'verbose':
                output.extend(self._format_ast_verbose(result, i + 1))
            else:
                output.append(self._format_ast_normal(result, i + 1))
        
        if len(results) > display_count:
            output.append(f"  ... and {len(results) - display_count} more code analysis findings")
        
        return output
    
    def _format_ast_normal(self, result, index: int) -> str:
        """Format single AST result with normal detail level."""
        # Get attributes with safe defaults
        result_type = getattr(result, 'type', 'unknown')
        file_path = getattr(result, 'file_path', 'unknown')
        
        # Format file path
        if hasattr(file_path, 'name'):
            file_display = file_path.name
        else:
            file_display = Path(str(file_path)).name
        
        return f"  {index:2d}. 🔍 {result_type} in {file_display}"
    
    def _format_ast_verbose(self, result, index: int) -> List[str]:
        """Format single AST result with verbose detail level."""
        output = []
        
        # Get attributes with safe defaults
        result_type = getattr(result, 'type', 'unknown')
        file_path = getattr(result, 'file_path', 'unknown')
        
        # Header
        output.append(f"  {index:2d}. 🔍 Code Analysis - {result_type}")
        
        # File location
        if hasattr(file_path, 'name'):
            output.append(f"      📁 File: {file_path}")
        else:
            output.append(f"      📁 File: {file_path}")
        
        # Additional details if available
        if hasattr(result, 'entities') and result.entities:
            output.append(f"      🏗️  Entities: {len(result.entities)} found")
        
        if hasattr(result, 'complexity') and result.complexity:
            output.append(f"      🧮 Complexity: {result.complexity}")
        
        output.append("")  # Blank line separator
        
        return output
    
    def _format_json(self, results) -> str:
        """Format results as JSON for tool integration."""
        output = {
            'summary': {
                'total_findings': len(results.todo_findings) + len(results.ast_results) + len(results.pattern_results),
                'todo_count': len(results.todo_findings),
                'pattern_count': len(results.pattern_results),
                'ast_count': len(results.ast_results)
            },
            'findings': {
                'todos': self._serialize_findings(results.todo_findings),
                'patterns': self._serialize_findings(results.pattern_results),
                'ast': self._serialize_findings(results.ast_results)
            }
        }
        
        return json.dumps(output, indent=2, default=str)
    
    def _format_markdown(self, results) -> str:
        """Format results as structured markdown."""
        output = []
        
        # Header
        total_findings = len(results.todo_findings) + len(results.ast_results) + len(results.pattern_results)
        output.append(f"# Scout Analysis Report")
        output.append(f"**Total Findings**: {total_findings}")
        output.append("")
        
        # TODO section
        if results.todo_findings:
            output.append("## 📝 TODO Findings")
            for i, finding in enumerate(results.todo_findings[:self.limit]):
                content = getattr(finding, 'content', 'No content')
                file_path = getattr(finding, 'file_path', 'unknown')
                line_number = getattr(finding, 'line_number', 0)
                
                output.append(f"### {i+1}. {content}")
                output.append(f"- **File**: {file_path}")
                if line_number > 0:
                    output.append(f"- **Line**: {line_number}")
                output.append("")
        
        # Security/Pattern section
        if results.pattern_results:
            output.append("## 🚨 Security & Pattern Issues")
            for i, result in enumerate(results.pattern_results[:self.limit]):
                result_type = getattr(result, 'type', 'unknown')
                file_path = getattr(result, 'file_path', 'unknown')
                severity = getattr(result, 'severity', 'unknown')
                
                output.append(f"### {i+1}. {result_type}")
                output.append(f"- **File**: {file_path}")
                output.append(f"- **Severity**: {severity}")
                output.append("")
        
        return "\n".join(output)
    
    def _serialize_findings(self, findings) -> List[Dict[str, Any]]:
        """Serialize findings for JSON output."""
        serialized = []
        for finding in findings[:self.limit]:
            item = {}
            
            # Common attributes
            for attr in ['type', 'file_path', 'line_number', 'content', 'severity', 
                        'confidence', 'security_risk', 'performance_impact', 'classification']:
                if hasattr(finding, attr):
                    value = getattr(finding, attr)
                    if hasattr(value, '__str__'):
                        item[attr] = str(value)
                    else:
                        item[attr] = value
            
            # Metadata if available
            if hasattr(finding, 'metadata') and finding.metadata:
                item['metadata'] = finding.metadata
            
            serialized.append(item)
        
        return serialized