#!/usr/bin/env python3
"""
Scout Agent CLI Commands
Implements stage → review → commit workflow for Copper Alloy Brass CLI
"""

import json
import os
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from typing import Optional, Dict

console = Console()

def add_scout_commands(cli_group):
    """Add Scout Agent commands to the main CLI group"""
    
    @cli_group.group(name="scout")
    def scout():
        """Scout Agent - Proactive TODO detection and research"""
        pass
    
    @scout.command(name="scan")
    @click.option("--path", default=".", help="Directory path to scan")
    @click.option("--stage", is_flag=True, help="Stage findings instead of just displaying")
    @click.option("--filter", "filter_types", multiple=True, 
                  help="Filter by TODO types (TODO, FIXME, BUG, etc.)")
    @click.option("--deep-analysis", is_flag=True, help="Enable all analyzers (AST, patterns, evolution)")
    @click.option("--ast", is_flag=True, help="Enable AST analysis for code structure")
    @click.option("--patterns", is_flag=True, help="Enable pattern analysis for code smells")
    @click.option("--security", is_flag=True, help="Enable security pattern detection")
    @click.option("--evolution", is_flag=True, help="Track issue evolution over time")
    @click.option("--max-workers", type=int, default=4, help="Maximum parallel analysis workers")
    def scout_scan(path: str, stage: bool, filter_types: tuple, deep_analysis: bool,
                   ast: bool, patterns: bool, security: bool, evolution: bool, max_workers: int):
        """Scan directory for TODO items and optionally perform deep analysis"""
        try:
            from coppersun_brass.agents.scout.scout_agent import ScoutAgent
            from coppersun_brass.core.context.dcp_manager import DCPManager
            
            # Configure analysis types
            analysis_types = set()
            if deep_analysis:
                # Deep analysis enables all
                use_deep = True
                analysis_types = None  # Use all
            else:
                # Individual flags
                use_deep = ast or patterns or security or evolution
                analysis_types.add('todo')  # Always include TODO
                if ast:
                    analysis_types.add('ast')
                if patterns or security:
                    analysis_types.add('patterns')
                if evolution:
                    analysis_types.add('evolution')
            
            # Create Scout agent with config
            config = {'max_workers': max_workers}
            dcp_manager = DCPManager() if stage else None
            agent = ScoutAgent(dcp_manager=dcp_manager, config=config)
            
            # Run analysis
            console.print(f"🔍 Analyzing {path}...", style="blue")
            result = agent.analyze(path, deep_analysis=use_deep, analysis_types=analysis_types)
            
            # Display results
            _display_analysis_results(result, filter_types)
            
            # Stage if requested
            if stage and result.todo_findings:
                stage_result = agent.stage_findings(result)
                console.print(Panel(
                    f"[green]✅ Staged {stage_result['staged']} findings[/green]\n"
                    f"[yellow]⚠️  Skipped {stage_result['duplicates']} duplicates[/yellow]\n"
                    f"[blue]📊 Total staged: {stage_result['total_staged']}[/blue]",
                    title="🏗️  Staging Results"
                ))
                
        except ImportError as e:
            console.print(f"❌ Error importing Scout modules: {e}", style="red")
        except Exception as e:
            console.print(f"❌ Scan failed: {e}", style="red")
    
    @scout.command(name="review")
    @click.option("--min-priority", type=int, help="Minimum priority score (0-100)")
    @click.option("--min-confidence", type=float, help="Minimum confidence (0.0-1.0)")
    @click.option("--todo-type", multiple=True, help="Filter by TODO types")
    @click.option("--researchable-only", is_flag=True, help="Show only researchable items")
    @click.option("--file-pattern", help="Filter by file name pattern")
    @click.option("--format", "output_format", default="table", 
                  type=click.Choice(["table", "tree", "json"]), help="Output format")
    def scout_review(min_priority: Optional[int], min_confidence: Optional[float], 
                     todo_type: tuple, researchable_only: bool, file_pattern: Optional[str],
                     output_format: str):
        """Review staged TODO findings"""
        try:
            from coppersun_brass.agents.scout.dcp_integrator import ScoutDCPIntegrator
            
            integrator = ScoutDCPIntegrator()
            
            # Build filter criteria
            criteria = {}
            if min_priority is not None:
                criteria["min_priority"] = min_priority
            if min_confidence is not None:
                criteria["min_confidence"] = min_confidence
            if todo_type:
                criteria["todo_type"] = list(todo_type)
            if researchable_only:
                criteria["researchable_only"] = True
            if file_pattern:
                criteria["file_pattern"] = file_pattern
            
            review = integrator.review_staged(criteria)
            
            if review["total_staged"] == 0:
                console.print("📭 No staged findings to review", style="yellow")
                return
            
            if output_format == "json":
                _display_json_review(review)
            elif output_format == "tree":
                _display_tree_review(review)
            else:
                _display_table_review(review)
                
        except ImportError as e:
            console.print(f"❌ Error importing Scout modules: {e}", style="red")
        except Exception as e:
            console.print(f"❌ Review failed: {e}", style="red")
    
    @scout.command(name="analyze")
    @click.argument("path", default=".")
    @click.option("--output", "-o", type=click.Choice(['console', 'json', 'dcp']), 
                  default="console", help="Output format")
    @click.option("--save-report", type=click.Path(), help="Save analysis report to file")
    def scout_analyze(path: str, output: str, save_report: Optional[str]):
        """Run deep analysis and view detailed report"""
        try:
            from coppersun_brass.agents.scout.scout_agent import ScoutAgent
            
            agent = ScoutAgent()
            
            console.print(f"🔬 Running deep analysis on {path}...", style="blue")
            result = agent.analyze(path, deep_analysis=True)
            
            if output == 'console':
                _display_analysis_results(result)
            elif output == 'json':
                # Convert to JSON-serializable format
                report = {
                    'timestamp': result.analysis_timestamp.isoformat(),
                    'duration': result.analysis_duration,
                    'files_analyzed': result.total_files_analyzed,
                    'total_issues': result.total_issues_found,
                    'critical_issues': result.critical_issues,
                    'security_issues': result.security_issues,
                    'analyzers_used': result.analyzers_used,
                    'todo_count': len(result.todo_findings),
                    'persistent_issues': len(result.persistent_issues),
                    'evolution_report': result.evolution_report
                }
                console.print(json.dumps(report, indent=2))
            elif output == 'dcp':
                observations = result.to_dcp_observations()
                console.print(f"Generated {len(observations)} DCP observations")
            
            if save_report:
                # Save detailed report
                report_data = {
                    'analysis': {
                        'path': path,
                        'timestamp': result.analysis_timestamp.isoformat(),
                        'duration': result.analysis_duration,
                        'analyzers': result.analyzers_used
                    },
                    'summary': {
                        'files_analyzed': result.total_files_analyzed,
                        'total_issues': result.total_issues_found,
                        'critical_issues': result.critical_issues,
                        'security_issues': result.security_issues
                    },
                    'findings': {
                        'todos': [{
                            'file': f.file_path,
                            'line': f.line_number,
                            'type': f.todo_type,
                            'content': f.content,
                            'priority': f.priority_score
                        } for f in result.todo_findings[:50]],  # Limit to 50
                        'persistent_issues': [{
                            'file': i.file_path,
                            'type': i.issue_type,
                            'days_old': (i.last_seen - i.first_seen).days,
                            'sprints': i.sprint_count
                        } for i in result.persistent_issues[:20]]
                    },
                    'evolution': result.evolution_report
                }
                
                with open(save_report, 'w') as f:
                    json.dump(report_data, f, indent=2)
                console.print(f"✅ Report saved to {save_report}")
                
        except ImportError as e:
            console.print(f"❌ Error importing Scout modules: {e}", style="red")
        except Exception as e:
            console.print(f"❌ Analysis failed: {e}", style="red")
    
    @scout.command(name="commit")
    @click.option("--min-priority", type=int, help="Minimum priority score to commit")
    @click.option("--min-confidence", type=float, help="Minimum confidence to commit")
    @click.option("--todo-type", multiple=True, help="Commit only these TODO types")
    @click.option("--researchable-only", is_flag=True, help="Commit only researchable items")
    @click.option("--dry-run", is_flag=True, help="Show what would be committed")
    @click.confirmation_option(prompt="Are you sure you want to commit findings to DCP?")
    def scout_commit(min_priority: Optional[int], min_confidence: Optional[float],
                     todo_type: tuple, researchable_only: bool, dry_run: bool):
        """Commit staged findings to DCP"""
        try:
            from coppersun_brass.agents.scout.dcp_integrator import ScoutDCPIntegrator
            from coppersun_brass.core.context.dcp_manager import DCPManager
            
            # Create integrator with DCP manager
            dcp_manager = DCPManager()
            integrator = ScoutDCPIntegrator(dcp_manager=dcp_manager)
            
            # Build filter criteria
            criteria = {}
            if min_priority is not None:
                criteria["min_priority"] = min_priority
            if min_confidence is not None:
                criteria["min_confidence"] = min_confidence
            if todo_type:
                criteria["todo_type"] = list(todo_type)
            if researchable_only:
                criteria["researchable_only"] = True
            
            result = integrator.commit_staged(criteria, dry_run=dry_run)
            
            if "error" in result:
                console.print(f"❌ {result['error']}", style="red")
                return
            
            if dry_run:
                console.print(Panel(
                    f"[blue]🧪 Dry Run Results[/blue]\n"
                    f"[green]Would commit: {result['would_commit']} findings[/green]\n"
                    f"[yellow]Would remain staged: {result['would_remain_staged']}[/yellow]",
                    title="🔍 Commit Preview"
                ))
                
                if "findings_preview" in result:
                    console.print("\n📝 Sample findings to commit:")
                    for i, finding in enumerate(result["findings_preview"], 1):
                        console.print(f"  {i}. [bold]{finding['type']}[/bold] "
                                    f"(P:{finding['priority']}) {finding['content']}")
            else:
                console.print(Panel(
                    f"[green]✅ Committed {result['committed']} findings to DCP[/green]\n"
                    f"[blue]📊 Remaining staged: {result['remaining_staged']}[/blue]\n"
                    f"[cyan]🔗 DCP observations added: {result['observations_added']}[/cyan]",
                    title="🚀 Commit Complete"
                ))
                
        except ImportError as e:
            console.print(f"❌ Error importing modules: {e}", style="red")
        except Exception as e:
            console.print(f"❌ Commit failed: {e}", style="red")
    
    @scout.command(name="clear")
    @click.option("--min-priority", type=int, help="Clear only items above this priority")
    @click.option("--todo-type", multiple=True, help="Clear only these TODO types")
    @click.option("--all", "clear_all", is_flag=True, help="Clear all staged findings")
    @click.confirmation_option(prompt="Are you sure you want to clear staged findings?")
    def scout_clear(min_priority: Optional[int], todo_type: tuple, clear_all: bool):
        """Clear staged TODO findings"""
        try:
            from coppersun_brass.agents.scout.dcp_integrator import ScoutDCPIntegrator
            
            integrator = ScoutDCPIntegrator()
            
            if clear_all:
                criteria = None
            else:
                criteria = {}
                if min_priority is not None:
                    criteria["min_priority"] = min_priority
                if todo_type:
                    criteria["todo_type"] = list(todo_type)
            
            result = integrator.clear_staged(criteria)
            
            console.print(Panel(
                f"[red]🗑️  Cleared {result['cleared']} findings[/red]\n"
                f"[blue]📊 Remaining staged: {result['remaining']}[/blue]",
                title="🧹 Clear Complete"
            ))
            
        except ImportError as e:
            console.print(f"❌ Error importing Scout modules: {e}", style="red")
        except Exception as e:
            console.print(f"❌ Clear failed: {e}", style="red")
    
    @scout.command(name="status")
    def scout_status():
        """Show Scout Agent status and staged findings summary"""
        try:
            from coppersun_brass.agents.scout.dcp_integrator import ScoutDCPIntegrator
            
            integrator = ScoutDCPIntegrator()
            review = integrator.review_staged()
            
            if review["total_staged"] == 0:
                console.print(Panel(
                    "[yellow]📭 No staged findings[/yellow]\n"
                    "[dim]Use 'brass scout scan --stage' to find and stage TODO items[/dim]",
                    title="🕵️ Scout Agent Status"
                ))
                return
            
            # Create status summary
            status_content = []
            status_content.append(f"[green]📦 Total staged: {review['total_staged']}[/green]")
            status_content.append(f"[blue]🔬 Researchable: {review['researchable_count']}[/blue]")
            
            # Priority breakdown
            status_content.append("\n[bold]Priority Distribution:[/bold]")
            for priority_range, count in review['by_priority'].items():
                if count > 0:
                    status_content.append(f"  {priority_range}: {count}")
            
            # Type breakdown
            status_content.append("\n[bold]By Type:[/bold]")
            for todo_type, count in review['by_type'].items():
                status_content.append(f"  {todo_type}: {count}")
            
            console.print(Panel(
                "\n".join(status_content),
                title="🕵️ Scout Agent Status"
            ))
            
        except ImportError as e:
            console.print(f"❌ Error importing Scout modules: {e}", style="red")
        except Exception as e:
            console.print(f"❌ Status check failed: {e}", style="red")

