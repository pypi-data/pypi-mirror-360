"""JavaScript/TypeScript analyzer for deep code understanding.

General Staff Role: G2 Intelligence - JavaScript/TypeScript Specialist
Provides deep analysis of JavaScript and TypeScript code to identify patterns,
complexity, and potential issues that inform AI strategic planning.

Persistent Value: Creates detailed JS/TS observations that help AI understand
modern web application architecture and make framework-aware recommendations.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set
from datetime import datetime
import logging
import os
import shlex
import atexit

from .base_analyzer import BaseAnalyzer, AnalysisResult, CodeEntity, CodeIssue, CodeMetrics

logger = logging.getLogger(__name__)


class JavaScriptAnalyzer(BaseAnalyzer):
    """JavaScript analyzer using Node.js AST parsers for deep understanding.
    
    This analyzer provides intelligence about JavaScript code structure,
    patterns, and potential issues to support AI decision-making.
    Supports modern JavaScript including ES6+, JSX, and common patterns.
    """
    
    # Thresholds for AI assessment
    COMPLEXITY_THRESHOLDS = {
        'low': 5,
        'medium': 10,
        'high': 15,
        'critical': 20
    }
    
    FUNCTION_LENGTH_THRESHOLDS = {
        'acceptable': 30,
        'concerning': 50,
        'problematic': 100
    }
    
    # JS-specific patterns to detect
    CALLBACK_DEPTH_THRESHOLD = 3
    PROMISE_CHAIN_LENGTH_THRESHOLD = 5
    
    def __init__(self, dcp_path: Optional[str] = None):
        """Initialize JavaScript analyzer with DCP integration."""
        super().__init__(dcp_path)
        self._supported_languages = {'javascript', 'jsx'}
        self.parser_script = self._create_parser_script()
        self._check_node_availability()
        
    def supports_language(self, language: str) -> bool:
        """Check if analyzer supports given language."""
        return language.lower() in self._supported_languages
        
    def _check_node_availability(self):
        """Check if Node.js is available for parsing."""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning("Node.js not available, JS analysis will be limited")
                self.node_available = False
            else:
                self.node_available = True
                logger.info(f"Using Node.js {result.stdout.strip()} for JS parsing")
        except FileNotFoundError:
            logger.warning("Node.js not found, JS analysis will be limited")
            self.node_available = False
            
    def _create_parser_script(self) -> str:
        """Create Node.js script for parsing JavaScript.
        
        Returns path to the parser script that uses @babel/parser.
        """
        # Create temporary parser script with proper cleanup
        parser_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.js', 
            delete=False,
            prefix='brass_parser_'
        )
        
        # Register cleanup on exit
        atexit.register(lambda: self._cleanup_file(parser_file.name))
        
        parser_js = '''
const fs = require('fs');
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

// Read file from command line argument
const filePath = process.argv[2];
const code = fs.readFileSync(filePath, 'utf8');

// Parse options for maximum compatibility
const parseOptions = {
    sourceType: 'unambiguous',
    plugins: [
        'jsx',
        'typescript',
        'decorators-legacy',
        'dynamicImport',
        'classProperties',
        'optionalChaining',
        'nullishCoalescingOperator',
        'asyncGenerators',
        'objectRestSpread'
    ]
};

try {
    const ast = parser.parse(code, parseOptions);
    
    const analysis = {
        entities: [],
        imports: [],
        exports: [],
        complexity: {},
        issues: [],
        metrics: {
            lines: code.split('\\n').length,
            functions: 0,
            classes: 0,
            callbacks: 0,
            promises: 0,
            asyncFunctions: 0
        }
    };
    
    // Traverse AST to extract information
    traverse(ast, {
        FunctionDeclaration(path) {
            analysis.entities.push({
                type: 'function',
                name: path.node.id ? path.node.id.name : '<anonymous>',
                line_start: path.node.loc.start.line,
                line_end: path.node.loc.end.line,
                async: path.node.async,
                generator: path.node.generator,
                params: path.node.params.length
            });
            analysis.metrics.functions++;
            if (path.node.async) analysis.metrics.asyncFunctions++;
        },
        
        ArrowFunctionExpression(path) {
            // Check if it's a callback (nested in CallExpression)
            if (path.findParent(p => p.isCallExpression())) {
                analysis.metrics.callbacks++;
            }
            
            analysis.entities.push({
                type: 'arrow_function',
                name: '<arrow>',
                line_start: path.node.loc.start.line,
                line_end: path.node.loc.end.line,
                async: path.node.async,
                params: path.node.params.length
            });
        },
        
        ClassDeclaration(path) {
            const methods = path.node.body.body.filter(
                member => member.type === 'MethodDefinition'
            ).length;
            
            analysis.entities.push({
                type: 'class',
                name: path.node.id ? path.node.id.name : '<anonymous>',
                line_start: path.node.loc.start.line,
                line_end: path.node.loc.end.line,
                methods: methods,
                superClass: path.node.superClass ? true : false
            });
            analysis.metrics.classes++;
        },
        
        ImportDeclaration(path) {
            analysis.imports.push({
                source: path.node.source.value,
                line: path.node.loc.start.line
            });
        },
        
        CallExpression(path) {
            // Detect promise chains
            if (path.node.callee.property && 
                ['then', 'catch', 'finally'].includes(path.node.callee.property.name)) {
                analysis.metrics.promises++;
            }
        },
        
        // Detect console.log (potential security issue)
        MemberExpression(path) {
            if (path.node.object.name === 'console') {
                analysis.issues.push({
                    type: 'console_statement',
                    line: path.node.loc.start.line,
                    severity: 'low'
                });
            }
        }
    });
    
    // Calculate cyclomatic complexity for functions
    // (Simplified - real implementation would be more thorough)
    analysis.complexity.average = Math.max(1, 
        Math.floor(analysis.metrics.callbacks / 2 + 
                   analysis.metrics.promises / 3));
    
    console.log(JSON.stringify(analysis, null, 2));
    
} catch (error) {
    console.error(JSON.stringify({
        error: error.message,
        type: 'parse_error',
        file: filePath
    }));
    process.exit(1);
}
        '''
        
        parser_file.write(parser_js)
        parser_file.close()
        return parser_file.name
        
    def analyze(self, file_path: Path) -> AnalysisResult:
        """Analyze JavaScript/TypeScript file for deep understanding.
        
        Args:
            file_path: Path to JS/TS file
            
        Returns:
            AnalysisResult with comprehensive JavaScript intelligence
        """
        if not self.node_available:
            return self._create_fallback_analysis(file_path)
            
        try:
            # First check if we have the required npm packages
            self._ensure_parser_dependencies()
            
            # Run parser script with secure path handling
            safe_file_path = shlex.quote(str(file_path))
            safe_parser_script = shlex.quote(self.parser_script)
            
            result = subprocess.run(
                ['node', safe_parser_script, safe_file_path],
                capture_output=True,
                text=True,
                timeout=10,
                shell=False  # Explicitly disable shell
            )
            
            if result.returncode != 0:
                logger.error(f"Parser error: {result.stderr}")
                return self._create_fallback_analysis(file_path)
                
            # Parse the analysis results
            analysis_data = json.loads(result.stdout)
            
            # Convert to our standard format
            return self._convert_to_analysis_result(file_path, analysis_data)
            
        except subprocess.TimeoutExpired:
            logger.error(f"Parser timeout for {file_path}")
            return self._create_fallback_analysis(file_path)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid parser output: {e}")
            return self._create_fallback_analysis(file_path)
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return self._create_fallback_analysis(file_path)
            
    def _ensure_parser_dependencies(self):
        """Ensure required npm packages are available.
        
        For now, we'll create a simple notice. In production,
        this would check for and install dependencies.
        """
        # Check if @babel/parser is available
        check_result = subprocess.run(
            ['node', '-e', "require.resolve('@babel/parser')"],
            capture_output=True
        )
        
        if check_result.returncode != 0:
            # Create a setup script for the user
            setup_script = Path(self.parser_script).parent / "setup_js_parser.sh"
            setup_script.write_text("""#!/bin/bash
