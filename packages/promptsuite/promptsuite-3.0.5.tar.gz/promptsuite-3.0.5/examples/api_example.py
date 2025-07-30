#!/usr/bin/env python3
"""
PromptSuite() API Example Script

This script demonstrates how to use the PromptSuite() class for programmatic
generation of prompt variations.
"""

import os

import pandas as pd

from promptsuite import PromptSuite
from promptsuite.core.template_keys import (
    INSTRUCTION, PROMPT_FORMAT, QUESTION_KEY, OPTIONS_KEY, GOLD_KEY,
    PARAPHRASE_WITH_LLM, CONTEXT_VARIATION, SHUFFLE_VARIATION
)
from promptsuite.core.template_keys import (
    PROMPT_FORMAT_VARIATIONS, FEW_SHOT_KEY, CONTEXT_KEY,
    ENUMERATE_VARIATION,
    INSTRUCTION_VARIATIONS, FORMAT_STRUCTURE_VARIATION, TYPOS_AND_NOISE_VARIATION
)


def example_with_sample_data_few_shot():
    # Create instance
    ps = PromptSuite()

    # Load data with at least 4 examples for few-shot
    data = pd.DataFrame({
        'question': [
            'What is 2+2?',
            'What is 5+3?',
            'What is 10-4?',
            'What is 3*3?',
            'What is 20/4?'
        ],
        'answer': ['4', '8', '6', '9', '5']
    })
    ps.load_dataframe(data)

    # Set template with few-shot configuration
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about math.',
        PROMPT_FORMAT: 'Question: {question}\nAnswer: {answer}',
        PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION],  # surface variations
        'gold': 'answer',
        'few_shot': {
            'count': 2,  # Use 2 examples
            'format': 'same_examples__no_variations',  # Same examples for all questions
            'split': 'all'  # Use all data for examples
        }
    }
    ps.set_template(template)

    # Configure and generate
    ps.configure(max_rows=4, variations_per_field=2)
    variations = ps.generate(verbose=True)

    # Display results with few-shot examples
    print(f"\n✅ Generated {len(variations)} variations")
    print("\n" + "=" * 50)

    # Show first few variations to see few-shot in action
    for i, var in enumerate(variations[:12]):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(var['prompt'])
        print("-" * 50)

    # Export results
    ps.export("few_shot_examples.json", format="json")
    print("\n✅ Exported to few_shot_examples.json")

    # Show info
    ps.info()


def example_with_enumerate():
    """Example demonstrating the new enumerate functionality."""

    print("🚀 PromptSuite() API Example with Enumerate")
    print("=" * 50)

    # Initialize the API
    ps = PromptSuite()

    # Create sample data
    sample_data = [
        {
            "question": "What is the capital of France?",
            "options": ["London", "Berlin", "Paris", "Madrid"],
            "answer": 2  # Paris is at index 2
        },
        {
            "question": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "answer": 1  # 4 is at index 1
        },
        {
            "question": "Which planet is closest to the Sun?",
            "options": ["Venus", "Mercury", "Earth", "Mars"],
            "answer": 1  # Mercury is at index 1
        }
    ]

    df = pd.DataFrame(sample_data)

    # Load the data
    print("\n1. Loading data...")
    ps.load_dataframe(df)
    print("📝 Data format: answers are indices (0-based), not text values")

    # Configure template with enumerate
    print("\n2. Setting template with enumerate...")
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
        QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION],
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        },
        ENUMERATE_VARIATION: {
            'field': 'options',  # Which field to enumerate
            'type': '1234'  # Use numbers: 1. 2. 3. 4.
        }
    }

    ps.set_template(template)
    print("✅ Template configured with enumerate field")
    print("   - Will enumerate 'options' field with numbers (1234)")

    # Configure generation parameters
    print("\n3. Configuring generation...")
    ps.configure(
        max_rows=3,
        variations_per_field=2,
        max_variations_per_row=10,
        random_seed=42
    )

    # Show current status
    print("\n4. Current status:")
    ps.info()

    # Generate variations
    print("\n5. Generating variations...")
    variations = ps.generate(verbose=True)

    # Show results
    print(f"\n6. Results: Generated {len(variations)} variations")

    # Display first few variations to see enumerate in action
    for i, variation in enumerate(variations[:7]):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(variation.get('prompt', 'No prompt found'))
        print("-" * 50)

    # Export results
    print("\n8. Exporting results...")
    ps.export("enumerate_example.json", format="json")

    print("\n✅ Enumerate example completed successfully!")


def example_enumerate_types():
    """Example showing different enumerate types."""

    print("\n" + "=" * 50)
    print("🔢 Different Enumerate Types Example")
    print("=" * 50)

    ps = PromptSuite()

    # Simple data
    data = [{
        "question": "Which is correct?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "answer": 0
    }]
    ps.load_dataframe(pd.DataFrame(data))

    # Test different enumerate types
    enumerate_types = [
        ("1234", "Numbers"),
        ("ABCD", "Uppercase letters"),
        ("abcd", "Lowercase letters"),
        ("roman", "Roman numerals")
    ]

    for enum_type, description in enumerate_types:
        print(f"\n--- {description} ({enum_type}) ---")

        template = {
            INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
            PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
            QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION],
            GOLD_KEY: {
                'field': 'answer',
                'type': 'index',
                'options_field': 'options'
            },
            ENUMERATE_VARIATION: {
                'field': 'options',
                'type': enum_type
            }
        }

        ps.set_template(template)
        ps.configure(max_rows=1, variations_per_field=1, max_variations_per_row=1)

        try:
            variations = ps.generate(verbose=False)
            if variations:
                print("Result:")
                print(variations[0].get('prompt', 'No prompt'))
        except Exception as e:
            print(f"Error with {enum_type}: {e}")


def example_with_sample_data():
    """Main example demonstrating the new specialized augmenters."""
    print("🚀 PromptSuite() API Example with New Specialized Augmenters")
    print("=" * 60)

    # Create instance
    ps = PromptSuite()

    # Load data with multiple examples
    data = pd.DataFrame({
        'question': [
            'What is the capital of France?',
            'What is 2+2?',
            # 'Which planet is closest to the Sun?',
            # 'What is the largest mammal?'
        ],
        'options': [
            'London, Berlin, Paris, Madrid',
            '3, 4, 5, 6',
            # 'Venus, Mercury, Earth, Mars',
            # 'Elephant, Blue Whale, Giraffe, Lion'
        ],
        'answer': [2, 1]  # 0-based indices
        # 'answer': [2, 1, 1, 1]  # 0-based indices
    })
    ps.load_dataframe(data)
    print(f"📝 Loaded {len(data)} questions with multiple choice options")

    # Configure template with new specialized augmenters
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
        QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION, TYPOS_AND_NOISE_VARIATION],  # Use both new augmenters
        OPTIONS_KEY: [SHUFFLE_VARIATION, FORMAT_STRUCTURE_VARIATION, ENUMERATE_VARIATION],
        # Format structure + enumerate
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        }
    }
    ps.set_template(template)
    print("✅ Template configured with new specialized augmenters:")
    print("   - FormatStructureAugmenter: Semantic-preserving format changes")
    print("   - TextNoiseAugmenter: Robustness testing with noise injection")
    print("   - Enumerate: Automatic option numbering")

    # Configure and generate
    ps.configure(max_rows=4, variations_per_field=3, max_variations_per_row=20, random_seed=42)
    variations = ps.generate(verbose=True)

    # Display results
    print(f"\n✅ Generated {len(variations)} variations with new augmenters")
    print("\n" + "=" * 50)

    # Show first few variations to see the new augmenters in action
    for i, var in enumerate(variations[:25]):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(var['prompt'])
        print("-" * 50)

    # Export results
    ps.export("new_augmenters_demo.json", format="json")
    print("\n✅ Exported to new_augmenters_demo.json")

    # Show info
    ps.info()


def example_platform_switching():
    """Example showing how to switch between AI platforms."""

    print("\n" + "=" * 50)
    print("🔄 Platform Switching Example - WITH ACTUAL API CALLS")
    print("=" * 50)

    # Initialize API
    ps = PromptSuite()

    # Create simple data
    data = [{"question": "What is AI?", "answer": "Artificial Intelligence"}]
    ps.load_dataframe(pd.DataFrame(data))

    # Simple template with paraphrase (requires API key)
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Question: {question}\nAnswer: {answer}',
        INSTRUCTION_VARIATIONS: [PARAPHRASE_WITH_LLM],
        GOLD_KEY: 'answer'  # Simple format - just the field name
    }
    ps.set_template(template)

    # Test platforms with actual API calls
    platforms_to_test = [
        # ("TogetherAI", "meta-llama/Llama-3.1-8B-Instruct-Turbo"),
        ("OpenAI", "gpt-4o-mini")
    ]

    for i, (platform_name, model_name) in enumerate(platforms_to_test, 1):
        print(f"\n{i}. Testing {platform_name} with {model_name}:")
        print("-" * 40)

        ps.configure(api_platform=platform_name, model_name=model_name, max_rows=1, variations_per_field=2)
        ps.info()

        # Try to generate variations
        print(f"   🚀 Attempting to generate variations with {model_name}...")
        variations = ps.generate(verbose=False)

        if variations:
            print(f"   ✅ SUCCESS: Generated {len(variations)} variations")
            print(f"   📝 Sample variation:")
            print(f"      {variations[0].get('prompt', 'No prompt')[:100]}...")
        else:
            print(f"   ⚠️  No variations generated")

    # Test with DEBUG: Check what gets passed to Paraphrase augmenter
    print(f"\n" + "=" * 50)
    print("🔍 DEBUG: Check Paraphrase Augmenter Configuration")
    print("=" * 50)
    # Set a dummy OpenAI key
    dummy_openai_key = "sk_test_dummy_openai_key"
    os.environ['OPENAI_API_KEY'] = dummy_openai_key
    print(f"🔧 Set dummy OpenAI API key: {dummy_openai_key}")

    # Create new PromptSuite instance
    ps_debug = PromptSuite()
    ps_debug.load_dataframe(pd.DataFrame(data))
    ps_debug.set_template(template)

    # Configure with OpenAI platform explicitly
    ps_debug.configure(api_platform="OpenAI", model_name="gpt-4o-mini", max_rows=1, variations_per_field=1)
    variations = ps_debug.generate(verbose=False)
    assert len(variations) == 1, "Expected 1 variation with dummy key"
    print(f"\n" + "=" * 50)
    print("💡 Platform Switching Test Summary:")
    print("   - This test verifies that platform switching actually works")
    print("   - It attempts real API calls to test connectivity")
    print("   - Requires valid API keys to pass fully")
    print("   - Tests dummy API key rejection for security")
    print("   - Check the results above to see which platforms work")
    print("=" * 50)


