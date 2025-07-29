"""Observation Relationship Tracking System

General Staff Role: Intelligence Analysis (G2) - Pattern Recognition
Tracks relationships between observations to enable AI agents to understand
how observations connect, derive insights, and build decision chains.

Persistent Value: Creates a knowledge graph of observation relationships
that helps AI understand causality, correlation, and decision provenance.
"""

import json
import time
import uuid
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .constants import FilePaths, ObservationTypes

logger = logging.getLogger(__name__)


class RelationshipType(Enum):
    """Types of relationships between observations."""
    CAUSED_BY = "caused_by"           # Observation A caused observation B
    FOLLOWED_BY = "followed_by"       # Observation A was followed by B (temporal)
    REFERENCES = "references"         # Observation A references B (content)
    DUPLICATES = "duplicates"         # Observation A duplicates B
    CONTRADICTS = "contradicts"       # Observation A contradicts B
    SUPPORTS = "supports"             # Observation A supports B
    RESOLVES = "resolves"             # Observation A resolves B
    SUPERSEDES = "supersedes"         # Observation A supersedes B
    GROUPS_WITH = "groups_with"       # Observation A groups with B (thematic)
    DERIVES_FROM = "derives_from"     # Observation A derives from B


@dataclass
class ObservationRelationship:
    """Represents a relationship between two observations."""
    id: str
    source_obs_id: str
    target_obs_id: str
    relationship_type: RelationshipType
    confidence: float  # 0.0 to 1.0
    created_at: datetime
    created_by: str  # Agent that created the relationship
    metadata: Dict[str, Any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)  # Supporting evidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'source_obs_id': self.source_obs_id,
            'target_obs_id': self.target_obs_id,
            'relationship_type': self.relationship_type.value,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'metadata': self.metadata,
            'evidence': self.evidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ObservationRelationship':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            source_obs_id=data['source_obs_id'],
            target_obs_id=data['target_obs_id'],
            relationship_type=RelationshipType(data['relationship_type']),
            confidence=data['confidence'],
            created_at=datetime.fromisoformat(data['created_at']),
            created_by=data['created_by'],
            metadata=data.get('metadata', {}),
            evidence=data.get('evidence', [])
        )


@dataclass
class ObservationChain:
    """Represents a chain of related observations."""
    id: str
    observations: List[str]  # Observation IDs in order
    chain_type: str  # e.g., "causal", "temporal", "thematic"
    strength: float  # Overall chain strength (0.0 to 1.0)
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'observations': self.observations,
            'chain_type': self.chain_type,
            'strength': self.strength,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class RelationshipInsight:
    """Represents an insight derived from relationship analysis."""
    id: str
    insight_type: str  # e.g., "pattern", "anomaly", "trend"
    description: str
    confidence: float
    supporting_relationships: List[str]  # Relationship IDs
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'insight_type': self.insight_type,
            'description': self.description,
            'confidence': self.confidence,
            'supporting_relationships': self.supporting_relationships,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }


