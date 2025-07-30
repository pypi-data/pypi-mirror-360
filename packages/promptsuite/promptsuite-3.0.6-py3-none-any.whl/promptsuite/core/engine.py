"""
PromptSuiteEngine: A library for generating multi-prompt datasets from single-prompt datasets.

IMPORTANT: PromptSuiteEngine assumes clean input data:
- All DataFrame cells contain simple values (strings, numbers)
- No NaN values (use empty strings instead)
- No nested arrays or complex objects in cells
- All columns exist as specified in the template

If your data doesn't meet these requirements, clean it before passing to PromptSuiteEngine.
"""

import json
import time
from typing import Dict, List, Any, Optional, Callable

import pandas as pd
from tqdm import tqdm

from promptsuite.core.exceptions import (
    InvalidTemplateError, MissingInstructionTemplateError,
    UnsupportedFileFormatError, UnsupportedExportFormatError
)
from promptsuite.core.models import (
    GoldFieldConfig, VariationConfig, VariationContext, FieldVariation
)
from promptsuite.core.template_keys import (
    PROMPT_FORMAT, FEW_SHOT_KEY, INSTRUCTION_VARIATIONS, PROMPT_FORMAT_VARIATIONS
)
from promptsuite.core.template_parser import TemplateParser
from promptsuite.generation import VariationGenerator, PromptBuilder, FewShotHandler
from promptsuite.shared.constants import GenerationDefaults