# Helper functions for display formatting

def _display_findings(findings):
    """Display findings in a nice table format"""
    if not findings:
        return
    
    table = Table(title="🔍 Scout Agent - TODO Findings")
    table.add_column("File", style="cyan")
    table.add_column("Line", style="magenta")
    table.add_column("Type", style="red")
    table.add_column("Priority", style="green")
    table.add_column("Content", style="white")
    table.add_column("Research", style="blue")
    
    for finding in sorted(findings, key=lambda x: x.priority_score, reverse=True):
        research_icon = "🔬" if finding.is_researchable else ""
        
        table.add_row(
            finding.file_path.split("/")[-1],  # Just filename
            str(finding.line_number),
            finding.todo_type,
            str(finding.priority_score),
            finding.content[:50] + "..." if len(finding.content) > 50 else finding.content,
            research_icon
        )
    
    console.print(table)

def _display_analysis_results(result, filter_types=None):
    """Display comprehensive analysis results"""
    # Display summary
    console.print(Panel(
        f"[green]📊 Analysis Complete[/green]\n"
        f"Files analyzed: {result.total_files_analyzed}\n"
        f"Total issues: {result.total_issues_found}\n"
        f"Critical issues: {result.critical_issues}\n"
        f"Security issues: {result.security_issues}\n"
        f"Analyzers used: {', '.join(result.analyzers_used)}\n"
        f"Duration: {result.analysis_duration:.2f}s",
        title="📋 Analysis Summary"
    ))
    
    # Display TODO findings
    if result.todo_findings:
        filtered_findings = result.todo_findings
        if filter_types:
            filtered_findings = [f for f in filtered_findings if f.todo_type in filter_types]
        
        if filtered_findings:
            console.print("\n[bold]TODO/FIXME Findings:[/bold]")
            _display_findings(filtered_findings[:20])  # Show top 20
            if len(filtered_findings) > 20:
                console.print(f"\n... and {len(filtered_findings) - 20} more findings")
    
    # Display AST analysis results
    if result.ast_results:
        console.print("\n[bold]🧬 AST Analysis Results:[/bold]")
        complexity_issues = []
        doc_issues = []
        
        for ast_result in result.ast_results:
            for issue in ast_result.issues:
                if issue.issue_type == 'high_complexity':
                    complexity_issues.append(issue)
                elif issue.issue_type == 'missing_docstring':
                    doc_issues.append(issue)
        
        if complexity_issues:
            console.print(f"  High complexity functions: {len(complexity_issues)}")
        if doc_issues:
            console.print(f"  Missing documentation: {len(doc_issues)}")
    
    # Display pattern analysis results
    if result.pattern_results:
        console.print("\n[bold]🔍 Pattern Analysis Results:[/bold]")
        pattern_summary = {}
        
        for pattern_result in result.pattern_results:
            for issue in pattern_result.issues:
                pattern_type = issue.metadata.get('pattern_type', 'unknown')
                pattern_summary[pattern_type] = pattern_summary.get(pattern_type, 0) + 1
        
        for ptype, count in pattern_summary.items():
            emoji = "🔒" if ptype == 'security' else "⚠️" if ptype == 'anti_pattern' else "🧹"
            console.print(f"  {emoji} {ptype}: {count} issues")
    
    # Display evolution tracking
    if result.persistent_issues:
        console.print(f"\n[bold]📈 Persistent Issues:[/bold]")
        console.print(f"  Issues persisting 2+ sprints: {len(result.persistent_issues)}")
        
        # Show top persistent issues
        for issue in result.persistent_issues[:5]:
            days_old = (issue.last_seen - issue.first_seen).days
            console.print(f"  - {issue.issue_type} in {os.path.basename(issue.file_path)} "
                         f"({days_old} days, {issue.sprint_count} sprints)")
    
    # Display errors if any
    if result.errors:
        console.print(f"\n[yellow]⚠️  Analysis errors: {len(result.errors)}[/yellow]")
        for error in result.errors[:3]:
            console.print(f"  - {error['analyzer']}: {error['error'][:50]}...")

