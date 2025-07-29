"""
Codebase Learning Engine - Pure Python Built-ins Only
=====================================================

🩸 BLOOD OATH COMPLIANT: Uses ONLY Python standard library
✅ Learns from existing code patterns, comments, and project structure
✅ Enhances pure Python ML analysis with project-specific intelligence
✅ Zero user effort - automatic learning from codebase

Restores adaptive intelligence functionality without heavy ML dependencies.
"""

import re
import json
import sqlite3
import statistics
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

@dataclass
class CodebasePattern:
    """A pattern learned from codebase analysis."""
    pattern_type: str           # e.g., "todo_security", "fixme_performance"
    pattern_subtype: str        # e.g., "sql_injection", "nested_loops"
    frequency: int              # How often this pattern appears
    context_weight: float       # Importance in this project (0.0 - 2.0)
    priority_keywords: List[str] # Associated priority words
    resolution_rate: float      # Percentage that get resolved (0.0 - 1.0)
    project_context: str        # Project type context
    confidence_multiplier: float # Adjustment factor for ML confidence
    last_updated: str          # ISO timestamp
    sample_comments: List[str] # Example comments for this pattern

@dataclass  
class ProjectContext:
    """Project-wide context learned from codebase."""
    project_type: str           # web, data, library, cli, etc.
    primary_language: str       # python, javascript, rust, etc.
    tech_stack: List[str]       # frameworks, libraries detected
    complexity_level: str       # simple, moderate, complex
    maintenance_activity: str   # active, moderate, low
    domain_vocabulary: Dict[str, float] # domain terms and weights
    file_type_distribution: Dict[str, int] # file extensions and counts
    total_files: int
    total_todos: int
    avg_file_size: float