def example_with_huggingface():
    """Example using HuggingFace datasets (SQuAwith classic QA template and gold field expression extraction."""
    print("\n" + "=" * 50)
    print("🤗 HuggingFace Dataset Example (SQuAD, zero-shot, classic QA, gold field expression)")
    print("=" * 50)

    try:
        ps = PromptSuite()

        # Load 3 examples from SQuAD directly
        print("\n1. Loading SQuAD dataset (3 samples)...")
        ps.load_dataset("rajpurkar/squad", split="train[:3]")

        # Classic QA template with gold field expression for SQuAD
        template = {
            INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
            PROMPT_FORMAT: 'Read the context and answer the question.\\nContext: {context}\\nQuestion: {question}\\nAnswer:',
            CONTEXT_KEY: [FORMAT_STRUCTURE_VARIATION],  # Reword the context
            QUESTION_KEY: [],
            GOLD_KEY: "answers['text'][0]"
        }
        ps.set_template(template)
        ps.configure(max_rows=3, variations_per_field=1, max_variations_per_row=1)

        print("\n2. Generating variations...")
        variations = ps.generate(verbose=True)

        print(f"\n✅ Generated {len(variations)} variations\n")
        for i, v in enumerate(variations):
            print(f"Prompt {i + 1}:")
            print(v["prompt"])
            # print("Expected answer:", v["answers['text'][0]"])
            print("-" * 40)

    except Exception as e:
        print(f"❌ HuggingFace example failed: {e}")


def example_different_templates():
    """Examples showing different template configurations."""

    print("\n" + "=" * 50)
    print("📝 Different Template Examples")
    print("=" * 50)

    # Simple QA template (text-based answers)
    simple_template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Question: {question}\nAnswer: {answer}',
        QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION],
        GOLD_KEY: 'answer'  # Simple format for text answers
    }

    # Multiple choice template (index-based answers)
    multiple_choice_template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Choose the correct answer:\nQ: {question}\nOptions: {options}\nA: {answer}',
        QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION],
        OPTIONS_KEY: [FORMAT_STRUCTURE_VARIATION, SHUFFLE_VARIATION],
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',  # Answer is index in options
            'options_field': 'options'
        }
    }

    # Complex template with multiple variations
    complex_template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Context: {context}\nQuestion: {question}\nAnswer: {answer}',
        CONTEXT_KEY: [FORMAT_STRUCTURE_VARIATION, PARAPHRASE_WITH_LLM],
        QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION],
        GOLD_KEY: {
            'field': 'answer',
            'type': 'value'  # Answer is text value
        },
        FEW_SHOT_KEY: {
            'count': 1,
            'format': 'same_examples__no_variations',
            'split': 'all'
        }
    }

    # Platform-specific template with different configurations
    platform_templates = {
        'TogetherAI': {
            INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
            PROMPT_FORMAT: 'Using Llama model: {question}\nAnswer: {answer}',
            QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION],
            GOLD_KEY: 'answer'
        },
        'OpenAI': {
            INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
            PROMPT_FORMAT: 'Using GPT model: {question}\nAnswer: {answer}',
            QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION],
            GOLD_KEY: 'answer'
        }
    }

    print("Simple template structure (text answers):")
    for key, value in simple_template.items():
        print(f"   {key}: {value}")

    print("\nMultiple choice template (index answers):")
    for key, value in multiple_choice_template.items():
        print(f"   {key}: {value}")

    print("\nComplex template structure:")
    for key, value in complex_template.items():
        print(f"   {key}: {value}")

    print("\nPlatform-specific templates:")
    for platform, template in platform_templates.items():
        print(f"\n{platform} template:")
        for key, value in template.items():
            print(f"   {key}: {value}")


def example_gold_field_formats():
    """Example showing different gold field configuration formats."""

    print("\n" + "=" * 50)
    print("🏆 Gold Field Configuration Examples")
    print("=" * 50)

    # Example data for different formats
    print("1. Index-based multiple choice data:")
    index_data = [
        {
            "question": "What color is the sky?",
            "options": ["Red", "Blue", "Green", "Yellow"],
            "answer": 1  # Blue (index 1)
        }
    ]
    print("   Data:", index_data[0])

    index_template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Q: {question}\nOptions: {options}\nA: {answer}',
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        }
    }
    print("   Template gold config:", index_template[GOLD_KEY])

    print("\n2. Value-based multiple choice data:")
    value_data = [
        {
            "question": "What color is the sky?",
            "options": ["Red", "Blue", "Green", "Yellow"],
            "answer": "Blue"  # Text value
        }
    ]
    print("   Data:", value_data[0])

    value_template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Q: {question}\nOptions: {options}\nA: {answer}',
        GOLD_KEY: {
            'field': 'answer',
            'type': 'value',
            'options_field': 'options'
        }
    }
    print("   Template gold config:", value_template[GOLD_KEY])


def example_environment_variables():
    """Example showing how to work with environment variables."""

    print("\n" + "=" * 50)
    print("🌍 Environment Variables Example")
    print("=" * 50)

    # Show current environment variables
    print("Current API key environment variables:")
    together_key = os.getenv("TOGETHER_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    print(f"   TOGETHER_API_KEY: {'✅ Set' if together_key else '❌ Not set'}")
    print(f"   OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")

    # Initialize API and show how keys are automatically selected
    ps = PromptSuite()

    print(f"\nDefault platform API key detection:")
    print(f"   Platform: {ps.config['api_platform']}")
    print(f"   API Key: {'✅ Found' if ps.config['api_key'] else '❌ Not found'}")
    # Test platform switching
    print(f"\nTesting platform switching:")
    for platform in ["TogetherAI", "OpenAI"]:
        ps.configure(api_platform=platform)
        key_found = ps.config['api_key'] is not None
        print(f"   {platform}: {'✅ API key found' if key_found else '❌ No API key'}")


def example_with_simple_qa():
    """Example loading 5 examples from simple_qa_test.csv (simple QA format)."""
    print("\n" + "=" * 50)
    print("📄 Simple QA CSV Example (simple_qa_test.csv)")
    print("=" * 50)

    # Path to the CSV file
    csv_path = os.path.join(os.path.dirname(__file__), '../../../data/simple_qa_test.csv')
    csv_path = os.path.abspath(csv_path)

    # Load the first 5 rows from the CSV
    df = pd.read_csv(csv_path).head(5)
    print(f"Loaded {len(df)} rows from {csv_path}")
    print(df[['problem', 'answer']])

    # Initialize the API
    ps = PromptSuite()
    ps.load_dataframe(df)

    # Set a simple QA template
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Question: {problem}\nAnswer: {answer}',
        GOLD_KEY: 'answer',
        FEW_SHOT_KEY: {
            'count': 2,
            'format': 'same_examples__no_variations',
            'split': 'all'
        }
    }
    ps.set_template(template)

    # Configure and generate
    ps.configure(max_rows=5, variations_per_field=2)
    variations = ps.generate(verbose=True)

    print(f"\n✅ Generated {len(variations)} variations from simple_qa_test.csv")
    print("\n" + "=" * 50)
    for i, var in enumerate(variations[:3]):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(var['prompt'])
        print("-" * 50)

    # Export results
    ps.export("simple_qa_example.json", format="json")
    print("\n✅ Exported to simple_qa_example.json")
    ps.info()


def example_answer_the_question_prompt_only():
    """Example: Prompt instructs to answer the question, but does not include the answer (no gold, no few-shot)."""
    print("\n" + "=" * 50)
    print("📝 Example: 'Answer the question' Prompt Only (No Gold, No Few-shot)")
    print("=" * 50)

    # Sample data: question + answer, but we use only the question in the prompt
    data = [
        {"question": "What is the capital of France?", "answer": "Paris"},
        {"question": "How many days are in a week?", "answer": "7"},
        {"question": "Who wrote Romeo and Juliet?", "answer": "Shakespeare"}
    ]

    df = pd.DataFrame(data)
    ps = PromptSuite()
    ps.load_dataframe(df)

    # Template: instructs to answer the question, but does not include the answer
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Please answer the following question:\n{question}',
        QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION]
    }
    ps.set_template(template)

    ps.configure(max_rows=3, variations_per_field=2)
    variations = ps.generate(verbose=True)

    print(f"\n✅ Generated {len(variations)} variations (prompt only, no gold, no few-shot)")
    for i, var in enumerate(variations[:3]):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(var['prompt'])
        print("-" * 50)

    ps.export("answer_the_question_prompt_only.json", format="json")
    print("\n✅ Exported to answer_the_question_prompt_only.json")
    ps.info()


def example_with_system_prompt_few_shot():
    ps = PromptSuite()
    data = pd.DataFrame({
        'question': ['What is 2+2?', 'What is 3*3?', 'What is 5+3?'],
        'answer': ['4', '9', '8']
    })
    ps.load_dataframe(data)
    template = {
        INSTRUCTION: 'You are a helpful math assistant. Answer clearly.',
        PROMPT_FORMAT: 'Question: {question}\nAnswer: {answer}',
        QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION],
        GOLD_KEY: 'answer',
        FEW_SHOT_KEY: {
            'count': 2,
            'format': 'same_examples__no_variations',  # Same examples for all questions
            'split': 'all'
        }
    }
    ps.set_template(template)
    ps.configure(max_rows=3, variations_per_field=1)
    variations = ps.generate(verbose=True)
    print("\n=== System Prompt Few-shot Example ===")
    for v in variations:
        print(v['prompt'])
        print("--- Conversation:")
        for msg in v['conversation']:
            print(f"[{msg['role']}] {msg['content']}")
        print("====================\n")


def example_system_prompt_with_placeholder():
    print("\n=== System Prompt with Placeholder Example ===")
    ps = PromptSuite()
    data = pd.DataFrame({
        'question': [
            'What is the largest planet in our solar system?',
            'Which chemical element has the symbol O?',
            'What is the fastest land animal?',
            'What is the smallest prime number?',
            'Which continent is known as the \"Dark Continent\"?'
        ],
        'options': [
            'Earth, Jupiter, Mars, Venus',
            'Oxygen, Gold, Silver, Iron',
            'Lion, Cheetah, Horse, Leopard',
            '1, 2, 3, 0',
            'Asia, Africa, Europe, Australia'
        ],
        'answer': [1, 0, 1, 1, 1],
        'subject': ['Astronomy', 'Chemistry', 'Biology', 'Mathematics', 'Geography']
    })
    ps.load_dataframe(data)
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about {subject}.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer:',
        QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION],
        OPTIONS_KEY: ['shuffle'],
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        }
    }
    ps.set_template(template)
    ps.configure(max_rows=5, variations_per_field=1)
    variations = ps.generate(verbose=True)
    for i, var in enumerate(variations):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(var['prompt'])
        print("-" * 50)


def example_system_prompt_with_placeholder_and_few_shot():
    print("\n=== System Prompt with Placeholder + Few-shot Example ===")
    ps = PromptSuite()
    data = pd.DataFrame({
        'question': [
            'What is the largest planet in our solar system?',
            'Which chemical element has the symbol O?',
            'What is the fastest land animal?',
            'What is the smallest prime number?',
            'Which continent is known as the \"Dark Continent\"?'
        ],
        'options': [
            'Earth, Jupiter, Mars, Venus',
            'Oxygen, Gold, Silver, Iron',
            'Lion, Cheetah, Horse, Leopard',
            '1, 2, 3, 0',
            'Asia, Africa, Europe, Australia'
        ],
        'answer': [1, 0, 1, 1, 1],
        'subject': ['Astronomy', 'Chemistry', 'Biology', 'Mathematics', 'Geography']
    })
    ps.load_dataframe(data)
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about {subject}.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer:',
        QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION],
        OPTIONS_KEY: ['shuffle'],
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        },
        FEW_SHOT_KEY: {
            'count': 1,
            'format': 'same_examples__no_variations',  # Same examples for all questions
            'split': 'all'
        }
    }
    ps.set_template(template)
    ps.configure(max_rows=5, variations_per_field=2)
    variations = ps.generate(verbose=True)
    for i, var in enumerate(variations):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(var['prompt'])
        print("--- Conversation:")
        for msg in var['conversation']:
            print(f"[{msg['role']}] {msg['content']}")
        print("-" * 50)


