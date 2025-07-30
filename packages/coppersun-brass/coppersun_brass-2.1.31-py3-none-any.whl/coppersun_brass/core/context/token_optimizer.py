"""Token optimization system for DCP management"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

class TokenOptimizer:
    """Manages DCP token usage with pruning capabilities"""
    
    def __init__(self, soft_limit=8000, hard_limit=10000):
        self.soft_limit = soft_limit
        self.hard_limit = hard_limit
        
    def estimate_tokens(self, data: Any) -> int:
        """Estimate token count for any data structure"""
        if isinstance(data, dict) or isinstance(data, list):
            json_str = json.dumps(data, separators=(',', ':'))
        else:
            json_str = str(data)
            
        # Industry standard: ~4 characters per token
        base_tokens = len(json_str) // 4
        
        # Add 10% buffer for prompt wrapping
        return int(base_tokens * 1.1)
    
    def prune_dcp(self, dcp_data: Dict) -> Dict:
        """Remove stale observations to stay under token limit"""
        current_tokens = self.estimate_tokens(dcp_data)
        
        if current_tokens < self.soft_limit:
            return dcp_data
            
        print(f"Token count {current_tokens} exceeds soft limit {self.soft_limit}, pruning...")
        
        # Create a copy to avoid modifying original
        pruned_dcp = dcp_data.copy()
        
        # Sort observations by age and priority
        observations = dcp_data.get("current_observations", [])
        
        # Add created_at if missing (for legacy data)
        for obs in observations:
            if "created_at" not in obs:
                obs["created_at"] = datetime.utcnow().isoformat()
        
        # Sort by priority (descending) and age (newest first)
        sorted_obs = sorted(
            observations,
            key=lambda x: (
                -x.get("priority", 0),  # Higher priority first
                x.get("created_at", "")  # Newer first
            )
        )
        
        # Calculate base token count without observations
        base_dcp = {k: v for k, v in dcp_data.items() if k != "current_observations"}
        base_tokens = self.estimate_tokens(base_dcp)
        
        # Keep high-priority and recent items
        pruned_observations = []
        token_count = base_tokens
        
        for obs in sorted_obs:
            obs_tokens = self.estimate_tokens(obs)
            
            # Always keep high priority items
            if obs.get("priority", 0) >= 80:
                pruned_observations.append(obs)
                token_count += obs_tokens
            # Keep others if under soft limit
            elif token_count + obs_tokens < self.soft_limit:
                pruned_observations.append(obs)
                token_count += obs_tokens
            else:
                # Log what we're pruning
                print(f"  Pruning observation: {obs.get('id', 'unknown')} "
                      f"(priority: {obs.get('priority', 0)})")
        
        pruned_dcp["current_observations"] = pruned_observations
        
        # Also prune old recommendations if needed
        if token_count > self.soft_limit:
            recommendations = dcp_data.get("strategic_recommendations", [])
            
            # Remove completed recommendations older than 7 days
            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
            active_recs = []
            
            for rec in recommendations:
                # Keep if no annotation or recent
                if ("claude_annotation" not in rec or 
                    rec.get("created_at", week_ago) > week_ago):
                    active_recs.append(rec)
                else:
                    print(f"  Pruning completed recommendation: {rec.get('summary', '')[:50]}...")
            
            pruned_dcp["strategic_recommendations"] = active_recs
        
        final_tokens = self.estimate_tokens(pruned_dcp)
        print(f"Pruning complete. Tokens reduced from {current_tokens} to {final_tokens}")
        
        return pruned_dcp
    
    def get_token_report(self, dcp_data: Dict) -> str:
        """Generate a token usage report"""
        total_tokens = self.estimate_tokens(dcp_data)
        
        # Break down by section
        sections = {}
        for key, value in dcp_data.items():
            sections[key] = self.estimate_tokens(value)
        
        report = f"Token Usage Report\n"
        report += f"==================\n"
        report += f"Total: {total_tokens} tokens "
        
        if total_tokens > self.hard_limit:
            report += f"❌ EXCEEDS HARD LIMIT ({self.hard_limit})\n"
        elif total_tokens > self.soft_limit:
            report += f"⚠️  EXCEEDS SOFT LIMIT ({self.soft_limit})\n"
        else:
            report += f"✅ OK\n"
        
        report += f"\nBreakdown by section:\n"
        for section, tokens in sorted(sections.items(), key=lambda x: x[1], reverse=True):
            percentage = (tokens / total_tokens) * 100
            report += f"  {section}: {tokens} tokens ({percentage:.1f}%)\n"
        
        return report
