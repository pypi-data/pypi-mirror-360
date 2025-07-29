"""TypeScript analyzer extending JavaScript analysis with type information.

General Staff Role: G2 Intelligence - TypeScript Specialist
Provides enhanced analysis of TypeScript code leveraging type information
to identify additional patterns and provide type-aware recommendations.

Persistent Value: Creates TypeScript-specific observations that help AI
understand type safety, interface contracts, and architectural patterns.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import tempfile
import os
import atexit
import shlex
import subprocess

from .javascript_analyzer import JavaScriptAnalyzer
from .base_analyzer import AnalysisResult, CodeEntity, CodeIssue, CodeMetrics

logger = logging.getLogger(__name__)


class TypeScriptAnalyzer(JavaScriptAnalyzer):
    """TypeScript analyzer extending JavaScript analysis with type awareness.
    
    This analyzer provides additional intelligence about TypeScript-specific
    patterns, type safety issues, and architectural decisions.
    """
    
    def __init__(self, dcp_path: Optional[str] = None):
        """Initialize TypeScript analyzer."""
        super().__init__(dcp_path)
        self._supported_languages = {'typescript', 'tsx'}
        self.parser_script = self._create_typescript_parser_script()
        
    def _create_typescript_parser_script(self) -> str:
        """Create enhanced parser script for TypeScript.
        
        Returns path to TypeScript-aware parser script.
        """
        # Create temporary parser script with proper cleanup
        parser_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.js', 
            delete=False,
            prefix='brass_ts_parser_'
        )
        
        # Register cleanup on exit
        atexit.register(lambda: self._cleanup_file(parser_file.name))
        
        parser_ts = '''
const fs = require('fs');
const parser = require('@typescript-eslint/parser');
const { TSESTree } = require('@typescript-eslint/types');

// Read file from command line argument
const filePath = process.argv[2];
const code = fs.readFileSync(filePath, 'utf8');

// Parse options for TypeScript
const parseOptions = {
    loc: true,
    range: true,
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: {
        jsx: filePath.endsWith('.tsx')
    }
};

try {
    const ast = parser.parse(code, parseOptions);
    
    const analysis = {
        entities: [],
        imports: [],
        exports: [],
        types: [],
        interfaces: [],
        complexity: {},
        issues: [],
        metrics: {
            lines: code.split('\\n').length,
            functions: 0,
            classes: 0,
            interfaces: 0,
            types: 0,
            generics: 0,
            anyUsage: 0,
            strictMode: false
        }
    };
    
    // Simple AST traversal for TypeScript-specific features
    function traverse(node, parent = null) {
        if (!node || typeof node !== 'object') return;
        
        switch (node.type) {
            case 'FunctionDeclaration':
            case 'FunctionExpression':
            case 'ArrowFunctionExpression':
                analysis.entities.push({
                    type: 'function',
                    name: node.id ? node.id.name : '<anonymous>',
                    line_start: node.loc.start.line,
                    line_end: node.loc.end.line,
                    async: node.async || false,
                    generator: node.generator || false,
                    params: node.params ? node.params.length : 0,
                    returnType: node.returnType ? true : false,
                    typeParams: node.typeParameters ? true : false
                });
                analysis.metrics.functions++;
                break;
                
            case 'ClassDeclaration':
                analysis.entities.push({
                    type: 'class',
                    name: node.id ? node.id.name : '<anonymous>',
                    line_start: node.loc.start.line,
                    line_end: node.loc.end.line,
                    abstract: node.abstract || false,
                    implements: node.implements ? node.implements.length : 0,
                    typeParams: node.typeParameters ? true : false
                });
                analysis.metrics.classes++;
                break;
                
            case 'TSInterfaceDeclaration':
                analysis.interfaces.push({
                    name: node.id.name,
                    line: node.loc.start.line,
                    extends: node.extends ? node.extends.length : 0,
                    members: node.body.body.length
                });
                analysis.metrics.interfaces++;
                break;
                
            case 'TSTypeAliasDeclaration':
                analysis.types.push({
                    name: node.id.name,
                    line: node.loc.start.line,
                    generic: node.typeParameters ? true : false
                });
                analysis.metrics.types++;
                if (node.typeParameters) analysis.metrics.generics++;
                break;
                
            case 'TSAnyKeyword':
                analysis.metrics.anyUsage++;
                analysis.issues.push({
                    type: 'any_type_usage',
                    line: node.loc.start.line,
                    severity: 'medium'
                });
                break;
                
            case 'ImportDeclaration':
                analysis.imports.push({
                    source: node.source.value,
                    line: node.loc.start.line,
                    typeOnly: node.importKind === 'type'
                });
                break;
        }
        
        // Traverse children
        for (const key in node) {
            if (key === 'parent' || key === 'loc' || key === 'range') continue;
            const child = node[key];
            if (Array.isArray(child)) {
                child.forEach(item => traverse(item, node));
            } else if (child && typeof child === 'object') {
                traverse(child, node);
            }
        }
    }
    
    traverse(ast);
    
    // Calculate type safety score
    const typeSafetyScore = Math.max(0, 100 - (analysis.metrics.anyUsage * 5));
    analysis.metrics.typeSafetyScore = typeSafetyScore;
    
    // Detect strict mode
    analysis.metrics.strictMode = code.includes('"use strict"') || 
                                 code.includes("'use strict'");
    
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
        
        parser_file.write(parser_ts)
        parser_file.close()
        return parser_file.name
        
    def analyze(self, file_path: Path) -> AnalysisResult:
        """Analyze TypeScript file with enhanced type awareness.
        
        Args:
            file_path: Path to TypeScript file
            
        Returns:
            AnalysisResult with TypeScript-specific intelligence
        """
        # Get base JavaScript analysis
        result = super().analyze(file_path)
        
        # Update language
        result.language = 'typescript'
        
        # If we got a proper parse, enhance with TypeScript-specific checks
        if result.analysis_metadata.get('parse_success'):
            self._enhance_typescript_analysis(result)
            
        return result
        
    def _enhance_typescript_analysis(self, result: AnalysisResult):
        """Add TypeScript-specific analysis to results.
        
        Args:
            result: Base analysis result to enhance
        """
        # Check for TypeScript-specific issues
        ts_metrics = result.metrics.language_specific_metrics
        
        # Check for excessive 'any' usage
        any_usage = ts_metrics.get('any_usage', 0)
        if any_usage > 5:
            result.issues.append(CodeIssue(
                issue_type='excessive_any_usage',
                severity='medium' if any_usage < 10 else 'high',
                file_path=result.file_path,
                line_number=1,
                entity_name='file',
                description=f"File uses 'any' type {any_usage} times",
                ai_recommendation="Replace 'any' with specific types or 'unknown' for better type safety",
                fix_complexity='moderate',
                metadata={'any_count': any_usage}
            ))
            
        # Check for missing return types
        functions_without_types = sum(
            1 for e in result.entities 
            if e.entity_type in ['function', 'method'] 
            and not e.metadata.get('returnType')
        )
        
        if functions_without_types > 3:
            result.issues.append(CodeIssue(
                issue_type='missing_return_types',
                severity='low',
                file_path=result.file_path,
                line_number=1,
                entity_name='file',
                description=f"{functions_without_types} functions lack explicit return types",
                ai_recommendation="Add explicit return type annotations for better type safety and documentation",
                fix_complexity='simple'
            ))
            
        # Check for interface vs type alias usage
        interfaces = ts_metrics.get('interfaces', 0)
        types = ts_metrics.get('types', 0)
        
        if interfaces == 0 and types > 5:
            result.issues.append(CodeIssue(
                issue_type='prefer_interfaces',
                severity='low',
                file_path=result.file_path,
                line_number=1,
                entity_name='file',
                description="Consider using interfaces instead of type aliases for object types",
                ai_recommendation="Interfaces provide better error messages and extend capabilities",
                fix_complexity='simple'
            ))
            
        # Update metrics with TypeScript-specific data
        result.metrics.language_specific_metrics.update({
            'type_safety_score': ts_metrics.get('typeSafetyScore', 100),
            'strict_mode': ts_metrics.get('strictMode', False),
            'uses_generics': ts_metrics.get('generics', 0) > 0,
            'interface_count': interfaces,
            'type_alias_count': types
        })
        
    def _get_typescript_recommendation(self, issue_type: str) -> str:
        """Get TypeScript-specific recommendations.
        
        Args:
            issue_type: Type of issue
            
        Returns:
            Strategic recommendation for AI
        """
        recommendations = {
            'any_type_usage': "Replace 'any' with specific types, 'unknown', or generic constraints",
            'missing_return_types': "Add explicit return type annotations for public APIs",
            'no_explicit_any': "Enable 'noImplicitAny' in tsconfig.json for stricter typing",
            'excessive_type_assertions': "Reduce type assertions; use type guards instead",
            'missing_null_checks': "Enable 'strictNullChecks' for null safety"
        }
        
        return recommendations.get(
            issue_type,
            super()._get_js_recommendation(issue_type)
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