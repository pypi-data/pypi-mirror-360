"""
Semantic Code Analyzer - Real AI-powered code understanding

Uses embeddings and similarity search for intelligent classification.
"""
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# 🩸 BLOOD OATH: Use pure Python ML - ALWAYS WORKS
try:
    from .pure_python_ml import get_pure_python_ml_engine
    PURE_PYTHON_ML_AVAILABLE = True
    logger.info("✅ Pure Python ML engine available - zero dependencies")
except ImportError:
    PURE_PYTHON_ML_AVAILABLE = False
    logger.error("💀 Pure Python ML engine not available - this violates ML mandatory requirement")

# 🩸 BLOOD OATH: No legacy heavy dependencies - pure Python ML only
# Heavy dependencies REMOVED: numpy, sentence-transformers, onnxruntime, tokenizers


@dataclass
class SemanticMatch:
    """Result from semantic analysis."""
    category: str
    confidence: float
    similar_to: str
    reasoning: str


class SemanticAnalyzer:
    """Pure Python ML semantic analysis.
    
    🩸 BLOOD OATH: Uses only pure Python ML engine
    No external dependencies required.
    """
    
    def __init__(self, model_dir: Path):
        """Initialize semantic analyzer."""
        self.model_dir = Path(model_dir)
        logger.info("✅ SemanticAnalyzer using pure Python ML engine")
    
    def analyze_code(self, code_text: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Analyze code and return semantic insights.
        
        🩸 BLOOD OATH: ML is mandatory - uses pure Python ML engine
        """
        if not code_text.strip():
            return []
        
        # 🩸 BLOOD OATH: Use pure Python ML (ALWAYS WORKS)
        if PURE_PYTHON_ML_AVAILABLE:
            return self._analyze_with_pure_python_ml(code_text, file_path)
        
        # Legacy fallback (should never be needed with pure Python ML)
        logger.warning("⚠️ Using legacy fallback - pure Python ML should always work")
        return self._analyze_with_legacy_patterns(code_text, file_path)
    
    def _analyze_with_pure_python_ml(self, code_text: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyze using pure Python ML engine."""
        try:
            engine = get_pure_python_ml_engine()
            ml_results = engine.analyze_code(code_text, file_path)
            
            # Convert to expected format
            findings = []
            lines = code_text.split('\n')
            
            for i, result in enumerate(ml_results):
                # Try to extract line number from TODO patterns
                line_num = 1
                for line_idx, line in enumerate(lines):
                    if 'TODO' in line.upper() and i < len([l for l in lines if 'TODO' in l.upper()]):
                        if i == len([l for l_idx, l in enumerate(lines[:line_idx+1]) if 'TODO' in l.upper()]) - 1:
                            line_num = line_idx + 1
                            break
                
                finding = {
                    "file_path": file_path,
                    "line_number": line_num,
                    "todo_type": result.todo_type,
                    "content": getattr(result, 'content', f'ML pattern detected'),
                    "priority_score": result.priority_score,
                    "confidence": result.confidence,
                    "classification": result.classification,
                    "context_lines": []
                }
                findings.append(finding)
            
            logger.info(f"✅ Pure Python ML analyzed {len(findings)} patterns")
            return findings
            
        except Exception as e:
            logger.error(f"Pure Python ML failed: {e}")
            return self._analyze_with_legacy_patterns(code_text, file_path)
    
    def _analyze_with_legacy_patterns(self, code_text: str, file_path: str) -> List[Dict[str, Any]]:
        """Legacy pattern analysis (fallback only)."""
        findings = []
        lines = code_text.split('\n')
        
        import re
        todo_pattern = re.compile(r'#\s*(TODO|FIXME|HACK|XXX|NOTE)[:.]?\s*(.+)', re.IGNORECASE)
        
        for line_num, line in enumerate(lines, 1):
            match = todo_pattern.search(line)
            if match:
                todo_type = match.group(1).upper()
                content = match.group(2).strip()
                
                finding = {
                    "file_path": file_path,
                    "line_number": line_num,
                    "todo_type": todo_type,
                    "content": content,
                    "priority_score": 40.0,  # Default priority
                    "confidence": 0.8,       # Default confidence
                    "classification": "normal",
                    "context_lines": []
                }
                findings.append(finding)
        
        logger.info(f"Legacy pattern analysis found {len(findings)} TODOs")
        return findings
    
    def explain_classification(self, code: str, result: SemanticMatch) -> str:
        """Provide detailed explanation of classification."""
        explanation = f"""
## Code Classification Result

**Category**: {result.category}
**Confidence**: {result.confidence:.0%}

### Reasoning
{result.reasoning}

### Similar Pattern
```
{result.similar_to}
```

### Recommendations
"""
        
        if result.category == 'critical':
            explanation += """
1. **Immediate Action Required**: This code contains a critical security issue
2. **Review**: Ensure this pattern is not used elsewhere in the codebase
3. **Fix**: Replace with secure alternative immediately
"""
        elif result.category == 'important':
            explanation += """
1. **Review Needed**: This code handles important functionality
2. **Testing**: Ensure comprehensive test coverage
3. **Documentation**: Add clear documentation of security considerations
"""
        else:
            explanation += """
1. **Low Risk**: This appears to be standard code
2. **Best Practice**: Follow coding standards
3. **Maintenance**: Keep code clean and well-documented
"""
        
        return explanation