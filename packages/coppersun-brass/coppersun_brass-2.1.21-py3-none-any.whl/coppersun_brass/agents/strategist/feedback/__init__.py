"""
Feedback Integration System for Copper Alloy Brass Planning.

This module provides:
- FeedbackCollector: Captures user feedback on recommendations
- PreferenceLearner: Learns preferences from feedback patterns
- PersonalizationEngine: Applies preferences to recommendations
- InteractiveFeedback: Guided feedback collection
- UserProfileManager: Manages user and team profiles
"""

from .feedback_collector import (
    FeedbackCollector,
    FeedbackEntry,
    FeedbackType,
    AdoptionStatus,
    RecommendationRegistry
)

from .preference_learner import (
    PreferenceLearner,
    UserPreferences,
    DataThresholdGuard
)

from .personalization_engine import (
    PersonalizationEngine,
    PersonalizationConfig
)

from .user_profile import (
    UserProfileManager,
    UserProfile,
    TeamProfile
)

from .interactive_feedback import (
    InteractiveFeedbackWizard,
    create_interactive_wizard
)

__all__ = [
    'FeedbackCollector',
    'FeedbackEntry', 
    'FeedbackType',
    'AdoptionStatus',
    'RecommendationRegistry',
    'PreferenceLearner',
    'UserPreferences',
    'DataThresholdGuard',
    'PersonalizationEngine',
    'PersonalizationConfig',
    'UserProfileManager',
    'UserProfile',
    'TeamProfile',
    'InteractiveFeedbackWizard',
    'create_interactive_wizard'
]