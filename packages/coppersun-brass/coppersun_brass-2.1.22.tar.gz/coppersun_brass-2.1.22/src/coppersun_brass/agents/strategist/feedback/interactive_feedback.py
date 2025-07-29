"""
InteractiveFeedback: Guided feedback collection wizard.

This component provides:
- Interactive prompts for feedback collection
- Guided walkthroughs for preferences
- Simplified feedback entry
- User-friendly rating collection
"""

import click
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .feedback_collector import FeedbackCollector, AdoptionStatus
from .preference_learner import PreferenceLearner, UserPreferences

logger = logging.getLogger(__name__)


class InteractiveFeedbackWizard:
    """
    Interactive feedback collection wizard for CLI.
    
    Features:
    - Guided feedback collection
    - Simple prompts for ratings
    - Adoption status collection
    - Preference summary display
    """
    
    def __init__(self, 
                 feedback_collector: FeedbackCollector,
                 preference_learner: PreferenceLearner):
        """
        Initialize wizard with collectors.
        
        Args:
            feedback_collector: Feedback collection instance
            preference_learner: Preference learning instance
        """
        self.collector = feedback_collector
        self.learner = preference_learner
    
    def collect_feedback_interactively(self, 
                                     recommendations: List[Dict],
                                     recommendation_type: str) -> int:
        """
        Interactively collect feedback on recommendations.
        
        Args:
            recommendations: List of recommendations to rate
            recommendation_type: 'gap' or 'practice'
            
        Returns:
            Number of feedback entries collected
        """
        click.echo("\n🎯 Interactive Feedback Collection")
        click.echo("=" * 50)
        click.echo(f"Help us learn your preferences by rating these {recommendation_type}s.\n")
        
        feedback_count = 0
        
        for i, rec in enumerate(recommendations, 1):
            # Display recommendation
            self._display_recommendation(rec, recommendation_type, i, len(recommendations))
            
            # Ask for feedback
            if click.confirm("\nWould you like to provide feedback?", default=True):
                feedback_given = self._collect_single_feedback(rec, recommendation_type)
                if feedback_given:
                    feedback_count += 1
                    click.echo(click.style("✓ Feedback recorded!", fg='green'))
            else:
                click.echo("Skipping...")
            
            # Ask if user wants to continue
            if i < len(recommendations):
                if not click.confirm("\nContinue to next item?", default=True):
                    break
            
            click.echo("")
        
        # Show summary
        if feedback_count > 0:
            click.echo(f"\n✅ Collected feedback on {feedback_count} items.")
            self._show_preference_update()
        else:
            click.echo("\n📝 No feedback collected.")
        
        return feedback_count
    
    def _display_recommendation(self, 
                              rec: Dict, 
                              rec_type: str,
                              current: int,
                              total: int) -> None:
        """Display a single recommendation nicely."""
        click.echo(f"\n[{current}/{total}] ", nl=False)
        
        if rec_type == 'gap':
            # Display gap
            capability = rec.get('capability', 'Unknown')
            current_score = rec.get('current_score', 0)
            target_score = rec.get('target_score', 100)
            risk = rec.get('risk_score', 0)
            effort = rec.get('effort', 'unknown')
            
            click.echo(click.style(f"{capability.title()} Gap", fg='yellow', bold=True))
            click.echo(f"Current: {current_score}% → Target: {target_score}% (Risk: {risk}/100)")
            click.echo(f"Effort: {effort}")
            
            if rec.get('recommendations'):
                click.echo("Recommendations:")
                for r in rec['recommendations'][:2]:
                    click.echo(f"  • {r}")
                    
        else:  # practice
            # Display practice
            title = rec.get('title', 'Unknown Practice')
            desc = rec.get('description', '')
            category = rec.get('category', 'general')
            severity = rec.get('severity', 'recommended')
            effort = rec.get('effort', 'medium')
            
            severity_color = {
                'critical': 'red',
                'important': 'yellow',
                'recommended': 'cyan'
            }.get(severity, 'white')
            
            click.echo(click.style(title, fg=severity_color, bold=True))
            click.echo(f"Category: {category} | Severity: {severity} | Effort: {effort}")
            click.echo(f"{desc[:100]}..." if len(desc) > 100 else desc)
    
    def _collect_single_feedback(self, rec: Dict, rec_type: str) -> bool:
        """Collect feedback for a single recommendation."""
        rec_id = rec.get('id') if rec_type == 'practice' else rec.get('capability', 'unknown')
        
        # Rating
        rating = None
        if click.confirm("Rate this item?", default=True):
            rating = click.prompt(
                "Rating (1-5 stars)",
                type=click.IntRange(1, 5),
                default=3
            )
            
            # Optional comment for low ratings
            comment = None
            if rating <= 2:
                if click.confirm("Add a comment about your rating?"):
                    comment = click.prompt("Comment")
            
            success, msg = self.collector.collect_rating(
                rec_id, rec_type, rating, comment
            )
            if not success:
                click.echo(click.style(f"Error: {msg}", fg='red'))
                return False
        
        # Adoption status (for practices)
        if rec_type == 'practice':
            if click.confirm("Track adoption status?", default=False):
                status_map = {
                    '1': AdoptionStatus.ADOPTED,
                    '2': AdoptionStatus.DEFERRED,
                    '3': AdoptionStatus.REJECTED,
                    '4': AdoptionStatus.PARTIAL
                }
                
                click.echo("\nAdoption status:")
                click.echo("1. Adopted (will implement)")
                click.echo("2. Deferred (maybe later)")
                click.echo("3. Rejected (not applicable)")
                click.echo("4. Partial (some parts)")
                
                choice = click.prompt(
                    "Choose status",
                    type=click.Choice(['1', '2', '3', '4']),
                    default='2'
                )
                
                status = status_map[choice]
                
                # Optional reason
                reason = None
                if status in [AdoptionStatus.REJECTED, AdoptionStatus.DEFERRED]:
                    if click.confirm("Add a reason?"):
                        reason = click.prompt("Reason")
                
                success, msg = self.collector.collect_adoption(
                    rec_id, rec_type, status, reason
                )
                if not success:
                    click.echo(click.style(f"Error: {msg}", fg='red'))
                    return False
        
        return True
    
    def _show_preference_update(self) -> None:
        """Show updated preferences after feedback."""
        try:
            summary = self.learner.get_preference_summary()
            
            if not summary.get('personalization_enabled'):
                remaining = 5 - summary.get('feedback_count', 0)
                click.echo(f"\n📊 Preference Learning Status:")
                click.echo(f"Feedback collected: {summary.get('feedback_count', 0)}")
                click.echo(f"Need {remaining} more feedback entries to enable personalization.")
            else:
                click.echo(f"\n✨ Personalization Active!")
                click.echo(f"Confidence: {summary.get('confidence_score', 0):.0%}")
                
                # Show top preferences
                if summary.get('top_capability_preferences'):
                    click.echo("\nYour capability preferences:")
                    for pref in summary['top_capability_preferences'][:3]:
                        click.echo(f"  • {pref['capability']}: {pref['weight']:.0%}")
                
                if summary.get('top_category_preferences'):
                    click.echo("\nYour practice preferences:")
                    for pref in summary['top_category_preferences'][:3]:
                        click.echo(f"  • {pref['category']}: {pref['weight']:.0%}")
                        
        except Exception as e:
            logger.error(f"Failed to show preferences: {e}")
    
    def guide_initial_preferences(self) -> UserPreferences:
        """
        Guide user through initial preference setup.
        
        Returns:
            Initial preferences
        """
        click.echo("\n🚀 Preference Setup Wizard")
        click.echo("=" * 50)
        click.echo("Let's set up your initial preferences for better recommendations.\n")
        
        # Capability focus
        click.echo("Which areas are most important to you?")
        click.echo("(Rate each from 1-5, where 5 is most important)\n")
        
        capabilities = [
            'security', 'testing', 'documentation', 'performance',
            'error_handling', 'code_quality', 'api_design'
        ]
        
        capability_weights = {}
        for cap in capabilities:
            importance = click.prompt(
                f"{cap.replace('_', ' ').title()}",
                type=click.IntRange(1, 5),
                default=3
            )
            capability_weights[cap] = (importance - 1) / 4.0
        
        # Effort preference
        click.echo("\n\nWhat's your preference for implementation effort?")
        effort_pref = click.prompt(
            "Prefer quick wins (1) or comprehensive solutions (5)?",
            type=click.IntRange(1, 5),
            default=3
        )
        
        effort_weights = {
            'small': 0.8 if effort_pref <= 2 else 0.3,
            'medium': 0.6,
            'large': 0.3 if effort_pref <= 2 else 0.8
        }
        
        # Create initial preferences
        from .preference_learner import UserPreferences
        
        preferences = UserPreferences(
            user_id="default",
            capability_weights=capability_weights,
            effort_preferences=effort_weights,
            feedback_count=0,
            last_updated=datetime.now(timezone.utc)
        )
        
        click.echo("\n✅ Initial preferences set!")
        click.echo("These will be refined as you provide feedback on recommendations.")
        
        return preferences


def create_interactive_wizard(dcp_path: Optional[str] = None) -> InteractiveFeedbackWizard:
    """
    Create an interactive feedback wizard.
    
    Args:
        dcp_path: Path to DCP file/directory
        
    Returns:
        Configured wizard instance
    """
    collector = FeedbackCollector(dcp_path)
    learner = PreferenceLearner(dcp_path)
    return InteractiveFeedbackWizard(collector, learner)