def example_system_prompt_with_context_and_few_shot():
    """Example demonstrating context variations with both few-shot and zero-shot examples."""
    print("\n=== System Prompt with Context Variations + Few-shot/Zero-shot Examples ===")

    # Check if API key is available
    api_key = os.getenv("TOGETHER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Warning: No API key found!")
        print("   Context variations require an API key to work properly.")
        print("   Set your API key with:")
        print("   export TOGETHER_API_KEY='your_key'")
        print("   or")
        print("   export OPENAI_API_KEY='your_key'")
        print("   The example will still run but context variations may not work as expected.\n")

    # Initialize the API
    ps = PromptSuite()

    # Create sample data with questions about different subjects
    data = pd.DataFrame({
        'question': [
            'What is the capital of France?',
            'Which planet is closest to the Sun?',
            'What is the chemical symbol for gold?',
            'How many sides does a triangle have?',
            'Who wrote Romeo and Juliet?',
            'What is the largest ocean on Earth?',
            'Which element has the atomic number 1?',
            'What is the square root of 16?'
        ],
        'options': [
            'London, Berlin, Paris, Madrid',
            'Venus, Mercury, Earth, Mars',
            'Au, Ag, Fe, Cu',
            '2, 3, 4, 5',
            'Shakespeare, Dickens, Austen, Twain',
            'Atlantic, Pacific, Indian, Arctic',
            'Helium, Hydrogen, Oxygen, Carbon',
            '2, 4, 8, 16'
        ],
        'answer': [2, 1, 0, 1, 0, 1, 1, 1],  # 0-based indices
        'subject': ['Geography', 'Astronomy', 'Chemistry', 'Mathematics', 'Literature', 'Geography', 'Chemistry',
                    'Mathematics']
    })

    ps.load_dataframe(data)
    print(f"📝 Loaded {len(data)} questions across different subjects")

    # Test 1: Zero-shot with context variations
    print("\n1️⃣ Zero-shot with Context Variations:")
    print("-" * 50)

    template_zero_shot = {
        INSTRUCTION: 'You are a knowledgeable assistant. Answer the following multiple choice questions.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer:',
        QUESTION_KEY: [CONTEXT_VARIATION],  # Use context variations
        OPTIONS_KEY: ['shuffle'],
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        }
    }

    ps.set_template(template_zero_shot)
    ps.configure(max_rows=1, variations_per_field=2, max_variations_per_row=6)

    variations_zero_shot = ps.generate(verbose=True)

    print(f"\n✅ Generated {len(variations_zero_shot)} zero-shot variations with context")

    # Show variations with context (longer prompts)
    context_variations = [v for v in variations_zero_shot if len(v.get('prompt', '')) > 400]
    no_context_variations = [v for v in variations_zero_shot if len(v.get('prompt', '')) <= 400]

    print(f"   - {len(context_variations)} variations WITH context")
    print(f"   - {len(no_context_variations)} variations WITHOUT context")

    # Show first variation without context
    if no_context_variations:
        print(f"\nZero-shot Variation (No Context):")
        print("-" * 40)
        print(no_context_variations[0]['prompt'])
        print("-" * 40)

    # Show first variation with context
    if context_variations:
        print(f"\nZero-shot Variation (With Context):")
        print("-" * 40)
        context_prompt = context_variations[0]['prompt']
        if len(context_prompt) > 800:
            print(context_prompt[:800] + "...")
        else:
            print(context_prompt)
        print("-" * 40)

    # Export zero-shot results
    print("\n4️⃣ Exporting zero-shot results...")
    ps.export("context_variations_zero_shot.json", format="json")
    print("   - context_variations_zero_shot.json")

    # Test 2: Few-shot with context variations
    print("\n2️⃣ Few-shot with Context Variations:")
    print("-" * 50)

    template_few_shot = {
        INSTRUCTION: 'You are a knowledgeable assistant. Answer the following multiple choice questions.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer:',
        QUESTION_KEY: [CONTEXT_VARIATION],  # Use context variations
        OPTIONS_KEY: ['shuffle'],
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        },
        FEW_SHOT_KEY: {
            'count': 1,
            'format': 'same_examples__no_variations',  # Same examples for all questions
            'split': 'train'  # Use only training data
        }
    }

    ps.set_template(template_few_shot)
    ps.configure(max_rows=3, variations_per_field=2, max_variations_per_row=6)

    variations_few_shot = ps.generate(verbose=True)

    print(f"\n✅ Generated {len(variations_few_shot)} few-shot variations with context")

    # Show variations with context (longer prompts)
    context_variations_fs = [v for v in variations_few_shot if len(v.get('prompt', '')) > 400]
    no_context_variations_fs = [v for v in variations_few_shot if len(v.get('prompt', '')) <= 400]

    print(f"   - {len(context_variations_fs)} variations WITH context")
    print(f"   - {len(no_context_variations_fs)} variations WITHOUT context")

    # Show first variation without context
    if no_context_variations_fs:
        print(f"\nFew-shot Variation (No Context):")
        print("-" * 40)
        print(no_context_variations_fs[0]['prompt'])
        print("\n--- Conversation (Few-shot examples):")
        for msg in no_context_variations_fs[0]['conversation']:
            print(f"[{msg['role']}] {msg['content']}")
        print("-" * 40)

    # Show first variation with context
    if context_variations_fs:
        print(f"\nFew-shot Variation (With Context):")
        print("-" * 40)
        context_prompt_fs = context_variations_fs[0]['prompt']
        if len(context_prompt_fs) > 800:
            print(context_prompt_fs[:800] + "...")
        else:
            print(context_prompt_fs)
        print("\n--- Conversation (Few-shot examples):")
        for msg in context_variations_fs[0]['conversation']:
            print(f"[{msg['role']}] {msg['content']}")
        print("-" * 40)

    # Test 3: Compare context variations with and without few-shot
    print("\n3️⃣ Comparison: Context Variations Impact:")
    print("-" * 50)

    # Export results
    print("\n5️⃣ Exporting results...")
    ps.export("context_variations_few_shot.json", format="json")

    print("✅ Exported to:")
    print("   - context_variations_few_shot.json")

    if not api_key:
        print("\n💡 To see context variations in action:")
        print("   1. Set your API key: export TOGETHER_API_KEY='your_key'")
        print("   2. Run this example again")
        print("   3. You'll see questions with added background context")

    print("\n✅ Context variations with few-shot/zero-shot example completed!")


def example_simple_context_variations():
    """Simple example showing context variations concept without requiring API key."""
    print("\n=== Simple Context Variations Example (No API Key Required) ===")

    # Initialize the API
    ps = PromptSuite()

    # Simple data
    data = pd.DataFrame({
        'question': [
            'What is 2+2?',
            'What color is the sky?',
            'How many days are in a week?'
        ],
        'answer': ['4', 'Blue', '7']
    })

    ps.load_dataframe(data)
    print(f"📝 Loaded {len(data)} simple questions")

    # Template with rewordings (works without API key)
    template = {
        INSTRUCTION: 'You are a helpful assistant. Answer the following questions.',
        PROMPT_FORMAT: 'Question: {question}\nAnswer: {answer}',
        QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION],  # This works without API key
        GOLD_KEY: 'answer'
    }

    ps.set_template(template)
    ps.configure(max_rows=3, variations_per_field=2, max_variations_per_row=6)

    variations = ps.generate(verbose=True)

    print(f"\n✅ Generated {len(variations)} variations with rewordings")
    for i, var in enumerate(variations[:3]):
        print(f"\nVariation {i + 1}:")
        print("-" * 40)
        print(var['prompt'])
        print("-" * 40)

    print("\n💡 This example shows how rewordings work without API key.")
    print("   Context variations would add background information but require API access.")

    # Export results
    ps.export("simple_context_example.json", format="json")
    print("✅ Exported to simple_context_example.json")


def example_enumerate_as_field_variation():
    """Example demonstrating enumerate as a field variation to get multiple enumeration types."""
    print("\n=== Enumerate as Field Variation Example ===")

    # Initialize the API
    ps = PromptSuite()

    # Create sample data
    data = pd.DataFrame({
        'question': [
            'What is the capital of France?',
        ],
        'options': [
            'London, Berlin, Paris, Madrid',
        ],
        'answer': [2]  # 0-based indices
    })

    ps.load_dataframe(data)
    print(f"📝 Loaded {len(data)} questions")

    # Configure template with enumerate as field variation
    print("\n2. Setting template with enumerate as field variation...")
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
        # QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION],
        OPTIONS_KEY: [SHUFFLE_VARIATION, ENUMERATE_VARIATION],  # Use enumerate as field variation
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        }
    }

    ps.set_template(template)
    print("✅ Template configured with enumerate as field variation")
    print("   - Will generate multiple enumeration types for options field")

    # Configure generation parameters
    print("\n3. Configuring generation...")
    ps.configure(
        max_rows=1,
        variations_per_field=2,  # Generate 4 variations with different enumeration types
        max_variations_per_row=8,
        random_seed=42
    )

    # Generate variations
    print("\n4. Generating variations...")
    variations = ps.generate(verbose=True)

    # Show results
    print(f"\n5. Results: Generated {len(variations)} variations")

    # Display variations to see different enumeration types
    for i, variation in enumerate(variations):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(variation.get('prompt', 'No prompt found'))
        print("-" * 50)

    # Export results
    print("\n6. Exporting results...")
    ps.export("enumerate_field_variation.json", format="json")

    print("\n✅ Enumerate as field variation example completed!")


def example_many_augmenters_on_small_dataset():
    """Example: Apply context, shuffle, rewording, and paraphrase on a tiny dataset (2 rows)."""
    print("\n=== Many Augmenters on Small Dataset Example ===")
    # Check API key for context/paraphrase
    api_key = os.getenv("TOGETHER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Warning: No API key found! Some augmenters may not work.")

    # Tiny dataset
    data = pd.DataFrame({
        'question': [
            'What is the capital of France?',
            'What is 2+2?'
        ],
        'options': [
            ['London', 'Berlin', 'Paris', 'Madrid'],
            ['3', '4', '5', '6'],        ],
        'answer': [2, 1]  # 0-based indices
    })

    ps = PromptSuite()
    ps.load_dataframe(data)
    print(f"📝 Loaded {len(data)} questions")

    # Template: apply all augmenters
    template = {
        INSTRUCTION: 'Answer the following multiple choice questions.',
        INSTRUCTION_VARIATIONS: [PARAPHRASE_WITH_LLM],  # Reword the instruction
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
        PROMPT_FORMAT_VARIATIONS : [FORMAT_STRUCTURE_VARIATION],
        OPTIONS_KEY: [SHUFFLE_VARIATION, ENUMERATE_VARIATION],
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        }
    }
    ps.set_template(template)
    print("✅ Template with context, shuffle, rewording, paraphrase")

    # Configure: all variations, but limit for demo
    ps.configure(
        max_rows=1,
        variations_per_field=2,  # 2 per augmenter per field
        max_variations_per_row=16,
        random_seed=42
    )
    print("\nGenerating variations...")
    variations = ps.generate(verbose=True)
    ps.export("many_augmenters_small_dataset.json", format="json")
    print(f"\n✅ Generated {len(variations)} variations\n")
    for i, v in enumerate(variations):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(v.get('prompt', 'No prompt'))
        print("-" * 50)
    print("\nDone.")