class PromptSuiteEngine:
    """
    Main class for generating prompt variations based on dictionary templates.
    
    Template format:
    {
        "instruction": "Process the following input:\n",
        "instruction variations": ["paraphrase", "surface"],
        "prompt format": "{input}\nOutput: {output}",
        "prompt format variations": ["paraphrase", "surface"],
        "gold": "output",  # Name of the column containing the correct output/label
        "few_shot": {
            "count": 2,
            "format": "same_examples__no_variations",  # 'same_examples__no_variations', 'same_examples__synchronized_order_variations', 'different_examples__same_shuffling_order_across_rows', or 'different_examples__different_order_per_variation'
            "split": "train"    # or "test" or "all"
        },
        "input": ["surface"]
    }
    """

    def __init__(self, max_variations_per_row: Optional[int] = GenerationDefaults.MAX_VARIATIONS_PER_ROW):
        """Initialize PromptSuiteEngine with maximum variations limit."""
        self.max_variations_per_row = max_variations_per_row
        self.template_parser = TemplateParser()

        # Initialize the new refactored components
        self.variation_generator = VariationGenerator()
        self.prompt_builder = PromptBuilder()
        self.few_shot_handler = FewShotHandler()

    def generate_variations(
            self,
            template: dict,
            data: pd.DataFrame,
            variations_per_field: int = GenerationDefaults.VARIATIONS_PER_FIELD,
            api_key: str = None,
            seed: Optional[int] = None,
            progress_callback: Optional[Callable] = None,
            max_rows: Optional[int] = None,
            model_name: Optional[str] = None,
            api_platform: Optional[str] = None,
            **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate prompt variations based on dictionary template and data.
        
        Args:
            template: Dictionary template with field configurations
            data: DataFrame with the data
            variations_per_field: Number of variations per field
            api_key: API key for services that require it
            seed: Random seed for reproducibility
            progress_callback: Optional callback function for progress updates
                              Should accept (row_idx, total_rows, variations_this_row, total_variations, eta)
            max_rows: Optional maximum number of rows to process
        
        Returns:
            List of generated variations
        """
        # Validate template
        is_valid, errors = self.template_parser.validate_template(template)
        if not is_valid:
            raise InvalidTemplateError(errors, template)

        # Load data if needed
        if isinstance(data, str):
            data = self._load_data(data)
        else:
            # Even for DataFrames passed directly, check for string lists
            data = self._convert_string_lists_to_lists(data)

        # Parse template
        fields = self.template_parser.parse(template)
        variation_fields = self.template_parser.get_variation_fields()
        few_shot_fields = self.template_parser.get_few_shot_fields()
        enumerate_fields = self.template_parser.get_enumerate_fields()



        # Create configuration objects
        gold_config = GoldFieldConfig.from_template(template.get('gold', None))
        variation_config = VariationConfig(
            variations_per_field=variations_per_field,
            api_key=api_key,
            max_variations_per_row=self.max_variations_per_row,
            seed=seed,
            model_name=model_name,
            api_platform=api_platform
        )
        instruction = self.template_parser.get_instruction()

        # Get prompt_format template from user - required
        prompt_format = self.template_parser.get_prompt_format()
        if not prompt_format:
            raise MissingInstructionTemplateError()

        # Validate gold field requirement
        self.few_shot_handler.validate_gold_field_requirement(prompt_format, gold_config.field, few_shot_fields)

        # PRE-GENERATE instruction and prompt format variations (shared across all rows)
        # This avoids running the same augmenters (like paraphrase) multiple times
        pre_generated_variations = {}
        
        # Generate instruction variations once
        if INSTRUCTION_VARIATIONS in variation_fields and variation_fields[INSTRUCTION_VARIATIONS]:
            print(f"🔄 Pre-generating instruction variations ({len(variation_fields[INSTRUCTION_VARIATIONS])} types)...")
            instruction_variations = self.variation_generator.generate_instruction_variations(
                instruction, variation_fields, variation_config
            )
            pre_generated_variations[INSTRUCTION_VARIATIONS] = [
                FieldVariation(data=var, gold_update=None) for var in instruction_variations
            ]
            print(f"✅ Generated {len(instruction_variations)} instruction variations")
        else:
            pre_generated_variations[INSTRUCTION_VARIATIONS] = [
                FieldVariation(data=instruction, gold_update=None)
            ]

        # Generate prompt format variations once
        if PROMPT_FORMAT_VARIATIONS in variation_fields and variation_fields[PROMPT_FORMAT_VARIATIONS]:
            print(f"🔄 Pre-generating prompt format variations ({len(variation_fields[PROMPT_FORMAT_VARIATIONS])} types)...")
            prompt_format_variations = self.variation_generator.generate_prompt_format_variations(
                prompt_format, variation_fields, variation_config
            )
            pre_generated_variations[PROMPT_FORMAT_VARIATIONS] = [
                FieldVariation(data=var, gold_update=None) for var in prompt_format_variations
            ]
            print(f"✅ Generated {len(prompt_format_variations)} prompt format variations")
        else:
            pre_generated_variations[PROMPT_FORMAT_VARIATIONS] = [
                FieldVariation(data=prompt_format, gold_update=None)
            ]

        all_variations = []

        # Filter data by split if few-shot split is configured
        target_split = None
        if few_shot_fields:
            target_split = few_shot_fields[0].few_shot_split
            print(f"🎯 Filtering data to generate variations for rows that are NOT from '{target_split}' split")
        
        # Filter data for generation based on target split
        generation_data = self._filter_data_by_split(data, target_split)
        
        # Apply max_rows filter
        if max_rows is not None and len(generation_data) > max_rows:
            generation_data = generation_data.iloc[:max_rows]
            print(f"📊 Limited to first {len(generation_data)} rows after split filtering")
        
        # For each data row (only from the target split)
        start_time = time.time()
        total_rows = len(generation_data)
        
        with tqdm(enumerate(generation_data.iterrows()), desc="Generating variations", total=total_rows) as pbar:
            for pbar_row_idx, (row_idx, row) in pbar:
                row_start_time = time.time()
                
                # Generate variations for row-specific fields only (not instruction/prompt format)
                field_variations = self.variation_generator.generate_row_specific_field_variations(
                    variation_fields,
                    row,
                    variation_config,
                    gold_config,
                    pre_generated_variations,  # Pass pre-generated variations
                    template  # Pass template for few-shot handling
                )

                # Create variation context
                variation_context = VariationContext(
                    row_data=row,
                    row_index=row_idx,
                    template=template,
                    field_variations=field_variations,
                    gold_config=gold_config,
                    variation_config=variation_config,
                    data=data  # Pass full data for few-shot examples
                )

                # Generate row variations with limit for efficiency
                row_variations = self.few_shot_handler.create_row_variations(
                    variation_context,
                    few_shot_fields[0] if few_shot_fields else None,
                    self.max_variations_per_row,  # Pass the limit directly
                    self.prompt_builder
                )

                all_variations.extend(row_variations)
                
                # Update progress bar with detailed information
                row_time = time.time() - row_start_time
                variations_this_row = len(row_variations)
                total_variations_so_far = len(all_variations)
                avg_time_per_row = (time.time() - start_time) / (pbar_row_idx + 1)
                eta = avg_time_per_row * (total_rows - pbar_row_idx - 1)
                
                pbar.set_postfix({
                    'row': f"{pbar_row_idx + 1}/{total_rows}",
                    'variations': f"{variations_this_row}",
                    'total': f"{total_variations_so_far}",
                    'avg_time': f"{avg_time_per_row:.2f}s",
                    'eta': f"{eta:.1f}s"
                })
                
                if progress_callback:
                    progress_callback(row_idx, total_rows, variations_this_row, total_variations_so_far, eta)

        return all_variations

    def _load_data(self, data_path: str) -> pd.DataFrame:
        """Load data from file path and automatically convert string representations of lists."""
        if data_path.endswith('.csv'):
            df = pd.read_csv(data_path)
        elif data_path.endswith('.json'):
            with open(data_path, 'r') as f:
                json_data = json.load(f)
            df = pd.DataFrame(json_data)
        else:
            raise UnsupportedFileFormatError(data_path, ['.csv', '.json'])

        # Auto-convert string representations of lists to actual lists
        return self._convert_string_lists_to_lists(df)

    def _convert_string_lists_to_lists(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert string representations of lists back to actual Python lists.
        
        This handles cases where data was saved/loaded from CSV/JSON and 
        list columns became strings like "['item1', 'item2', 'item3']"
        """
        import ast
        import warnings
        def safe_eval(value):
            """Try to evaluate a string as a Python literal, suppressing SyntaxWarnings."""
            if isinstance(value, str):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", SyntaxWarning)
                    try:
                        return ast.literal_eval(value)
                    except (ValueError, SyntaxError):
                        return value
            return value

        df_copy = df.copy()

        # Apply safe_eval to all columns - it will only convert what it can
        for column in df_copy.columns:
            original_values = df_copy[column].copy()
            df_copy[column] = df_copy[column].apply(safe_eval)

            # Check if anything actually changed (meaning we converted some values)
            if not df_copy[column].equals(original_values):
                print(f"✅ Converted some values in column '{column}' from strings to Python objects")

        return df_copy

    def get_stats(self, variations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about generated variations."""
        if not variations:
            return {}

        row_counts = {}
        for var in variations:
            row_idx = var.get('original_row_index', 0)
            row_counts[row_idx] = row_counts.get(row_idx, 0) + 1

        # Get field info from template config
        template_config = variations[0].get('template_config', {})
        field_count = len([k for k in template_config.keys() if k not in [FEW_SHOT_KEY, PROMPT_FORMAT]])
        has_few_shot = FEW_SHOT_KEY in template_config
        has_custom_prompt_format = PROMPT_FORMAT in template_config

        return {
            'total_variations': len(variations),
            'original_rows': len(row_counts),
            'avg_variations_per_row': sum(row_counts.values()) / len(row_counts) if row_counts else 0,
            'template_fields': field_count,
            'has_few_shot': has_few_shot,
            'has_custom_prompt_format': has_custom_prompt_format,
            'min_variations_per_row': min(row_counts.values()) if row_counts else 0,
            'max_variations_per_row_per_row': max(row_counts.values()) if row_counts else 0,
        }

    def parse_template(self, template: dict) -> Dict[str, List[str]]:
        """Parse template to extract fields and their variation types."""
        self.template_parser.parse(template)
        return self.template_parser.get_variation_fields()

    @staticmethod
    def _prepare_variations_for_conversation_export(variations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance variations with conversation field to match API format.
        This is a shared utility function to ensure consistent conversation JSON output.
        
        Args:
            variations: List of generated variations
            
        Returns:
            List of variations with conversation field added and extra fields removed
        """
        enhanced_variations = []

        for variation in variations:
            # Create a new variation with reorganized structure
            enhanced_var = {
                'original_row_index': variation.get('original_row_index', 0),
                'variation_count': variation.get('variation_count', 1),
                'prompt': variation.get('prompt', ''),
                'conversation': None,  # Will be set below
                'gold_updates': variation.get('gold_updates'),
                'original_row_data': variation.get('original_row_data', {}),  # NEW: Include original data
                'configuration': {
                    'template_config': variation.get('template_config', {}),
                    'field_values': variation.get('field_values', {})
                }
            }

            # Add conversation field if not already present
            if 'conversation' in variation and variation['conversation']:
                enhanced_var['conversation'] = variation['conversation']
            else:
                # Build conversation from prompt
                prompt = variation.get('prompt', '')

                # Split prompt into conversation parts if it contains few-shot examples
                parts = prompt.split('\n\n')
                conversation = []

                for i, part in enumerate(parts):
                    part = part.strip()
                    if not part:
                        continue

                    # Check if this is the last part (incomplete question)
                    if i == len(parts) - 1:
                        # Last part - this is the question without answer
                        conversation.append({
                            "role": "user",
                            "content": part
                        })
                    else:
                        # This is a complete Q&A pair
                        # Split by the last occurrence of newline to separate question and answer
                        lines = part.split('\n')
                        if len(lines) >= 2:
                            # Assume the last line is the answer
                            answer = lines[-1].strip()
                            question = '\n'.join(lines[:-1]).strip()

                            conversation.append({
                                "role": "user",
                                "content": question
                            })
                            conversation.append({
                                "role": "assistant",
                                "content": answer
                            })
                        else:
                            # Single line - treat as user message
                            conversation.append({
                                "role": "user",
                                "content": part
                            })

                enhanced_var['conversation'] = conversation

            enhanced_variations.append(enhanced_var)

        return enhanced_variations

    def save_variations(self, variations: List[Dict[str, Any]], output_path: str, format: str = "json"):
        """Save variations to file."""
        if format == "json":
            # Prepare variations to conversation format before dumping to JSON
            conversation_variations = PromptSuiteEngine._prepare_variations_for_conversation_export(variations)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_variations, f, indent=2, ensure_ascii=False)

        elif format == "csv":
            flattened = []
            for var in variations:
                flat_var = {
                    'prompt': var['prompt'],
                    'original_row_index': var.get('original_row_index', ''),
                    'variation_count': var.get('variation_count', ''),
                }
                # Add original row data with 'original_' prefix
                for key, value in var.get('original_row_data', {}).items():
                    flat_var[f'original_{key}'] = value
                # Add field values with 'field_' prefix
                for key, value in var.get('field_values', {}).items():
                    flat_var[f'field_{key}'] = value
                flattened.append(flat_var)

            df = pd.DataFrame(flattened)
            df.to_csv(output_path, index=False, encoding='utf-8')

        elif format == "txt":
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, var in enumerate(variations):
                    f.write(f"=== Variation {i + 1} ===\n")
                    f.write(var['prompt'])
                    f.write("\n\n")

        else:
            raise UnsupportedExportFormatError(format, ["json", "csv", "txt"])



    def _filter_data_by_split(self, data: pd.DataFrame, target_split: Optional[str]) -> pd.DataFrame:
        """
        Filter data by split for generation.
        
        Args:
            data: Full dataset
            target_split: Target split ('train', 'test', or None for all)
            
        Returns:
            Filtered DataFrame containing only rows from the target split
        """
        if target_split is None:
            return data
        
        if 'split' not in data.columns:
            print(f"⚠️ Warning: No 'split' column found in data, using all data for generation")
            return data
        
        filtered_data = data[data['split'] != target_split].copy()
        print(f"📊 Filtered data: {len(filtered_data)} rows NOT from '{target_split}' split (out of {len(data)} total)")
        
        return filtered_data
