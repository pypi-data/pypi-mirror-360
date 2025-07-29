"""
UserProfile: Manages user profiles and team configurations.

This component implements:
- User profile creation and management
- Team profile inheritance
- Profile export/import
- Profile versioning
- Multi-user support
"""

import json
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib

# DCP integration
try:
    from coppersun_brass.core.context.dcp_manager import DCPManager
    DCP_AVAILABLE = True
except ImportError:
    DCP_AVAILABLE = False
    DCPManager = None

logger = logging.getLogger(__name__)


@dataclass
class TeamProfile:
    """Team-level preferences and policies."""
    team_id: str
    name: str
    
    # Mandatory preferences (override user preferences)
    mandatory_capabilities: List[str] = field(default_factory=list)
    forbidden_practices: List[str] = field(default_factory=list)
    required_frameworks: List[str] = field(default_factory=list)
    
    # Suggested preferences (used as defaults)
    default_capability_weights: Dict[str, float] = field(default_factory=dict)
    default_severity_weights: Dict[str, float] = field(default_factory=dict)
    
    # Policies
    max_effort_level: str = "large"  # small, medium, large
    min_security_score: int = 80
    require_test_coverage: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass 
class UserProfile:
    """Complete user profile including preferences and metadata."""
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    
    # Team membership
    team_id: Optional[str] = None
    
    # Role-based defaults
    role: str = "developer"  # developer, lead, architect, manager
    
    # Profile settings
    personalization_enabled: bool = True
    share_anonymized_data: bool = True
    
    # Preference snapshot
    preference_snapshot: Optional[Dict[str, Any]] = None
    
    # Activity tracking
    last_active: Optional[datetime] = None
    total_feedback_given: int = 0
    total_recommendations_received: int = 0
    
    # Profile versioning
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime objects
        for key in ['created_at', 'updated_at', 'last_active']:
            if data.get(key) and isinstance(data[key], datetime):
                data[key] = data[key].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create from dictionary."""
        # Convert ISO strings back to datetime
        for key in ['created_at', 'updated_at', 'last_active']:
            if data.get(key) and isinstance(data[key], str):
                data[key] = datetime.fromisoformat(data[key].replace('Z', '+00:00'))
        return cls(**data)


class UserProfileManager:
    """
    Manages user profiles and team configurations.
    
    Features:
    - Multi-user profile support
    - Team profile inheritance
    - Profile persistence via DCP
    - Export/import capabilities
    - Profile migration
    """
    
    def __init__(self, dcp_path: Optional[str] = None):
        """
        Initialize manager.
        
        Args:
            dcp_path: Path to DCP file/directory
        """
        self.dcp_manager = None
        if DCP_AVAILABLE and dcp_path:
            try:
                # DCPManager expects project root directory
                if dcp_path.endswith('.json'):
                    project_root = str(Path(dcp_path).parent)
                else:
                    project_root = dcp_path
                self.dcp_manager = DCPManager(project_root)
                logger.info("UserProfileManager: DCP integration enabled")
            except Exception as e:
                logger.warning(f"UserProfileManager: DCP unavailable: {e}")
        
        self._profiles_cache = {}
        self._teams_cache = {}
    
    def create_profile(self, 
                      user_id: str,
                      email: Optional[str] = None,
                      name: Optional[str] = None,
                      role: str = "developer",
                      team_id: Optional[str] = None) -> UserProfile:
        """
        Create a new user profile.
        
        Args:
            user_id: Unique user identifier
            email: User email
            name: Display name
            role: User role
            team_id: Team membership
            
        Returns:
            Created profile
        """
        # Check if profile exists
        existing = self.get_profile(user_id)
        if existing:
            logger.warning(f"Profile already exists for {user_id}")
            return existing
        
        # Create new profile
        profile = UserProfile(
            user_id=user_id,
            email=email,
            name=name,
            role=role,
            team_id=team_id
        )
        
        # Apply team defaults if applicable
        if team_id:
            team = self.get_team(team_id)
            if team:
                profile = self._apply_team_defaults(profile, team)
        
        # Save profile
        self._save_profile(profile)
        
        # Record creation event
        self._record_profile_event('created', user_id)
        
        return profile
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            Profile or None if not found
        """
        # Check cache
        if user_id in self._profiles_cache:
            return self._profiles_cache[user_id]
        
        # Load from DCP
        profile = self._load_profile(user_id)
        if profile:
            self._profiles_cache[user_id] = profile
        
        return profile
    
    def update_profile(self, 
                      user_id: str,
                      updates: Dict[str, Any]) -> Optional[UserProfile]:
        """
        Update user profile.
        
        Args:
            user_id: User identifier
            updates: Fields to update
            
        Returns:
            Updated profile or None if not found
        """
        profile = self.get_profile(user_id)
        if not profile:
            logger.error(f"Profile not found: {user_id}")
            return None
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        # Update metadata
        profile.updated_at = datetime.now(timezone.utc)
        profile.version += 1
        
        # Save changes
        self._save_profile(profile)
        
        # Clear cache
        if user_id in self._profiles_cache:
            del self._profiles_cache[user_id]
        
        return profile
    
    def delete_profile(self, user_id: str) -> bool:
        """
        Delete user profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            Success status
        """
        # Remove from cache
        if user_id in self._profiles_cache:
            del self._profiles_cache[user_id]
        
        # Remove from DCP
        success = self._delete_profile_from_dcp(user_id)
        
        if success:
            self._record_profile_event('deleted', user_id)
        
        return success
    
    def create_team(self, 
                   team_id: str,
                   name: str,
                   **kwargs) -> TeamProfile:
        """
        Create a team profile.
        
        Args:
            team_id: Unique team identifier
            name: Team name
            **kwargs: Additional team settings
            
        Returns:
            Created team profile
        """
        team = TeamProfile(
            team_id=team_id,
            name=name,
            **kwargs
        )
        
        self._save_team(team)
        return team
    
    def get_team(self, team_id: str) -> Optional[TeamProfile]:
        """Get team profile."""
        if team_id in self._teams_cache:
            return self._teams_cache[team_id]
        
        team = self._load_team(team_id)
        if team:
            self._teams_cache[team_id] = team
        
        return team
    
    def list_profiles(self, 
                     team_id: Optional[str] = None,
                     role: Optional[str] = None) -> List[UserProfile]:
        """
        List all profiles with optional filters.
        
        Args:
            team_id: Filter by team
            role: Filter by role
            
        Returns:
            List of matching profiles
        """
        profiles = self._load_all_profiles()
        
        # Apply filters
        if team_id:
            profiles = [p for p in profiles if p.team_id == team_id]
        
        if role:
            profiles = [p for p in profiles if p.role == role]
        
        return profiles
    
    def export_profile(self, user_id: str) -> Optional[str]:
        """
        Export profile to JSON string.
        
        Args:
            user_id: User identifier
            
        Returns:
            JSON string or None
        """
        profile = self.get_profile(user_id)
        if not profile:
            return None
        
        # Include preferences if available
        export_data = {
            'profile': profile.to_dict(),
            'export_version': '1.0',
            'export_date': datetime.now(timezone.utc).isoformat()
        }
        
        return json.dumps(export_data, indent=2)
    
    def import_profile(self, json_data: str, override_id: Optional[str] = None) -> Optional[UserProfile]:
        """
        Import profile from JSON.
        
        Args:
            json_data: JSON string
            override_id: Override user_id if provided
            
        Returns:
            Imported profile or None
        """
        try:
            data = json.loads(json_data)
            profile_data = data.get('profile', {})
            
            if override_id:
                profile_data['user_id'] = override_id
            
            # Create profile from data
            profile = UserProfile.from_dict(profile_data)
            
            # Save imported profile
            self._save_profile(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to import profile: {e}")
            return None
    
    def _apply_team_defaults(self, profile: UserProfile, team: TeamProfile) -> UserProfile:
        """Apply team defaults to profile."""
        # Set team overrides in preference snapshot
        if not profile.preference_snapshot:
            profile.preference_snapshot = {}
        
        profile.preference_snapshot['team_overrides'] = {
            'mandatory_capabilities': team.mandatory_capabilities,
            'forbidden_practices': team.forbidden_practices,
            'required_frameworks': team.required_frameworks,
            'max_effort': team.max_effort_level,
            'min_security_score': team.min_security_score
        }
        
        return profile
    
    def _save_profile(self, profile: UserProfile) -> None:
        """Save profile to DCP."""
        if not self.dcp_manager:
            return
        
        try:
            # Load all profiles
            profiles_data = self._load_profiles_data()
            
            # Update or add profile
            profiles_data[profile.user_id] = profile.to_dict()
            
            # Save back to DCP
            self.dcp_manager.update_metadata({
                'user_profiles': profiles_data
            })
            
            logger.info(f"Saved profile for {profile.user_id}")
            
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")
    
    def _load_profile(self, user_id: str) -> Optional[UserProfile]:
        """Load profile from DCP."""
        if not self.dcp_manager:
            return None
        
        try:
            profiles_data = self._load_profiles_data()
            
            if user_id in profiles_data:
                return UserProfile.from_dict(profiles_data[user_id])
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load profile: {e}")
            return None
    
    def _load_all_profiles(self) -> List[UserProfile]:
        """Load all profiles from DCP."""
        if not self.dcp_manager:
            return []
        
        try:
            profiles_data = self._load_profiles_data()
            
            profiles = []
            for user_id, data in profiles_data.items():
                try:
                    profile = UserProfile.from_dict(data)
                    profiles.append(profile)
                except Exception as e:
                    logger.error(f"Failed to load profile {user_id}: {e}")
            
            return profiles
            
        except Exception as e:
            logger.error(f"Failed to load profiles: {e}")
            return []
    
    def _load_profiles_data(self) -> Dict[str, Dict[str, Any]]:
        """Load raw profiles data from DCP."""
        if not self.dcp_manager:
            return {}
        
        try:
            dcp_data = self.dcp_manager.read_dcp()
            if not dcp_data:
                return {}
            
            meta = dcp_data.get('meta', {})
            return meta.get('user_profiles', {})
            
        except Exception:
            return {}
    
    def _delete_profile_from_dcp(self, user_id: str) -> bool:
        """Delete profile from DCP."""
        if not self.dcp_manager:
            return False
        
        try:
            profiles_data = self._load_profiles_data()
            
            if user_id in profiles_data:
                del profiles_data[user_id]
                
                # Save back
                self.dcp_manager.update_metadata({
                    'user_profiles': profiles_data
                })
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete profile: {e}")
            return False
    
    def _save_team(self, team: TeamProfile) -> None:
        """Save team profile to DCP."""
        if not self.dcp_manager:
            return
        
        try:
            # Load all teams
            teams_data = self._load_teams_data()
            
            # Convert team to dict
            team_dict = asdict(team)
            # Convert datetimes
            for key in ['created_at', 'updated_at']:
                if key in team_dict and isinstance(team_dict[key], datetime):
                    team_dict[key] = team_dict[key].isoformat()
            
            # Update or add team
            teams_data[team.team_id] = team_dict
            
            # Save back to DCP
            self.dcp_manager.update_metadata({
                'team_profiles': teams_data
            })
            
            logger.info(f"Saved team profile for {team.team_id}")
            
        except Exception as e:
            logger.error(f"Failed to save team: {e}")
    
    def _load_team(self, team_id: str) -> Optional[TeamProfile]:
        """Load team from DCP."""
        if not self.dcp_manager:
            return None
        
        try:
            teams_data = self._load_teams_data()
            
            if team_id in teams_data:
                data = teams_data[team_id]
                # Convert ISO strings back to datetime
                for key in ['created_at', 'updated_at']:
                    if data.get(key) and isinstance(data[key], str):
                        data[key] = datetime.fromisoformat(data[key].replace('Z', '+00:00'))
                
                return TeamProfile(**data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load team: {e}")
            return None
    
    def _load_teams_data(self) -> Dict[str, Dict[str, Any]]:
        """Load raw teams data from DCP."""
        if not self.dcp_manager:
            return {}
        
        try:
            dcp_data = self.dcp_manager.read_dcp()
            if not dcp_data:
                return {}
            
            meta = dcp_data.get('meta', {})
            return meta.get('team_profiles', {})
            
        except Exception:
            return {}
    
    def _record_profile_event(self, event_type: str, user_id: str) -> None:
        """Record profile event in DCP."""
        if not self.dcp_manager:
            return
        
        try:
            observation = {
                "type": "user_profile_event",
                "priority": 20,
                "details": {
                    "event_type": event_type,
                    "user_id": user_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
            self.dcp_manager.add_observation(observation)
            
        except Exception as e:
            logger.error(f"Failed to record event: {e}")
    
    def migrate_anonymous_data(self, from_user: str = "default", to_user: str = None) -> bool:
        """
        Migrate anonymous user data to named profile.
        
        Args:
            from_user: Source user ID (default: "default")
            to_user: Target user ID
            
        Returns:
            Success status
        """
        if not to_user:
            return False
        
        # Get source profile
        source = self.get_profile(from_user)
        if not source:
            logger.warning(f"No profile found for {from_user}")
            return False
        
        # Check target doesn't exist
        if self.get_profile(to_user):
            logger.error(f"Target profile {to_user} already exists")
            return False
        
        # Create new profile with migrated data
        target = UserProfile(
            user_id=to_user,
            preference_snapshot=source.preference_snapshot,
            total_feedback_given=source.total_feedback_given,
            total_recommendations_received=source.total_recommendations_received,
            created_at=source.created_at  # Preserve original creation
        )
        
        # Save new profile
        self._save_profile(target)
        
        # Record migration
        self._record_profile_event('migrated', f"{from_user}->{to_user}")
        
        return True