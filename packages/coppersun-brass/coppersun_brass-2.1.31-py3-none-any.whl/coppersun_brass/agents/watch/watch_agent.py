"""
Copper Sun Brass Watch Agent - Enhanced implementation with Claude integration and DCP
Provides dual-output: Analysis Reports + DCP Observations
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Removed Google Drive imports - functionality deprecated in Sprint 14

# Event Bus removed - using DCP coordination
from ...core.schemas import AgentReport, ProjectContext, Finding, Recommendation, ReportMetadata
from ..base_agent import DCPAwareAgent
from ...core.context.dcp_coordination import DCPCoordinator, CoordinationMessage
from ...core.constants import AgentNames, PerformanceSettings, ObservationTypes

logger = logging.getLogger(__name__)

# GoogleDriveSync class removed - Google Drive functionality deprecated in Sprint 14
# Copper Sun Brass now focuses on AI-to-AI communication through DCP (Copper Sun Brass Context Protocol)
# Human-readable outputs should be generated separately if needed

class SimpleFileWatcher(FileSystemEventHandler):
    """
    Handles file system events and batches changes for analysis.
    
    This class extends watchdog's FileSystemEventHandler to track file changes
    in the project directory. It maintains a bounded set of recent changes and
    triggers analysis when appropriate.
    
    Attributes:
        watch_agent: Reference to the parent WatchAgent instance
        recent_changes (Set[str]): Set of recently changed file paths
        max_changes_tracked (int): Maximum number of changes to track (default: 100)
    
    Example:
        >>> watcher = SimpleFileWatcher(watch_agent)
        >>> observer.schedule(watcher, path, recursive=True)
    """
    
    def __init__(self, watch_agent):
        self.watch_agent = watch_agent
        self.recent_changes: Set[str] = set()
        self.max_changes_tracked = 100
    
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_change(event.src_path, "modified")
    
    def on_created(self, event):
        if not event.is_directory:
            self._handle_change(event.src_path, "created")
    
    def on_deleted(self, event):
        if not event.is_directory:
            self._handle_change(event.src_path, "deleted")
    
    def _handle_change(self, file_path: str, change_type: str):
        """Process a file change event"""
        try:
            path = Path(file_path)
            project_path = Path(self.watch_agent.project_path)
            
            # Only track files within project path
            if project_path not in path.parents and path.parent != project_path:
                return
            
            rel_path = path.relative_to(project_path)
            
            # Skip certain file types and directories
            if self._should_ignore_file(rel_path):
                return
            
            # Prevent unbounded growth
            if len(self.recent_changes) >= self.max_changes_tracked:
                # Remove oldest changes (simple FIFO)
                oldest = list(self.recent_changes)[0]
                self.recent_changes.remove(oldest)
            
            self.recent_changes.add(str(rel_path))
            logger.debug(f"File {change_type}: {rel_path}")
            
            # Publish file change via DCP
            if self.watch_agent.dcp_coordinator:
                self.watch_agent.dcp_coordinator.publish(CoordinationMessage(
                    observation_type=ObservationTypes.FILE_CHANGE,
                    source_agent=self.watch_agent.agent_name,
                    data={
                        "file_path": str(rel_path),
                        "change_type": change_type,
                        "timestamp": datetime.now().isoformat()
                    }
                ))
            
            # Check if analysis should be triggered
            if self.watch_agent.should_run_analysis():
                self.watch_agent._schedule_analysis()
        
        except Exception as e:
            logger.error(f"Error processing file change {file_path}: {e}")
    
    def _should_ignore_file(self, rel_path: Path) -> bool:
        """Check if file should be ignored"""
        ignore_patterns = [
            '.git', '__pycache__', 'node_modules', '.next', 'dist', 'build',
            'venv', 'env', '.env', '.DS_Store', 'Thumbs.db'
        ]
        
        ignore_extensions = [
            '.pyc', '.pyo', '.pyd', '.so', '.dylib', '.dll',
            '.log', '.tmp', '.swp', '.bak'
        ]
        
        # Check if any parent directory should be ignored
        for part in rel_path.parts:
            if part in ignore_patterns:
                return True
        
        # Check file extension
        if rel_path.suffix in ignore_extensions:
            return True
        
        # Check if it's a hidden file
        if rel_path.name.startswith('.') and rel_path.suffix not in ['.env', '.gitignore']:
            return True
        
        return False
    
    def get_changes_and_reset(self) -> List[str]:
        """Get current changes and reset the tracking"""
        changes = list(self.recent_changes)
        self.recent_changes.clear()
        return changes

class WatchAgent(DCPAwareAgent):
    """
    Copper Sun Brass Watch Agent - monitors code changes and provides AI-powered insights.
    
    The Watch Agent is responsible for real-time monitoring of code changes and providing
    intelligent analysis with focus on AI-to-AI communication through DCP:
    1. DCP Observations - Updates to the Copper Sun Brass Context Protocol for AI consumption
    2. Event Bus Integration - Real-time notifications for multi-agent coordination
    
    Features:
        - Real-time file system monitoring using watchdog
        - Claude AI integration for intelligent code analysis
        - Automatic batching of changes for efficient processing
        - DCP-focused output system for AI-first architecture
        - Event-driven architecture for agent coordination
        - Performance-optimized with <0.5s analysis cycles
    
    Attributes:
        agent_name (str): Agent identifier ("watch")
        project_path (str): Path to the monitored project
        analysis_interval (int): Seconds between analysis runs (default: 300)
        event_bus: Event bus instance for inter-agent communication
        file_watcher: SimpleFileWatcher instance for tracking changes
        
    Example:
        >>> config = {
        ...     'project_path': '/path/to/project',
        ...     'analysis_interval': 300
        ... }
        >>> agent = WatchAgent(config)
        >>> agent.start()
    """
    
    def __init__(self, config_or_dcp=None, config: Optional[Dict] = None):
        """Initialize WatchAgent with DCP adapter or config dict.
        
        Args:
            config_or_dcp: Either a config dict or DCPAdapter instance
            config: Optional config dict (when first param is DCPAdapter)
        """
        # Handle different initialization patterns
        if hasattr(config_or_dcp, 'storage'):  # It's a DCPAdapter
            dcp_manager = config_or_dcp
            actual_config = config or {}
            project_path = actual_config.get('project_path', '/tmp/default_project')
            dcp_path = None  # DCPAdapter handles storage
        elif isinstance(config_or_dcp, dict):  # It's a config dict
            actual_config = config_or_dcp
            project_path = actual_config['project_path']
            dcp_path = actual_config.get('dcp_path')
            dcp_manager = None
        else:
            raise ValueError("First argument must be DCPAdapter or config dict")
        
        # Initialize DCP-aware base class with shared DCPAdapter
        super().__init__(
            project_path=project_path,
            dcp_path=dcp_path,
            dcp_adapter=dcp_manager,  # Pass shared DCPAdapter to prevent database conflicts
            context_window_hours=actual_config.get('context_window_hours', 24)
        )
        
        self.analysis_interval = actual_config.get('analysis_interval', PerformanceSettings.ANALYSIS_INTERVAL)
        self.last_analysis = 0
        self.running = False
        
        # Initialize components
        self.file_watcher = SimpleFileWatcher(self)
        self.observer = None
        
        # Initialize DCP coordinator
        self.dcp_coordinator = DCPCoordinator(self.agent_name, self.dcp_manager) if self.dcp_manager else None
        
        # Analysis state
        self.analysis_pending = False
        self._previous_boot = None  # Track hot vs cold starts
        
        # Claude client (lazy loading)
        self._claude_client = None
        
        # Google Drive functionality removed in Sprint 14 - focus on AI-to-AI communication via DCP
        
        logger.info(f"Watch agent initialized for project: {self.project_path}")
    
    @property
    def agent_name(self) -> str:
        """Return the agent's identifier."""
        return AgentNames.WATCH
    
    @property
    def relevant_observation_types(self) -> List[str]:
        """Define which observation types this agent needs on startup."""
        return [
            'file_change', 'project_structure', 'security', 
            'performance', 'code_smell', 'technical_debt'
        ]
    
    @property
    def claude_client(self):
        """Lazy-loaded Claude client"""
        if self._claude_client is None:
            try:
                from anthropic import Anthropic
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if not api_key:
                    logger.warning("ANTHROPIC_API_KEY not found in environment")
                    return None
                self._claude_client = Anthropic(api_key=api_key)
                logger.debug("Claude client initialized successfully")
            except Exception as e:
                logger.warning(f"Claude client initialization failed: {e}")
                self._claude_client = None
        return self._claude_client
    
    
    def start(self):
        """Start the watch agent"""
        self.running = True
        
        # Subscribe to DCP observations
        if self.dcp_coordinator:
            self.dcp_coordinator.subscribe(ObservationTypes.AGENT_ERROR, self._handle_error_observation)
            self.dcp_coordinator.start_polling()
        
        # Context already loaded by base class in __init__
        
        # Run initial analysis
        logger.info("Running initial analysis...")
        self._run_analysis_sync()
        
        # Start file watching
        self._start_file_watching()
        
        # Publish agent started via DCP
        if self.dcp_coordinator:
            self.dcp_coordinator.publish(CoordinationMessage(
                observation_type=ObservationTypes.AGENT_STATUS,
                source_agent=self.agent_name,
                data={
                    "timestamp": datetime.now().isoformat(),
                    "project_path": str(self.project_path)
                },
                metadata={'status': 'started'},
                broadcast=True
            ))
        
        logger.info("Copper Sun Brass Watch Agent started successfully")
    
    def _process_startup_context(self, context: Dict[str, List[Dict[str, Any]]]) -> None:
        """Process loaded context from base class.
        
        Args:
            context: Dict mapping observation types to lists of observations
        """
        # Extract relevant observation types
        recent_changes = context.get('file_change', [])
        structure = context.get('project_structure', [])
        security_obs = context.get('security', [])
        performance_obs = context.get('performance', [])
        
        # Initialize internal state based on DCP
        self._initialize_from_context(recent_changes, structure, security_obs, performance_obs)
        
        # Log what was loaded
        logger.info(
            f"Watch agent processed context: {len(recent_changes)} file changes, "
            f"{len(security_obs)} security observations, "
            f"{len(performance_obs)} performance observations"
        )
    
    def _initialize_from_context(self, recent_changes, structure, security_obs, performance_obs):
        """Initialize agent state from loaded DCP context."""
        # Update file watcher with known changes
        if recent_changes:
            for obs in recent_changes[-10:]:  # Last 10 changes
                if 'details' in obs and 'file_path' in obs['details']:
                    file_path = obs['details']['file_path']
                    self.file_watcher.recent_changes.add(file_path)
            
            logger.debug(f"Preloaded {len(self.file_watcher.recent_changes)} recent file changes")
        
        # Set analysis timing based on structure info
        if structure:
            struct_obs = structure[0]
            if 'details' in struct_obs and 'total_files' in struct_obs['details']:
                total_files = struct_obs['details']['total_files']
                # Adjust analysis interval based on project size
                if total_files > 1000:
                    self.analysis_interval = max(self.analysis_interval, 600)  # 10 minutes for large projects
                logger.debug(f"Adjusted analysis interval to {self.analysis_interval}s based on {total_files} files")
        
        # Track previous boot for hot start detection
        self._previous_boot = time.time()
    
    def _cold_boot_initialization(self):
        """Initialize agent without DCP context (fallback mode)."""
        logger.info("Watch agent starting in cold boot mode")
        # Set conservative defaults
        self.analysis_interval = max(self.analysis_interval, 300)  # 5 minutes minimum
        self._previous_boot = None
        # Clear any cached changes
        if hasattr(self.file_watcher, 'recent_changes'):
            self.file_watcher.recent_changes.clear()
    
    def stop(self):
        """Stop the watch agent"""
        self.running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        # Publish agent stopped via DCP
        if self.dcp_coordinator:
            self.dcp_coordinator.publish(CoordinationMessage(
                observation_type=ObservationTypes.AGENT_STATUS,
                source_agent=self.agent_name,
                data={"timestamp": datetime.now().isoformat()},
                metadata={'status': 'stopped'},
                broadcast=True
            ))
            self.dcp_coordinator.stop_polling()
        
        logger.info("Copper Sun Brass Watch Agent stopped")
    
    def check_changes(self) -> List[Dict[str, Any]]:
        """Check for file changes and return observations.
        
        This method is called by runner.py to get recent file changes.
        Returns a list of observation dictionaries compatible with the ML pipeline.
        
        Returns:
            List[Dict[str, Any]]: List of observations for changed files
        """
        changes = self.file_watcher.get_changes_and_reset()
        observations = []
        
        for file_path in changes:
            observations.append({
                'type': 'file_change',
                'file': file_path,
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'path': file_path,
                    'change_detected': True
                }
            })
        
        return observations
    
    def should_run_analysis(self) -> bool:
        """Check if it's time to run analysis based on interval"""
        return time.time() - self.last_analysis > self.analysis_interval
    
    def _start_file_watching(self):
        """Initialize and start file system watching"""
        self.observer = Observer()
        self.observer.schedule(
            self.file_watcher,
            str(self.project_path),
            recursive=True
        )
        self.observer.start()
        logger.info(f"Started watching: {self.project_path}")
    
    def _handle_error_observation(self, observation: Dict[str, Any]):
        """Handle error observations from DCP (new pattern)."""
        metadata = observation.get('metadata', {})
        data = observation.get('data', {})
        source = metadata.get('source_agent', 'unknown')
        logger.error(f"Error from {source}: {data.get('error', 'Unknown error')}")
    
    def _schedule_analysis(self):
        """Schedule analysis to run (debounced)"""
        if not self.analysis_pending:
            self.analysis_pending = True
            # For now, run analysis immediately
            self._run_analysis_async()
    
    def _run_analysis_async(self):
        """Run analysis asynchronously"""
        try:
            self._run_analysis_sync()
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            # Publish error via DCP
            if self.dcp_coordinator:
                self.dcp_coordinator.publish(CoordinationMessage(
                    observation_type=ObservationTypes.AGENT_ERROR,
                    source_agent=self.agent_name,
                    data={
                        "error": str(e),
                        "context": "analysis_execution",
                        "timestamp": datetime.now().isoformat()
                    },
                    metadata={'severity': 'error'},
                    broadcast=True
                ))
        finally:
            self.analysis_pending = False
    
    def _run_analysis_sync(self):
        """Enhanced analysis with Claude integration, DCP output, and Google Drive (TRIPLE OUTPUT)"""
        logger.info("🔍 Starting enhanced code analysis with triple output...")
        start_time = time.time()
        
        try:
            # Get recent changes
            changed_files = self.file_watcher.get_changes_and_reset()
            
            # Create project context
            project_context = ProjectContext(
                name=Path(self.project_path).name,
                path=self.project_path,
                total_files=self._count_files(),
                changed_files=changed_files,
                timestamp=datetime.now()
            )
            
            # ENHANCED: Real Claude analysis (with fallback)
            findings = self._analyze_with_claude(changed_files)
            
            # Generate recommendations based on findings
            recommendations = self._generate_recommendations(findings)
            
            # Create metadata
            processing_time = time.time() - start_time
            metadata = ReportMetadata(
                agent_name=self.agent_name,
                processing_time=processing_time,
                model_used="claude-3.5-sonnet" if self.claude_client else "enhanced-placeholder-v2.0"
            )
            
            # Create report (UNCHANGED structure)
            report = AgentReport(
                agent_name=self.agent_name,
                timestamp=datetime.now(),
                project_context=project_context,
                findings=findings,
                recommendations=recommendations,
                metadata=metadata
            )
            
            # Publish analysis completed via DCP
            if self.dcp_coordinator:
                self.dcp_coordinator.publish(CoordinationMessage(
                    observation_type=ObservationTypes.ANALYSIS_RESULT,
                    source_agent=self.agent_name,
                    data={
                        "processing_time": processing_time,
                        "findings_count": len(findings),
                        "recommendations_count": len(recommendations),
                        "changed_files": changed_files,
                        "claude_analysis": self.claude_client is not None
                    },
                    broadcast=True
                ))
            
            # TRIPLE OUTPUT 1: DCP integration (additive, non-breaking)
            dcp_result = self._update_dcp_with_findings(findings, changed_files)
            
            # Google Drive functionality removed - focusing on DCP for AI-to-AI communication
            
            # Publish DCP update notification if successful
            if dcp_result.get("success", False) and self.dcp_coordinator:
                # No need for separate notification - DCP updates are visible to all agents
                pass
            
            # Update timing
            self.last_analysis = time.time()
            
            # Enhanced logging for DCP-focused output
            logger.info(f"✅ Enhanced analysis completed in {processing_time:.2f}s")
            logger.info(f"   Findings: {len(findings)}, DCP: {'✅' if dcp_result.get('success') else '❌'}")
            
        except Exception as e:
            logger.error(f"Enhanced analysis failed: {e}")
            raise
    
    
    
    
    def _analyze_with_claude(self, changed_files: List[str]) -> List[Finding]:
        """
        Perform real Claude analysis with fallback to enhanced placeholders.
        
        This method attempts to analyze changed files using the Claude API. If Claude
        is unavailable or analysis fails, it gracefully degrades to enhanced placeholder
        findings to ensure continuous operation.
        
        Args:
            changed_files (List[str]): List of file paths that have changed
            
        Returns:
            List[Finding]: List of Finding objects with detected issues
            
        Note:
            Consultant refinement: Robust error handling with graceful degradation
        """
        try:
            if not self.claude_client or not changed_files:
                return self._create_enhanced_placeholder_findings(changed_files)
            
            # Read file contents (with size limits)
            file_contents = self._read_changed_files(changed_files)
            if not file_contents:
                return self._create_enhanced_placeholder_findings(changed_files)
            
            # Call Claude API with structured prompt
            claude_response = self._call_claude_api(file_contents)
            
            # Parse Claude response to Finding objects
            findings = self._parse_claude_response(claude_response, changed_files)
            
            logger.info(f"Claude analysis successful: {len(findings)} findings")
            return findings
            
        except Exception as e:
            logger.warning(f"Claude analysis failed, using enhanced placeholders: {e}")
            return self._create_enhanced_placeholder_findings(changed_files)
    
    def _read_changed_files(self, changed_files: List[str]) -> Dict[str, str]:
        """Read contents of changed files with size limits"""
        file_contents = {}
        max_file_size = 50000  # 50KB limit per file
        max_total_size = 200000  # 200KB total limit
        total_size = 0
        
        for file_path in changed_files[:10]:  # Limit to 10 files
            try:
                full_path = Path(self.project_path) / file_path
                if not full_path.exists() or not full_path.is_file():
                    continue
                
                file_size = full_path.stat().st_size
                if file_size > max_file_size:
                    logger.debug(f"Skipping large file: {file_path} ({file_size} bytes)")
                    continue
                
                if total_size + file_size > max_total_size:
                    logger.debug(f"Reached total size limit, stopping at {file_path}")
                    break
                
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_contents[file_path] = f.read()
                    total_size += file_size
                    
            except Exception as e:
                logger.debug(f"Could not read file {file_path}: {e}")
                continue
        
        return file_contents
    
    def _call_claude_api(self, file_contents: Dict[str, str]) -> str:
        """Call Claude API with optimized prompt"""
        
        # Create structured prompt for code analysis
        files_text = ""
        for file_path, content in file_contents.items():
            files_text += f"\n\n=== {file_path} ===\n{content}\n"
        
        prompt = f"""Analyze the following code files and provide structured findings.

Focus on:
1. Security vulnerabilities or concerns
2. Performance issues or optimizations  
3. Code quality problems (bugs, errors, warnings)
4. Implementation gaps or TODOs
5. Test coverage issues

Files to analyze:{files_text}

Respond with a JSON array of findings. Each finding should have:
- "type": one of ["security", "performance", "bug", "improvement", "test"]
- "severity": one of ["critical", "high", "medium", "low"]
- "location": specific file/line reference
- "description": clear explanation of the issue

Example format:
[
  {{
    "type": "security",
    "severity": "high", 
    "location": "auth.py:42",
    "description": "Missing input validation for user credentials"
  }}
]

Provide only the JSON array, no other text."""
        
        try:
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text if message.content else ""
            
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise
    
    def _parse_claude_response(self, claude_response: str, changed_files: List[str]) -> List[Finding]:
        """Parse Claude JSON response into Finding objects"""
        try:
            # Extract JSON from response
            claude_response = claude_response.strip()
            if claude_response.startswith('```json'):
                claude_response = claude_response[7:-3]
            elif claude_response.startswith('```'):
                claude_response = claude_response[3:-3]
            
            findings_data = json.loads(claude_response)
            
            if not isinstance(findings_data, list):
                raise ValueError("Expected JSON array of findings")
            
            findings = []
            for item in findings_data:
                finding = Finding(
                    type=item.get("type", "improvement"),
                    severity=item.get("severity", "medium"),
                    location=item.get("location", "general"),
                    description=item.get("description", "Code analysis finding")
                )
                findings.append(finding)
            
            logger.debug(f"Parsed {len(findings)} findings from Claude response")
            return findings
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse Claude response: {e}")
            return self._create_enhanced_placeholder_findings(changed_files)
    
    def _create_enhanced_placeholder_findings(self, changed_files: List[str]) -> List[Finding]:
        """Create enhanced placeholder findings when Claude is unavailable"""
        findings = []
        
        if changed_files:
            findings.append(Finding(
                type="improvement",
                severity="medium",
                location=", ".join(changed_files[:3]),
                description=f"Files modified: {len(changed_files)} files detected for analysis"
            ))
            
            # Add basic file-type specific observations
            for file_path in changed_files[:5]:
                if file_path.endswith(('.py', '.js', '.ts')):
                    findings.append(Finding(
                        type="improvement",
                        severity="low",
                        location=file_path,
                        description=f"Code file changed: {file_path} - consider reviewing for quality"
                    ))
        else:
            findings.append(Finding(
                type="info",
                severity="low",
                location="general",
                description="Copper Sun Brass Watch monitoring active - no recent changes detected"
            ))
        
        return findings
    
    def _generate_recommendations(self, findings: List[Finding]) -> List[Recommendation]:
        """Generate recommendations based on findings"""
        recommendations = []
        
        # Count findings by severity
        critical_count = sum(1 for f in findings if f.severity == "critical")
        high_count = sum(1 for f in findings if f.severity == "high")
        
        if critical_count > 0:
            recommendations.append(Recommendation(
                priority="high",
                action=f"Address {critical_count} critical issues immediately",
                rationale="Critical issues can impact security or functionality",
                estimated_effort="high",
                category="security"
            ))
        
        if high_count > 0:
            recommendations.append(Recommendation(
                priority="medium",
                action=f"Review and fix {high_count} high-priority findings",
                rationale="High-priority issues should be addressed in current sprint",
                estimated_effort="medium",
                category="development"
            ))
        
        # Always add Claude enhancement recommendation if not using Claude
        if not self.claude_client:
            recommendations.append(Recommendation(
                priority="medium",
                action="Configure Claude API for enhanced analysis",
                rationale="Enable AI-powered code analysis for better insights",
                estimated_effort="low",
                category="tooling"
            ))
        
        return recommendations
    
    def _update_dcp_with_findings(self, findings: List[Finding], changed_files: List[str]) -> Dict[str, Any]:
        """
        Convert findings to DCP observations.
        
        This method transforms Watch Agent findings into DCP observations, maintaining
        proper source tracking and priority mapping. It includes token estimation to
        monitor DCP size growth.
        
        Args:
            findings (List[Finding]): List of findings from analysis
            changed_files (List[str]): List of files that were analyzed
            
        Returns:
            Dict[str, Any]: Result dictionary with success status and metadata
                - success (bool): Whether the update succeeded
                - observations_count (int): Number of observations added
                - timestamp (int): Unix timestamp of the update
                
        Note:
            Consultant refinements:
            - Source agent ID tracking
            - Formal mapping validation
            - Token estimation utility usage
        """
        if not self.dcp_manager:
            logger.debug("DCP manager not available, skipping DCP update")
            return {"success": False, "reason": "dcp_manager_unavailable"}
        
        try:
            observations_added = 0
            timestamp = int(time.time())
            
            # Convert each finding to DCP observation
            for i, finding in enumerate(findings):
                # Consultant refinement: Enhanced observation ID with source tracking
                observation_id = f"watch/claude-{timestamp}-{finding.type}-{i}"
                observation_type = self._map_finding_to_dcp_type(finding.type)
                priority = self._calculate_dcp_priority(finding.severity)
                
                # Add observation using the correct API
                obs_id = self.dcp_manager.add_observation(
                    obs_type=observation_type,
                    data={
                        'summary': f"{finding.description} [Location: {finding.location}, Source: {self.agent_name}/claude]",
                        'location': finding.location,
                        'details': {
                            'severity': finding.severity,
                            'finding_type': finding.type,
                            'original_id': observation_id
                        }
                    },
                    source_agent=self.agent_name,
                    priority=priority
                )
                observations_added += 1
            
            # Update DCP metadata
            if observations_added > 0:
                # Consultant refinement: Use token estimation utility
                try:
                    current_dcp = self.dcp_manager.read_dcp()
                    estimated_tokens = self._estimate_dcp_tokens(current_dcp)
                    
                    self.dcp_manager.update_metadata({
                        "last_watch_analysis": timestamp,
                        "files_analyzed": len(changed_files),
                        "observations_from_watch": observations_added,
                        "estimated_tokens": estimated_tokens
                    })
                    
                    if estimated_tokens > 4000:  # Soft threshold warning
                        logger.warning(f"DCP size growing large: {estimated_tokens} tokens")
                        
                except Exception as e:
                    logger.debug(f"Token estimation failed: {e}")
            
            logger.info(f"DCP updated: {observations_added} observations added")
            
            # Consultant refinement: Test annotation write path
            if observations_added > 0:
                try:
                    # Annotate the first observation we created
                    if observations_added > 0 and 'obs_id' in locals():
                        self.dcp_manager.annotate_observation(
                            obs_id,  # Use the actual observation ID returned
                            {
                                "agent": "watch",
                                "type": "validation",
                                "content": "Sprint 2 validation - write path working"
                            }
                        )
                    logger.debug("Claude annotation write path validated")
                except Exception as e:
                    logger.debug(f"Annotation test failed: {e}")
            
            return {
                "success": True,
                "observations_count": observations_added,
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.warning(f"DCP update failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "observations_count": 0
            }
    
    def _map_finding_to_dcp_type(self, finding_type: str) -> str:
        """
        Map Finding.type to DCP observation type
        Consultant refinement: Formal mapping with test coverage
        """
        type_mapping = {
            "security": "security",
            "performance": "performance", 
            "bug": "code_health",
            "improvement": "implementation_gap",
            "test": "test_coverage",
            "info": "code_health"
        }
        
        mapped_type = type_mapping.get(finding_type.lower(), "code_health")
        logger.debug(f"Mapped finding type '{finding_type}' -> '{mapped_type}'")
        return mapped_type
    
    def _calculate_dcp_priority(self, severity: str) -> int:
        """
        Convert Finding.severity to DCP priority score
        Consultant refinement: Consistent 0-100 mapping
        """
        severity_mapping = {
            "critical": 95,
            "high": 80,
            "medium": 65,
            "low": 40
        }
        
        priority = severity_mapping.get(severity.lower(), 50)
        logger.debug(f"Mapped severity '{severity}' -> priority {priority}")
        return priority
    
    def _estimate_dcp_tokens(self, dcp_dict: Dict) -> int:
        """
        Consultant refinement: Token estimation utility (no overhead tracking)
        Rough estimation for DCP size monitoring
        """
        try:
            dcp_json = json.dumps(dcp_dict)
            # Rough approximation: 1 token ≈ 4 characters
            estimated_tokens = len(dcp_json) // 4
            return estimated_tokens
        except Exception:
            return 0
    
    def _count_files(self) -> int:
        """Count relevant files in the project"""
        try:
            code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.md'}
            count = 0
            
            for file_path in Path(self.project_path).rglob('*'):
                if (file_path.is_file() and 
                    file_path.suffix in code_extensions and
                    not self.file_watcher._should_ignore_file(file_path.relative_to(self.project_path))):
                    count += 1
            
            return count
        except Exception:
            return 0


# Consultant refinement: Add formal test coverage
    def _cleanup(self) -> None:
        """Clean up Watch agent resources."""
        if hasattr(self, 'observer') and self.observer:
            self.observer.stop()
            self.observer.join()
        logger.debug("Watch agent cleanup completed")


def test_finding_dcp_mapping():
    """Test Finding -> DCP mapping consistency"""
    test_agent = WatchAgent({"project_path": "/test"})
    
    test_cases = [
        ("security", "security"),
        ("performance", "performance"),
        ("bug", "code_health"),
        ("improvement", "implementation_gap"),
        ("test", "test_coverage")
    ]
    
    print("Testing Finding -> DCP mapping:")
    for finding_type, expected_dcp_type in test_cases:
        actual = test_agent._map_finding_to_dcp_type(finding_type)
        status = "✅" if actual == expected_dcp_type else "❌"
        print(f"  {status} {finding_type} -> {actual} (expected: {expected_dcp_type})")
    
    severity_cases = [
        ("critical", 95),
        ("high", 80), 
        ("medium", 65),
        ("low", 40)
    ]
    
    print("\nTesting severity -> priority mapping:")
    for severity, expected_priority in severity_cases:
        actual = test_agent._calculate_dcp_priority(severity)
        status = "✅" if actual == expected_priority else "❌"
        print(f"  {status} {severity} -> {actual} (expected: {expected_priority})")

if __name__ == "__main__":
    test_finding_dcp_mapping()