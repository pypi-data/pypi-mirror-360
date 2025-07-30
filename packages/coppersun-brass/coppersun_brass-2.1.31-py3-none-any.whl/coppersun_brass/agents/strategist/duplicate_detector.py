# coppersun_brass/agents/strategist/duplicate_detector.py
"""
Duplicate detection engine for Copper Alloy Brass observations
Identifies redundant observations using content similarity and timing analysis
"""

import hashlib
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Set, Tuple, Optional
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)

class DuplicateDetector:
    """
    Detects duplicate observations using multiple similarity measures
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Similarity thresholds
        self.content_threshold = self.config.get('content_threshold', 0.85)
        self.location_threshold = self.config.get('location_threshold', 0.9)
        self.time_window_hours = self.config.get('time_window_hours', 24)
        
        # Enable/disable detection methods
        self.use_content_hash = self.config.get('use_content_hash', True)
        self.use_semantic_similarity = self.config.get('use_semantic_similarity', True)
        self.use_location_matching = self.config.get('use_location_matching', True)
        self.use_temporal_grouping = self.config.get('use_temporal_grouping', True)
        
        # Cache for expensive operations
        self._content_cache = {}
        self._hash_cache = {}
        
        logger.debug(f"Duplicate detector initialized with thresholds: content={self.content_threshold}, location={self.location_threshold}")
    
    def find_duplicates(self, observations: List[Dict]) -> Dict[str, List[str]]:
        """
        Find duplicate observations and group them
        
        Args:
            observations: List of observation dictionaries
            
        Returns:
            Dict mapping canonical observation IDs to lists of duplicate IDs
        """
        if len(observations) < 2:
            return {}
        
        logger.debug(f"Analyzing {len(observations)} observations for duplicates")
        
        duplicates = {}
        processed_ids = set()
        
        for i, obs in enumerate(observations):
            obs_id = obs.get('id', f'obs_{i}')
            
            if obs_id in processed_ids:
                continue
            
            # Find all observations similar to this one
            similar_obs = self._find_similar_observations(obs, observations[i+1:])
            
            if similar_obs:
                # Use earliest observation as canonical
                all_similar = [obs] + similar_obs
                canonical = min(all_similar, key=lambda x: self._get_observation_timestamp(x))
                canonical_id = canonical.get('id', obs_id)
                
                # Collect duplicate IDs
                duplicate_ids = [
                    o.get('id', f'obs_{observations.index(o)}') 
                    for o in all_similar 
                    if o.get('id') != canonical_id
                ]
                
                if duplicate_ids:
                    duplicates[canonical_id] = duplicate_ids
                    processed_ids.update([canonical_id] + duplicate_ids)
                    
                    logger.info(f"Found duplicate group: {canonical_id} with {len(duplicate_ids)} duplicates")
        
        return duplicates
    
    def _find_similar_observations(self, target_obs: Dict, candidate_obs: List[Dict]) -> List[Dict]:
        """Find observations similar to target observation"""
        similar = []
        
        for candidate in candidate_obs:
            similarity_score = self._calculate_similarity(target_obs, candidate)
            
            if similarity_score >= self.content_threshold:
                similar.append(candidate)
                logger.debug(f"Similar observation found: {similarity_score:.2f} similarity")
        
        return similar
    
    def _calculate_similarity(self, obs1: Dict, obs2: Dict) -> float:
        """
        Calculate overall similarity between two observations
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        scores = []
        weights = []
        
        # Content similarity
        if self.use_content_hash or self.use_semantic_similarity:
            content_score = self._calculate_content_similarity(obs1, obs2)
            scores.append(content_score)
            weights.append(0.6)  # Content is most important
        
        # Location similarity - only add if location exists
        if self.use_location_matching:
            location_score = self._calculate_location_similarity(obs1, obs2)
            # Only include location in calculation if either observation has location
            if self._extract_location(obs1) or self._extract_location(obs2):
                scores.append(location_score)
                weights.append(0.3)
        
        # Temporal proximity
        if self.use_temporal_grouping:
            temporal_score = self._calculate_temporal_similarity(obs1, obs2)
            scores.append(temporal_score)
            weights.append(0.1)
        
        # Weighted average
        if not scores:
            return 0.0
        
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        total_weight = sum(weights)
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _calculate_content_similarity(self, obs1: Dict, obs2: Dict) -> float:
        """Calculate content-based similarity"""
        # Fast hash check first
        if self.use_content_hash:
            hash1 = self._get_content_hash(obs1)
            hash2 = self._get_content_hash(obs2)
            if hash1 == hash2:
                return 1.0
        
        # Semantic similarity check
        if self.use_semantic_similarity:
            return self._calculate_semantic_similarity(obs1, obs2)
        
        return 0.0
    
    def _calculate_semantic_similarity(self, obs1: Dict, obs2: Dict) -> float:
        """Calculate semantic similarity between observation summaries"""
        summary1 = self._normalize_text(obs1.get('summary', ''))
        summary2 = self._normalize_text(obs2.get('summary', ''))
        
        if not summary1 or not summary2:
            return 0.0
        
        # Use sequence matcher for text similarity
        matcher = SequenceMatcher(None, summary1, summary2)
        ratio = matcher.ratio()
        
        # Boost similarity for common patterns
        if self._has_common_patterns(summary1, summary2):
            ratio = min(1.0, ratio * 1.1)
        
        return ratio
    
    def _calculate_location_similarity(self, obs1: Dict, obs2: Dict) -> float:
        """Calculate location-based similarity"""
        location1 = self._extract_location(obs1)
        location2 = self._extract_location(obs2)
        
        if not location1 or not location2:
            return 0.0
        
        # Exact match
        if location1 == location2:
            return 1.0
        
        # Partial match (same file, different lines)
        if self._same_file_different_lines(location1, location2):
            return 0.8
        
        # Same directory
        if self._same_directory(location1, location2):
            return 0.6
        
        return 0.0
    
    def _calculate_temporal_similarity(self, obs1: Dict, obs2: Dict) -> float:
        """Calculate temporal proximity similarity"""
        time1 = self._get_observation_timestamp(obs1)
        time2 = self._get_observation_timestamp(obs2)
        
        if not time1 or not time2:
            return 0.0
        
        time_diff = abs((time1 - time2).total_seconds() / 3600)  # Hours
        
        if time_diff <= 1:  # Within 1 hour
            return 1.0
        elif time_diff <= self.time_window_hours:
            # Linear decay over time window
            return 1.0 - (time_diff / self.time_window_hours)
        else:
            return 0.0
    
    def _get_content_hash(self, obs: Dict) -> str:
        """Get content hash for fast duplicate detection"""
        obs_id = obs.get('id', '')
        
        if obs_id in self._hash_cache:
            return self._hash_cache[obs_id]
        
        # Create hash from key content fields
        content_parts = [
            obs.get('type', ''),
            self._normalize_text(obs.get('summary', '')),
            self._extract_location(obs) or ''
        ]
        
        content_str = '|'.join(content_parts)
        content_hash = hashlib.md5(content_str.encode()).hexdigest()
        
        # Cache result
        self._hash_cache[obs_id] = content_hash
        
        return content_hash
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ''
        
        # Convert to lowercase
        normalized = text.lower()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Remove common noise words
        noise_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        words = normalized.split()
        filtered_words = [w for w in words if w not in noise_words]
        
        return ' '.join(filtered_words)
    
    def _extract_location(self, obs: Dict) -> Optional[str]:
        """Extract location information from observation"""
        summary = obs.get('summary', '')
        
        # Look for common location patterns
        location_patterns = [
            r'\[Location: ([^\]]+)\]',
            r'Location: ([^\,\|]+)',
            r'in ([a-zA-Z0-9_./\\-]+\.[a-zA-Z]+)',
            r'file: ([a-zA-Z0-9_./\\-]+)',
            r'([a-zA-Z0-9_./\\-]+\.py:\d+)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, summary, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _has_common_patterns(self, text1: str, text2: str) -> bool:
        """Check if texts share common patterns"""
        # Check for shared technical terms
        tech_patterns = [
            r'\b(todo|fixme|bug|error|warning|critical)\b',
            r'\b(missing|undefined|not found|failed)\b',
            r'\b(security|performance|optimization)\b'
        ]
        
        for pattern in tech_patterns:
            if re.search(pattern, text1, re.IGNORECASE) and re.search(pattern, text2, re.IGNORECASE):
                return True
        
        return False
    
    def _same_file_different_lines(self, loc1: str, loc2: str) -> bool:
        """Check if locations are same file but different lines"""
        # Extract file parts (remove line numbers)
        file1 = re.sub(r':\d+.*$', '', loc1)
        file2 = re.sub(r':\d+.*$', '', loc2)
        
        return file1 == file2 and loc1 != loc2
    
    def _same_directory(self, loc1: str, loc2: str) -> bool:
        """Check if locations are in same directory"""
        import os
        
        dir1 = os.path.dirname(loc1)
        dir2 = os.path.dirname(loc2)
        
        return dir1 == dir2 and dir1 != ''
    
    def _get_observation_timestamp(self, obs: Dict) -> Optional[datetime]:
        """Get observation timestamp as datetime object"""
        created_str = obs.get('created_at')
        if not created_str:
            return None
        
        try:
            return datetime.fromisoformat(created_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return None
    
    def get_duplicate_stats(self, duplicates: Dict[str, List[str]]) -> Dict[str, int]:
        """Get statistics about detected duplicates"""
        total_duplicates = sum(len(dups) for dups in duplicates.values())
        
        return {
            'duplicate_groups': len(duplicates),
            'total_duplicates': total_duplicates,
            'space_saved': total_duplicates,  # Number of observations that can be removed
            'largest_group': max((len(dups) for dups in duplicates.values()), default=0)
        }
    
    def get_status(self) -> Dict[str, any]:
        """Get duplicate detector status"""
        return {
            'content_threshold': self.content_threshold,
            'location_threshold': self.location_threshold,
            'time_window_hours': self.time_window_hours,
            'cache_size': len(self._content_cache) + len(self._hash_cache),
            'methods_enabled': {
                'content_hash': self.use_content_hash,
                'semantic_similarity': self.use_semantic_similarity,
                'location_matching': self.use_location_matching,
                'temporal_grouping': self.use_temporal_grouping
            }
        }