def example_paraphrase_instruction_only():
    """Test: Single multiple choice question, only INSTRUCTION uses PARAPHRASE_WITH_LLM, with {subject} placeholder."""
    print("\n=== Paraphrase Instruction Only Example ===")
    # Single example

    data = pd.DataFrame({
        'question': [
            'What is the capital of France?',
            'What is 2+2?'
        ],
        'options': [
            'London, Berlin, Paris, Madrid',
            '3, 4, 5, 6'
        ],
        'answer': [2, 1],
        'subject': ['Geography', 'Geography']
        # 0-based indices
    })

    ps = PromptSuite()
    ps.load_dataframe(data)
    print(f"📝 Loaded {len(data)} question")

    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about {subject}.',
        INSTRUCTION_VARIATIONS: [PARAPHRASE_WITH_LLM],
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer:',
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        }
    }
    ps.set_template(template)
    print("✅ Template with only instruction paraphrasing")

    ps.configure(max_rows=3, variations_per_field=3, max_variations_per_row=20)
    variations = ps.generate(verbose=True)
    print(f"\n✅ Generated {len(variations)} variations\n")
    for i, v in enumerate(variations):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(v.get('prompt', 'No prompt'))
        print("-" * 50)
    print("\nDone.")


def example_format_structure():
    """Example demonstrating the new FormatStructureAugmenter for semantic-preserving format variations."""
    print("\n=== Format Structure Augmenter Example ===")

    # Create sample data
    data = pd.DataFrame({
        'question': [
            'What is the capital of France?',
            'What is 2+2?'
        ],
        'options': [
            'London, Berlin, Paris, Madrid',
            '3, 4, 5, 6'
        ],
        'answer': [2, 1]  # 0-based indices
    })

    ps = PromptSuite()
    ps.load_dataframe(data)
    print(f"📝 Loaded {len(data)} questions")

    # Configure template with format structure variations and enumerate
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
        PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION],  # Use format structure variations
        OPTIONS_KEY: [ENUMERATE_VARIATION],  # Use enumerate as field variation
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        }
    }

    ps.set_template(template)
    print("✅ Template configured with format structure variations + enumerate")
    print("   - Will generate semantic-preserving format changes")
    print("   - Will enumerate 'options' field with random enumeration types")

    # Pass seed via configure
    seed = 1234
    print(f"Using seed={seed}")
    ps.configure(
        max_rows=2,
        variations_per_field=5,
        max_variations_per_row=20,  # Increased to get more variations
        random_seed=seed
    )

    # Generate variations
    variations = ps.generate(verbose=True)

    # Show results
    print(f"\n✅ Generated {len(variations)} format structure variations with enumerate")

    # Display variations to see format structure changes
    for i, variation in enumerate(variations[:15]):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(variation.get('prompt', 'No prompt found'))
        print("-" * 50)

    # Export results
    ps.export("format_structure_example.json", format="json")
    print("\n✅ Format structure example completed!")


def example_typos_and_noise():
    """Example demonstrating the new TextNoiseAugmenter for robustness testing with noise injection."""
    print("\n=== Typos and Noise Augmenter Example ===")

    # Create sample data
    data = pd.DataFrame({
        'question': [
            'What is the capital of France?',
            'What is 2+2?'
        ],
        'options': [
            'London, Berlin, Paris, Madrid',
            '3, 4, 5, 6'
        ],
        'answer': [2, 1]  # 0-based indices
    })

    ps = PromptSuite()
    ps.load_dataframe(data)
    print(f"📝 Loaded {len(data)} questions")

    # Configure template with typos and noise variations and enumerate
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
        QUESTION_KEY: [TYPOS_AND_NOISE_VARIATION],  # Use typos and noise variations
        OPTIONS_KEY: [ENUMERATE_VARIATION],  # Use enumerate as field variation
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        }
    }

    ps.set_template(template)
    print("✅ Template configured with typos and noise variations + enumerate")
    print("   - Will generate robustness testing with noise injection")
    print("   - Will enumerate 'options' field with random enumeration types")

    # Configure generation parameters
    ps.configure(
        max_rows=2,
        variations_per_field=2,
        max_variations_per_row=20,  # Increased to get more variations
        random_seed=42
    )

    # Generate variations
    variations = ps.generate(verbose=True)

    # Show results
    print(f"\n✅ Generated {len(variations)} typos and noise variations with enumerate")

    # Display variations to see noise injection
    for i, variation in enumerate(variations[:10]):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(variation.get('prompt', 'No prompt found'))
        print("-" * 50)

    # Export results
    ps.export("typos_and_noise_example.json", format="json")
    print("\n✅ Typos and noise example completed!")


def example_combined_specialized_augmenters():
    """Example demonstrating both new specialized augmenters together."""
    print("\n=== Combined Specialized Augmenters Example ===")

    # Create sample data
    data = pd.DataFrame({
        'question': [
            'What is the capital of France?'
        ],
        'options': [
            'London, Berlin, Paris, Madrid'
        ],
        'answer': [2]  # 0-based index
    })

    ps = PromptSuite()
    ps.load_dataframe(data)
    print(f"📝 Loaded {len(data)} question")

    # Configure template with both specialized augmenters and enumerate
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
        QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION, TYPOS_AND_NOISE_VARIATION],  # Use both augmenters
        OPTIONS_KEY: [FORMAT_STRUCTURE_VARIATION, TYPOS_AND_NOISE_VARIATION, ENUMERATE_VARIATION],
        # Use both augmenters + enumerate
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        }
    }

    ps.set_template(template)
    print("✅ Template configured with both specialized augmenters + enumerate")
    print("   - FormatStructureAugmenter: Semantic-preserving format changes")
    print("   - TextNoiseAugmenter: Robustness testing with noise injection")
    print("   - Will enumerate 'options' field with random enumeration types")

    # Configure generation parameters
    ps.configure(
        max_rows=1,
        variations_per_field=2,
        max_variations_per_row=8,
        random_seed=42
    )

    # Generate variations
    variations = ps.generate(verbose=True)

    # Show results
    print(f"\n✅ Generated {len(variations)} combined variations with enumerate")

    # Display variations to see both types of changes
    for i, variation in enumerate(variations):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(variation.get('prompt', 'No prompt found'))
        print("-" * 50)

    # Export results
    ps.export("combined_specialized_augmenters.json", format="json")
    print("\n✅ Combined specialized augmenters example completed!")


def example_backward_compatibility_rewording():
    """Example demonstrating backward compatibility with REWORDING."""
    print("\n=== Backward Compatibility with REWORDING Example ===")

    # Create sample data
    data = pd.DataFrame({
        'question': [
            'What is the capital of France?'
        ],
        'options': [
            'London, Berlin, Paris, Madrid'
        ],
        'answer': [2]  # 0-based index
    })

    ps = PromptSuite()
    ps.load_dataframe(data)
    print(f"📝 Loaded {len(data)} question")

    # Configure template with REWORDING (should map to TextNoiseAugmenter) and enumerate
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
        QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION],  # This should map to TextNoiseAugmenter
        OPTIONS_KEY: [FORMAT_STRUCTURE_VARIATION, ENUMERATE_VARIATION],
        # This should map to TextNoiseAugmenter + enumerate
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        }
    }

    ps.set_template(template)
    print("✅ Template configured with REWORDING (maps to TextNoiseAugmenter) + enumerate")
    print("   - Backward compatibility maintained")
    print("   - Will enumerate 'options' field with random enumeration types")

    # Configure generation parameters
    ps.configure(
        max_rows=1,
        variations_per_field=2,
        max_variations_per_row=4,
        random_seed=42
    )

    # Generate variations
    variations = ps.generate(verbose=True)

    # Show results
    print(f"\n✅ Generated {len(variations)} variations with REWORDING and enumerate")

    # Display variations
    for i, variation in enumerate(variations):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(variation.get('prompt', 'No prompt found'))
        print("-" * 50)

    # Export results
    ps.export("backward_compatibility_rewording.json", format="json")
    print("\n✅ Backward compatibility example completed!")


def example_shuffle_template():
    """Debug example for complex template with multiple variations to understand variation count."""
    print("\n=== Complex Template Debug Example ===")
    print("🔍 Debugging variation count with complex template")
    print("=" * 60)

    # Create instance
    ps = PromptSuite()

    # Load data with 4 examples
    data = pd.DataFrame({
        'question': [
            'What is the largest planet?',
            'Which element has symbol O?',
            'What is the fastest land animal?',
            'What is the smallest prime number?'
        ],
        'options': [
            ['Mars', 'Earth', 'Jupiter', 'Venus'],
            ['Oxygen', 'Gold', 'Silver'],
            ['Lion', 'Cheetah', 'Horse'],
            ['1', '2', '3']
        ],
        'answer': [2, 0, 1, 1]  # Indices: Jupiter=2, Oxygen=0, Cheetah=1, 2=1
    })
    ps.load_dataframe(data)
    print(f"📝 Loaded {len(data)} questions")

    # Complex template with multiple variations
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers).',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
        OPTIONS_KEY: [SHUFFLE_VARIATION, ENUMERATE_VARIATION],
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        },
        FEW_SHOT_KEY: {
            'count': 2,
            'format': 'same_examples__no_variations',
            'split': 'all'
        }
    }
    ps.set_template(template)
    print("✅ Template configured with complex variations:")
    print("   - INSTRUCTION_VARIATIONS: [TYPOS_AND_NOISE_VARIATION]")
    print("   - PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION, TYPOS_AND_NOISE_VARIATION]")
    print("   - QUESTION_KEY: [TYPOS_AND_NOISE_VARIATION]")
    print("   - OPTIONS_KEY: [SHUFFLE_VARIATION, TYPOS_AND_NOISE_VARIATION]")
    print("   - FEW_SHOT_KEY: count=2, format=same_examples__no_variations, split=all")

    # Configure with 3 variations per field
    ps.configure(
        max_rows=1,
        variations_per_field=3,
        max_variations_per_row=22,  # High limit to see all variations
        random_seed=42
    )
    variations = ps.generate(verbose=True)

    # Show field values for first few variations to understand what's being varied
    print(f"\n🔍 Field values analysis (first 3 variations):")
    for i, var in enumerate(variations[:6]):
        print(f"\nVariation {i + 1} (Row {var.get('original_row_index', 0)}):")
        field_values = var.get('field_values', {})
        for field, value in field_values.items():
            # Truncate long values for readability
            if len(str(value)) > 50:
                value = str(value)[:50] + "..."
            print(f"   - {field}: {value}")

    # Export results for further analysis
    ps.export("shuffle_template_debug.json", format="json")
    print(f"\n✅ Exported to shuffle_template_debug.json for further analysis")

    # Show final stats
    ps.info()


