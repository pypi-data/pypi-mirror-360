"""
Project-specific learning component that trains on user's actual codebase.
"""
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from coppersun_brass.core.context.dcp_manager import DCPManager

logger = logging.getLogger(__name__)


class ProjectLearner:
    """
    Learns from the user's actual codebase to provide immediate personalization.
    """
    
    def __init__(self, dcp_path: Optional[str] = None):
        """
        Initialize project learner.
        
        General Staff Role: This component provides project-specific intelligence
        by learning from the actual codebase rather than generic patterns.
        """
        self.dcp = DCPManager(dcp_path)
        self._learning_status = self._load_learning_status()
        # Lazy load these to avoid circular imports
        self.pattern_extractor = None
        self.training_coordinator = None
    
    def _load_learning_status(self) -> Dict[str, Any]:
        """Load or initialize learning status."""
        status_file = Path.home() / '.brass' / 'project_learning_status.json'
        if status_file.exists():
            with open(status_file) as f:
                return json.load(f)
        return {
            'first_run_completed': False,
            'last_training': None,
            'observations_processed': 0,
            'model_version': 0
        }
    
    def _save_learning_status(self):
        """Save learning status."""
        status_file = Path.home() / '.brass' / 'project_learning_status.json'
        status_file.parent.mkdir(parents=True, exist_ok=True)
        with open(status_file, 'w') as f:
            json.dump(self._learning_status, f, indent=2)
    
    async def learn_from_initial_analysis(self, observations: List[Dict[str, Any]]):
        """
        Learn from Scout's initial analysis of the codebase.
        
        Args:
            observations: List of observations from Scout's analysis
        """
        logger.info(f"Starting project-specific learning from {len(observations)} observations")
        
        # Extract immediate patterns for instant application
        immediate_patterns = await self._extract_immediate_patterns(observations)
        
        # Store patterns in DCP for immediate use
        await self._store_immediate_patterns(immediate_patterns)
        
        # Schedule background training if sufficient data
        if len(observations) >= 10:  # Minimum threshold
            asyncio.create_task(self._background_training(observations))
        
        # Update status
        self._learning_status['first_run_completed'] = True
        self._learning_status['observations_processed'] = len(observations)
        self._save_learning_status()
        
        logger.info("Initial learning completed, background training scheduled")
    
    async def _extract_immediate_patterns(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract patterns that can be applied immediately."""
        patterns = {
            'naming_conventions': {},
            'code_style': {},
            'common_patterns': {},
            'project_structure': {}
        }
        
        # Analyze naming conventions
        function_names = []
        variable_names = []
        class_names = []
        
        for obs in observations:
            if obs.get('type') == 'file_analysis':
                data = obs.get('data', {})
                
                # Extract names from AST data if available
                if 'ast_analysis' in data:
                    ast_data = data['ast_analysis']
                    function_names.extend(ast_data.get('function_names', []))
                    variable_names.extend(ast_data.get('variable_names', []))
                    class_names.extend(ast_data.get('class_names', []))
        
        # Detect naming patterns
        patterns['naming_conventions'] = {
            'functions': self._detect_naming_pattern(function_names),
            'variables': self._detect_naming_pattern(variable_names),
            'classes': self._detect_naming_pattern(class_names)
        }
        
        # Detect code style preferences
        patterns['code_style'] = self._detect_code_style(observations)
        
        # Extract common code patterns
        patterns['common_patterns'] = self._extract_common_patterns(observations)
        
        return patterns
    
    def _detect_naming_pattern(self, names: List[str]) -> str:
        """Detect predominant naming convention."""
        if not names:
            return 'unknown'
        
        patterns = {
            'snake_case': 0,
            'camelCase': 0,
            'PascalCase': 0,
            'kebab-case': 0
        }
        
        for name in names:
            if '_' in name and name.islower():
                patterns['snake_case'] += 1
            elif name[0].islower() and any(c.isupper() for c in name[1:]):
                patterns['camelCase'] += 1
            elif name[0].isupper() and any(c.isupper() for c in name[1:]):
                patterns['PascalCase'] += 1
            elif '-' in name:
                patterns['kebab-case'] += 1
        
        return max(patterns, key=patterns.get)
    
    def _detect_code_style(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect code style preferences from observations."""
        style = {
            'indentation': 'spaces',  # or 'tabs'
            'indent_size': 4,
            'quote_style': 'single',  # or 'double'
            'semicolons': False,  # for JS/TS
            'trailing_comma': False
        }
        
        # Analyze actual code content to detect style
        # This is simplified - real implementation would parse code
        for obs in observations:
            if obs.get('type') == 'file_analysis':
                content = obs.get('data', {}).get('content', '')
                if content:
                    # Detect indentation
                    if '\t' in content:
                        style['indentation'] = 'tabs'
                    
                    # Detect quote style (simplified)
                    single_quotes = content.count("'")
                    double_quotes = content.count('"')
                    if double_quotes > single_quotes * 1.5:
                        style['quote_style'] = 'double'
        
        return style
    
    def _extract_common_patterns(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract common code patterns from the project."""
        patterns = []
        
        # Look for repeated structures, common imports, etc.
        imports_count = {}
        function_patterns = {}
        
        for obs in observations:
            if obs.get('type') == 'file_analysis':
                data = obs.get('data', {})
                
                # Count imports
                for imp in data.get('imports', []):
                    imports_count[imp] = imports_count.get(imp, 0) + 1
                
                # Track function patterns
                for func in data.get('functions', []):
                    pattern = f"{func.get('params_count', 0)}_params"
                    function_patterns[pattern] = function_patterns.get(pattern, 0) + 1
        
        # Convert to patterns
        common_imports = [imp for imp, count in imports_count.items() if count >= 3]
        patterns.append({
            'type': 'common_imports',
            'values': common_imports,
            'confidence': 0.8
        })
        
        return patterns
    
    async def _store_immediate_patterns(self, patterns: Dict[str, Any]):
        """Store patterns in DCP for immediate use."""
        observation = {
            'id': f'project_patterns_{datetime.now().isoformat()}',
            'type': 'file_analysis',
            'timestamp': datetime.now().isoformat(),
            'summary': f"Learned {len(patterns)} immediate patterns from initial project analysis",
            'data': {
                'patterns': patterns,
                'learning_phase': 'immediate',
                'applied': True,
                'source': 'project_learner'
            }
        }
        
        await self.dcp.add_observation(observation)
        logger.info("Stored immediate patterns for project-specific analysis")
    
    async def _background_training(self, observations: List[Dict[str, Any]]):
        """Run background training on project code."""
        logger.info("Starting background training on project code")
        
        try:
            # Lazy load training coordinator
            if self.training_coordinator is None:
                try:
                    from coppersun_brass.core.learning.training_coordinator import TrainingCoordinator
                    self.training_coordinator = TrainingCoordinator(str(Path(self.dcp.config.project_root) / '.brass'))
                except ImportError:
                    logger.warning("Training coordinator not available")
                    return
            
            # Prepare training data from observations
            training_data = self._prepare_training_data(observations)
            
            # Use existing training coordinator
            success = await self.training_coordinator.train_models(
                force=True,  # Force training even with limited data
                training_data=training_data
            )
            
            if success:
                self._learning_status['last_training'] = datetime.now().isoformat()
                self._learning_status['model_version'] += 1
                self._save_learning_status()
                logger.info("Background training completed successfully")
            else:
                logger.warning("Background training failed")
                
        except Exception as e:
            logger.error(f"Error in background training: {e}")
    
    def _prepare_training_data(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare training data from observations."""
        training_examples = []
        
        for obs in observations:
            if obs.get('type') == 'file_analysis':
                data = obs.get('data', {})
                
                # Create training example
                example = {
                    'content': data.get('content', ''),
                    'language': data.get('language', 'unknown'),
                    'complexity': data.get('complexity_score', 0),
                    'issues_found': len(data.get('patterns_found', [])),
                    'file_type': Path(data.get('file_path', '')).suffix,
                    'quality_score': self._calculate_quality_score(data)
                }
                
                training_examples.append(example)
        
        return {
            'examples': training_examples,
            'project_patterns': self._learning_status.get('patterns', {}),
            'training_type': 'project_specific'
        }
    
    def _calculate_quality_score(self, file_data: Dict[str, Any]) -> float:
        """Calculate a quality score for training."""
        # Simple heuristic - real implementation would be more sophisticated
        score = 1.0
        
        # Penalize for issues found
        issues = len(file_data.get('patterns_found', []))
        score -= (issues * 0.1)
        
        # Penalize for high complexity
        complexity = file_data.get('complexity_score', 0)
        if complexity > 10:
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def get_project_patterns(self) -> Optional[Dict[str, Any]]:
        """Get learned project patterns for use in analysis."""
        # Load from DCP
        observations = self.dcp.get_observations_by_type('project_learning')
        if observations:
            latest = max(observations, key=lambda x: x.get('timestamp', ''))
            return latest.get('data', {}).get('patterns')
        return None
    
    def should_retrain(self) -> bool:
        """Check if retraining is needed based on new observations."""
        # Retrain if significant new code added or time elapsed
        last_training = self._learning_status.get('last_training')
        if not last_training:
            return True
        
        # Check time elapsed (retrain weekly)
        from datetime import datetime, timedelta
        last_time = datetime.fromisoformat(last_training)
        if datetime.now() - last_time > timedelta(days=7):
            return True
        
        # Check observation count (retrain every 100 new observations)
        current_obs = len(self.dcp.get_all_observations())
        last_obs = self._learning_status.get('observations_processed', 0)
        if current_obs - last_obs > 100:
            return True
        
        return False