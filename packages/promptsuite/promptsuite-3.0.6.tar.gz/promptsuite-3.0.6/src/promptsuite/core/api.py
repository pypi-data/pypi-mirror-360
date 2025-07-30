"""
PromptSuite Python API for programmatic usage.

This module provides a high-level Python API for PromptSuite that allows users
to generate prompt variations programmatically without the Streamlit UI.
"""

import json
import os
import random
import time
from pathlib import Path
from typing import Dict, List, Any, Union, Optional, Callable

import pandas as pd
# Try to load environment variables
from dotenv import load_dotenv

from promptsuite.core.exceptions import (
    DatasetLoadError, FileNotFoundError, DataParsingError, InvalidDataFormatError,
    InvalidTemplateError, InvalidConfigurationError, UnknownConfigurationError,
    DataNotLoadedError, MissingTemplateError, NoResultsToExportError,
    UnsupportedExportFormatError, ExportWriteError, PromptSuiteEngineError
)
from promptsuite.core.exceptions import GenerationError
from promptsuite.core.template_keys import (
    PROMPT_FORMAT, GOLD_KEY, FEW_SHOT_KEY,
    PARAPHRASE_WITH_LLM
)
from promptsuite.core.template_parser import TemplateParser
from promptsuite.shared.constants import GenerationDefaults, PLATFORMS_API_KEYS_VARS
from .engine import PromptSuiteEngine

load_dotenv()