def example_complex_template_debug():
    """Debug example for complex template with multiple variations to understand variation count."""
    print("\n=== Complex Template Debug Example ===")
    print("🔍 Debugging variation count with complex template")
    print("=" * 60)

    # Create instance
    ps = PromptSuite()

    # Load data with 4 examples
    data = pd.DataFrame({
        'question': [
            'What is the largest planet?',
            'Which element has symbol O?',
            'What is the fastest land animal?',
            'What is the smallest prime number?'
        ],
        'options': [
            ['Mars', 'Earth', 'Jupiter', 'Venus'],
            ['Oxygen', 'Gold', 'Silver'],
            ['Lion', 'Cheetah', 'Horse'],
            ['1', '2', '3']
        ],
        'answer': [2, 0, 1, 1]  # Indices: Jupiter=2, Oxygen=0, Cheetah=1, 2=1
    })
    ps.load_dataframe(data)
    print(f"📝 Loaded {len(data)} questions")

    # Complex template with multiple variations
    template = {
        INSTRUCTION: 'The following are multiple choice questions (with answers).',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
        INSTRUCTION_VARIATIONS: [TYPOS_AND_NOISE_VARIATION],
        PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION, TYPOS_AND_NOISE_VARIATION],
        QUESTION_KEY: [TYPOS_AND_NOISE_VARIATION],
        OPTIONS_KEY: [SHUFFLE_VARIATION],
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        },
        FEW_SHOT_KEY: {
            'count': 1,
            'format': 'same_examples__no_variations',
            'split': 'all'
        }
    }
    ps.set_template(template)
    print("✅ Template configured with complex variations:")
    print("   - INSTRUCTION_VARIATIONS: [TYPOS_AND_NOISE_VARIATION]")
    print("   - PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION, TYPOS_AND_NOISE_VARIATION]")
    print("   - QUESTION_KEY: [TYPOS_AND_NOISE_VARIATION]")
    print("   - OPTIONS_KEY: [SHUFFLE_VARIATION, TYPOS_AND_NOISE_VARIATION]")
    print("   - FEW_SHOT_KEY: count=1, format=same_examples__no_variations, split=all")

    # Configure with 3 variations per field
    ps.configure(
        max_rows=2,
        variations_per_field=3,
        max_variations_per_row=10,  # High limit to see all variations
        random_seed=42
    )
    print(f"\n⚙️ Configuration:")
    print(f"   - max_rows: 4")
    print(f"   - variations_per_field: 3")
    print(f"   - max_variations_per_row: 50")
    print(f"   - random_seed: 42")

    # Calculate expected variations
    print(f"\n🧮 EXPECTED VARIATIONS CALCULATION:")
    print(f"   - Fields with variations: 4")
    print(f"   - Variations per field: 3")
    print(f"   - Combinatorial product: 3^4 = 81 variations per row")
    print(f"   - Total expected: 4 rows × 81 variations = 324 variations")

    # Generate variations
    print("\n🚀 Generating variations...")
    variations = ps.generate(verbose=True)

    # Debug analysis
    print(f"\n📊 DEBUG ANALYSIS:")
    print(f"   - Total variations generated: {len(variations)}")
    print(f"   - Expected: 324 variations")
    print(f"   - Actual: {len(variations)} variations")

    # Count variations per row
    row_counts = {}
    for var in variations:
        row_idx = var.get('original_row_index', 0)
        row_counts[row_idx] = row_counts.get(row_idx, 0) + 1

    print(f"\n📈 Variations per row:")
    for row_idx in sorted(row_counts.keys()):
        count = row_counts[row_idx]
        print(f"   - Row {row_idx}: {count} variations")

    # Show field values for first few variations to understand what's being varied
    print(f"\n🔍 Field values analysis (first 3 variations):")
    for i, var in enumerate(variations[:3]):
        print(f"\nVariation {i + 1} (Row {var.get('original_row_index', 0)}):")
        field_values = var.get('field_values', {})
        for field, value in field_values.items():
            # Truncate long values for readability
            if len(str(value)) > 50:
                value = str(value)[:50] + "..."
            print(f"   - {field}: {value}")

    # Show what's different between variations
    if len(variations) >= 2:
        print(f"\n🔍 What's different between variations:")
        var1 = variations[0]
        var2 = variations[1]

        field_values1 = var1.get('field_values', {})
        field_values2 = var2.get('field_values', {})

        for field in field_values1.keys():
            if field in field_values2:
                val1 = str(field_values1[field])
                val2 = str(field_values2[field])
                if val1 != val2:
                    print(f"   - {field}: '{val1[:30]}...' vs '{val2[:30]}...'")

    # Export results for further analysis
    ps.export("complex_template_debug.json", format="json")
    print(f"\n✅ Exported to complex_template_debug.json for further analysis")

    # Show final stats
    ps.info()

    print(f"\n💡 EXPLANATION:")
    print(f"   The high number of variations is due to combinatorial explosion:")
    print(f"   - Each field with variations generates 3 variations")
    print(f"   - All combinations are created using itertools.product")
    print(f"   - This results in 3^4 = 81 possible combinations per row")
    print(f"   - The system then samples up to max_variations_per_row=50 from these")
    print(f"   - To get fewer variations, either:")
    print(f"     1. Reduce variations_per_field (e.g., to 1 or 2)")
    print(f"     2. Reduce max_variations_per_row")
    print(f"     3. Use fewer fields with variations")


def example_few_shot_train_test_split():
    """Test few-shot behavior with train/test split to understand how same_examples__no_variations works."""
    print("\n" + "=" * 60)
    print("🔍 Testing Few-Shot with Train/Test Split")
    print("=" * 60)

    # Create dataset with train/test split
    data = pd.DataFrame({
        'question': [
            # Training examples (will be used for few-shot)
            'What is 2+2?',
            'What is 3+3?',
            'What is 4+4?',
            'What is 5+5?',
            'What is 6+6?',
            # Test examples (will be the target questions)
            'What is 7+7?',
            'What is 8+8?',
            'What is 9+9?'
        ],
        'options': [
            # Training options
            '3, 4, 5, 6',
            '5, 6, 7, 8',
            '7, 8, 9, 10',
            '9, 10, 11, 12',
            '11, 12, 13, 14',
            # Test options
            '13, 14, 15, 16',
            '15, 16, 17, 18',
            '17, 18, 19, 20'
        ],
        'answer': [1, 1, 1, 1, 1, 1, 1, 1],  # All answers are option B
        'split': ['train', 'train', 'train', 'train', 'train', 'test', 'test', 'test']
    })

    print(f"📊 Dataset Overview:")
    print(f"   - Total examples: {len(data)}")
    print(f"   - Train examples: {len(data[data['split'] == 'train'])}")
    print(f"   - Test examples: {len(data[data['split'] == 'test'])}")

    print("\n📝 Train Examples:")
    train_data = data[data['split'] == 'train']
    for i, row in train_data.iterrows():
        print(f"   {i}: {row['question']} -> {row['options'].split(', ')[row['answer']]}")

    print("\n📝 Test Examples (targets):")
    test_data = data[data['split'] == 'test']
    for i, row in test_data.iterrows():
        print(f"   {i}: {row['question']} -> {row['options'].split(', ')[row['answer']]}")

    # Test 1: Ordered few-shot with train split
    print("\n" + "=" * 40)
    print("🔧 Test 1: ORDERED few-shot using TRAIN split")
    print("=" * 40)

    ps = PromptSuite()
    ps.load_dataframe(data)

    template_ordered_train = {
        INSTRUCTION: 'Answer the following multiple choice math questions.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer:',
        OPTIONS_KEY: [SHUFFLE_VARIATION, ENUMERATE_VARIATION],  # Shuffle options for variety
        # GOLD_KEY:'answer',

        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        },
        FEW_SHOT_KEY: {
            'count': 2,
            'format': 'same_examples__no_variations',  # Same examples for all questions
            'split': 'train'  # Use only training data
        }
    }

    ps.set_template(template_ordered_train)
    ps.configure(max_rows=8, variations_per_field=2, max_variations_per_row=6)  # Process all rows

    variations_ordered = ps.generate(verbose=False)

    print(f"✅ Generated {len(variations_ordered)} variations with ORDERED few-shot")
    ps.export("few_shot_train_test_ordered.json", format="json")

    # Show few-shot examples for each test question
    test_variations = [v for v in variations_ordered if v.get('original_row_index', 0) >= 5]  # Test rows are 5,6,7

    for i, var in enumerate(test_variations):
        row_idx = var.get('original_row_index', 0)
        question = data.iloc[row_idx]['question']
        print(f"\n📋 Test Question {i + 1} (Row {row_idx}): {question}")
        print("Few-shot examples used:")

        conversation = var.get('conversation', [])
        if conversation:
            for msg in conversation:
                if msg['role'] == 'user':
                    # Extract few-shot examples
                    content = msg['content']
                    if 'Question:' in content:
                        examples = content.split('Question:')[:-1]  # Remove last part (current question)
                        for j, example in enumerate(examples):
                            if example.strip():
                                print(f"   Example {j + 1}: Question: {example.strip()}")

    # Test 2: Random per row few-shot with train split
    print("\n" + "=" * 40)
    print("🔄 Test 2: RANDOM PER ROW few-shot using TRAIN split")
    print("=" * 40)

    template_random_per_row_train = {
        INSTRUCTION: 'Answer the following multiple choice math questions.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer:',
        OPTIONS_KEY: [SHUFFLE_VARIATION],  # Shuffle options for variety
        ENUMERATE_VARIATION: {
            'field': 'options',  # Which field to enumerate
            'type': '1234'  # Use numbers: 1. 2. 3. 4.
        },
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        },
        FEW_SHOT_KEY: {
            'count': 2,
            'format': 'different_examples__same_shuffling_order_across_rows',  # Same examples, different order
            'split': 'train'  # Use only training data
        }
    }

    ps.set_template(template_random_per_row_train)
    ps.configure(max_rows=8, variations_per_field=2, max_variations_per_row=3)

    variations_random_per_row = ps.generate(verbose=False)

    print(f"✅ Generated {len(variations_random_per_row)} variations with RANDOM PER ROW few-shot")

    # Show few-shot examples for each test question
    test_variations_random_per_row = [v for v in variations_random_per_row if v.get('original_row_index', 0) >= 5]

    for i, var in enumerate(test_variations_random_per_row):
        row_idx = var.get('original_row_index', 0)
        question = data.iloc[row_idx]['question']
        print(f"\n🔄 Test Question {i + 1} (Row {row_idx}): {question}")
        print("Few-shot examples used:")

        conversation = var.get('conversation', [])
        if conversation:
            for msg in conversation:
                if msg['role'] == 'user':
                    content = msg['content']
                    if 'Question:' in content:
                        examples = content.split('Question:')[:-1]
                        for j, example in enumerate(examples):
                            if example.strip():
                                print(f"   Example {j + 1}: Question: {example.strip()}")

    # Export results for analysis
    ps.export("few_shot_train_test_analysis.json", format="json")
    print(f"\n✅ Exported analysis to few_shot_train_test_analysis.json")


