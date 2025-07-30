# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.
"""
Adapter for the Joule help documentation dataset.
"""

from typing import Dict, List, Any
from llama_llama_prompt_ops.core.datasets import DatasetAdapter


class JouleAdapter(DatasetAdapter):
    """Adapter for the Joule help documentation dataset."""
    
    def adapt(self) -> List[Dict[str, Any]]:
        """
        Transform Joule dataset format into standardized format.
        
        Returns:
            List of standardized examples
        """
        data = self.load_raw_data()
        return [
            {
                "inputs": {
                    "question": doc["fields"]["question"],
                    "context": doc["fields"]["context"]
                },
                "outputs": {
                    "answer": doc["answer"]
                }
            }
            for doc in data
        ]
