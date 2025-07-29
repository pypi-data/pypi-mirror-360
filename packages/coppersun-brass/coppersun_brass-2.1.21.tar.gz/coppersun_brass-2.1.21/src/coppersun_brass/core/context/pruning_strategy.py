#!/usr/bin/env python3
"""
Smart pruning strategy for DCP observations to manage token usage
"""

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DCPPruningStrategy:
    """Implements intelligent pruning to keep DCP within token limits"""
    
    def __init__(self, token_limit: int = 8000, char_per_token_ratio: float = 4.0):
        """
        Args:
            token_limit: Target token limit (80% of max for safety)
            char_per_token_ratio: Estimated chars per token (default 4.0)
        """
        self.token_limit = token_limit
        self.char_per_token_ratio = char_per_token_ratio
        self.archive_dir = Path(".brass/dcp_archives")
        self.archive_dir.mkdir(exist_ok=True, parents=True)
    
    def prune_observations(self, dcp_data: Dict) -> Tuple[Dict, Dict]:
        """
        Prune observations intelligently to fit within token budget
        
        Returns:
            Tuple of (pruned_dcp, archive_data)
        """
        observations = dcp_data.get('current_observations', [])
        
        # Calculate current size
        current_size = len(json.dumps(dcp_data))
        current_tokens = current_size / self.char_per_token_ratio
        
        logger.info(f"Current DCP: {len(observations)} observations, ~{int(current_tokens)} tokens")
        
        if current_tokens <= self.token_limit:
            return dcp_data, {}
        
        # Sort observations by importance score
        scored_obs = []
        for obs in observations:
            score = self._calculate_importance_score(obs)
            scored_obs.append((score, obs))
        
        # Sort by score (highest first)
        scored_obs.sort(reverse=True, key=lambda x: x[0])
        
        # Keep observations until we hit token limit
        kept_observations = []
        archived_observations = []
        
        # Always keep recent high-priority items
        recent_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        
        # First pass: Keep must-have observations
        remaining_obs = []
        for score, obs in scored_obs:
            if self._is_must_keep(obs, recent_cutoff):
                kept_observations.append(obs)
            else:
                remaining_obs.append((score, obs))
        
        # Calculate space used by must-keeps
        temp_dcp = dcp_data.copy()
        temp_dcp['current_observations'] = kept_observations
        used_tokens = len(json.dumps(temp_dcp)) / self.char_per_token_ratio
        
        # Second pass: Add remaining by score until limit
        for score, obs in remaining_obs:
            # Estimate size with this observation
            test_obs = kept_observations + [obs]
            temp_dcp['current_observations'] = test_obs
            test_tokens = len(json.dumps(temp_dcp)) / self.char_per_token_ratio
            
            if test_tokens <= self.token_limit:
                kept_observations.append(obs)
                used_tokens = test_tokens
            else:
                archived_observations.append(obs)
        
        # Update DCP
        pruned_dcp = dcp_data.copy()
        pruned_dcp['current_observations'] = kept_observations
        
        # Create archive
        archive_data = {
            "archived_at": datetime.now(timezone.utc).isoformat(),
            "reason": "token_limit_pruning",
            "original_count": len(observations),
            "kept_count": len(kept_observations),
            "archived_count": len(archived_observations),
            "observations": archived_observations
        }
        
        logger.info(f"Pruned to {len(kept_observations)} observations, ~{int(used_tokens)} tokens")
        logger.info(f"Archived {len(archived_observations)} observations")
        
        return pruned_dcp, archive_data
    
    def _calculate_importance_score(self, obs: Dict[str, Any]) -> float:
        """Calculate importance score for an observation"""
        score = 0.0
        
        # Priority weight (0-100 -> 0-40 points)
        priority = obs.get('priority', 50)
        score += (priority / 100) * 40
        
        # Recency weight (0-30 points)
        created_str = obs.get('created_at', '')
        if created_str:
            try:
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                age_days = (datetime.now(timezone.utc) - created).days
                recency_score = max(0, 30 - age_days)  # Loses 1 point per day
                score += recency_score
            except:
                pass
        
        # Type weight (0-20 points)
        obs_type = obs.get('type', '')
        type_weights = {
            'security_issue': 20,
            'fixme_item': 18,
            'todo_item': 15,
            'performance_issue': 15,
            'test_coverage': 12,
            'implementation_gap': 10,
            'file_analysis': 8,
            'sprint_completion': 5  # Lower priority for archiving
        }
        score += type_weights.get(obs_type, 10)
        
        # Source diversity (0-10 points)
        source = obs.get('source_agent', '')
        if source in ['scout', 'watch', 'strategist', 'planner']:
            score += 10  # Prefer agent observations
        
        return score
    
    def _is_must_keep(self, obs: Dict, recent_cutoff: datetime) -> bool:
        """Determine if observation must be kept"""
        # Always keep critical security/bug items
        if obs.get('type') in ['security_issue', 'fixme_item'] and obs.get('priority', 0) >= 80:
            return True
        
        # Keep very recent items (last 24 hours)
        created_str = obs.get('created_at', '')
        if created_str:
            try:
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                if created >= datetime.now(timezone.utc) - timedelta(hours=24):
                    return True
            except (ValueError, TypeError):
                # Invalid timestamp format - skip this check
                pass
        
        # Keep latest sprint completion
        if obs.get('type') == 'sprint_completion' and obs.get('id', '').endswith(str(int(datetime.now().timestamp()))[:8]):
            return True
        
        return False
    
    def archive_observations(self, archive_data: Dict[str, Any]) -> Optional[Path]:
        """Save archived observations to file"""
        if not archive_data or not archive_data.get('observations'):
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = self.archive_dir / f"dcp_archive_{timestamp}.json"
        
        try:
            with open(archive_path, 'w') as f:
                json.dump(archive_data, f, indent=2)
            
            logger.info(f"Archived {archive_data['archived_count']} observations to {archive_path}")
            return archive_path
        except (OSError, IOError) as e:
            logger.error(f"Failed to archive observations: {e}")
            return None
    
    def get_archive_summary(self) -> Dict[str, Any]:
        """Get summary of archived observations"""
        archives = list(self.archive_dir.glob("dcp_archive_*.json"))
        
        total_archived = 0
        by_type = {}
        
        for archive_path in archives:
            try:
                with open(archive_path, 'r') as f:
                    data = json.load(f)
                    total_archived += data.get('archived_count', 0)
                    
                    for obs in data.get('observations', []):
                        obs_type = obs.get('type', 'unknown')
                        by_type[obs_type] = by_type.get(obs_type, 0) + 1
            except (OSError, json.JSONDecodeError) as e:
                logger.warning(f"Failed to read archive {archive_path}: {e}")
        
        return {
            "archive_count": len(archives),
            "total_observations": total_archived,
            "by_type": by_type,
            "archive_dir": str(self.archive_dir)
        }