def example_few_shot_random_per_row_vs_ordered():
    """Detailed comparison of random_per_row vs ordered few-shot to understand the differences."""
    print("\n" + "=" * 60)
    print("⚖️  Detailed Comparison: Random Per Row vs Ordered Few-Shot")
    print("=" * 60)

    # Create a larger dataset to see rotation effects
    data = pd.DataFrame({
        'question': [
            'What is the capital of France?',
            'What is the capital of Germany?',
            'What is the capital of Italy?',
            'What is the capital of Spain?',
            'What is the capital of UK?',
            'What is the capital of Japan?',
            'What is the capital of China?',
            'What is the capital of Russia?'
        ],
        'options': [
            'London, Paris, Berlin, Madrid',
            'Paris, Berlin, Rome, Madrid',
            'Berlin, Rome, Paris, London',
            'Madrid, Paris, Berlin, Rome',
            'London, Berlin, Paris, Madrid',
            'Tokyo, Beijing, Seoul, Bangkok',
            'Beijing, Tokyo, Seoul, Bangkok',
            'Moscow, Kiev, Warsaw, Prague'
        ],
        'answer': [1, 1, 1, 0, 0, 0, 0, 0],  # Correct answers
        'split': ['train', 'train', 'train', 'train', 'test', 'test', 'test', 'test']
    })

    print(f"📊 Dataset: {len(data)} geography questions")
    print(f"   - Train: {len(data[data['split'] == 'train'])} examples")
    print(f"   - Test: {len(data[data['split'] == 'test'])} examples")

    # Test both formats with same configuration
    formats = ['same_examples__synchronized_order_variations', 'different_examples__different_order_per_variation']

    for format_type in formats:
        print(f"\n" + "=" * 30)
        print(f"🔍 Testing {format_type.upper()} format")
        print("=" * 30)

        ps = PromptSuite()()
        ps.load_dataframe(data)

        template = {
            INSTRUCTION: 'Answer the following geography questions.',
            PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer:',
            GOLD_KEY: {
                'field': 'answer',
                'type': 'index',
                'options_field': 'options'
            },
            FEW_SHOT_KEY: {
                'count': 2,
                'format': format_type,
                'split': 'train'
            }
        }

        ps.set_template(template)
        ps.configure(max_rows=8, variations_per_field=1, max_variations_per_row=1)

        variations = ps.generate(verbose=False)

        # Analyze test questions only
        test_variations = [v for v in variations if v.get('original_row_index', 0) >= 4]

        print(f"📋 {format_type.upper()} Results:")

        for i, var in enumerate(test_variations):
            row_idx = var.get('original_row_index', 0)
            question = data.iloc[row_idx]['question']

            print(f"\n   Test Question {i + 1} (Row {row_idx}):")
            print(f"   Q: {question}")

            # Extract few-shot examples
            conversation = var.get('conversation', [])
            few_shot_questions = []

            if conversation:
                for msg in conversation:
                    if msg['role'] == 'user':
                        content = msg['content']
                        # Find all questions in the content
                        lines = content.split('\n')
                        for line in lines:
                            if line.startswith('Question:') and line != f"Question: {question}":
                                few_shot_questions.append(line.replace('Question: ', ''))

            print(f"   Few-shot examples:")
            for j, fs_q in enumerate(few_shot_questions):
                print(f"     {j + 1}. {fs_q}")

        # Export for this format
        ps.export(f"few_shot_{format_type}_analysis.json", format="json")

    print(f"\n" + "=" * 60)
    print("🔍 ANALYSIS SUMMARY")
    print("=" * 60)

    print("📊 Expected Behavior:")
    print("   SAME_EXAMPLES__SYNCHRONIZED_ORDER_VARIATIONS format:")
    print("     - Should use the SAME 2 training examples for ALL test questions")
    print("     - Examples: Always questions 0,1 (France, Germany)")
    print()
    print("   DIFFERENT_EXAMPLES__DIFFERENT_ORDER_PER_VARIATION format:")
    print("     - Should use DIFFERENT training examples for each test question")
    print("     - Based on random_state=current_row_idx")
    print("     - Each test question gets different training examples")

    print("\n💡 Key Points to Verify:")
    print("   1. Does 'same_examples__synchronized_order_variations' really use the same examples for all test questions?")
    print("   2. Does 'different_examples__different_order_per_variation' use different examples for each test question?")
    print("   3. Are only TRAIN examples used (no test examples in few-shot)?")
    print("   4. Is the current question excluded from few-shot examples?")

    print("\n✅ Check the exported JSON files for detailed analysis!")


def test_enumerated_gold_in_few_shot():
    """Test that enumerated options show correct enumerated gold values in few-shot examples."""
    print("\n" + "=" * 60)
    print("🧪 TESTING ENUMERATED GOLD VALUES IN FEW-SHOT")
    print("=" * 60)

    # Simple test data
    data = pd.DataFrame({
        'question': ['What is 2+2?', 'What is 3+3?', 'What is 4+4?'],
        'options': [['3', '4', '5', '6'], ['5', '6', '7', '8'], ['7', '8', '9', '10']],
        'answer': [1, 1, 1],  # All answers are index 1 (second option)
        'split': ['train', 'train', 'test']
    })

    print("📊 Test Data:")
    print(data.to_string(index=True))

    template = {
        INSTRUCTION: 'Answer the following multiple choice math questions.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer:',
        OPTIONS_KEY: [ENUMERATE_VARIATION],  # This should enumerate the options
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        },
        FEW_SHOT_KEY: {
            'count': 2,
            'format': 'same_examples__no_variations',
            'split': 'train'
        }
    }

    ps = PromptSuite()
    ps.load_dataframe(data)
    ps.set_template(template)
    ps.configure(max_rows=3, variations_per_field=3, max_variations_per_row=3)

    variations = ps.generate(verbose=False)

    print(f"\n✅ Generated {len(variations)} variations")

    # Show the test question result
    test_var = None
    for var in variations:
        if var.get('original_row_index', 0) == 2:  # Test row
            test_var = var
            break

    if test_var:
        print(f"\n📝 Test Question Result:")
        conversation = test_var.get('conversation', [])
        if conversation:
            for msg in conversation:
                if msg['role'] == 'user':
                    print("PROMPT:")
                    print(msg['content'])
                    print("\n🎯 Expected: Few-shot answers should be '2. 4' and '2. 6' (enumerated format)")

                    # Check if the few-shot examples show enumerated answers
                    content = msg['content']
                    if '2. 4' in content and '2. 6' in content:
                        print("✅ SUCCESS: Few-shot examples show enumerated gold values!")
                    elif '4' in content and '6' in content:
                        print("⚠️  PARTIAL: Few-shot examples show gold values but not enumerated")
                    else:
                        print("❌ FAILED: Few-shot examples don't show expected gold values")
                    break
    else:
        print("❌ Could not find test question variation")


def example_list_data_support():
    """Example demonstrating support for list data format (instead of comma-separated strings)."""
    print("\n=== List Data Format Support Example ===")

    # Create sample data with actual Python lists instead of comma-separated strings
    data = pd.DataFrame({
        'question': [
            'Which technique is used for DNA amplification?',
            'What is the most common programming language for data science?',
            'What is the capital of France?',
            'Which planet is closest to the Sun?'
        ],
        'choices': [
            ['polymerase chain reaction.', 'single strand conformational polymorphism analysis.', 'Southern blotting.',
             'Western blotting.'],
            ['Python', 'R', 'Java', 'C++'],
            ['London', 'Paris', 'Berlin', 'Madrid'],
            ['Venus', 'Mercury', 'Earth', 'Mars']
        ],
        'answer': [0, 0, 1, 1],  # Correct choice indices
        'subject': ['Biology', 'Computer Science', 'Geography', 'Astronomy']
    })

    print("📊 Sample Data with List Format:")
    print(f"   Question 1 choices: {data.iloc[0]['choices']}")
    print(f"   Question 2 choices: {data.iloc[1]['choices']}")
    print(f"   Data type: {type(data.iloc[0]['choices'])}")

    ps = PromptSuite()
    ps.load_dataframe(data)
    print(f"📝 Loaded {len(data)} questions with list-format choices")

    # Configure template with shuffle and enumerate operations
    template = {
        INSTRUCTION: "The following are multiple choice questions (with answers) about {subject}.",
        PROMPT_FORMAT: "Question: {question}\nChoices: {choices}\nAnswer:\n{answer}",
        PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION],
        'choices': [SHUFFLE_VARIATION, ENUMERATE_VARIATION],
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'choices'
        },
        FEW_SHOT_KEY: {
            'count': 2,  # Reduced from 5 to work with smaller datasets
            'format': 'same_examples__no_variations',
            'split': 'all'
        }
    }

    ps.set_template(template)
    print("✅ Template configured with list data support:")
    print("   - choices field: shuffle + enumerate operations")
    print("   - Gold field: index-based with choices as options_field")

    # Configure generation parameters
    ps.configure(
        max_rows=4,
        variations_per_field=2,
        max_variations_per_row=4,
        random_seed=42
    )

    # Generate variations
    print("\n🚀 Generating variations with list data...")
    variations = ps.generate(verbose=True)

    # Show results
    print(f"\n✅ Generated {len(variations)} variations with list data support")

    # Display first few variations to see shuffle and enumerate in action
    for i, variation in enumerate(variations[:4]):
        print(f"\nVariation {i + 1}:")
        print("-" * 50)
        print(variation.get('prompt', 'No prompt found'))
        print("-" * 50)

        # Show field values to see how list was processed
        field_values = variation.get('field_values', {})
        if 'choices' in field_values:
            print(f"Processed choices: {field_values['choices']}")

        # Show gold updates
        gold_updates = variation.get('gold_updates', {})
        if gold_updates:
            print(f"Gold updates: {gold_updates}")

    # Export results
    ps.export("list_data_support_example.json", format="json")
    print("\n✅ List data support example completed!")
    print("✅ Exported to list_data_support_example.json")