class CodebaseLearningEngine:
    """
    Learn from codebase patterns to enhance ML analysis.
    
    🩸 BLOOD OATH: Zero external dependencies beyond Python standard library
    ✅ Uses: re, json, sqlite3, statistics, pathlib, collections
    ❌ Never uses: numpy, sklearn, torch, pandas, etc.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize codebase learning engine."""
        self.storage_path = storage_path or Path(".brass") / "learning_data.db"
        self.patterns = {}          # Learned patterns cache
        self.project_context = None # Project context cache
        self.vocabulary_weights = {} # Term importance weights
        
        # Create storage directory if needed
        self.storage_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Initialize SQLite database
        self._init_database()
        
        # Load existing patterns
        self._load_patterns()
        
        logger.info("✅ Codebase Learning Engine initialized")
    
    def _init_database(self):
        """Initialize SQLite database for pattern storage."""
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS codebase_patterns (
                    id INTEGER PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    pattern_subtype TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    project_path TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS project_context (
                    project_path TEXT PRIMARY KEY,
                    context_data TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    scan_version TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    def analyze_codebase(self, project_path: Path) -> ProjectContext:
        """
        Analyze entire codebase to learn patterns and context.
        
        Args:
            project_path: Root path of project to analyze
            
        Returns:
            ProjectContext with learned information
        """
        logger.info(f"🔍 Analyzing codebase: {project_path}")
        
        # Collect all relevant files
        code_files = self._collect_code_files(project_path)
        logger.info(f"📁 Found {len(code_files)} code files")
        
        # Extract comment patterns
        comment_patterns = self._extract_comment_patterns(code_files)
        logger.info(f"💬 Extracted {len(comment_patterns)} comment patterns")
        
        # Analyze project structure
        project_context = self._analyze_project_structure(project_path, code_files)
        logger.info(f"🏗️  Detected project type: {project_context.project_type}")
        
        # Build vocabulary weights
        vocabulary_weights = self._build_vocabulary_weights(comment_patterns, project_context)
        logger.info(f"📝 Built vocabulary: {len(vocabulary_weights)} terms")
        
        # Calculate pattern importance and confidence multipliers
        enhanced_patterns = self._calculate_pattern_weights(
            comment_patterns, project_context, vocabulary_weights
        )
        logger.info(f"⚖️  Calculated weights for {len(enhanced_patterns)} patterns")
        
        # Store learned patterns
        self._store_patterns(enhanced_patterns, str(project_path))
        self._store_project_context(project_context, str(project_path))
        
        # Cache for immediate use
        self.patterns = {p.pattern_type + "_" + p.pattern_subtype: p for p in enhanced_patterns}
        self.project_context = project_context
        self.vocabulary_weights = vocabulary_weights
        
        logger.info("✅ Codebase analysis complete")
        return project_context
    
    def _collect_code_files(self, project_path: Path) -> List[Path]:
        """Collect all relevant code files for analysis."""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.rs', '.go', '.java', 
            '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.swift',
            '.kt', '.scala', '.clj', '.hs', '.elm', '.vue', '.svelte'
        }
        
        code_files = []
        ignore_dirs = {
            'node_modules', '.git', '__pycache__', '.venv', 'venv',
            'target', 'build', 'dist', '.next', '.nuxt', 'vendor'
        }
        
        for file_path in project_path.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix.lower() in code_extensions and
                not any(ignore_dir in file_path.parts for ignore_dir in ignore_dirs)):
                code_files.append(file_path)
        
        return code_files
    
    def _extract_comment_patterns(self, code_files: List[Path]) -> List[Dict[str, Any]]:
        """Extract TODO/FIXME/HACK patterns from comments."""
        patterns = []
        
        # Enhanced regex for comment patterns
        comment_regex = re.compile(
            r'(?:#|//|/\*|\*|<!--)\s*'  # Comment start
            r'(TODO|FIXME|HACK|XXX|NOTE|BUG|OPTIMIZE|REFACTOR|DEPRECATE|REMOVE)'  # Marker
            r'[:\s]*'  # Optional colon/space
            r'(.+?)(?:\*/|-->|$)',  # Content until end or close
            re.IGNORECASE | re.MULTILINE
        )
        
        priority_regex = re.compile(
            r'\b(CRITICAL|URGENT|HIGH|MEDIUM|LOW|MINOR|TRIVIAL|IMPORTANT|ASAP|SOON|LATER|SOMEDAY)\b',
            re.IGNORECASE
        )
        
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for match in comment_regex.finditer(content):
                    marker = match.group(1).upper()
                    comment_text = match.group(2).strip()
                    
                    # Find line number
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # Extract priority keywords
                    priority_matches = priority_regex.findall(comment_text)
                    
                    # Classify comment content
                    subtype = self._classify_comment_content(comment_text)
                    
                    pattern = {
                        'file_path': str(file_path),
                        'line_number': line_number,
                        'marker': marker,
                        'content': comment_text,
                        'subtype': subtype,
                        'priority_keywords': [p.upper() for p in priority_matches],
                        'file_extension': file_path.suffix,
                        'relative_path': str(file_path.relative_to(file_path.parents[-2]))
                    }
                    
                    patterns.append(pattern)
                    
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")
        
        return patterns
    
    def _classify_comment_content(self, comment_text: str) -> str:
        """Classify comment content into categories."""
        text_lower = comment_text.lower()
        
        # Security patterns
        security_keywords = [
            'security', 'vulnerability', 'injection', 'xss', 'csrf', 'auth',
            'password', 'token', 'encrypt', 'decrypt', 'secure', 'attack',
            'malicious', 'sanitize', 'validate', 'escape'
        ]
        
        # Performance patterns  
        performance_keywords = [
            'performance', 'slow', 'optimize', 'speed', 'memory', 'cpu',
            'bottleneck', 'cache', 'database', 'query', 'index', 'algorithm',
            'complexity', 'efficient', 'parallel', 'async'
        ]
        
        # Architecture patterns
        architecture_keywords = [
            'architecture', 'design', 'pattern', 'structure', 'organize',
            'refactor', 'modular', 'coupling', 'cohesion', 'interface',
            'api', 'dependency', 'separation', 'abstraction'
        ]
        
        # Bug/Error patterns
        bug_keywords = [
            'bug', 'error', 'exception', 'crash', 'fail', 'broken',
            'incorrect', 'wrong', 'issue', 'problem', 'fix'
        ]
        
        # Feature patterns
        feature_keywords = [
            'feature', 'implement', 'add', 'create', 'build', 'develop',
            'enhancement', 'improvement', 'functionality', 'capability'
        ]
        
        # Count keyword matches
        security_score = sum(1 for kw in security_keywords if kw in text_lower)
        performance_score = sum(1 for kw in performance_keywords if kw in text_lower)
        architecture_score = sum(1 for kw in architecture_keywords if kw in text_lower)
        bug_score = sum(1 for kw in bug_keywords if kw in text_lower)
        feature_score = sum(1 for kw in feature_keywords if kw in text_lower)
        
        # Determine primary category
        scores = {
            'security': security_score,
            'performance': performance_score,
            'architecture': architecture_score,
            'bug': bug_score,
            'feature': feature_score
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return 'general'
        
        # Return category with highest score
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _analyze_project_structure(self, project_path: Path, code_files: List[Path]) -> ProjectContext:
        """Analyze project structure to understand context."""
        
        # Detect project type from files and structure
        project_type = self._detect_project_type(project_path, code_files)
        
        # Detect primary language
        primary_language = self._detect_primary_language(code_files)
        
        # Detect tech stack
        tech_stack = self._detect_tech_stack(project_path)
        
        # Calculate complexity metrics
        complexity_level = self._calculate_complexity_level(code_files)
        
        # Assess maintenance activity
        maintenance_activity = self._assess_maintenance_activity(project_path)
        
        # Build file type distribution
        file_type_dist = Counter(f.suffix.lower() for f in code_files)
        
        # Calculate basic metrics
        total_files = len(code_files)
        total_size = sum(f.stat().st_size for f in code_files if f.exists())
        avg_file_size = total_size / total_files if total_files > 0 else 0
        
        return ProjectContext(
            project_type=project_type,
            primary_language=primary_language,
            tech_stack=tech_stack,
            complexity_level=complexity_level,
            maintenance_activity=maintenance_activity,
            domain_vocabulary={},  # Will be populated later
            file_type_distribution=dict(file_type_dist),
            total_files=total_files,
            total_todos=0,  # Will be updated
            avg_file_size=avg_file_size
        )
    
    def _detect_project_type(self, project_path: Path, code_files: List[Path]) -> str:
        """Detect project type from structure and files."""
        
        # Check for specific framework files
        framework_indicators = {
            'web': ['package.json', 'yarn.lock', 'webpack.config.js', 'next.config.js', 'nuxt.config.js'],
            'data': ['requirements.txt', 'environment.yml', 'Pipfile', 'jupyter', 'notebook'],
            'mobile': ['android', 'ios', 'flutter', 'react-native'],
            'library': ['setup.py', 'pyproject.toml', 'Cargo.toml', 'go.mod', 'pom.xml'],
            'cli': ['bin/', 'cmd/', 'cli.py', 'main.py', '__main__.py'],
            'api': ['api/', 'routes/', 'endpoints/', 'controllers/']
        }
        
        # Count indicators for each type
        type_scores = defaultdict(int)
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                file_name = file_path.name.lower()
                rel_path = str(file_path.relative_to(project_path)).lower()
                
                for proj_type, indicators in framework_indicators.items():
                    for indicator in indicators:
                        if indicator in file_name or indicator in rel_path:
                            type_scores[proj_type] += 1
        
        # Additional heuristics based on file content
        if any('.py' in f.suffix for f in code_files):
            # Python-specific detection
            if any('django' in str(f) or 'flask' in str(f) for f in project_path.rglob('*')):
                type_scores['web'] += 3
            if any('pytest' in str(f) or 'test_' in f.name for f in code_files):
                type_scores['library'] += 2
        
        # Return type with highest score
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        
        return 'general'
    
    def _detect_primary_language(self, code_files: List[Path]) -> str:
        """Detect primary programming language."""
        language_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.rs': 'rust',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift'
        }
        
        language_counts = Counter()
        total_size_by_lang = defaultdict(int)
        
        for file_path in code_files:
            ext = file_path.suffix.lower()
            if ext in language_extensions:
                language = language_extensions[ext]
                language_counts[language] += 1
                try:
                    total_size_by_lang[language] += file_path.stat().st_size
                except:
                    pass
        
        # Weight by both file count and total code size
        if language_counts:
            # Combine file count and size metrics
            weighted_scores = {}
            total_files = sum(language_counts.values())
            total_size = sum(total_size_by_lang.values())
            
            for lang in language_counts:
                file_ratio = language_counts[lang] / total_files
                size_ratio = total_size_by_lang[lang] / total_size if total_size > 0 else 0
                weighted_scores[lang] = (file_ratio + size_ratio) / 2
            
            return max(weighted_scores.items(), key=lambda x: x[1])[0]
        
        return 'unknown'
    
    def _detect_tech_stack(self, project_path: Path) -> List[str]:
        """Detect technology stack from project files."""
        tech_indicators = {
            # Python frameworks
            'django': ['django', 'manage.py', 'settings.py'],
            'flask': ['flask', 'app.py', 'wsgi.py'],
            'fastapi': ['fastapi', 'uvicorn', 'starlette'],
            'pytest': ['pytest', 'test_', 'conftest.py'],
            
            # JavaScript frameworks
            'react': ['react', 'jsx', 'tsx', 'package.json'],
            'vue': ['vue', '.vue', 'nuxt'],
            'angular': ['angular', '@angular', 'ng '],
            'express': ['express', 'app.js', 'server.js'],
            'nextjs': ['next.js', 'next.config.js'],
            
            # Databases
            'postgresql': ['postgres', 'psycopg', 'pg_'],
            'mysql': ['mysql', 'pymysql', 'mysql2'],
            'mongodb': ['mongo', 'pymongo', 'mongoose'],
            'redis': ['redis', 'redis-py'],
            'sqlite': ['sqlite', 'sqlite3'],
            
            # Other tools
            'docker': ['dockerfile', 'docker-compose', '.dockerignore'],
            'kubernetes': ['k8s', 'kubectl', 'deployment.yaml'],
            'aws': ['boto3', 'aws-', 'lambda'],
            'tensorflow': ['tensorflow', 'tf.', 'keras'],
            'pytorch': ['torch', 'pytorch', 'nn.']
        }
        
        detected_tech = []
        
        # Check files and content
        for tech, indicators in tech_indicators.items():
            score = 0
            
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    file_content = str(file_path).lower()
                    
                    # Check filename and path
                    for indicator in indicators:
                        if indicator in file_content:
                            score += 1
                    
                    # Check file content for imports/dependencies
                    if file_path.suffix in ['.py', '.js', '.ts', '.json', '.yml', '.yaml']:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                                for indicator in indicators:
                                    if indicator in content:
                                        score += 2  # Higher weight for content matches
                        except:
                            pass
            
            if score >= 2:  # Threshold for detection
                detected_tech.append(tech)
        
        return detected_tech
    
    def _calculate_complexity_level(self, code_files: List[Path]) -> str:
        """Calculate project complexity level."""
        total_files = len(code_files)
        
        if total_files < 20:
            return 'simple'
        elif total_files < 100:
            return 'moderate'
        else:
            return 'complex'
    
    def _assess_maintenance_activity(self, project_path: Path) -> str:
        """Assess project maintenance activity level."""
        # Check git activity if available
        git_dir = project_path / '.git'
        if git_dir.exists():
            try:
                # Look for recent commits (simplified heuristic)
                recent_files = []
                for file_path in project_path.rglob('*'):
                    if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts']:
                        try:
                            mtime = file_path.stat().st_mtime
                            recent_files.append(mtime)
                        except:
                            pass
                
                if recent_files:
                    recent_files.sort(reverse=True)
                    # Check if files were modified in last 30 days
                    thirty_days_ago = datetime.now().timestamp() - (30 * 24 * 60 * 60)
                    recent_count = sum(1 for mtime in recent_files if mtime > thirty_days_ago)
                    
                    if recent_count > len(recent_files) * 0.1:  # 10% of files modified recently
                        return 'active'
                    elif recent_count > 0:
                        return 'moderate'
                    else:
                        return 'low'
            except:
                pass
        
        return 'unknown'
    
    def _build_vocabulary_weights(self, comment_patterns: List[Dict], project_context: ProjectContext) -> Dict[str, float]:
        """Build vocabulary weights based on comment analysis."""
        
        # Extract all words from comments
        all_words = []
        for pattern in comment_patterns:
            # Tokenize comment content
            words = re.findall(r'\b\w+\b', pattern['content'].lower())
            all_words.extend(words)
        
        # Calculate term frequency
        word_counts = Counter(all_words)
        total_words = len(all_words)
        
        # Calculate weights based on frequency and context
        vocabulary_weights = {}
        
        for word, count in word_counts.items():
            if len(word) < 3:  # Skip very short words
                continue
                
            # Base weight from frequency
            frequency_weight = count / total_words
            
            # Boost important technical terms
            technical_boost = 1.0
            if word in ['security', 'performance', 'bug', 'error', 'optimize', 'refactor']:
                technical_boost = 2.0
            elif word in ['critical', 'urgent', 'important', 'asap']:
                technical_boost = 1.5
            
            # Context-specific boosts
            context_boost = 1.0
            if project_context.project_type == 'web' and word in ['api', 'endpoint', 'route', 'auth']:
                context_boost = 1.3
            elif project_context.project_type == 'data' and word in ['model', 'dataset', 'analysis']:
                context_boost = 1.3
            
            final_weight = frequency_weight * technical_boost * context_boost
            vocabulary_weights[word] = min(2.0, final_weight)  # Cap at 2.0
        
        return vocabulary_weights
    
    def _calculate_pattern_weights(
        self, 
        comment_patterns: List[Dict], 
        project_context: ProjectContext,
        vocabulary_weights: Dict[str, float]
    ) -> List[CodebasePattern]:
        """Calculate pattern weights and confidence multipliers."""
        
        # Group patterns by type and subtype
        pattern_groups = defaultdict(list)
        for pattern in comment_patterns:
            key = f"{pattern['marker']}_{pattern['subtype']}"
            pattern_groups[key].append(pattern)
        
        learned_patterns = []
        
        for pattern_key, patterns in pattern_groups.items():
            marker, subtype = pattern_key.split('_', 1)
            
            # Calculate base metrics
            frequency = len(patterns)
            
            # Collect priority keywords
            all_priority_keywords = []
            sample_comments = []
            
            for pattern in patterns[:5]:  # Sample first 5
                all_priority_keywords.extend(pattern['priority_keywords'])
                sample_comments.append(pattern['content'][:100])  # Truncate for storage
            
            priority_keywords = list(set(all_priority_keywords))
            
            # Calculate context weight based on frequency and project type
            project_total_patterns = len(comment_patterns)
            frequency_ratio = frequency / project_total_patterns if project_total_patterns > 0 else 0
            
            # Base context weight
            context_weight = min(2.0, frequency_ratio * 10)  # Scale and cap
            
            # Apply vocabulary weights
            vocab_boost = 1.0
            for pattern in patterns:
                words = re.findall(r'\\b\\w+\\b', pattern['content'].lower())
                pattern_vocab_score = sum(vocabulary_weights.get(word, 0) for word in words)
                vocab_boost = max(vocab_boost, pattern_vocab_score)
            
            context_weight *= min(1.5, vocab_boost)
            
            # Calculate confidence multiplier
            confidence_multiplier = self._calculate_confidence_multiplier(
                marker, subtype, frequency, priority_keywords, project_context
            )
            
            # Estimate resolution rate (heuristic based on marker type)
            resolution_rate = {
                'TODO': 0.6,      # 60% of TODOs get resolved
                'FIXME': 0.8,     # 80% of FIXMEs get resolved
                'HACK': 0.3,      # 30% of HACKs get resolved
                'XXX': 0.4,       # 40% of XXXs get resolved
                'NOTE': 0.2,      # 20% of NOTEs get resolved
                'BUG': 0.9,       # 90% of BUGs get resolved
                'OPTIMIZE': 0.5,  # 50% of optimizations get done
            }.get(marker, 0.5)
            
            # Adjust based on priority keywords
            if any(kw in ['CRITICAL', 'URGENT', 'IMPORTANT'] for kw in priority_keywords):
                resolution_rate = min(1.0, resolution_rate * 1.3)
            elif any(kw in ['MINOR', 'TRIVIAL', 'SOMEDAY'] for kw in priority_keywords):
                resolution_rate = max(0.1, resolution_rate * 0.7)
            
            learned_pattern = CodebasePattern(
                pattern_type=marker.lower(),
                pattern_subtype=subtype,
                frequency=frequency,
                context_weight=context_weight,
                priority_keywords=priority_keywords,
                resolution_rate=resolution_rate,
                project_context=project_context.project_type,
                confidence_multiplier=confidence_multiplier,
                last_updated=datetime.now().isoformat(),
                sample_comments=sample_comments
            )
            
            learned_patterns.append(learned_pattern)
        
        return learned_patterns
    
    def _calculate_confidence_multiplier(
        self, 
        marker: str, 
        subtype: str, 
        frequency: int,
        priority_keywords: List[str],
        project_context: ProjectContext
    ) -> float:
        """Calculate confidence multiplier for this pattern type."""
        
        # Base multiplier by marker type
        base_multipliers = {
            'TODO': 1.0,
            'FIXME': 1.2,     # FIXMEs are more urgent
            'HACK': 0.8,      # HACKs are often low priority
            'XXX': 0.9,       # XXX are medium priority
            'NOTE': 0.7,      # NOTEs are informational
            'BUG': 1.5,       # BUGs are high priority
            'OPTIMIZE': 1.1,  # Optimizations are moderately important
        }
        
        base_multiplier = base_multipliers.get(marker, 1.0)
        
        # Subtype adjustments
        subtype_adjustments = {
            'security': 1.4,      # Security issues are high priority
            'performance': 1.2,   # Performance issues are important
            'bug': 1.3,          # Bugs are high priority
            'architecture': 1.1,  # Architecture improvements are moderate
            'feature': 1.0,      # Features are baseline
            'general': 0.9       # General items are lower priority
        }
        
        subtype_adjustment = subtype_adjustments.get(subtype, 1.0)
        
        # Frequency adjustment (more common patterns in this project get slight boost)
        frequency_adjustment = min(1.2, 1.0 + (frequency / 100))
        
        # Priority keyword adjustments
        priority_adjustment = 1.0
        if any(kw in ['CRITICAL', 'URGENT'] for kw in priority_keywords):
            priority_adjustment = 1.5
        elif any(kw in ['IMPORTANT', 'HIGH'] for kw in priority_keywords):
            priority_adjustment = 1.2
        elif any(kw in ['MINOR', 'TRIVIAL', 'SOMEDAY'] for kw in priority_keywords):
            priority_adjustment = 0.6
        
        # Project context adjustments
        context_adjustment = 1.0
        if project_context.project_type == 'web' and subtype == 'security':
            context_adjustment = 1.3  # Security is critical for web projects
        elif project_context.project_type == 'data' and subtype == 'performance':
            context_adjustment = 1.2  # Performance matters for data projects
        
        # Combine all adjustments
        final_multiplier = (
            base_multiplier * 
            subtype_adjustment * 
            frequency_adjustment * 
            priority_adjustment * 
            context_adjustment
        )
        
        # Clamp to reasonable bounds
        return max(0.3, min(2.0, final_multiplier))
    
    def _store_patterns(self, patterns: List[CodebasePattern], project_path: str):
        """Store learned patterns in SQLite database."""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                # Clear existing patterns for this project
                conn.execute(
                    "DELETE FROM codebase_patterns WHERE project_path = ?", 
                    (project_path,)
                )
                
                # Insert new patterns
                for pattern in patterns:
                    pattern_data = json.dumps(asdict(pattern))
                    conn.execute("""
                        INSERT INTO codebase_patterns 
                        (pattern_type, pattern_subtype, pattern_data, last_updated, project_path)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        pattern.pattern_type,
                        pattern.pattern_subtype, 
                        pattern_data,
                        pattern.last_updated,
                        project_path
                    ))
                
                conn.commit()
                logger.info(f"✅ Stored {len(patterns)} patterns for {project_path}")
                
        except Exception as e:
            logger.error(f"Failed to store patterns: {e}")
    
    def _store_project_context(self, context: ProjectContext, project_path: str):
        """Store project context in database."""
        try:
            context_data = json.dumps(asdict(context))
            
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO project_context 
                    (project_path, context_data, last_updated, scan_version)
                    VALUES (?, ?, ?, ?)
                """, (project_path, context_data, datetime.now().isoformat(), "1.0"))
                
                conn.commit()
                logger.info(f"✅ Stored project context for {project_path}")
                
        except Exception as e:
            logger.error(f"Failed to store project context: {e}")
    
    def _load_patterns(self, project_path: Optional[str] = None):
        """Load learned patterns from database."""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                if project_path:
                    cursor = conn.execute("""
                        SELECT pattern_data FROM codebase_patterns 
                        WHERE project_path = ?
                    """, (project_path,))
                else:
                    cursor = conn.execute("SELECT pattern_data FROM codebase_patterns")
                
                for row in cursor.fetchall():
                    pattern_data = json.loads(row[0])
                    pattern = CodebasePattern(**pattern_data)
                    key = f"{pattern.pattern_type}_{pattern.pattern_subtype}"
                    self.patterns[key] = pattern
                
                logger.info(f"✅ Loaded {len(self.patterns)} patterns")
                
        except Exception as e:
            logger.warning(f"Failed to load patterns: {e}")
    
    def get_confidence_adjustment(
        self, 
        pattern_type: str, 
        pattern_subtype: str,
        project_context: Optional[str] = None
    ) -> float:
        """
        Get confidence adjustment multiplier for a pattern.
        
        Args:
            pattern_type: Type of pattern (todo, fixme, etc.)
            pattern_subtype: Subtype (security, performance, etc.)
            project_context: Optional project context filter
            
        Returns:
            Confidence multiplier (0.3 - 2.0)
        """
        key = f"{pattern_type.lower()}_{pattern_subtype.lower()}"
        
        if key in self.patterns:
            pattern = self.patterns[key]
            
            # Check if project context matches
            if project_context and pattern.project_context != project_context:
                return 1.0  # No adjustment for different context
            
            return pattern.confidence_multiplier
        
        return 1.0  # No adjustment if pattern not learned
    
    def enhance_ml_analysis(self, analysis_results: List[Any], project_path: Optional[Path] = None) -> List[Any]:
        """
        Enhance ML analysis results with learned codebase patterns.
        
        Args:
            analysis_results: Results from pure Python ML analysis
            project_path: Optional project path for context
            
        Returns:
            Enhanced results with adjusted confidence scores
        """
        if not analysis_results:
            return analysis_results
        
        enhanced_results = []
        adjustments_applied = 0
        
        for result in analysis_results:
            enhanced_result = result
            
            # Extract pattern information from result
            pattern_type = getattr(result, 'todo_type', 'unknown').lower()
            pattern_subtype = getattr(result, 'classification', 'general').lower()
            
            # Get confidence adjustment
            adjustment = self.get_confidence_adjustment(
                pattern_type, 
                pattern_subtype,
                self.project_context.project_type if self.project_context else None
            )
            
            if adjustment != 1.0:
                # Apply adjustment to confidence
                if hasattr(enhanced_result, 'confidence'):
                    enhanced_result.confidence *= adjustment
                    enhanced_result.confidence = max(0.1, min(1.0, enhanced_result.confidence))
                
                # Apply adjustment to priority score
                if hasattr(enhanced_result, 'priority_score'):
                    enhanced_result.priority_score *= adjustment
                    enhanced_result.priority_score = max(1, min(100, enhanced_result.priority_score))
                
                adjustments_applied += 1
            
            enhanced_results.append(enhanced_result)
        
        if adjustments_applied > 0:
            logger.info(f"✅ Applied {adjustments_applied} codebase learning adjustments")
        
        return enhanced_results
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get status of the codebase learning system."""
        return {
            'enabled': True,
            'patterns_learned': len(self.patterns),
            'project_context_available': self.project_context is not None,
            'vocabulary_terms': len(self.vocabulary_weights),
            'storage_path': str(self.storage_path),
            'project_type': self.project_context.project_type if self.project_context else 'unknown',
            'last_analysis': getattr(self, '_last_analysis_time', 'never'),
            'dependencies': ['re', 'json', 'sqlite3', 'statistics', 'pathlib', 'collections'],
            'heavy_dependencies': [],  # None!
            'blood_oath_compliant': True
        }


# Demo and testing
if __name__ == "__main__":
    import tempfile
    import json
    
    print("🎺 Testing Codebase Learning Engine")
    print("=" * 50)
    
    # Create test project structure
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project = Path(temp_dir) / "test_project"
        test_project.mkdir()
        
        # Create sample files with different comment patterns
        (test_project / "security.py").write_text("""
