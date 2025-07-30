# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.
"""
DOX dataset module for document extraction tasks.

This module contains adapters and metrics for the DOX benchmark.
"""

from llama_llama_prompt_ops.datasets.dox.adapter import DoxAdapter
from llama_llama_prompt_ops.datasets.dox.metric import DoxMetric

__all__ = ["DoxAdapter", "DoxMetric"]
