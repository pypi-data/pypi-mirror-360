
# 🩸 BLOOD OATH: GRADUATED PERMISSION DEPENDENCY SYSTEM 🩸
# ========================================================
#
# AMENDMENT: July 6, 2025 - Graduated Permission System Implemented
# This system protects against heavy dependencies while allowing
# reasoned discussion for medium-weight packages.
#
# TIER 1: FORBIDDEN DEPENDENCIES (NEVER ALLOWED - >50MB):
# - onnxruntime, torch, tensorflow (500MB+ ML frameworks)
# - scikit-learn, pandas, scipy (50-100MB+ data science)
#
# TIER 2: RESTRICTED DEPENDENCIES (REQUIRE APPROVAL - 5-50MB):
# - numpy, sqlalchemy, tokenizers, transformers, opencv-python
# - pillow, matplotlib, plotly (eliminated but can be reconsidered)
#
# TIER 3: APPROVED LIGHTWEIGHT DEPENDENCIES (<5MB):
# - Pure Python ML architecture (2.5MB)
# - Lightweight pattern matching and analysis
# - NO heavy dependencies in core install
#
# APPROVAL PROCESS FOR TIER 2:
# 1. Present specific use case and necessity
# 2. Document alternatives tried and why they failed  
# 3. Analyze size impact and performance implications
# 4. Provide fallback/removal strategy
# 5. Get explicit approval with review date
#
# The graduated system ensures:
# - <10MB package size maintained  
# - Reasoned decisions for legitimate needs
# - Protection against massive dependency bloat
# - Audit trail for all dependency decisions
#
# 🩸 BLOOD OATH AMENDED: July 6, 2025 (Graduated Permission System) 🩸

"""Copper Alloy Brass ML components for efficient code classification."""

from .quick_filter import QuickHeuristicFilter, QuickResult
from .efficient_classifier import EfficientMLClassifier
from .ml_pipeline import MLPipeline
from .semantic_analyzer import SemanticAnalyzer, SemanticMatch

__all__ = [
    'QuickHeuristicFilter',
    'QuickResult',
    'EfficientMLClassifier', 
    'MLPipeline',
    'SemanticAnalyzer',
    'SemanticMatch'
]