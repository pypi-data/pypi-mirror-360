# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.
"""
Adapter for the DOX delivery documents dataset.
"""

from typing import Dict, List, Any
from llama_llama_prompt_ops.core.datasets import DatasetAdapter


class DoxAdapter(DatasetAdapter):
    """Adapter for the DOX delivery documents dataset."""
    
    def __init__(self, dataset_path: str, use_template: bool = True, **kwargs):
        """
        Initialize the DOX adapter.
        
        Args:
            dataset_path: Path to the dataset file
            use_template: Whether to format questions using the DOX template
        """
        super().__init__(dataset_path)
        self.use_template = use_template
    
    def adapt(self) -> List[Dict[str, Any]]:
        """
        Transform DOX dataset format into standardized format.
        
        Returns:
            List of standardized examples
        """
        data = self.load_raw_data()
        standardized_data = []
        
        for doc in data:
            if self.use_template:
                question = self._format_question(doc)
            else:
                format_instructions = doc["fields"]["format_instructions"]
                page = doc["fields"]["page"]
                question = f"Format instructions: {format_instructions}\n\nDocument: {page}"
                
            standardized_data.append({
                "inputs": {
                    "question": question
                },
                "outputs": {
                    "answer": doc["answer"]
                },
                "metadata": {
                    "ground_truth": doc["answer"]
                }
            })
            
        return standardized_data
    
    def _format_question(self, doc: Dict[str, Any]) -> str:
        """
        Format a question using the DOX template.
        
        Args:
            doc: Document to format
            
        Returns:
            Formatted question
        """
        prompt_template = """You are a warehouse manager receiving a delivery. As an expert, you go through the attached delivery note and carefully extract the data that you require to receive the shipped goods and process them in your ERP system. So it is important to focus on the actually received goods and quantities.
        
        The document may be in English, German or any other language. Some of the fields that you need may be indicated by abbreviations in the language of the document. It is important that you carefully extract the information and that you only retrieve information actually on the document. If you have any doubts on a field, skip the field.
        Format instructions: {format_instructions}
        Return date fields in YYYY-MM-DD format.
        For country and currency use ISO format.
        Return missing values as empty string.
        Always return valid json and don't wrap your response in backticks!
        
        Here is the document: {page}
        """
        
        format_instructions = doc["fields"]["format_instructions"]
        page = doc["fields"]["page"]
        
        return prompt_template.format(
            format_instructions=format_instructions, 
            page=page
        )