# Install JavaScript parser dependencies
npm install --no-save @babel/parser @babel/traverse
""")
            logger.warning(
                f"JavaScript parser not set up. Run: bash {setup_script}"
            )
            
    def _convert_to_analysis_result(self, file_path: Path, 
                                   parser_data: Dict[str, Any]) -> AnalysisResult:
        """Convert parser output to standard AnalysisResult.
        
        Args:
            file_path: Path to analyzed file
            parser_data: Raw parser output
            
        Returns:
            Standardized AnalysisResult
        """
        entities = []
        issues = []
        
        # Convert entities
        for entity_data in parser_data.get('entities', []):
            entity = CodeEntity(
                entity_type=entity_data['type'],
                entity_name=entity_data['name'],
                file_path=str(file_path),
                line_start=entity_data['line_start'],
                line_end=entity_data['line_end'],
                parameters=list(range(entity_data.get('params', 0))),
                metadata={
                    'is_async': entity_data.get('async', False),
                    'is_generator': entity_data.get('generator', False),
                    'is_arrow': entity_data['type'] == 'arrow_function',
                    'method_count': entity_data.get('methods', 0),
                    'has_superclass': entity_data.get('superClass', False)
                }
            )
            
            # Estimate complexity based on function length
            entity.complexity_score = max(1, (entity.line_end - entity.line_start) // 10)
            
            entities.append(entity)
            
            # Check for issues
            self._check_javascript_issues(entity, issues)
            
        # Add parser-detected issues
        for issue_data in parser_data.get('issues', []):
            issues.append(CodeIssue(
                issue_type=issue_data['type'],
                severity=issue_data['severity'],
                file_path=str(file_path),
                line_number=issue_data['line'],
                entity_name='',
                description=f"{issue_data['type'].replace('_', ' ').title()} detected",
                ai_recommendation=self._get_js_recommendation(issue_data['type']),
                fix_complexity='trivial'
            ))
            
        # Create metrics
        metrics_data = parser_data.get('metrics', {})
        metrics = CodeMetrics(
            total_lines=metrics_data.get('lines', 0),
            code_lines=int(metrics_data.get('lines', 0) * 0.8),  # Estimate
            total_entities=len(entities),
            total_functions=metrics_data.get('functions', 0),
            total_classes=metrics_data.get('classes', 0),
            average_complexity=parser_data.get('complexity', {}).get('average', 1),
            language_specific_metrics={
                'async_functions': metrics_data.get('asyncFunctions', 0),
                'callbacks': metrics_data.get('callbacks', 0),
                'promises': metrics_data.get('promises', 0),
                'uses_jsx': any('.jsx' in str(imp.get('source', '')) 
                              for imp in parser_data.get('imports', [])),
                'framework': self._detect_framework(parser_data.get('imports', []))
            }
        )
        
        return AnalysisResult(
            file_path=str(file_path),
            language='javascript',
            analysis_timestamp=datetime.now(),
            entities=entities,
            issues=issues,
            metrics=metrics,
            imports=[imp['source'] for imp in parser_data.get('imports', [])],
            analysis_metadata={
                'analyzer': 'JavaScriptAnalyzer',
                'version': '1.0',
                'parser': '@babel/parser',
                'parse_success': True
            }
        )
        
    def _check_javascript_issues(self, entity: CodeEntity, issues: List[CodeIssue]):
        """Check for JavaScript-specific issues.
        
        Args:
            entity: Code entity to check
            issues: List to append issues to
        """
        # Check for long functions
        function_length = entity.line_end - entity.line_start + 1
        if function_length > self.FUNCTION_LENGTH_THRESHOLDS['problematic']:
            issues.append(CodeIssue(
                issue_type='long_function',
                severity='high',
                file_path=entity.file_path,
                line_number=entity.line_start,
                entity_name=entity.entity_name,
                description=f"Function is {function_length} lines long",
                ai_recommendation="Consider breaking into smaller functions for better testability",
                fix_complexity='moderate'
            ))
            
        # Check for callback complexity
        if entity.metadata.get('is_arrow') and entity.complexity_score > 5:
            issues.append(CodeIssue(
                issue_type='complex_callback',
                severity='medium',
                file_path=entity.file_path,
                line_number=entity.line_start,
                entity_name=entity.entity_name,
                description="Complex callback function detected",
                ai_recommendation="Consider using async/await or extracting to named function",
                fix_complexity='simple'
            ))
            
        # Check for missing async in promise-returning functions
        # (This would need more sophisticated detection in real implementation)
        
    def _detect_framework(self, imports: List[Dict[str, Any]]) -> str:
        """Detect JavaScript framework from imports.
        
        Args:
            imports: List of import data
            
        Returns:
            Detected framework name
        """
        import_sources = [imp.get('source', '') for imp in imports]
        
        if any('react' in src for src in import_sources):
            return 'react'
        elif any('vue' in src for src in import_sources):
            return 'vue'
        elif any('@angular' in src for src in import_sources):
            return 'angular'
        elif any('express' in src for src in import_sources):
            return 'express'
        else:
            return 'vanilla'
            
    def _get_js_recommendation(self, issue_type: str) -> str:
        """Get AI recommendation for JavaScript issue type.
        
        Args:
            issue_type: Type of issue
            
        Returns:
            Strategic recommendation for AI
        """
        recommendations = {
            'console_statement': "Remove console statements before production deployment",
            'eval_usage': "Replace eval() with safer alternatives like JSON.parse or Function constructor",
            'global_variable': "Use module pattern or ES6 modules to avoid global namespace pollution",
            'debugger_statement': "Remove debugger statements before committing",
            'alert_usage': "Replace alert() with proper UI notifications"
        }
        
        return recommendations.get(
            issue_type, 
            f"Review and fix {issue_type.replace('_', ' ')}"
        )
        
    def _create_fallback_analysis(self, file_path: Path) -> AnalysisResult:
        """Create basic analysis when Node.js parser unavailable.
        
        This provides degraded but still useful intelligence.
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Basic metrics
            total_lines = len(lines)
            
            # Simple pattern matching for basic intelligence
            function_count = sum(1 for line in lines 
                               if 'function' in line or '=>' in line)
            class_count = sum(1 for line in lines if 'class ' in line)
            
            # Basic issues detection
            issues = []
            for i, line in enumerate(lines, 1):
                if 'console.' in line:
                    issues.append(CodeIssue(
                        issue_type='console_statement',
                        severity='low',
                        file_path=str(file_path),
                        line_number=i,
                        entity_name='',
                        description='Console statement detected',
                        ai_recommendation='Remove console statements for production',
                        fix_complexity='trivial'
                    ))
                elif 'eval(' in line:
                    issues.append(CodeIssue(
                        issue_type='eval_usage',
                        severity='critical',
                        file_path=str(file_path),
                        line_number=i,
                        entity_name='',
                        description='Eval usage detected - security risk',
                        ai_recommendation='Replace eval with safer alternative',
                        fix_complexity='moderate'
                    ))
                    
            return AnalysisResult(
                file_path=str(file_path),
                language='javascript',
                analysis_timestamp=datetime.now(),
                entities=[],
                issues=issues,
                metrics=CodeMetrics(
                    total_lines=total_lines,
                    code_lines=int(total_lines * 0.8),
                    total_functions=function_count,
                    total_classes=class_count,
                    documentation_coverage=0.0
                ),
                analysis_metadata={
                    'analyzer': 'JavaScriptAnalyzer',
                    'version': '1.0',
                    'parser': 'fallback',
                    'parse_success': False,
                    'fallback_reason': 'Node.js unavailable'
                }
            )
            
        except Exception as e:
            logger.error(f"Fallback analysis failed: {e}")
            return AnalysisResult(
                file_path=str(file_path),
                language='javascript',
                analysis_timestamp=datetime.now(),
                entities=[],
                issues=[],
                metrics=CodeMetrics(),
                analysis_metadata={
                    'analyzer': 'JavaScriptAnalyzer',
                    'version': '1.0',
                    'error': str(e)
                }
            )
            
    def _cleanup_file(self, file_path: str):
        """Safely clean up temporary file."""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
    
    def __del__(self):
        """Clean up temporary parser script."""
        if hasattr(self, 'parser_script'):
            self._cleanup_file(self.parser_script)