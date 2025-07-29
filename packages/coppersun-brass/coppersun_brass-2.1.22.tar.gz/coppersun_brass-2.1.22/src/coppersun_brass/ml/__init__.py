
# 🩸 BLOOD OATH: ML DEPENDENCY CONFIGURATION 🩸
# =============================================
#
# This configuration MUST NOT CHANGE without running test_ml_dependencies_forever.py
#
# NEVER ADD TO CORE DEPENDENCIES:
# - onnxruntime>=1.16    (500MB+ download)
# - tokenizers>=0.14     (50MB+ download) 
# - numpy>=1.24          (20MB+ download)
#
# The 266KB ML architecture works with:
# - Pure Python pattern matching (fallback)
# - Lightweight 266KB pre-trained models (when available)
# - NO heavy dependencies in core install
#
# IF YOU VIOLATE THIS:
# - Install script will break (timeout/failure)
# - Users get 500MB+ downloads for basic install
# - Production deployment fails
#
# 🩸 BLOOD OATH SIGNED: July 2, 2025 🩸

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