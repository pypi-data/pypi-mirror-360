"""
Output Generator for Copper Alloy Brass

Generates JSON output files for Claude Code to read.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

from coppersun_brass.core.storage import BrassStorage
from coppersun_brass.config import BrassConfig
from coppersun_brass.integrations.content_safety import DualPurposeContentSafety

logger = logging.getLogger(__name__)


class OutputGenerator:
    """Generates structured output files for AI consumption."""
    
    def __init__(self, config: BrassConfig, storage: BrassStorage):
        """
        Initialize output generator.
        
        Args:
            config: Copper Alloy Brass configuration
            storage: Storage instance
        """
        self.config = config
        self.storage = storage
        self.output_dir = config.output_dir
        
        # Initialize content safety for Phase 3 customer-facing security analysis
        self.content_safety = DualPurposeContentSafety()
        logger.info("Content safety system initialized for customer security analysis")
        
    def generate_analysis_report(self) -> Path:
        """
        Generate comprehensive analysis report.
        
        Returns:
            Path to generated report file
        """
        # Get all observations
        observations = self.storage.get_all_observations()
        
        # Group by type
        grouped = {}
        for obs in observations:
            obs_type = obs['type']
            if obs_type not in grouped:
                grouped[obs_type] = []
            grouped[obs_type].append(obs)
        
        # Get resolution metrics for the report
        resolution_metrics = self.storage.get_resolution_metrics()
        
        # Create report structure
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'project_path': str(self.config.project_root),
                'total_observations': len(observations),
                'brass_version': '1.0.0'
            },
            'summary': {
                'total_todos': len(grouped.get('todo', [])),
                'total_files_analyzed': len(grouped.get('scout_analysis_summary', [])),
                'critical_issues': self._count_critical_issues(observations),
                'by_type': {k: len(v) for k, v in grouped.items()},
                'resolution_metrics': resolution_metrics
            },
            'todos': self._format_todos(grouped.get('todo', [])),
            'issues': self._format_issues(observations),
            'file_summaries': self._format_file_summaries(grouped.get('scout_analysis_summary', []))
        }
        
        # Write report
        report_path = self.output_dir / 'analysis_report.json'
        report_path.write_text(json.dumps(report, indent=2))
        logger.info(f"Generated analysis report: {report_path}")
        
        return report_path
    
    def generate_todo_list(self) -> Path:
        """
        Generate a focused TODO list.
        
        Returns:
            Path to generated TODO file
        """
        # Get only recent active (unresolved) TODOs from the last 24 hours to avoid duplicates
        # from multiple runs and exclude resolved TODOs
        since = datetime.now() - timedelta(hours=24)
        todos = self.storage.get_observations(obs_type='todo', since=since)
        
        # Filter out resolved TODOs
        active_todos = [todo for todo in todos if not todo.get('resolved', False)]
        
        # Deduplicate TODOs by file+line+content
        seen = set()
        unique_todos = []
        for todo in active_todos:
            data = todo.get('data', {})
            key = (data.get('file', ''), data.get('line', 0), data.get('content', ''))
            if key not in seen:
                seen.add(key)
                unique_todos.append(todo)
        
        # Sort by priority
        unique_todos.sort(key=lambda x: x.get('priority', 50), reverse=True)
        
        # Get resolution metrics for enhanced reporting
        resolution_metrics = self.storage.get_resolution_metrics()
        
        todo_list = {
            'generated_at': datetime.now().isoformat(),
            'total_todos': len(unique_todos),
            'resolution_metrics': resolution_metrics,
            'todos': [
                {
                    'file': todo.get('data', {}).get('file', 'unknown'),
                    'line': todo.get('data', {}).get('line', 0),
                    'content': todo.get('data', {}).get('content', ''),
                    'priority': todo.get('priority', 50),
                    'classification': todo.get('data', {}).get('classification', 'unclassified')
                }
                for todo in unique_todos
            ]
        }
        
        # Write TODO list
        todo_path = self.output_dir / 'todos.json'
        todo_path.write_text(json.dumps(todo_list, indent=2))
        logger.info(f"Generated TODO list: {todo_path}")
        
        return todo_path
    
    def generate_project_context(self) -> Path:
        """
        Generate project context information.
        
        Returns:
            Path to generated context file
        """
        # Get statistics
        stats = self.storage.get_activity_stats()
        
        context = {
            'project': {
                'path': str(self.config.project_root),
                'name': self.config.project_root.name,
                'analyzed_at': datetime.now().isoformat()
            },
            'statistics': {
                'files_analyzed': stats.get('files_analyzed', 0),
                'total_observations': stats.get('total_observations', 0),
                'critical_issues': stats.get('critical_count', 0),
                'important_issues': stats.get('important_count', 0)
            },
            'recent_activity': {
                'last_24h': stats
            }
        }
        
        # Write context
        context_path = self.output_dir / 'project_context.json'
        context_path.write_text(json.dumps(context, indent=2))
        logger.info(f"Generated project context: {context_path}")
        
        return context_path
    
    def _count_critical_issues(self, observations: List[Dict]) -> int:
        """Count critical issues from observations."""
        return sum(
            1 for obs in observations
            if obs.get('data', {}).get('classification') == 'critical'
        )
    
    def _format_todos(self, todos: List[Dict]) -> List[Dict]:
        """Format TODO observations for report, excluding resolved TODOs."""
        formatted = []
        for todo in todos:
            # Skip resolved TODOs
            if todo.get('resolved', False):
                continue
            data = todo.get('data', {})
            formatted.append({
                'file': data.get('file', 'unknown'),
                'line': data.get('line', 0),
                'content': data.get('content', ''),
                'priority': todo.get('priority', 50),
                'classification': data.get('classification', 'unclassified'),
                'ml_confidence': data.get('ml_confidence', 0.0)
            })
        return sorted(formatted, key=lambda x: x['priority'], reverse=True)
    
    def _format_issues(self, observations: List[Dict]) -> List[Dict]:
        """Format critical and important issues."""
        issues = []
        for obs in observations:
            data = obs.get('data', {})
            classification = data.get('classification', '')
            
            if classification in ['critical', 'important']:
                issues.append({
                    'type': obs.get('type'),
                    'severity': classification,
                    'file': data.get('file', 'unknown'),
                    'description': data.get('content', data.get('summary', '')),
                    'confidence': data.get('ml_confidence', 0.0)
                })
        
        return sorted(issues, key=lambda x: (
            0 if x['severity'] == 'critical' else 1,
            -x['confidence']
        ))
    
    def _format_file_summaries(self, summaries: List[Dict]) -> List[Dict]:
        """Format file analysis summaries."""
        formatted = []
        for summary in summaries:
            data = summary.get('data', {})
            formatted.append({
                'file': data.get('file_path', 'unknown'),
                'analyzed_at': summary.get('created_at', ''),
                'summary': data.get('summary', {}),
                'has_issues': data.get('total_issues', 0) > 0
            })
        return formatted
    
    def generate_all_outputs(self) -> Dict[str, Path]:
        """
        Generate all output files.
        
        Returns:
            Dictionary mapping output type to file path
        """
        outputs = {}
        
        try:
            outputs['analysis_report'] = self.generate_analysis_report()
            outputs['todo_list'] = self.generate_todo_list()
            outputs['project_context'] = self.generate_project_context()
            outputs['code_security_analysis'] = self.generate_code_security_analysis()  # ADD COMPREHENSIVE
            
            logger.info(f"Generated {len(outputs)} output files in {self.output_dir}")
        except Exception as e:
            logger.error(f"Failed to generate outputs: {e}")
        
        return outputs
    
    def generate_code_security_analysis(self) -> Path:
        """Generate comprehensive analysis covering ALL rich data types via OutputGenerator."""
        
        # Get ALL rich data types (already deduplicated by existing hash systems)
        todo_observations = self.storage.get_observations_by_type('todo', limit=100)
        code_issues = self.storage.get_observations_by_type('code_issue', limit=100)
        security_issues = self.storage.get_observations_by_type('security_issue', limit=50)
        code_entities = self.storage.get_observations_by_type('code_entity', limit=200)
        code_metrics = self.storage.get_observations_by_type('code_metrics', limit=50)
        persistent_issues = self.storage.get_observations_by_type('persistent_issue', limit=50)
        evolution_report = self._get_evolution_summary()
        
        # Build comprehensive structured markdown
        content = self._build_all_data_types_analysis(
            todo_observations, code_issues, security_issues, 
            code_entities, code_metrics, persistent_issues, evolution_report
        )
        
        file_path = self.output_dir / 'CODE_SECURITY_AND_QUALITY_ANALYSIS.md'
        file_path.write_text(content)
        logger.info(f"Generated comprehensive intelligence report: {file_path}")
        return file_path
    
    def _get_evolution_summary(self) -> Dict:
        """Get evolution summary data."""
        # For now, return empty dict - this can be enhanced later
        return {}
    
    def _build_all_data_types_analysis(self, todos, code_issues, security_issues, 
                                     entities, metrics, persistent, evolution):
        """Build structured markdown covering ALL rich data types."""
        sections = []
        
        # Import needed for datetime formatting
        from datetime import datetime
        import json
        
        # Header with comprehensive Claude Code context
        sections.append("# Code Security and Quality Analysis\n")
        sections.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        # Claude Code Context and Documentation
        sections.append("## 🤖 For Claude Code AI Assistant\n")
        sections.append("**Purpose**: This file contains comprehensive project intelligence generated by Copper Sun Brass to provide Claude Code with rich context about security vulnerabilities, code quality issues, architectural insights, and strategic recommendations.\n\n")
        
        sections.append("**How to Use This Intelligence**:\n")
        sections.append("- **Security Issues**: Critical vulnerabilities requiring immediate attention with CWE/OWASP classifications\n")
        sections.append("- **TODO Analysis**: Development tasks with priority scoring and research opportunities\n")
        sections.append("- **Code Quality**: Complexity analysis, documentation gaps, and architectural concerns\n")
        sections.append("- **Entity Analysis**: Function/class complexity, refactoring opportunities\n")
        sections.append("- **Project Metrics**: Aggregate statistics for informed decision-making\n")
        sections.append("- **Strategic Recommendations**: AI-generated actionable insights based on aggregate analysis\n\n")
        
        sections.append("## 📊 Data Categories Explained\n")
        sections.append("### Security Issues\n")
        sections.append("- **CWE**: Common Weakness Enumeration classification\n")
        sections.append("- **OWASP**: Open Web Application Security Project mapping\n")
        sections.append("- **Severity**: critical (immediate fix), high (next sprint), medium (planned), low (backlog)\n")
        sections.append("- **Fix Complexity**: trivial (< 1 hour), simple (< 1 day), moderate (< 1 week), complex (> 1 week)\n\n")
        
        sections.append("### TODO Analysis\n")
        sections.append("- **Priority Score**: 0-100 calculated based on keywords, context, and placement\n")
        sections.append("- **TODO Types**: TODO (general task), FIXME (bug fix), BUG (critical issue), NOTE (documentation)\n")
        sections.append("- **Confidence**: ML model confidence in classification (0.0-1.0)\n")
        sections.append("- **Researchable**: Flag indicating whether this TODO could benefit from AI research\n\n")
        
        sections.append("### Code Quality & Complexity\n")
        sections.append("- **Complexity Score**: Cyclomatic complexity (> 10 needs attention, > 20 requires refactoring)\n")
        sections.append("- **Documentation Coverage**: Percentage of entities with proper documentation\n")
        sections.append("- **Entity Types**: function, class, method, module - architectural building blocks\n")
        sections.append("- **Dependencies**: Internal/external dependencies affecting maintainability\n\n")
        
        sections.append("### Strategic Intelligence\n")
        sections.append("- **Persistence Tracking**: Issues appearing across multiple analysis runs\n")
        sections.append("- **Evolution Analysis**: How code quality and security posture changes over time\n")
        sections.append("- **Sprint Count**: Number of development cycles an issue has persisted\n")
        sections.append("- **Strategic Importance**: Business impact assessment of persistent issues\n\n")
        
        sections.append("---\n\n")
        
        # 1. Critical Security Issues (from pattern analysis)
        if security_issues:
            sections.append("## 🚨 Critical Security Issues\n")
            critical_security = [s for s in security_issues if s.get('data', {}).get('severity') == 'critical']
            high_security = [s for s in security_issues if s.get('data', {}).get('severity') == 'high']
            
            for issue_group, title in [(critical_security, "Critical"), (high_security, "High Priority")]:
                if issue_group:
                    sections.append(f"### {title} Security Issues\n")
                    for issue in issue_group[:10]:
                        data = issue.get('data', {})
                        sections.append(f"#### {data.get('pattern_name', 'Security Issue')} in {data.get('file_path', 'unknown')}:{data.get('line_number', 0)}\n")
                        sections.append("```json\n")
                        sections.append(json.dumps(data, indent=2))
                        sections.append("\n```\n")
                        sections.append(f"**CWE**: {data.get('cwe', 'N/A')} | **OWASP**: {data.get('owasp', 'N/A')}\n")
                        sections.append(f"**Impact**: {data.get('description', 'No description')}\n")
                        sections.append(f"**Recommendation**: {data.get('ai_recommendation', 'Review required')}\n\n")
        
        # 2. TODO Analysis (from TODO detector)
        if todos:
            sections.append("## 📋 TODO Analysis\n")
            high_priority_todos = [t for t in todos if t.get('data', {}).get('priority_score', 0) > 70]
            medium_priority_todos = [t for t in todos if 40 <= t.get('data', {}).get('priority_score', 0) <= 70]
            
            for todo_group, title in [(high_priority_todos, "High Priority"), (medium_priority_todos, "Medium Priority")]:
                if todo_group:
                    sections.append(f"### {title} TODOs\n")
                    for todo in todo_group[:15]:
                        data = todo.get('data', {})
                        sections.append(f"#### {data.get('file_path', 'unknown')}:{data.get('line_number', 0)} - {data.get('todo_type', 'TODO')}\n")
                        sections.append("```json\n")
                        sections.append(json.dumps(data, indent=2))
                        sections.append("\n```\n")
                        sections.append(f"**Content**: {data.get('content', 'No content')}\n")
                        sections.append(f"**Confidence**: {data.get('confidence', 0):.1%} | **Researchable**: {data.get('is_researchable', False)}\n\n")
        
        # 3. Code Quality Issues (from AST analysis)
        if code_issues:
            sections.append("## 🔍 Code Quality Issues\n")
            critical_code = [c for c in code_issues if c.get('data', {}).get('severity') == 'critical']
            high_code = [c for c in code_issues if c.get('data', {}).get('severity') == 'high']
            
            for issue_group, title in [(critical_code, "Critical"), (high_code, "High Priority")]:
                if issue_group:
                    sections.append(f"### {title} Code Issues\n")
                    for issue in issue_group[:10]:
                        data = issue.get('data', {})
                        sections.append(f"#### {data.get('issue_type', 'unknown').replace('_', ' ').title()} in {data.get('entity_name', 'unknown')}\n")
                        sections.append("```json\n")
                        sections.append(json.dumps(data, indent=2))
                        sections.append("\n```\n")
                        sections.append(f"**Location**: {data.get('file_path', 'unknown')}:{data.get('line_number', 0)}\n")
                        sections.append(f"**Fix Complexity**: {data.get('fix_complexity', 'unknown')}\n")
                        sections.append(f"**Recommendation**: {data.get('ai_recommendation', 'Review required')}\n\n")
        
        # 4. Complex Code Entities (from AST analysis)
        if entities:
            sections.append("## 🏗️ Complex Code Entities\n")
            complex_entities = sorted([e for e in entities if e.get('data', {}).get('complexity_score', 0) > 15], 
                                    key=lambda x: x.get('data', {}).get('complexity_score', 0), reverse=True)
            undocumented = [e for e in entities if not e.get('data', {}).get('has_docstring', True)]
            
            if complex_entities:
                sections.append("### High Complexity Entities\n")
                for entity in complex_entities[:10]:
                    data = entity.get('data', {})
                    sections.append(f"#### {data.get('entity_type', 'entity').title()}: {data.get('entity_name', 'unknown')}\n")
                    sections.append("```json\n")
                    sections.append(json.dumps(data, indent=2))
                    sections.append("\n```\n")
                    sections.append(f"**Location**: {data.get('file_path', 'unknown')}:{data.get('line_start', 0)}-{data.get('line_end', 0)}\n")
                    sections.append(f"**Complexity**: {data.get('complexity_score', 0)} | **Dependencies**: {len(data.get('dependencies', []))}\n\n")
            
            if undocumented:
                sections.append("### Undocumented Entities\n")
                for entity in undocumented[:15]:
                    data = entity.get('data', {})
                    sections.append(f"- **{data.get('entity_name', 'unknown')}** ({data.get('entity_type', 'entity')}) in {data.get('file_path', 'unknown')}:{data.get('line_start', 0)}\n")
                sections.append("\n")
        
        # 5. Aggregate Metrics (from AST analysis)
        if metrics:
            sections.append("## 📊 Code Metrics Summary\n")
            total_lines = sum(m.get('data', {}).get('total_lines', 0) for m in metrics)
            total_code_lines = sum(m.get('data', {}).get('code_lines', 0) for m in metrics)
            avg_complexity = sum(m.get('data', {}).get('average_complexity', 0) for m in metrics) / len(metrics) if metrics else 0
            avg_doc_coverage = sum(m.get('data', {}).get('documentation_coverage', 0) for m in metrics) / len(metrics) if metrics else 0
            
            sections.append("### Project Overview\n")
            sections.append("```json\n")
            sections.append(json.dumps({
                'total_lines_analyzed': total_lines,
                'code_lines': total_code_lines,
                'comment_ratio': (total_lines - total_code_lines) / total_lines if total_lines > 0 else 0,
                'average_complexity': round(avg_complexity, 2),
                'documentation_coverage': round(avg_doc_coverage, 2),
                'files_analyzed': len(metrics)
            }, indent=2))
            sections.append("\n```\n\n")
            
            sections.append("### Per-File Metrics\n")
            for metric in sorted(metrics, key=lambda x: x.get('data', {}).get('average_complexity', 0), reverse=True)[:10]:
                data = metric.get('data', {})
                sections.append(f"- **{data.get('file_path', 'unknown')}**: {data.get('code_lines', 0)} lines, complexity {data.get('average_complexity', 0):.1f}, {data.get('documentation_coverage', 0):.1%} documented\n")
            sections.append("\n")
        
        # 6. Evolution & Persistence Tracking (from evolution tracker)
        if persistent or evolution:
            sections.append("## 🔄 Evolution & Persistence Analysis\n")
            
            if persistent:
                sections.append("### Persistent Issues\n")
                chronic_issues = [p for p in persistent if p.get('data', {}).get('sprint_count', 0) >= 3]
                if chronic_issues:
                    sections.append("#### Chronic Issues (3+ Sprints)\n")
                    for issue in chronic_issues[:10]:
                        data = issue.get('data', {})
                        sections.append(f"##### {data.get('issue_type', 'unknown').replace('_', ' ').title()} in {data.get('file_path', 'unknown')}:{data.get('line_number', 0)}\n")
                        sections.append("```json\n")
                        sections.append(json.dumps(data, indent=2))
                        sections.append("\n```\n")
                        sections.append(f"**Persistence**: {data.get('sprint_count', 0)} sprints ({data.get('persistence_days', 0)} days)\n")
                        sections.append(f"**Strategic Importance**: {data.get('strategic_importance', 'unknown')}\n\n")
            
            if evolution:
                sections.append("### Evolution Summary\n")
                sections.append("```json\n")
                sections.append(json.dumps(evolution, indent=2))
                sections.append("\n```\n\n")
        
        # 7. Customer-Facing Security & Privacy Analysis (Phase 3 Enhancement)
        sections.append("## 🔒 Code Security & Privacy Analysis\n")
        sections.append("*Comprehensive automated security analysis for enterprise readiness and compliance*\n\n")
        
        security_analysis = self._generate_customer_security_analysis(todos, code_issues, security_issues, entities)
        sections.append(security_analysis)
        
        # 8. Strategic Recommendations
        sections.append("## 🎯 Strategic Recommendations\n")
        recommendations = self._generate_strategic_recommendations(
            security_issues, todos, code_issues, entities, persistent
        )
        for rec in recommendations:
            sections.append(f"- {rec}\n")
        sections.append("\n")
        
        return "\n".join(sections)

    def _generate_strategic_recommendations(self, security, todos, code_issues, entities, persistent):
        """Generate strategic recommendations based on ALL data types."""
        recommendations = []
        
        # Security recommendations
        critical_security = len([s for s in security if s.get('data', {}).get('severity') == 'critical'])
        if critical_security > 0:
            recommendations.append(f"🚨 **URGENT**: {critical_security} critical security issues require immediate attention")
        
        # TODO recommendations  
        high_priority_todos = len([t for t in todos if t.get('data', {}).get('priority_score', 0) > 70])
        if high_priority_todos > 10:
            recommendations.append(f"📋 **TODO Overflow**: {high_priority_todos} high-priority TODOs - schedule dedicated cleanup sprint")
        
        # Code quality recommendations
        complex_entities = len([e for e in entities if e.get('data', {}).get('complexity_score', 0) > 20])
        if complex_entities > 5:
            recommendations.append(f"🔧 **Complexity Crisis**: {complex_entities} highly complex entities need refactoring")
        
        # Documentation recommendations
        undocumented = len([e for e in entities if not e.get('data', {}).get('has_docstring', True)])
        total_entities = len(entities)
        if total_entities > 0 and undocumented / total_entities > 0.5:
            recommendations.append(f"📚 **Documentation Gap**: {undocumented}/{total_entities} entities lack documentation")
        
        # Persistence recommendations
        chronic_issues = len([p for p in persistent if p.get('data', {}).get('sprint_count', 0) >= 3])
        if chronic_issues > 5:
            recommendations.append(f"⏰ **Technical Debt Alert**: {chronic_issues} issues persisting 3+ sprints require strategic intervention")
        
        return recommendations
    
    def _generate_customer_security_analysis(self, todos, code_issues, security_issues, entities) -> str:
        """Generate customer-facing security and privacy analysis using Phase 3 dual-purpose content safety.
        
        This provides actionable security audit insights for customers using our breakthrough
        dual-purpose content safety system.
        
        Args:
            todos, code_issues, security_issues, entities: Observation data
            
        Returns:
            Formatted markdown section with customer security analysis
        """
        sections = []
        
        # Collect all code content for comprehensive analysis
        all_findings = []
        code_samples = []
        
        # Extract content from all observation types for analysis
        for observation_group in [todos, code_issues, security_issues, entities]:
            for obs in observation_group:
                data = obs.get('data', {})
                
                # Extract various content fields
                content_fields = ['content', 'snippet', 'description', 'pattern_text', 'entity_name']
                content = ''
                for field in content_fields:
                    if field in data and data[field]:
                        content = str(data[field])
                        break
                
                if content and len(content.strip()) > 5:
                    code_samples.append({
                        'content': content,
                        'file_path': data.get('file_path', 'unknown'),
                        'line_number': data.get('line_number', 0),
                        'observation_type': obs.get('type', 'unknown')
                    })
        
        # Analyze samples with content safety system
        total_samples = len(code_samples)
        if total_samples == 0:
            sections.append("### Summary\n")
            sections.append("No security concerns detected in available code samples.\n\n")
            return "\n".join(sections)
        
        # Run security analysis on samples
        all_security_findings = []
        high_risk_samples = 0
        medium_risk_samples = 0
        
        for sample in code_samples[:50]:  # Limit for performance
            try:
                safety_result = self.content_safety.analyze_content_comprehensive(
                    content=sample['content'],
                    file_path=sample['file_path'], 
                    line_number=sample['line_number']
                )
                
                if safety_result.customer_findings:
                    all_security_findings.extend(safety_result.customer_findings)
                    
                    if safety_result.risk_score == "HIGH":
                        high_risk_samples += 1
                    elif safety_result.risk_score == "MEDIUM":
                        medium_risk_samples += 1
                        
            except Exception as e:
                logger.debug(f"Content safety analysis failed for sample: {e}")
                continue
        
        # Generate customer report using the dual-purpose system
        customer_report = self.content_safety.generate_customer_security_report(all_security_findings)
        
        # Format for markdown output
        sections.append("### Executive Summary\n")
        sections.append(f"**{customer_report['summary']}**\n\n")
        
        sections.append(f"- **Files Analyzed**: {total_samples} code samples\n")
        sections.append(f"- **Security Items Found**: {customer_report['findings_count']}\n")
        sections.append(f"- **Risk Level**: {customer_report['risk_level']}\n")
        sections.append(f"- **Enterprise Readiness**: {customer_report['enterprise_readiness']}\n\n")
        
        # Risk breakdown
        if customer_report['findings_count'] > 0:
            sections.append("### Risk Assessment\n")
            
            findings_by_priority = customer_report['findings_by_priority']
            
            if findings_by_priority['high']:
                sections.append(f"#### 🚨 High Priority Issues ({len(findings_by_priority['high'])})\n")
                for finding in findings_by_priority['high'][:5]:
                    sections.append(f"- **{finding.type}** at {finding.location}\n")
                    sections.append(f"  - *Risk*: {finding.risk_explanation}\n")
                    sections.append(f"  - *Fix*: {finding.remediation}\n")
                sections.append("\n")
            
            if findings_by_priority['medium']:
                sections.append(f"#### ⚠️ Medium Priority Issues ({len(findings_by_priority['medium'])})\n")
                for finding in findings_by_priority['medium'][:5]:
                    sections.append(f"- **{finding.type}** at {finding.location}\n")
                    sections.append(f"  - *Fix*: {finding.remediation}\n")
                sections.append("\n")
            
            if findings_by_priority['low']:
                sections.append(f"#### ℹ️ Low Priority Items ({len(findings_by_priority['low'])})\n")
                sections.append("Professional language and documentation improvements identified.\n\n")
        
        # Actionable recommendations
        sections.append("### Recommended Actions\n")
        for i, recommendation in enumerate(customer_report['recommendations'], 1):
            sections.append(f"{i}. {recommendation}\n")
        sections.append("\n")
        
        # Compliance status
        sections.append("### Compliance & Privacy Status\n")
        
        # Count PII findings
        pii_findings = [f for f in all_security_findings if 'personal' in f.risk_explanation.lower() or 'identifier' in f.risk_explanation.lower()]
        secret_findings = [f for f in all_security_findings if 'api' in f.type.lower() or 'key' in f.type.lower() or 'password' in f.type.lower()]
        
        if pii_findings:
            sections.append(f"- **Privacy Compliance**: ⚠️ {len(pii_findings)} personal information items detected\n")
            sections.append("  - Review for GDPR/CCPA compliance\n")
            sections.append("  - Consider data anonymization for development\n")
        else:
            sections.append("- **Privacy Compliance**: ✅ No personal information detected in code\n")
        
        if secret_findings:
            sections.append(f"- **Secret Management**: ⚠️ {len(secret_findings)} hardcoded credentials detected\n")
            sections.append("  - Move to environment variables immediately\n")
            sections.append("  - Implement secure credential management\n")
        else:
            sections.append("- **Secret Management**: ✅ No hardcoded credentials detected\n")
        
        sections.append("\n")
        
        # Performance metrics
        sections.append("### Analysis Performance\n")
        sections.append(f"- **Samples Processed**: {total_samples}\n")
        sections.append(f"- **High Risk Samples**: {high_risk_samples}\n") 
        sections.append(f"- **Medium Risk Samples**: {medium_risk_samples}\n")
        sections.append(f"- **Analysis Engine**: Dual-purpose content safety with international PII detection\n")
        sections.append(f"- **Coverage**: US, EU, UK, India, Singapore, Australia compliance patterns\n\n")
        
        sections.append("---\n")
        sections.append("*This analysis was generated by Copper Sun Brass automated security analysis engine. ")
        sections.append("For enterprise deployment support, contact your development team.*\n\n")
        
        return "\n".join(sections)