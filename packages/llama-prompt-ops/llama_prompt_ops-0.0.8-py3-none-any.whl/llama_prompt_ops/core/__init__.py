# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.
"""
Core module for prompt migration and optimization.

This module provides the main functionality for migrating and optimizing prompts.
"""

from .evaluation import (
    Evaluator,
    StatisticalEvaluator,
    StatisticalResults,
    create_evaluator,
)
from .metrics import ExactMatchMetric, MetricBase
from .migrator import PromptMigrator
from .prompt_strategies import BaseStrategy, BasicOptimizationStrategy

__all__ = [
    "PromptMigrator",
    "BaseStrategy",
    "BasicOptimizationStrategy",
    "MetricBase",
    "ExactMatchMetric",
    "Evaluator",
    "StatisticalEvaluator",
    "StatisticalResults",
    "create_evaluator",
]