class PromptSuite:
    """
    High-level interface for PromptSuiteEngine - the easy way to generate prompt variations.
    
    This class provides a clean, step-by-step interface to generate prompt variations
    using the same functionality as the Streamlit web interface.
    
    Example usage:
#            >>> from promptsuite import PromptSuite
#        >>>
#        >>> # Initialize
#        >>> ps = PromptSuite()
#        >>>
#        >>> # Load data
#        >>> ps.load_dataset("squad", split="train")
#        >>>
#        >>> # Configure template
#        >>> template = {
#        >>>     INSTRUCTION_TEMPLATE_KEY: 'Answer: {question}\nAnswer: {answer}',
#        >>>     INSTRUCTION_KEY: [PARAPHRASE_WITH_LLM],
#        >>>     QUESTION_KEY: [REWORDING],
#        >>>     GOLD_KEY: {
#        >>>         'field': 'answer',
#        >>>         'type': 'value'
#        >>>     }
#        >>> }
#        >>> ps.set_template(template)
#        >>>
#        >>> # Configure and generate
#        >>> ps.configure(max_rows=10, variations_per_field=3)
#        >>> variations = sp.generate(verbose=True)
#        >>>
#        >>> # Export results
#        >>> ps.export("output.json", format="json")
#    """

    def __init__(self):
        """Initialize the PromptSuite."""
        self.sp = None
        self.data = None
        self.template = None
        self.config = {
            'max_rows': GenerationDefaults.MAX_ROWS,
            'variations_per_field': GenerationDefaults.VARIATIONS_PER_FIELD,
            'max_variations_per_row': GenerationDefaults.MAX_VARIATIONS_PER_ROW,
            'random_seed': GenerationDefaults.RANDOM_SEED,
            'api_platform': GenerationDefaults.API_PLATFORM,
            'api_key': None,  # Will be set based on platform
            'model_name': GenerationDefaults.MODEL_NAME
        }
        # Set API key based on default platform
        self.config['api_key'] = self._get_api_key_for_platform(self.config['api_platform'])

        self.results = None
        self.stats = None
        self.generation_time = None

    def _get_api_key_for_platform(self, platform: str) -> Optional[str]:
        """Get API key for the specified platform."""
        env_var = PLATFORMS_API_KEYS_VARS.get(platform)
        if env_var:
            return os.getenv(env_var)
        else:
            # Fallback to generic API_KEY
            return os.getenv("API_KEY")

    def load_dataset(self, dataset_name: str, *args, **kwargs) -> None:
        """
        Load data from HuggingFace datasets library.

        Args:
            dataset_name: Name of the HuggingFace dataset
            *args: Positional arguments to pass to datasets.load_dataset()
            **kwargs: Keyword arguments to pass to datasets.load_dataset()

        Raises:
            ImportError: If datasets library is not installed
            ValueError: If dataset cannot be loaded
        """
        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError(
                "HuggingFace datasets library is required for load_dataset(). "
                "Install it with: pip install datasets"
            )

        try:
            dataset = load_dataset(dataset_name, *args, **kwargs)

            # Handle dict of splits
            if isinstance(dataset, dict):
                dfs = []
                for split_name, split_dataset in dataset.items():
                    df = split_dataset.to_pandas()
                    df['split'] = split_name
                    dfs.append(df)
                self.data = pd.concat(dfs, ignore_index=True)
            else:
                self.data = dataset.to_pandas()
            print(f"✅ Loaded {len(self.data)} rows from {dataset_name}")
        except Exception as e:
            raise DatasetLoadError(dataset_name, str(e))

    def load_csv(self, filepath: Union[str, Path], **kwargs) -> None:
        """
        Load data from CSV file.
        
        Args:
            filepath: Path to the CSV file
            **kwargs: Additional arguments to pass to pandas.read_csv()
        
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV cannot be parsed
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(str(filepath), "CSV file")

        try:
            self.data = pd.read_csv(filepath, **kwargs)
            print(f"✅ Loaded {len(self.data)} rows from CSV: {filepath}")
        except Exception as e:
            raise DataParsingError(str(filepath), "CSV", str(e))

    def load_json(self, filepath: Union[str, Path], **kwargs) -> None:
        """
        Load data from JSON file.
        
        Args:
            filepath: Path to the JSON file
            **kwargs: Additional arguments to pass to pandas.read_json()
        
        Raises:
            FileNotFoundError: If JSON file doesn't exist
            ValueError: If JSON cannot be parsed
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(str(filepath), "JSON file")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            if isinstance(json_data, list):
                self.data = pd.DataFrame(json_data)
            elif isinstance(json_data, dict):
                self.data = pd.DataFrame([json_data])
            else:
                raise InvalidDataFormatError("list of objects or single object", type(json_data).__name__,
                                             str(filepath))

            print(f"✅ Loaded {len(self.data)} rows from JSON: {filepath}")
        except Exception as e:
            raise DataParsingError(str(filepath), "JSON", str(e))

    def load_dataframe(self, df: pd.DataFrame) -> None:
        """
        Load data from pandas DataFrame.
        
        Args:
            df: Pandas DataFrame containing the data
        
        Raises:
            ValueError: If df is not a pandas DataFrame
        """
        if not isinstance(df, pd.DataFrame):
            raise InvalidDataFormatError("pandas DataFrame", type(df).__name__)

        self.data = df.copy()
        print(f"✅ Loaded {len(self.data)} rows from DataFrame")

    def set_template(self, template_dict: Dict[str, Any]) -> None:
        """
        Set the template configuration (dictionary format).
        
        Args:
            template_dict: Dictionary template configuration
            
        Example template:
            {
                INSTRUCTION_TEMPLATE_KEY: 'Answer the question: {question}\nAnswer: {answer}',
                INSTRUCTION_KEY: [PARAPHRASE_WITH_LLM],
                QUESTION_KEY: [REWORDING],
                GOLD_KEY: {
                    'field': 'answer',
                    'type': 'value'
                },
                FEW_SHOT_KEY: {
                    'count': 2,
                    'format': 'shared_ordered_first_n',
                    'split': 'all'
                }
            }
        
        Raises:
            ValueError: If template is invalid
        """
        if not isinstance(template_dict, dict):
            raise InvalidDataFormatError("dictionary", type(template_dict).__name__)

        # Validate template using template parser
        parser = TemplateParser()
        is_valid, errors = parser.validate_template(template_dict)

        if not is_valid:
            raise InvalidTemplateError(errors, template_dict)

        self.template = template_dict
        print("✅ Template configuration set successfully")

    def configure(self, **kwargs) -> None:
        """
        Configure generation parameters.
        
        Args:
            max_rows: Maximum rows from data to use (default: None = all rows)
            variations_per_field: Variations per field (default: 3)
            max_variations_per_row: Maximum variations per row (default: None = unlimited)
                          If a row has more variations than this limit, 
                          the same subset of variations will be selected for all rows
            random_seed: Random seed for reproducibility (default: 42)
            api_platform: AI platform (supported: TogetherAI, OpenAI, Anthropic, Google, Cohere) (default: "TogetherAI")
            api_key: API key for paraphrase variations (default: from environment based on platform)
            model_name: LLM model name (default: platform-specific default)
        """
        # Handle platform change specially
        if 'api_platform' in kwargs:
            new_platform = kwargs['api_platform']
            from promptsuite.shared.model_client import get_supported_platforms
            supported_platforms = get_supported_platforms()
            
            if new_platform not in supported_platforms:
                raise InvalidConfigurationError("api_platform", new_platform, supported_platforms)

            self.config['api_platform'] = new_platform
            # Update API key based on new platform (unless explicitly provided)
            if 'api_key' not in kwargs:
                self.config['api_key'] = self._get_api_key_for_platform(new_platform)

        # Handle other parameters
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
            else:
                valid_params = list(self.config.keys())
                raise UnknownConfigurationError(key, valid_params)

        # Set random seed if specified
        if self.config['random_seed'] is not None:
            random.seed(self.config['random_seed'])

        print(f"✅ Configuration updated: {len(kwargs)} parameters")

    def generate(self, verbose: bool = False, progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """
        Generate variations with optional progress logging.
        
        Args:
            verbose: If True, print progress messages
            progress_callback: Optional callback function for progress updates
                              Should accept (row_idx, total_rows, variations_this_row, total_variations, eta)
        
        Returns:
            List of generated variations
        
        Raises:
            ValueError: If data or template not set, or generation fails
        """

        
        # Validate prerequisites
        if self.data is None:
            raise DataNotLoadedError()

        if self.template is None:
            raise MissingTemplateError()

        # Check if paraphrase variations need API key
        if self._needs_api_key() and not self.config['api_key']:
            platform = self.config['api_platform']
            env_var = "TOGETHER_API_KEY" if platform == "TogetherAI" else "OPENAI_API_KEY"
            print(f"⚠️ Warning: Template uses paraphrase variations but no API key found for {platform}.")
            print(f"   Set API key with: sp.configure(api_key='your_key')")
            print(f"   Or set environment variable: {env_var}")
            print(f"   Or change platform with: sp.configure(api_platform='TogetherAI'/'OpenAI')")

        if verbose:
            print("🚀 Starting PromptSuiteEngine generation...")
            print(f"   Using platform: {self.config['api_platform']}")

        start_time = time.time()

        try:
            # Step 1: Initialize
            if verbose:
                print("🔄 Step 1/5: Initializing PromptSuiteEngine...")

            self.sp = PromptSuiteEngine(max_variations_per_row=self.config['max_variations_per_row'])

            # Step 2: Prepare data
            if verbose:
                print(f"📊 Step 2/5: Preparing data... (using first {self.config['max_rows']} rows)")

            # Ensure data types are consistent to avoid pandas array comparison issues
            data_for_engine = self.data.copy()
            for col in data_for_engine.columns:
                if data_for_engine[col].dtype == 'object':
                    # Convert object columns to string to avoid array comparison issues
                    data_for_engine[col] = data_for_engine[col].astype(str)

            # Step 3: Configure parameters
            if verbose:
                print("⚙️ Step 3/5: Configuring generation parameters...")

            # Step 4: Generate variations
            if verbose:
                print("⚡ Step 4/5: Generating variations... (AI is working on variations)")
                print(f"   Processing {len(data_for_engine)} rows...")

            # Create simple progress callback for verbose mode
            def simple_progress_callback(row_idx, total_rows, variations_this_row, total_variations, eta):
                if verbose:
                    print(
                        f"   📊 Row {row_idx + 1}/{total_rows} • Variations: {variations_this_row} • Total: {total_variations}")

            # Use provided callback or simple verbose callback
            final_callback = progress_callback if progress_callback else (simple_progress_callback if verbose else None)

            # Debug - print what we're about to pass
            print(f"🔍 API CALLING ENGINE - About to call sp.generate_variations with:")
            print(f"   model_name: {self.config['model_name']}")
            print(f"   api_platform: {self.config['api_platform']}")
            
            self.results = self.sp.generate_variations(
                template=self.template,
                data=data_for_engine,
                variations_per_field=self.config['variations_per_field'],
                api_key=self.config['api_key'],
                seed=self.config['random_seed'],
                progress_callback=final_callback,
                max_rows=self.config['max_rows'],  # Pass max_rows to engine
                model_name=self.config['model_name'],
                api_platform=self.config['api_platform']
            )

            # Step 5: Compute statistics
            if verbose:
                print("📈 Step 5/5: Computing statistics...")

            self.stats = self.sp.get_stats(self.results)
            self.generation_time = time.time() - start_time

            if verbose:
                print(f"✅ Generated {len(self.results)} variations in {self.generation_time:.1f} seconds")
                print(f"   Average: {len(self.results) / len(data_for_engine):.1f} variations per row")
                print(f"   Speed: {self.generation_time / len(data_for_engine):.2f}s per row")

            return self.results

        except Exception as e:
            # Enhanced error reporting
            error_msg = f"Generation failed: {str(e)}"
            error_context = e.context if isinstance(e, PromptSuiteEngineError) else {}
            if verbose:
                import traceback
                print(f"❌ Error details: {error_msg}")
                print("🔍 Full traceback:")
                traceback.print_exc()
            raise GenerationError(error_msg, "generation", error_context)

    def export(self, filepath: Union[str, Path], format: str = "json") -> None:
        """
        Export results to file.
        
        Args:
            filepath: Output file path
            format: Export format ("json", "csv", "txt")
        
        Raises:
            ValueError: If no results to export or invalid format
        """
        if self.results is None:
            raise NoResultsToExportError()

        if format not in ["json", "csv", "txt"]:
            raise UnsupportedExportFormatError(format, ["json", "csv", "txt"])

        filepath = Path(filepath)

        try:
            self.sp.save_variations(self.results, str(filepath), format=format)
            print(f"✅ Results exported to {filepath} ({format} format)")
        except Exception as e:
            raise ExportWriteError(str(filepath), str(e))

    def get_results(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get generated variations as Python list.
        
        Returns:
            List of variations or None if no results
        """
        return self.results

    def get_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get generation statistics dictionary.
        
        Returns:
            Statistics dictionary or None if no results
        """
        return self.stats

    def _needs_api_key(self) -> bool:
        """Check if template requires an API key for paraphrase variations."""
        if not self.template:
            return False

        # Check if any field has paraphrase variations
        for field_name, variations in self.template.items():
            if field_name in [PROMPT_FORMAT, GOLD_KEY, FEW_SHOT_KEY]:
                continue

            if isinstance(variations, list) and PARAPHRASE_WITH_LLM in variations:
                return True

        return False

    def info(self) -> None:
        """Print current configuration and status information."""
        print("📋 PromptSuite Status:")
        print(f"   Data: {'✅ Loaded' if self.data is not None else '❌ Not loaded'} "
              f"({len(self.data)} rows)" if self.data is not None else "")
        print(f"   Template: {'✅ Set' if self.template is not None else '❌ Not set'}")
        print(f"   Results: {'✅ Generated' if self.results is not None else '❌ Not generated'} "
              f"({len(self.results)} variations)" if self.results is not None else "")

        print("\n⚙️ Current Configuration:")
        for key, value in self.config.items():
            if key == 'api_key' and value:
                print(f"   {key}: {'*' * 10} (hidden)")
            else:
                print(f"   {key}: {value}")

        if self.template:
            print(f"\n📝 Template Fields:")
            for field_name, config in self.template.items():
                if field_name == PROMPT_FORMAT:
                    print(
                        f"   {field_name}: {config[:50]}..." if len(str(config)) > 50 else f"   {field_name}: {config}")
                else:
                    print(f"   {field_name}: {config}")