def test_pruning():
    """Test the pruning strategy"""
    print("🧪 Testing DCP Pruning Strategy")
    print("=" * 50)
    
    # Load current DCP
    with open('coppersun_brass.context.json', 'r') as f:
        dcp_data = json.load(f)
    
    # Create pruner with aggressive limit for testing
    pruner = DCPPruningStrategy(token_limit=5000)  # Much lower than current ~10K
    
    # Test pruning
    pruned_dcp, archive_data = pruner.prune_observations(dcp_data)
    
    # Show results
    print(f"\nOriginal observations: {len(dcp_data.get('current_observations', []))}")
    print(f"Pruned observations: {len(pruned_dcp.get('current_observations', []))}")
    print(f"Archived observations: {len(archive_data.get('observations', []))}")
    
    # Show what types were kept
    kept_types = {}
    for obs in pruned_dcp.get('current_observations', []):
        t = obs.get('type', 'unknown')
        kept_types[t] = kept_types.get(t, 0) + 1
    
    print("\nKept observations by type:")
    for t, count in sorted(kept_types.items()):
        print(f"  {t}: {count}")
    
    # Estimate tokens
    pruned_size = len(json.dumps(pruned_dcp))
    pruned_tokens = pruned_size / 4.0
    print(f"\nPruned DCP size: {pruned_size} chars (~{int(pruned_tokens)} tokens)")
    
    return pruner, pruned_dcp, archive_data


if __name__ == "__main__":
    test_pruning()