# TODO: Fix SQL injection vulnerability - CRITICAL security issue
def unsafe_query(user_input):
    query = f"SELECT * FROM users WHERE id = {user_input}"
    return execute_query(query)

# FIXME: Authentication bypass possible here
def check_auth(token):
    # HACK: Temporary workaround - URGENT fix needed
    return True  # Always returns true!
        """)
        
        (test_project / "performance.py").write_text("""
# TODO: Optimize database queries - performance bottleneck
def slow_function():
    # FIXME: Nested loops causing O(n²) complexity
    for i in range(1000):
        for j in range(1000):
            expensive_operation(i, j)

# NOTE: Consider caching here for better performance
def calculate_stats():
    pass
        """)
        
        (test_project / "general.py").write_text("""
# TODO: Add error handling
# FIXME: Update documentation
# HACK: Remove this debug code someday
print("Debug info")

# NOTE: This works fine for now
def working_function():
    return "OK"
        """)
        
        # Test codebase learning
        learning_engine = CodebaseLearningEngine()
        
        print("🔍 Analyzing test codebase...")
        project_context = learning_engine.analyze_codebase(test_project)
        
        print(f"📊 Project Analysis Results:")
        print(f"  Type: {project_context.project_type}")
        print(f"  Language: {project_context.primary_language}")
        print(f"  Complexity: {project_context.complexity_level}")
        print(f"  Files: {project_context.total_files}")
        
        print(f"\n🎯 Learned Patterns:")
        for key, pattern in learning_engine.patterns.items():
            print(f"  {key}: {pattern.confidence_multiplier:.2f}x confidence")
            print(f"    Frequency: {pattern.frequency}, Context Weight: {pattern.context_weight:.2f}")
        
        print(f"\n⚙️  Learning Status:")
        status = learning_engine.get_learning_status()
        print(json.dumps(status, indent=2))
        
        print("\n✅ Codebase learning test completed!")
        print("🩸 Blood Oath Status: COMPLIANT - Zero external dependencies!")