def example_few_shot_unordered_random():
    """Example demonstrating the new shared_unordered_random_n few-shot format."""
    print("\n" + "=" * 60)
    print("🔄 Few-Shot Unordered Random Example")
    print("=" * 60)

    # Create dataset with train/test split
    data = pd.DataFrame({
        'question': [
            # Training examples (will be used for few-shot)
            'What is 2+2?',
            'What is 3+3?',
            'What is 4+4?',
            'What is 5+5?',
            'What is 6+6?',
            # Test examples (will be the target questions)
            'What is 7+7?',
            'What is 8+8?',
            'What is 9+9?'
        ],
        'options': [
            # Training options
            ['3', '4', '5', '6'],
            ['5', '6', '7', '8'],
            ['7', '8', '9', '10'],
            ['9', '10', '11', '12'],
            ['11', '12', '13', '14'],
            # Test options
            ['13', '14', '15', '16'],
            ['15', '16', '17', '18'],
            ['17', '18', '19', '20']
        ],
        'answer': [1, 1, 1, 1, 1, 1, 1, 1],  # All answers are option B
        'split': ['train', 'train', 'train', 'train', 'train', 'test', 'test', 'test']
    })

    print(f"📊 Dataset Overview:")
    print(f"   - Total examples: {len(data)}")
    print(f"   - Train examples: {len(data[data['split'] == 'train'])}")
    print(f"   - Test examples: {len(data[data['split'] == 'test'])}")

    # Test shared_unordered_random_n format
    print("\n" + "=" * 40)
    print("🔧 Testing shared_unordered_random_n format")
    print("=" * 40)

    ps = PromptSuite()
    ps.load_dataframe(data)

    template_unordered = {
        INSTRUCTION: 'Answer the following multiple choice math questions.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer:',
        OPTIONS_KEY: [SHUFFLE_VARIATION, ENUMERATE_VARIATION],
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        },
        FEW_SHOT_KEY: {
            'count': 2,
            'format': 'different_examples__same_shuffling_order_across_rows',  # Same examples, different order
            'split': 'train'
        }
    }

    ps.set_template(template_unordered)
    ps.configure(max_rows=1, variations_per_field=5, max_variations_per_row=10)

    variations_unordered = ps.generate(verbose=False)

    print(f"✅ Generated {len(variations_unordered)} variations with shared_unordered_random_n")
    ps.export("few_shot_unordered_random_example.json", format="json")

    # Show few-shot examples for each test question
    test_variations = [v for v in variations_unordered if v.get('original_row_index', 0) >= 5]

    for i, var in enumerate(test_variations):
        row_idx = var.get('original_row_index', 0)
        question = data.iloc[row_idx]['question']
        print(f"\n📋 Test Question {i + 1} (Row {row_idx}): {question}")
        print("Few-shot examples used (same examples, different order):")

        conversation = var.get('conversation', [])
        if conversation:
            for msg in conversation:
                if msg['role'] == 'user':
                    content = msg['content']
                    if 'Question:' in content:
                        examples = content.split('Question:')[:-1]
                        for j, example in enumerate(examples):
                            if example.strip():
                                print(f"   Example {j + 1}: Question: {example.strip()}")

    print(f"\n" + "=" * 60)
    print("🔍 ANALYSIS: shared_unordered_random_n vs shared_ordered_random_n")
    print("=" * 60)

    print("📊 Expected Behavior:")
    print("   DIFFERENT_EXAMPLES__SAME_SHUFFLING_ORDER_ACROSS_ROWS format:")
    print("     - Uses the SAME 2 random training examples for ALL test questions")
    print("     - BUT shuffles the ORDER of these examples for each test question")
    print("     - Examples: Same random selection, but order varies per question")
    print()
    print("   vs SHARED_ORDERED_RANDOM_N format:")
    print("     - Uses the SAME 2 random training examples for ALL test questions")
    print("     - AND keeps the SAME ORDER for all test questions")
    print("     - Examples: Same random selection, same order always")

    print("\n💡 Key Benefits of shared_unordered_random_n:")
    print("   1. Consistent example selection (same random examples)")
    print("   2. Order variation (shuffled order per question)")
    print("   3. Reduces position bias in few-shot examples")
    print("   4. Maintains reproducibility with fixed seed")

    print("\n✅ Check the exported JSON file for detailed analysis!")


def example_few_shot_random_per_row_vs_ordered_2():
    """Detailed comparison of random_per_row vs ordered few-shot to understand the differences."""
    print("\n" + "=" * 60)
    print("⚖️  Detailed Comparison: Random Per Row vs Ordered Few-Shot")
    print("=" * 60)

    # Create a larger dataset to see rotation effects
    data = pd.DataFrame({
        'question': [
            'What is the capital of France?',
            'What is the capital of Germany?',
            'What is the capital of Italy?',
            'What is the capital of Spain?',
            'What is the capital of UK?',
            'What is the capital of Japan?',
            'What is the capital of China?',
            'What is the capital of Russia?'
        ],
        'options': [
            ['London', 'Paris', 'Berlin', 'Madrid'],
            ['Paris', 'Berlin', 'Rome', 'Madrid'],
            ['Berlin', 'Rome', 'Paris', 'London'],
            ['Madrid', 'Paris', 'Berlin', 'Rome'],
            ['London', 'Berlin', 'Paris', 'Madrid'],
            ['Tokyo', 'Beijing', 'Seoul', 'Bangkok'],
            ['Beijing', 'Tokyo', 'Seoul', 'Bangkok'],
            ['Moscow', 'Kiev', 'Warsaw', 'Prague']
        ],
        'answer': [1, 1, 1, 0, 0, 0, 0, 0],  # Correct answers
        'split': ['train', 'train', 'train', 'train', 'test', 'test', 'test', 'test']
    })

    print(f"📊 Dataset: {len(data)} geography questions")
    print(f"   - Train: {len(data[data['split'] == 'train'])} examples")
    print(f"   - Test: {len(data[data['split'] == 'test'])} examples")

    # Test both formats with same configuration
    formats = ['same_examples__synchronized_order_variations', 'different_examples__different_order_per_variation']

    for format_type in formats:
        print(f"\n" + "=" * 30)
        print(f"🔍 Testing {format_type.upper()} format")
        print("=" * 30)

        ps = PromptSuite()
        ps.load_dataframe(data)

        template = {
            INSTRUCTION: 'Answer the following geography questions.',
            PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer:',
            GOLD_KEY: {
                'field': 'answer',
                'type': 'index',
                'options_field': 'options'
            },
            FEW_SHOT_KEY: {
                'count': 2,
                'format': format_type,
                'split': 'train'
            }
        }

        ps.set_template(template)
        ps.configure(max_rows=8, variations_per_field=1, max_variations_per_row=1)

        variations = ps.generate(verbose=False)

        # Analyze test questions only
        test_variations = [v for v in variations if v.get('original_row_index', 0) >= 4]

        print(f"📋 {format_type.upper()} Results:")

        for i, var in enumerate(test_variations):
            row_idx = var.get('original_row_index', 0)
            question = data.iloc[row_idx]['question']

            print(f"\n   Test Question {i + 1} (Row {row_idx}):")
            print(f"   Q: {question}")

            # Extract few-shot examples
            conversation = var.get('conversation', [])
            few_shot_questions = []

            if conversation:
                for msg in conversation:
                    if msg['role'] == 'user':
                        content = msg['content']
                        # Find all questions in the content
                        lines = content.split('\n')
                        for line in lines:
                            if line.startswith('Question:') and line != f"Question: {question}":
                                few_shot_questions.append(line.replace('Question: ', ''))

            print(f"   Few-shot examples:")
            for j, fs_q in enumerate(few_shot_questions):
                print(f"     {j + 1}. {fs_q}")

        # Export for this format
        ps.export(f"few_shot_{format_type}_analysis.json", format="json")

    print(f"\n" + "=" * 60)
    print("🔍 ANALYSIS SUMMARY")
    print("=" * 60)

    print("📊 Expected Behavior:")
    print("   SAME_EXAMPLES__SYNCHRONIZED_ORDER_VARIATIONS format:")
    print("     - Should use the SAME 2 training examples for ALL test questions")
    print("     - Examples: Always questions 0,1 (France, Germany)")
    print()
    print("   DIFFERENT_EXAMPLES__DIFFERENT_ORDER_PER_VARIATION format:")
    print("     - Should use DIFFERENT training examples for each test question")
    print("     - Based on random_state=current_row_idx")
    print("     - Each test question gets different training examples")

    print("\n💡 Key Points to Verify:")
    print("   1. Does 'same_examples__synchronized_order_variations' really use the same examples for all test questions?")
    print("   2. Does 'different_examples__different_order_per_variation' use different examples for each test question?")
    print("   3. Are only TRAIN examples used (no test examples in few-shot)?")
    print("   4. Is the current question excluded from few-shot examples?")

    print("\n✅ Check the exported JSON files for detailed analysis!")