class ObservationRelationshipTracker:
    """Tracks and analyzes relationships between observations.
    
    This system provides:
    1. Automatic relationship detection
    2. Manual relationship creation
    3. Relationship strength analysis
    4. Chain detection and analysis
    5. Insight generation from patterns
    """
    
    def __init__(self, project_path: str, dcp_manager=None):
        """Initialize relationship tracker.
        
        Args:
            project_path: Project root path
            dcp_manager: Optional DCP manager for observation access
        """
        self.project_path = Path(project_path)
        self.dcp_manager = dcp_manager
        
        # Storage paths
        self.relationships_file = self.project_path / FilePaths.CONFIG_DIR / "observation_relationships.json"
        self.chains_file = self.project_path / FilePaths.CONFIG_DIR / "observation_chains.json"
        self.insights_file = self.project_path / FilePaths.CONFIG_DIR / "relationship_insights.json"
        
        # Ensure storage directory exists
        self.relationships_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage
        self.relationships: Dict[str, ObservationRelationship] = {}
        self.chains: Dict[str, ObservationChain] = {}
        self.insights: Dict[str, RelationshipInsight] = {}
        
        # Indexes for fast lookups
        self._source_index: Dict[str, Set[str]] = {}  # obs_id -> relationship_ids
        self._target_index: Dict[str, Set[str]] = {}  # obs_id -> relationship_ids
        self._type_index: Dict[RelationshipType, Set[str]] = {}  # type -> relationship_ids
        
        # Analysis configuration
        self.auto_detect_enabled = True
        self.confidence_threshold = 0.3
        self.max_relationships_per_observation = 20
        
        # Threading
        self._lock = threading.RLock()
        self._analysis_thread = None
        self._shutdown = threading.Event()
        
        # Load existing data
        self._load_data()
        
        # Start automatic analysis
        if self.auto_detect_enabled:
            self.start_analysis()
    
    def add_relationship(
        self,
        source_obs_id: str,
        target_obs_id: str,
        relationship_type: RelationshipType,
        confidence: float,
        created_by: str,
        evidence: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Add a relationship between observations.
        
        Args:
            source_obs_id: Source observation ID
            target_obs_id: Target observation ID
            relationship_type: Type of relationship
            confidence: Confidence level (0.0 to 1.0)
            created_by: Agent creating the relationship
            evidence: Supporting evidence
            metadata: Additional metadata
            
        Returns:
            Relationship ID
        """
        with self._lock:
            # Generate unique ID
            relationship_id = f"rel_{uuid.uuid4().hex[:8]}_{int(time.time())}"
            
            # Create relationship
            relationship = ObservationRelationship(
                id=relationship_id,
                source_obs_id=source_obs_id,
                target_obs_id=target_obs_id,
                relationship_type=relationship_type,
                confidence=confidence,
                created_at=datetime.now(),
                created_by=created_by,
                metadata=metadata or {},
                evidence=evidence or []
            )
            
            # Store relationship
            self.relationships[relationship_id] = relationship
            
            # Update indexes
            self._update_indexes(relationship)
            
            # Save to disk
            self._save_relationships()
            
            logger.info(
                f"Added relationship: {source_obs_id} --{relationship_type.value}--> {target_obs_id} "
                f"(confidence: {confidence:.2f})"
            )
            
            return relationship_id
    
    def get_relationships(
        self,
        obs_id: Optional[str] = None,
        relationship_type: Optional[RelationshipType] = None,
        min_confidence: Optional[float] = None
    ) -> List[ObservationRelationship]:
        """Get relationships with optional filtering.
        
        Args:
            obs_id: Filter by observation ID (source or target)
            relationship_type: Filter by relationship type
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of matching relationships
        """
        with self._lock:
            relationships = list(self.relationships.values())
            
            # Filter by observation ID
            if obs_id:
                relationships = [
                    rel for rel in relationships
                    if rel.source_obs_id == obs_id or rel.target_obs_id == obs_id
                ]
            
            # Filter by type
            if relationship_type:
                relationships = [
                    rel for rel in relationships
                    if rel.relationship_type == relationship_type
                ]
            
            # Filter by confidence
            if min_confidence is not None:
                relationships = [
                    rel for rel in relationships
                    if rel.confidence >= min_confidence
                ]
            
            return relationships
    
    def get_related_observations(
        self,
        obs_id: str,
        max_depth: int = 2,
        relationship_types: Optional[List[RelationshipType]] = None
    ) -> Dict[str, Any]:
        """Get observations related to the given observation.
        
        Args:
            obs_id: Source observation ID
            max_depth: Maximum relationship depth to traverse
            relationship_types: Filter by relationship types
            
        Returns:
            Dictionary with related observations and paths
        """
        with self._lock:
            visited = set()
            result = {
                'direct_relationships': [],
                'related_observations': {},
                'relationship_paths': []
            }
            
            def traverse(current_obs_id: str, current_depth: int, path: List[str]):
                if current_depth > max_depth or current_obs_id in visited:
                    return
                
                visited.add(current_obs_id)
                
                # Get direct relationships
                direct_rels = [
                    rel for rel in self.relationships.values()
                    if rel.source_obs_id == current_obs_id
                ]
                
                # Filter by type if specified
                if relationship_types:
                    direct_rels = [
                        rel for rel in direct_rels
                        if rel.relationship_type in relationship_types
                    ]
                
                for rel in direct_rels:
                    target_id = rel.target_obs_id
                    
                    # Add to results
                    if current_depth == 1:  # Direct relationships
                        result['direct_relationships'].append(rel.to_dict())
                    
                    if target_id not in result['related_observations']:
                        result['related_observations'][target_id] = {
                            'depth': current_depth,
                            'relationships': []
                        }
                    
                    result['related_observations'][target_id]['relationships'].append(rel.to_dict())
                    
                    # Add path
                    current_path = path + [rel.id]
                    result['relationship_paths'].append({
                        'target_obs_id': target_id,
                        'path': current_path,
                        'depth': current_depth
                    })
                    
                    # Recurse
                    traverse(target_id, current_depth + 1, current_path)
            
            traverse(obs_id, 1, [])
            return result
    
    def detect_chains(self, min_chain_length: int = 3) -> List[ObservationChain]:
        """Detect chains of related observations.
        
        Args:
            min_chain_length: Minimum number of observations in a chain
            
        Returns:
            List of detected chains
        """
        with self._lock:
            chains = []
            visited_relationships = set()
            
            # Look for causal chains
            causal_rels = [
                rel for rel in self.relationships.values()
                if rel.relationship_type in [RelationshipType.CAUSED_BY, RelationshipType.FOLLOWED_BY]
            ]
            
            for start_rel in causal_rels:
                if start_rel.id in visited_relationships:
                    continue
                
                # Build chain starting from this relationship
                chain_obs = [start_rel.source_obs_id, start_rel.target_obs_id]
                chain_rels = [start_rel.id]
                current_obs = start_rel.target_obs_id
                
                # Follow the chain
                while True:
                    next_rels = [
                        rel for rel in causal_rels
                        if (rel.source_obs_id == current_obs and 
                            rel.id not in chain_rels and
                            rel.target_obs_id not in chain_obs)  # Avoid cycles
                    ]
                    
                    if not next_rels:
                        break
                    
                    # Take the highest confidence relationship
                    best_rel = max(next_rels, key=lambda r: r.confidence)
                    chain_obs.append(best_rel.target_obs_id)
                    chain_rels.append(best_rel.id)
                    current_obs = best_rel.target_obs_id
                
                # Create chain if long enough
                if len(chain_obs) >= min_chain_length:
                    chain_id = f"chain_{uuid.uuid4().hex[:8]}"
                    
                    # Calculate chain strength
                    strengths = [
                        self.relationships[rel_id].confidence
                        for rel_id in chain_rels
                    ]
                    chain_strength = sum(strengths) / len(strengths)
                    
                    chain = ObservationChain(
                        id=chain_id,
                        observations=chain_obs,
                        chain_type="causal",
                        strength=chain_strength,
                        created_at=datetime.now(),
                        metadata={
                            'relationship_ids': chain_rels,
                            'detection_method': 'causal_following'
                        }
                    )
                    
                    chains.append(chain)
                    visited_relationships.update(chain_rels)
            
            return chains
    
    def generate_insights(self) -> List[RelationshipInsight]:
        """Generate insights from relationship patterns.
        
        Returns:
            List of generated insights
        """
        with self._lock:
            insights = []
            
            # Insight 1: High-frequency relationship sources
            source_counts = {}
            for rel in self.relationships.values():
                source_counts[rel.source_obs_id] = source_counts.get(rel.source_obs_id, 0) + 1
            
            high_activity_sources = [
                obs_id for obs_id, count in source_counts.items()
                if count >= 5  # Threshold for high activity
            ]
            
            if high_activity_sources:
                insight_id = f"insight_{uuid.uuid4().hex[:8]}"
                insights.append(RelationshipInsight(
                    id=insight_id,
                    insight_type="pattern",
                    description=f"High-activity observations detected: {len(high_activity_sources)} observations with 5+ relationships",
                    confidence=0.8,
                    supporting_relationships=[
                        rel.id for rel in self.relationships.values()
                        if rel.source_obs_id in high_activity_sources
                    ],
                    created_at=datetime.now(),
                    metadata={
                        'high_activity_sources': high_activity_sources,
                        'threshold': 5
                    }
                ))
            
            # Insight 2: Relationship type distribution
            type_counts = {}
            for rel in self.relationships.values():
                rel_type = rel.relationship_type.value
                type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
            
            if type_counts:
                dominant_type = max(type_counts.items(), key=lambda x: x[1])
                if dominant_type[1] > len(self.relationships) * 0.4:  # More than 40%
                    insight_id = f"insight_{uuid.uuid4().hex[:8]}"
                    insights.append(RelationshipInsight(
                        id=insight_id,
                        insight_type="pattern",
                        description=f"Dominant relationship type: {dominant_type[0]} ({dominant_type[1]}/{len(self.relationships)} relationships)",
                        confidence=0.7,
                        supporting_relationships=[
                            rel.id for rel in self.relationships.values()
                            if rel.relationship_type.value == dominant_type[0]
                        ],
                        created_at=datetime.now(),
                        metadata={
                            'relationship_type_distribution': type_counts,
                            'dominant_type': dominant_type[0]
                        }
                    ))
            
            # Insight 3: Low confidence relationships (potential issues)
            low_confidence_rels = [
                rel for rel in self.relationships.values()
                if rel.confidence < 0.4
            ]
            
            if len(low_confidence_rels) > len(self.relationships) * 0.2:  # More than 20%
                insight_id = f"insight_{uuid.uuid4().hex[:8]}"
                insights.append(RelationshipInsight(
                    id=insight_id,
                    insight_type="anomaly",
                    description=f"High number of low-confidence relationships: {len(low_confidence_rels)}/{len(self.relationships)}",
                    confidence=0.6,
                    supporting_relationships=[rel.id for rel in low_confidence_rels],
                    created_at=datetime.now(),
                    metadata={
                        'low_confidence_threshold': 0.4,
                        'percentage': len(low_confidence_rels) / len(self.relationships) * 100
                    }
                ))
            
            return insights
    
    def auto_detect_relationships(self, recent_hours: int = 24) -> List[str]:
        """Automatically detect relationships in recent observations.
        
        Args:
            recent_hours: Only analyze observations from last N hours
            
        Returns:
            List of newly created relationship IDs
        """
        if not self.dcp_manager:
            logger.warning("Cannot auto-detect relationships without DCP manager")
            return []
        
        with self._lock:
            try:
                # Get recent observations
                cutoff = datetime.now() - timedelta(hours=recent_hours)
                dcp_data = self.dcp_manager.read_dcp()
                observations = dcp_data.get('observations', [])
                
                recent_obs = [
                    obs for obs in observations
                    if datetime.fromtimestamp(obs.get('timestamp', 0)) > cutoff
                ]
                
                if len(recent_obs) < 2:
                    return []
                
                new_relationships = []
                
                # Sort by timestamp
                recent_obs.sort(key=lambda x: x.get('timestamp', 0))
                
                # Detect temporal relationships (followed_by)
                for i in range(len(recent_obs) - 1):
                    current_obs = recent_obs[i]
                    next_obs = recent_obs[i + 1]
                    
                    # Check if they're close in time (within 1 hour)
                    time_diff = next_obs.get('timestamp', 0) - current_obs.get('timestamp', 0)
                    if time_diff <= 3600:  # 1 hour
                        confidence = max(0.3, 1.0 - (time_diff / 3600))  # Higher confidence for closer times
                        
                        rel_id = self.add_relationship(
                            source_obs_id=current_obs.get('id'),
                            target_obs_id=next_obs.get('id'),
                            relationship_type=RelationshipType.FOLLOWED_BY,
                            confidence=confidence,
                            created_by='auto_detector',
                            evidence=[f"Temporal proximity: {time_diff:.0f}s apart"],
                            metadata={'detection_method': 'temporal', 'time_diff_seconds': time_diff}
                        )
                        new_relationships.append(rel_id)
                
                # Detect content-based relationships
                for i, obs1 in enumerate(recent_obs):
                    for j, obs2 in enumerate(recent_obs[i+1:], i+1):
                        similarity = self._calculate_content_similarity(obs1, obs2)
                        
                        if similarity > 0.7:  # High similarity threshold
                            rel_id = self.add_relationship(
                                source_obs_id=obs1.get('id'),
                                target_obs_id=obs2.get('id'),
                                relationship_type=RelationshipType.DUPLICATES,
                                confidence=similarity,
                                created_by='auto_detector',
                                evidence=[f"Content similarity: {similarity:.2f}"],
                                metadata={'detection_method': 'content_similarity', 'similarity_score': similarity}
                            )
                            new_relationships.append(rel_id)
                        elif similarity > 0.4:  # Medium similarity
                            rel_id = self.add_relationship(
                                source_obs_id=obs1.get('id'),
                                target_obs_id=obs2.get('id'),
                                relationship_type=RelationshipType.REFERENCES,
                                confidence=similarity,
                                created_by='auto_detector',
                                evidence=[f"Content similarity: {similarity:.2f}"],
                                metadata={'detection_method': 'content_similarity', 'similarity_score': similarity}
                            )
                            new_relationships.append(rel_id)
                
                logger.info(f"Auto-detected {len(new_relationships)} relationships")
                return new_relationships
                
            except Exception as e:
                logger.error(f"Failed to auto-detect relationships: {e}")
                return []
    
    def _calculate_content_similarity(self, obs1: Dict[str, Any], obs2: Dict[str, Any]) -> float:
        """Calculate content similarity between observations.
        
        Args:
            obs1: First observation
            obs2: Second observation
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Simple similarity based on shared keywords
        def extract_keywords(obs):
            keywords = set()
            
            # Extract from summary
            summary = obs.get('summary', '')
            if summary:
                words = summary.lower().split()
                keywords.update(word.strip('.,!?') for word in words if len(word) > 3)
            
            # Extract from type
            obs_type = obs.get('type', '')
            if obs_type:
                keywords.add(obs_type)
            
            # Extract from data
            data = obs.get('data', {})
            if isinstance(data, dict):
                for value in data.values():
                    if isinstance(value, str) and len(value) < 100:
                        words = value.lower().split()
                        keywords.update(word.strip('.,!?') for word in words if len(word) > 3)
            
            return keywords
        
        keywords1 = extract_keywords(obs1)
        keywords2 = extract_keywords(obs2)
        
        if not keywords1 or not keywords2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))
        
        return intersection / union if union > 0 else 0.0
    
    def start_analysis(self) -> None:
        """Start automatic relationship analysis."""
        if self._analysis_thread and self._analysis_thread.is_alive():
            logger.warning("Relationship analysis already running")
            return
        
        self._shutdown.clear()
        self._analysis_thread = threading.Thread(
            target=self._analysis_loop,
            daemon=True,
            name="RelationshipAnalysis"
        )
        self._analysis_thread.start()
        logger.info("Relationship analysis started")
    
    def stop_analysis(self) -> None:
        """Stop automatic relationship analysis."""
        self._shutdown.set()
        if self._analysis_thread:
            self._analysis_thread.join(timeout=10)
        logger.info("Relationship analysis stopped")
    
    def _analysis_loop(self) -> None:
        """Main analysis loop."""
        while not self._shutdown.is_set():
            try:
                # Auto-detect new relationships
                if self.auto_detect_enabled:
                    self.auto_detect_relationships(recent_hours=1)
                
                # Update chains
                new_chains = self.detect_chains()
                if new_chains:
                    for chain in new_chains:
                        self.chains[chain.id] = chain
                    self._save_chains()
                
                # Generate insights
                new_insights = self.generate_insights()
                if new_insights:
                    for insight in new_insights:
                        self.insights[insight.id] = insight
                    self._save_insights()
                
            except Exception as e:
                logger.error(f"Error in relationship analysis loop: {e}")
            
            # Wait for next analysis cycle (30 minutes)
            self._shutdown.wait(1800)
    
    def _update_indexes(self, relationship: ObservationRelationship) -> None:
        """Update lookup indexes."""
        rel_id = relationship.id
        
        # Source index
        if relationship.source_obs_id not in self._source_index:
            self._source_index[relationship.source_obs_id] = set()
        self._source_index[relationship.source_obs_id].add(rel_id)
        
        # Target index
        if relationship.target_obs_id not in self._target_index:
            self._target_index[relationship.target_obs_id] = set()
        self._target_index[relationship.target_obs_id].add(rel_id)
        
        # Type index
        if relationship.relationship_type not in self._type_index:
            self._type_index[relationship.relationship_type] = set()
        self._type_index[relationship.relationship_type].add(rel_id)
    
    def _save_relationships(self) -> None:
        """Save relationships to disk."""
        try:
            data = {
                'relationships': [rel.to_dict() for rel in self.relationships.values()],
                'last_updated': datetime.now().isoformat(),
                'total_count': len(self.relationships)
            }
            
            with open(self.relationships_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save relationships: {e}")
    
    def _save_chains(self) -> None:
        """Save chains to disk."""
        try:
            data = {
                'chains': [chain.to_dict() for chain in self.chains.values()],
                'last_updated': datetime.now().isoformat(),
                'total_count': len(self.chains)
            }
            
            with open(self.chains_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save chains: {e}")
    
    def _save_insights(self) -> None:
        """Save insights to disk."""
        try:
            data = {
                'insights': [insight.to_dict() for insight in self.insights.values()],
                'last_updated': datetime.now().isoformat(),
                'total_count': len(self.insights)
            }
            
            with open(self.insights_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save insights: {e}")
    
    def _load_data(self) -> None:
        """Load existing data from disk."""
        # Load relationships
        try:
            if self.relationships_file.exists():
                with open(self.relationships_file, 'r') as f:
                    data = json.load(f)
                
                for rel_data in data.get('relationships', []):
                    rel = ObservationRelationship.from_dict(rel_data)
                    self.relationships[rel.id] = rel
                    self._update_indexes(rel)
                
                logger.info(f"Loaded {len(self.relationships)} relationships")
        except Exception as e:
            logger.warning(f"Failed to load relationships: {e}")
        
        # Load chains
        try:
            if self.chains_file.exists():
                with open(self.chains_file, 'r') as f:
                    data = json.load(f)
                
                for chain_data in data.get('chains', []):
                    chain = ObservationChain(
                        id=chain_data['id'],
                        observations=chain_data['observations'],
                        chain_type=chain_data['chain_type'],
                        strength=chain_data['strength'],
                        created_at=datetime.fromisoformat(chain_data['created_at']),
                        metadata=chain_data.get('metadata', {})
                    )
                    self.chains[chain.id] = chain
                
                logger.info(f"Loaded {len(self.chains)} chains")
        except Exception as e:
            logger.warning(f"Failed to load chains: {e}")
        
        # Load insights
        try:
            if self.insights_file.exists():
                with open(self.insights_file, 'r') as f:
                    data = json.load(f)
                
                for insight_data in data.get('insights', []):
                    insight = RelationshipInsight(
                        id=insight_data['id'],
                        insight_type=insight_data['insight_type'],
                        description=insight_data['description'],
                        confidence=insight_data['confidence'],
                        supporting_relationships=insight_data['supporting_relationships'],
                        created_at=datetime.fromisoformat(insight_data['created_at']),
                        metadata=insight_data.get('metadata', {})
                    )
                    self.insights[insight.id] = insight
                
                logger.info(f"Loaded {len(self.insights)} insights")
        except Exception as e:
            logger.warning(f"Failed to load insights: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get relationship tracking statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            type_counts = {}
            confidence_distribution = {'high': 0, 'medium': 0, 'low': 0}
            
            for rel in self.relationships.values():
                # Count by type
                rel_type = rel.relationship_type.value
                type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
                
                # Count by confidence
                if rel.confidence >= 0.7:
                    confidence_distribution['high'] += 1
                elif rel.confidence >= 0.4:
                    confidence_distribution['medium'] += 1
                else:
                    confidence_distribution['low'] += 1
            
            return {
                'total_relationships': len(self.relationships),
                'total_chains': len(self.chains),
                'total_insights': len(self.insights),
                'relationship_types': type_counts,
                'confidence_distribution': confidence_distribution,
                'auto_detect_enabled': self.auto_detect_enabled,
                'analysis_running': self._analysis_thread and self._analysis_thread.is_alive()
            }


# Convenience functions
def create_relationship_tracker(project_path: str, dcp_manager=None) -> ObservationRelationshipTracker:
    """Create and start a relationship tracker.
    
    Args:
        project_path: Project root path
        dcp_manager: Optional DCP manager
        
    Returns:
        Configured ObservationRelationshipTracker instance
    """
    return ObservationRelationshipTracker(project_path, dcp_manager)


def find_observation_chains(tracker: ObservationRelationshipTracker, obs_id: str) -> List[ObservationChain]:
    """Find chains that include a specific observation.
    
    Args:
        tracker: RelationshipTracker instance
        obs_id: Observation ID to search for
        
    Returns:
        List of chains containing the observation
    """
    return [
        chain for chain in tracker.chains.values()
        if obs_id in chain.observations
    ]