def _display_table_review(review):
    """Display review in table format"""
    console.print(Panel(
        f"[green]📊 Total staged: {review['total_staged']}[/green]\n"
        f"[blue]🔍 Filtered: {review['filtered_count']}[/blue]\n"
        f"[cyan]🔬 Researchable: {review['researchable_count']}[/cyan]",
        title="📋 Review Summary"
    ))
    
    # Priority distribution
    if review['by_priority']:
        console.print("\n[bold]🎯 Priority Distribution:[/bold]")
        for priority_range, count in review['by_priority'].items():
            if count > 0:
                console.print(f"  {priority_range}: {count}")
    
    # Show sample findings
    if review['findings']:
        table = Table(title="📝 Staged Findings (Top 10)")
        table.add_column("Priority", style="green")
        table.add_column("Type", style="red")
        table.add_column("Content", style="white")
        table.add_column("File", style="cyan")
        table.add_column("Research", style="blue")
        
        for finding in sorted(review['findings'], key=lambda x: x.priority_score, reverse=True)[:10]:
            research_icon = "🔬" if finding.is_researchable else ""
            content = finding.content[:40] + "..." if len(finding.content) > 40 else finding.content
            
            table.add_row(
                str(finding.priority_score),
                finding.todo_type,
                content,
                finding.file_path.split("/")[-1],
                research_icon
            )
        
        console.print(table)

def _display_tree_review(review):
    """Display review in tree format"""
    tree = Tree("🕵️ Scout Agent - Staged Findings")
    
    # Add priority branches
    priority_branch = tree.add("🎯 By Priority")
    for priority_range, count in review['by_priority'].items():
        if count > 0:
            priority_branch.add(f"{priority_range}: {count}")
    
    # Add type branches
    type_branch = tree.add("📝 By Type")
    for todo_type, count in review['by_type'].items():
        type_branch.add(f"{todo_type}: {count}")
    
    # Add file branches
    if review['by_file']:
        file_branch = tree.add("📁 By File")
        for file_name, count in list(review['by_file'].items())[:10]:  # Top 10 files
            file_branch.add(f"{file_name}: {count}")
    
    console.print(tree)

def _display_json_review(review):
    """Display review in JSON format"""
    # Remove findings object for cleaner JSON (just show stats)
    clean_review = {k: v for k, v in review.items() if k != 'findings'}
    console.print(json.dumps(clean_review, indent=2))