def example_few_shot_use_as_variations():
    """Test the new generate_variations parameter for few-shot configuration."""
    print("\n" + "=" * 60)
    print("🧪 Testing generate_variations Parameter for Few-Shot")
    print("=" * 60)

    # Create dataset with train/test split - 10 train examples, 2 test examples
    data = pd.DataFrame({
        'question': [
            # Training examples (10 examples)
            'What is the capital of France?',
            'What is the capital of Germany?', 
            'What is the capital of Italy?',
            'What is the capital of Spain?',
            'What is the capital of UK?',
            'What is the capital of Japan?',
            'What is the capital of China?',
            'What is the capital of Russia?',
            'What is the capital of Brazil?',
            'What is the capital of Canada?',
            # Test examples (2 examples)
            'What is the capital of Australia?',
            'What is the capital of India?'
        ],
        'options': [
            # Training options (as lists)
            ['London', 'Paris', 'Berlin', 'Madrid'],
            ['Paris', 'Berlin', 'Rome', 'Madrid'],
            ['Berlin', 'Rome', 'Paris', 'London'],
            ['Madrid', 'Paris', 'Berlin', 'Rome'],
            ['London', 'Berlin', 'Paris', 'Madrid'],
            ['Tokyo', 'Beijing', 'Seoul', 'Bangkok'],
            ['Beijing', 'Tokyo', 'Seoul', 'Bangkok'],
            ['Moscow', 'Kiev', 'Warsaw', 'Prague'],
            ['Brasilia', 'Rio de Janeiro', 'São Paulo', 'Salvador'],
            ['Ottawa', 'Toronto', 'Montreal', 'Vancouver'],
            # Test options (as lists)
            ['Sydney', 'Canberra', 'Melbourne', 'Perth'],
            ['New Delhi', 'Mumbai', 'Kolkata', 'Chennai']
        ],
        'answer': [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],  # Correct answer indices
        'split': ['train'] * 6 + ['test'] * 6
    })

    print(f"📊 Dataset Overview:")
    print(f"   - Total examples: {len(data)}")
    print(f"   - Train examples: {len(data[data['split'] == 'train'])}")
    print(f"   - Test examples: {len(data[data['split'] == 'test'])}")

    # Test 1: Regular few-shot with variations (generate_variations=True, default)
    print("\n" + "=" * 40)
    print("🔧 Test 1: Regular few-shot WITH variations (generate_variations=True)")
    print("=" * 40)

    ps1 = PromptSuite()
    ps1.load_dataframe(data)

    template_with_variations = {
        INSTRUCTION: 'Answer the following geography questions.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
        OPTIONS_KEY: [SHUFFLE_VARIATION, ENUMERATE_VARIATION],
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        },
        FEW_SHOT_KEY: {
            'count': 2,
            'format': 'different_examples__different_order_per_variation',  # different examples, different order
            'split': 'train',
        }
    }

    ps1.set_template(template_with_variations)
    ps1.configure(max_rows=2, variations_per_field=5, max_variations_per_row=10)  # Should get 5 variations per test question

    variations_with = ps1.generate(verbose=True)

    print(f"✅ Generated {len(variations_with)} variations WITH few-shot variations")
    
    # Count variations per test row
    test_row_counts_with = {}
    for var in variations_with:
        row_idx = var.get('original_row_index', 0)
        if row_idx >= 10:  # Test rows are 10, 11
            test_row_counts_with[row_idx] = test_row_counts_with.get(row_idx, 0) + 1

    print(f"📊 Variations per test row (WITH variations):")
    for row_idx in sorted(test_row_counts_with.keys()):
        count = test_row_counts_with[row_idx]
        print(f"   - Test Row {row_idx}: {count} variations")

    # Test 2: Few-shot without variations (generate_variations=False)
    print("\n" + "=" * 40)
    print("🔧 Test 2: Few-shot WITHOUT variations (generate_variations=False)")
    print("=" * 40)

    ps2 = PromptSuite()
    ps2.load_dataframe(data)

    template_without_variations = {
        INSTRUCTION: 'Answer the following geography questions.',
        PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
        # No field variations - only few-shot without variations
        GOLD_KEY: {
            'field': 'answer',
            'type': 'index',
            'options_field': 'options'
        },
        FEW_SHOT_KEY: {
            'count': 2,
            'format': 'same_examples__no_variations',  # Same examples, different order
            'split': 'train',
            'generate_variations': False  # NEW - don't generate variations
        }
    }

    ps2.set_template(template_without_variations)
    ps2.configure(max_rows=4, variations_per_field=1, max_variations_per_row=2)  # Should get only 1 variation per test question

    variations_without = ps2.generate(verbose=True)

    print(f"✅ Generated {len(variations_without)} variations WITHOUT few-shot variations")
    
    # Count variations per test row
    test_row_counts_without = {}
    for var in variations_without:
        row_idx = var.get('original_row_index', 0)
        if row_idx >= 10:  # Test rows are 10, 11
            test_row_counts_without[row_idx] = test_row_counts_without.get(row_idx, 0) + 1

    print(f"📊 Variations per test row (WITHOUT variations):")
    for row_idx in sorted(test_row_counts_without.keys()):
        count = test_row_counts_without[row_idx]
        print(f"   - Test Row {row_idx}: {count} variations")

    # Test 3: Verify that few-shot examples are different between test questions
    print("\n" + "=" * 40)
    print("🔍 Test 3: Verify few-shot examples are different per test question")
    print("=" * 40)

    # Get the variations for each test row (without variations)
    test_row_10_var = None
    test_row_11_var = None
    
    for var in variations_without:
        row_idx = var.get('original_row_index', 0)
        if row_idx == 10:
            test_row_10_var = var
        elif row_idx == 11:
            test_row_11_var = var

    if test_row_10_var and test_row_11_var:
        print(f"📋 Test Row 10 (Question: {data.iloc[10]['question']}):")
        conversation_10 = test_row_10_var.get('conversation', [])
        few_shot_examples_10 = []
        for msg in conversation_10:
            if msg['role'] == 'user' and 'Question:' in msg['content']:
                lines = msg['content'].split('\n')
                for line in lines:
                    if line.startswith('Question:') and line != f"Question: {data.iloc[10]['question']}":
                        few_shot_examples_10.append(line.replace('Question: ', ''))

        print(f"   Few-shot examples:")
        for i, example in enumerate(few_shot_examples_10):
            print(f"     {i+1}. {example}")

        print(f"\n📋 Test Row 11 (Question: {data.iloc[11]['question']}):")
        conversation_11 = test_row_11_var.get('conversation', [])
        few_shot_examples_11 = []
        for msg in conversation_11:
            if msg['role'] == 'user' and 'Question:' in msg['content']:
                lines = msg['content'].split('\n')
                for line in lines:
                    if line.startswith('Question:') and line != f"Question: {data.iloc[11]['question']}":
                        few_shot_examples_11.append(line.replace('Question: ', ''))

        print(f"   Few-shot examples:")
        for i, example in enumerate(few_shot_examples_11):
            print(f"     {i+1}. {example}")

        # Check if they're different
        if set(few_shot_examples_10) != set(few_shot_examples_11):
            print(f"\n✅ SUCCESS: Few-shot examples are DIFFERENT between test questions")
        else:
            print(f"\n❌ FAILED: Few-shot examples are the SAME between test questions")

    # Export results
    ps1.export("few_shot_with_variations.json", format="json")
    ps2.export("few_shot_without_variations.json", format="json")

    print(f"\n" + "=" * 60)
    print("📊 EXPECTED RESULTS SUMMARY")
    print("=" * 60)

    print("✅ With generate_variations=True (default):")
    print("   - Should generate multiple variations per test question")
    print("   - Each variation has different few-shot examples")
    print(f"   - Expected: ~5 variations per test question = ~10 total")
    print(f"   - Actual: {len(variations_with)} total variations")

    print("\n✅ With generate_variations=False (new feature):")
    print("   - Should generate only 1 variation per test question")
    print("   - Each test question gets different few-shot examples")
    print("   - But no variations of the few-shot examples")
    print(f"   - Expected: 1 variation per test question = 2 total")
    print(f"   - Actual: {len(variations_without)} total variations")

    print("\n💡 Key Benefits of generate_variations=False:")
    print("   1. Each example gets unique few-shot examples (random_per_row)")
    print("   2. No redundant variations of few-shot examples")
    print("   3. Faster generation with fewer variations")
    print("   4. Still maintains few-shot diversity between questions")

    print("\n✅ Test completed! Check exported JSON files for detailed analysis.")


def example_preserve_original_data():
    """Example demonstrating preservation of original data columns in the output."""
    print("\n=== Preserve Original Data Example ===")
    print("📊 Showing how original data columns are preserved in variations")
    
    # Create sample data with a category column that we want to preserve
    data = pd.DataFrame({
        'question': [
            'What is the capital of France?',
            'What is 2+2?',
            'Which planet is closest to the Sun?'
        ],
        'category': [
            'Geography',
            'Mathematics', 
            'Astronomy'
        ],
        'difficulty': [
            'Easy',
            'Easy',
            'Medium'
        ],
        'source': [
            'World Knowledge',
            'Basic Math',
            'Space Science'
        ],
        'answer': [
            'Paris',
            '4', 
            'Mercury'
        ]
    })
    
    print(f"📝 Original Dataset:")
    print(data.to_string(index=False))
    
    ps = PromptSuite()
    ps.load_dataframe(data)
    
    # Simple template that only varies the question, but we want to preserve all other columns
    template = {
        INSTRUCTION: "You are a helpful and harmless AI assistant. Please respond to the following request carefully.",
        PROMPT_FORMAT: f"User: {{{QUESTION_KEY}}}",
        QUESTION_KEY: [FORMAT_STRUCTURE_VARIATION],  # Only vary the question
        GOLD_KEY: 'answer'
    }
    
    ps.set_template(template)
    print("\n✅ Template configured to vary only the question field")
    print("   - category, difficulty, source columns are NOT in the template")
    print("   - But they should still appear in the output!")
    
    # Configure generation
    ps.configure(
        max_rows=3,
        variations_per_field=2,
        max_variations_per_row=4,
        random_seed=42
    )
    
    # Generate variations
    variations = ps.generate(verbose=True)
    
    print(f"\n✅ Generated {len(variations)} variations")
    
    # Show how original data is preserved
    print("\n📋 Original Data Preservation Analysis:")
    print("=" * 60)
    
    for i, variation in enumerate(variations[:3]):
        row_idx = variation.get('original_row_index', 0)
        original_data = variation.get('original_row_data', {})
        field_values = variation.get('field_values', {})
        
        print(f"\n🔍 Variation {i+1} (from row {row_idx}):")
        print(f"   Original question: {original_data.get('question', 'N/A')}")
        print(f"   Varied question:   {field_values.get('question', 'N/A')}")
        print(f"   Category:          {original_data.get('category', 'N/A')}")
        print(f"   Difficulty:        {original_data.get('difficulty', 'N/A')}")
        print(f"   Source:            {original_data.get('source', 'N/A')}")
        print(f"   Answer:            {original_data.get('answer', 'N/A')}")
        
        print(f"\n   Generated Prompt:")
        print(f"   {variation.get('prompt', 'N/A')}")
        
        # Show if data is properly preserved
        if original_data:
            print(f"   ✅ Original data preserved: {len(original_data)} fields")
        else:
            print(f"   ❌ Original data missing!")
    
    # Also show a sample of the raw variation structure
    if variations:
        print(f"\n🔍 Raw Variation Structure (first variation):")
        sample_var = variations[0]
        print(f"   Keys in variation: {list(sample_var.keys())}")
        if 'original_row_data' in sample_var:
            print(f"   Original row data keys: {list(sample_var['original_row_data'].keys())}")
        else:
            print(f"   ⚠️ 'original_row_data' key missing!")
    
    # Export results
    ps.export("preserve_original_data_example.json", format="json")
    print(f"\n✅ Exported to preserve_original_data_example.json")
    
    # Show the structure of the exported data
    print(f"\n📁 Exported JSON Structure:")
    print(f"   Each variation now contains:")
    print(f"   - 'original_row_data': All original columns from the dataset")
    print(f"   - 'field_values': Only the fields that were varied")
    print(f"   - 'prompt': The generated prompt")
    print(f"   - 'conversation': Conversation format")
    print(f"   - 'gold_updates': Any gold field updates")
    
    print(f"\n💡 Use Case:")
    print(f"   - You can now filter/group variations by category, difficulty, etc.")
    print(f"   - Original metadata is preserved for downstream analysis")
    print(f"   - No information is lost from the original dataset")
    
    return variations


if __name__ == "__main__":
    # Run the new preserve original data example
    # example_preserve_original_data()
    
    # Run the new unordered random few-shot example
    # example_few_shot_unordered_random()
    example_platform_switching()

    # Run the new list data support example first
    # example_list_data_support()

    # Run the new test first
    # test_enumerated_gold_in_few_shot()

    # Run the debug example
    # example_few_shot_train_test_split()
    # example_few_shot_random_per_row_vs_ordered_2()

    # # example_complex_template_debug()
    # example_many_augmenters_on_small_dataset()
    # # Uncomment other examples as needed:
    # example_shuffle_template()
    # example_with_sample_data_few_shot()
    # example_with_enumerate()
    # example_enumerate_types()
    # example_enumerate_as_field_variation()
    # example_with_system_prompt_few_shot()
    # example_platform_switching()
    # example_with_huggingface()
    # example_different_templates()
    # example_gold_field_formats()
    # example_environment_variables()
    # example_with_simple_qa()
    # example_system_prompt_with_placeholder()
    # example_system_prompt_with_placeholder_and_few_shot()

    # Run context examples
    # example_simple_context_variations()  # Works without API key
    # example_system_prompt_with_context_and_few_shot()  # Full context example

    # example_many_augmenters_on_small_dataset()
    # example_paraphrase_instruction_only()

    # New specialized augmenter examples
    # example_format_structure()  # Semantic-preserving format variations
    # example_typos_and_noise()  # Robustness testing with noise injection
    # example_combined_specialized_augmenters()  # Both augmenters together
    # example_backward_compatibility_rewording()  # Backward compatibility with REWORDING

    print("\n🎉 All examples completed!")
    print("\n✨ NEW FEATURE: Original Data Preservation")
    print("   - All original columns from your dataset are now preserved in variations")
    print("   - Check 'original_row_data' field in exported JSON for complete original data")
    print("   - No information is lost, even for columns not used in templates")
    print("   - Perfect for maintaining metadata like categories, difficulty levels, etc.")
