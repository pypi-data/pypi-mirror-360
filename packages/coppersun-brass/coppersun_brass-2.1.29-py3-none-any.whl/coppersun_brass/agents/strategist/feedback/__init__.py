"""
Feedback Integration System for Copper Alloy Brass Planning.

This module provides:
- FeedbackCollector: Captures user feedback on recommendations (UNUSED - ready for activation)
- PersonalizationEngine: Applies preferences to recommendations (UNUSED - ready for activation)

ARCHIVED FEATURES (moved to archive/future-features/):
- PreferenceLearner: Learns preferences from feedback patterns
- UserProfileManager: Manages user and team profiles  
- InteractiveFeedback: Guided feedback collection
"""

# UNUSED IMPORTS - READY FOR ACTIVATION
# These imports are available but not currently used in the main pipeline.
# See docs/implementation/STRATEGIST_FEATURE_ROADMAP.md for activation procedures.

from .feedback_collector import (                        # UNUSED: User feedback system (3-4h to activate)
    FeedbackCollector,
    FeedbackEntry,
    FeedbackType,
    AdoptionStatus,
    RecommendationRegistry
)

from .personalization_engine import (                   # UNUSED: ML recommendation customization (8-12h to activate)
    PersonalizationEngine,
    PersonalizationConfig
)

# ARCHIVED FEATURES - moved to archive/future-features/orphaned-feedback-features/
# preference_learner, user_profile, interactive_feedback were truly orphaned with no imports
# and have been moved to archive for future development

__all__ = [
    # Available but unused features (ready for activation)
    'FeedbackCollector',
    'FeedbackEntry', 
    'FeedbackType',
    'AdoptionStatus',
    'RecommendationRegistry',
    'PersonalizationEngine',
    'PersonalizationConfig'
    
    # Archived features removed from exports:
    # 'PreferenceLearner', 'UserPreferences', 'DataThresholdGuard',
    # 'UserProfileManager', 'UserProfile', 'TeamProfile',
    # 'InteractiveFeedbackWizard', 'create_interactive_wizard'
]