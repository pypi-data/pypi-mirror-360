"""Python-specific AST analyzer for deep code understanding.

General Staff Role: G2 Intelligence - Python Specialist
Provides deep analysis of Python code structure to identify patterns,
complexity, and potential issues that inform AI strategic planning.

Persistent Value: Creates detailed Python-specific observations that
help AI understand code evolution and make language-aware recommendations.
"""

import ast
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set
from datetime import datetime
import logging

from .base_analyzer import BaseAnalyzer, AnalysisResult, CodeEntity, CodeIssue, CodeMetrics

logger = logging.getLogger(__name__)


class ComplexityVisitor(ast.NodeVisitor):
    """Calculate cyclomatic complexity for Python code.
    
    This helps AI assess code maintainability and identify
    refactoring opportunities.
    """
    
    def __init__(self):
        self.complexity = 1  # Base complexity
        
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_Assert(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_BoolOp(self, node):
        # Each 'and'/'or' adds to complexity
        self.complexity += len(node.values) - 1
        self.generic_visit(node)
        
    def visit_Lambda(self, node):
        self.complexity += 1
        self.generic_visit(node)


class PythonAnalyzer(BaseAnalyzer):
    """Python-specific analyzer using AST for deep code understanding.
    
    This analyzer provides intelligence about Python code structure,
    patterns, and potential issues to support AI decision-making.
    """
    
    # Thresholds for AI assessment (based on best practices)
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
    
    PARAMETER_THRESHOLDS = {
        'ideal': 3,
        'acceptable': 5,
        'concerning': 7
    }
    
    # Memory limits for file processing
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_AST_NODES = 50000  # Prevent memory exhaustion on generated files
    
    def __init__(self, dcp_path: Optional[str] = None):
        """Initialize Python analyzer with DCP integration."""
        super().__init__(dcp_path)
        self._supported_languages = {'python'}
        self.current_file: Optional[str] = None
        self.entities: List[CodeEntity] = []
        self.issues: List[CodeIssue] = []
        self.imports: Set[str] = set()
        self.dependencies: Set[str] = set()
        
    def supports_language(self, language: str) -> bool:
        """Python analyzer only supports Python."""
        return language.lower() == 'python'
        
    def analyze(self, file_path: Path) -> AnalysisResult:
        """Analyze Python file using AST for deep understanding.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            AnalysisResult with comprehensive Python intelligence
        """
        self.current_file = str(file_path)
        self.entities.clear()
        self.issues.clear()
        self.imports.clear()
        self.dependencies.clear()
        
        try:
            # Check file size before reading
            file_size = file_path.stat().st_size
            if file_size > self.MAX_FILE_SIZE:
                logger.warning(f"File {file_path} exceeds size limit ({file_size} > {self.MAX_FILE_SIZE})")
                return self._create_limited_analysis(file_path, "File too large for AST analysis")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))
            
            # Check AST complexity
            node_count = sum(1 for _ in ast.walk(tree))
            if node_count > self.MAX_AST_NODES:
                logger.warning(f"File {file_path} has too many AST nodes ({node_count} > {self.MAX_AST_NODES})")
                return self._create_limited_analysis(file_path, "AST too complex for analysis")
            
            # Calculate file fingerprint for change detection
            ast_fingerprint = self._calculate_ast_fingerprint(tree)
            
            # Analyze the AST
            self._analyze_node(tree)
            
            # Calculate metrics
            metrics = self._calculate_metrics(content)
            
            # Create result optimized for AI consumption
            return AnalysisResult(
                file_path=str(file_path),
                language='python',
                analysis_timestamp=datetime.now(),
                entities=self.entities,
                issues=self.issues,
                metrics=metrics,
                dependencies=list(self.dependencies),
                imports=list(self.imports),
                ast_fingerprint=ast_fingerprint,
                analysis_metadata={
                    'analyzer': 'PythonAnalyzer',
                    'version': '1.0',
                    'ast_parse_success': True
                }
            )
            
        except SyntaxError as e:
            # Graceful degradation - still provide value even with syntax errors
            logger.warning(f"Syntax error in {file_path}: {e}")
            return self._create_error_result(file_path, f"Syntax error: {e}")
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return self._create_error_result(file_path, str(e))
            
    def _analyze_node(self, node: ast.AST, parent_class: Optional[str] = None, depth: int = 0):
        """Recursively analyze AST nodes to extract intelligence.
        
        Args:
            node: AST node to analyze
            parent_class: Parent class name for context
            depth: Current nesting depth
        """
        # Handle imports for dependency tracking
        if isinstance(node, ast.Import):
            for alias in node.names:
                self.dependencies.add(alias.name.split('.')[0])
                
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                self.dependencies.add(node.module.split('.')[0])
                self.imports.add(node.module)
                
        # Analyze functions and methods
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._analyze_function(node, parent_class, depth)
            
        # Analyze classes
        elif isinstance(node, ast.ClassDef):
            self._analyze_class(node, depth)
            
        # Recursively analyze children
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                self._analyze_node(child, child.name, depth + 1)
            else:
                self._analyze_node(child, parent_class, depth + 1)
                
    def _analyze_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], 
                         parent_class: Optional[str], depth: int):
        """Extract intelligence about a function for AI assessment.
        
        Args:
            node: Function AST node
            parent_class: Parent class if this is a method
            depth: Nesting depth
        """
        # Create entity for AI understanding
        entity = CodeEntity(
            entity_type='method' if parent_class else 'function',
            entity_name=node.name,
            file_path=self.current_file,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            parent_entity=parent_class,
            parameters=[arg.arg for arg in node.args.args],
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            docstring=ast.get_docstring(node)
        )
        
        # Calculate complexity for AI assessment
        complexity_visitor = ComplexityVisitor()
        complexity_visitor.visit(node)
        entity.complexity_score = complexity_visitor.complexity
        
        # Extract dependencies this function uses
        entity.dependencies = self._extract_function_dependencies(node)
        
        # Add metadata for AI context
        entity.metadata = {
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'has_return': self._has_return(node),
            'has_yield': self._has_yield(node),
            'nesting_depth': depth,
            'is_private': node.name.startswith('_'),
            'is_dunder': node.name.startswith('__') and node.name.endswith('__'),
            'uses_type_hints': self._has_type_hints(node)
        }
        
        self.entities.append(entity)
        
        # Check for issues that AI should know about
        self._check_function_issues(entity, node)
        
    def _analyze_class(self, node: ast.ClassDef, depth: int):
        """Extract intelligence about a class for AI assessment.
        
        Args:
            node: Class AST node
            depth: Nesting depth
        """
        # Create entity for AI understanding
        entity = CodeEntity(
            entity_type='class',
            entity_name=node.name,
            file_path=self.current_file,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            docstring=ast.get_docstring(node)
        )
        
        # Analyze class structure
        methods = []
        properties = []
        class_vars = []
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                properties.append(item.target.id)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_vars.append(target.id)
        
        # Extract base classes for inheritance understanding
        base_classes = []
        for base in node.bases:
            base_classes.append(self._get_name(base))
        
        entity.metadata = {
            'base_classes': base_classes,
            'method_count': len(methods),
            'property_count': len(properties),
            'class_var_count': len(class_vars),
            'has_init': '__init__' in methods,
            'is_dataclass': any(d for d in entity.decorators if 'dataclass' in d),
            'is_abstract': any(base for base in base_classes if 'ABC' in base),
            'nesting_depth': depth
        }
        
        self.entities.append(entity)
        
        # Check for class-level issues
        self._check_class_issues(entity, node, methods)
        
    def _check_function_issues(self, entity: CodeEntity, node: ast.AST):
        """Identify function-level issues for AI strategic planning.
        
        Args:
            entity: CodeEntity for the function
            node: Function AST node
        """
        # Check complexity
        if entity.complexity_score > self.COMPLEXITY_THRESHOLDS['critical']:
            severity = 'critical'
        elif entity.complexity_score > self.COMPLEXITY_THRESHOLDS['high']:
            severity = 'high'
        elif entity.complexity_score > self.COMPLEXITY_THRESHOLDS['medium']:
            severity = 'medium'
        else:
            severity = None
            
        if severity:
            self.issues.append(CodeIssue(
                issue_type='high_complexity',
                severity=severity,
                file_path=entity.file_path,
                line_number=entity.line_start,
                entity_name=entity.entity_name,
                description=f"Function has cyclomatic complexity of {entity.complexity_score}",
                ai_recommendation=f"Consider breaking '{entity.entity_name}' into smaller functions. High complexity makes code harder to test and maintain.",
                fix_complexity='moderate' if severity == 'medium' else 'complex'
            ))
            
        # Check function length
        function_length = entity.line_end - entity.line_start + 1
        if function_length > self.FUNCTION_LENGTH_THRESHOLDS['problematic']:
            self.issues.append(CodeIssue(
                issue_type='long_function',
                severity='high',
                file_path=entity.file_path,
                line_number=entity.line_start,
                entity_name=entity.entity_name,
                description=f"Function is {function_length} lines long",
                ai_recommendation=f"Extract logical sections of '{entity.entity_name}' into separate functions for better readability",
                fix_complexity='moderate'
            ))
            
        # Check parameter count
        param_count = len(entity.parameters)
        if param_count > self.PARAMETER_THRESHOLDS['concerning']:
            self.issues.append(CodeIssue(
                issue_type='too_many_parameters',
                severity='medium',
                file_path=entity.file_path,
                line_number=entity.line_start,
                entity_name=entity.entity_name,
                description=f"Function has {param_count} parameters",
                ai_recommendation="Consider using a configuration object or named tuple to group related parameters",
                fix_complexity='simple'
            ))
            
        # Check for missing docstring on public functions
        if not entity.docstring and not entity.entity_name.startswith('_'):
            self.issues.append(CodeIssue(
                issue_type='missing_docstring',
                severity='low',
                file_path=entity.file_path,
                line_number=entity.line_start,
                entity_name=entity.entity_name,
                description="Public function lacks documentation",
                ai_recommendation="Add a docstring explaining purpose, parameters, return value, and any exceptions raised",
                fix_complexity='trivial'
            ))
            
    def _check_class_issues(self, entity: CodeEntity, node: ast.ClassDef, methods: List[str]):
        """Identify class-level issues for AI strategic planning.
        
        Args:
            entity: CodeEntity for the class
            node: Class AST node
            methods: List of method names in class
        """
        method_count = entity.metadata['method_count']
        
        # Check for large classes
        if method_count > 20:
            self.issues.append(CodeIssue(
                issue_type='large_class',
                severity='medium',
                file_path=entity.file_path,
                line_number=entity.line_start,
                entity_name=entity.entity_name,
                description=f"Class has {method_count} methods",
                ai_recommendation="Consider splitting into smaller, more focused classes following Single Responsibility Principle",
                fix_complexity='complex'
            ))
            
        # Check for missing docstring
        if not entity.docstring:
            self.issues.append(CodeIssue(
                issue_type='missing_docstring',
                severity='low',
                file_path=entity.file_path,
                line_number=entity.line_start,
                entity_name=entity.entity_name,
                description="Class lacks documentation",
                ai_recommendation="Add class docstring explaining purpose, usage, and key methods",
                fix_complexity='trivial'
            ))
            
        # Check for missing __init__
        if not entity.metadata['has_init'] and not entity.metadata['is_dataclass']:
            self.issues.append(CodeIssue(
                issue_type='missing_init',
                severity='low',
                file_path=entity.file_path,
                line_number=entity.line_start,
                entity_name=entity.entity_name,
                description="Class has no __init__ method",
                ai_recommendation="Consider adding __init__ method or using @dataclass decorator",
                fix_complexity='simple',
                metadata={'has_methods': method_count > 0}
            ))
            
    def _calculate_metrics(self, content: str) -> CodeMetrics:
        """Calculate file-level metrics for AI assessment.
        
        Args:
            content: File content
            
        Returns:
            CodeMetrics for strategic assessment
        """
        lines = content.split('\n')
        total_lines = len(lines)
        
        # Count line types
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        in_docstring = False
        docstring_delim = None
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                blank_lines += 1
                continue
                
            # Handle docstrings
            if stripped.startswith('"""') or stripped.startswith("'''"):
                delim = stripped[:3]
                if in_docstring and delim == docstring_delim:
                    in_docstring = False
                    comment_lines += 1
                elif not in_docstring:
                    in_docstring = True
                    docstring_delim = delim
                    comment_lines += 1
                else:
                    comment_lines += 1
            elif in_docstring:
                comment_lines += 1
            elif stripped.startswith('#'):
                comment_lines += 1
            else:
                code_lines += 1
                
        # Calculate complexity metrics
        total_complexity = sum(e.complexity_score for e in self.entities)
        avg_complexity = total_complexity / len(self.entities) if self.entities else 0
        max_complexity = max((e.complexity_score for e in self.entities), default=0)
        
        # Calculate documentation coverage
        documented_entities = sum(1 for e in self.entities if e.docstring)
        doc_coverage = documented_entities / len(self.entities) if self.entities else 0
        
        # Count issues by severity
        issues_by_severity = {
            'low': 0,
            'medium': 0,
            'high': 0,
            'critical': 0
        }
        for issue in self.issues:
            issues_by_severity[issue.severity] = issues_by_severity.get(issue.severity, 0) + 1
            
        return CodeMetrics(
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            total_entities=len(self.entities),
            total_functions=sum(1 for e in self.entities if e.entity_type == 'function'),
            total_classes=sum(1 for e in self.entities if e.entity_type == 'class'),
            average_complexity=avg_complexity,
            max_complexity=max_complexity,
            documentation_coverage=doc_coverage,
            issues_by_severity=issues_by_severity,
            language_specific_metrics={
                'uses_type_hints': any(e.metadata.get('uses_type_hints') for e in self.entities),
                'async_functions': sum(1 for e in self.entities if e.metadata.get('is_async')),
                'dataclasses': sum(1 for e in self.entities if e.metadata.get('is_dataclass')),
                'abstract_classes': sum(1 for e in self.entities if e.metadata.get('is_abstract'))
            }
        )
        
    def _calculate_ast_fingerprint(self, tree: ast.AST) -> str:
        """Calculate fingerprint of AST for change detection.
        
        Args:
            tree: AST to fingerprint
            
        Returns:
            Hex string fingerprint
        """
        # Create a simplified representation of the AST structure
        ast_dump = ast.dump(tree, annotate_fields=False)
        # Remove line numbers and other volatile data
        ast_structure = ''.join(c for c in ast_dump if c.isalnum() or c in '(),')
        return hashlib.sha256(ast_structure.encode()).hexdigest()[:16]
        
    def _extract_function_dependencies(self, node: ast.AST) -> List[str]:
        """Extract what a function depends on.
        
        Args:
            node: Function AST node
            
        Returns:
            List of dependencies
        """
        dependencies = set()
        
        class DependencyVisitor(ast.NodeVisitor):
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    dependencies.add(node.id)
                    
            def visit_Attribute(self, node):
                if isinstance(node.value, ast.Name):
                    dependencies.add(node.value.id)
                    
        visitor = DependencyVisitor()
        visitor.visit(node)
        
        # Filter out built-ins and parameters
        builtins = set(dir(__builtins__))
        params = {arg.arg for arg in node.args.args} if hasattr(node, 'args') else set()
        
        return list(dependencies - builtins - params)[:10]  # Limit to 10 most relevant
        
    def _has_return(self, node: ast.AST) -> bool:
        """Check if function has explicit return."""
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value is not None:
                return True
        return False
        
    def _has_yield(self, node: ast.AST) -> bool:
        """Check if function is a generator."""
        for child in ast.walk(node):
            if isinstance(child, (ast.Yield, ast.YieldFrom)):
                return True
        return False
        
    def _has_type_hints(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> bool:
        """Check if function uses type hints."""
        # Check return type
        if node.returns:
            return True
        # Check parameter types
        for arg in node.args.args:
            if arg.annotation:
                return True
        return False
        
    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Extract readable decorator name."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
            return decorator.func.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_name(decorator.value)}.{decorator.attr}"
        return 'unknown_decorator'
        
    def _get_name(self, node: ast.AST) -> str:
        """Extract name from various AST node types."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return 'unknown'
        
    def _create_limited_analysis(self, file_path: Path, reason: str) -> AnalysisResult:
        """Create limited analysis for files that exceed resource limits.
        
        Provides basic metrics without full AST analysis.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Basic line counting
            total_lines = len(lines)
            code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
            
            return AnalysisResult(
                file_path=str(file_path),
                language='python',
                analysis_timestamp=datetime.now(),
                entities=[],
                issues=[
                    CodeIssue(
                        issue_type='analysis_limited',
                        severity='medium',
                        file_path=str(file_path),
                        line_number=1,
                        entity_name='file',
                        description=f"Limited analysis: {reason}",
                        ai_recommendation="Consider breaking this file into smaller modules",
                        fix_complexity='moderate',
                        metadata={'reason': reason, 'file_size': file_path.stat().st_size}
                    )
                ],
                metrics=CodeMetrics(
                    total_lines=total_lines,
                    code_lines=code_lines,
                    documentation_coverage=0.0,
                    language_specific_metrics={'analysis_limited': True}
                ),
                analysis_metadata={
                    'analyzer': 'PythonAnalyzer',
                    'version': '1.0',
                    'ast_parse_success': False,
                    'limitation_reason': reason
                }
            )
        except Exception as e:
            return self._create_error_result(file_path, str(e))
    
    def _create_error_result(self, file_path: Path, error_message: str) -> AnalysisResult:
        """Create result for files that couldn't be parsed.
        
        Still provides value to AI by indicating the issue.
        """
        return AnalysisResult(
            file_path=str(file_path),
            language='python',
            analysis_timestamp=datetime.now(),
            entities=[],
            issues=[
                CodeIssue(
                    issue_type='parse_error',
                    severity='critical',
                    file_path=str(file_path),
                    line_number=1,
                    entity_name='file',
                    description=error_message,
                    ai_recommendation="Fix syntax errors before deeper analysis can proceed",
                    fix_complexity='varies'
                )
            ],
            metrics=CodeMetrics(),
            analysis_metadata={
                'analyzer': 'PythonAnalyzer',
                'version': '1.0',
                'ast_parse_success': False,
                'error': error_message
            }
        )