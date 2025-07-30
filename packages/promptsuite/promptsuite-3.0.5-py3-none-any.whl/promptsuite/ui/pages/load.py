import sys
from pathlib import Path
import base64

import streamlit as st

# Add the src directory to the path to import promptsuite
base_dir = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(base_dir))

from promptsuite.core import SHUFFLE_VARIATION
from promptsuite.ui.pages import (
    upload_data,
    template_builder,
    generate_variations
)
from promptsuite.ui.utils.progress_indicator import show_progress_indicator
from promptsuite.core.template_keys import (
    CONTEXT_KEY,
    PARAPHRASE_WITH_LLM,
    INSTRUCTION, PROMPT_FORMAT, PROMPT_FORMAT_VARIATIONS, INSTRUCTION_VARIATIONS, GOLD_KEY, FEW_SHOT_KEY, OPTIONS_KEY,
    QUESTION_KEY, FORMAT_STRUCTURE_VARIATION, TYPOS_AND_NOISE_VARIATION, ENUMERATE_VARIATION
)


def get_logo_base64(logo_path):
    """Convert logo image to base64 string for HTML embedding"""
    try:
        with open(logo_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""


def main():
    """Main Streamlit app for PromptSuite 2.0"""
    # Set up page configuration
    st.set_page_config(
        layout="wide",
        page_title="PromptSuite 2.0 - Multi-Prompt Dataset Generator",
        page_icon="🚀"
    )

    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stProgress .st-bo {
        background-color: #f0f2f6;
    }
    .step-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # App header with logo replacing rocket emoji
    logo_path = Path(__file__).parent.parent.parent.parent.parent / "logo.png"
    
    # Create inline header with logo instead of rocket emoji
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 15px;">
            <img src="data:image/png;base64,{get_logo_base64(logo_path) if logo_path.exists() else ''}" 
                 alt="PromptSuite Logo" style="width: 50px; height: 50px;">
            <h1 style="margin: 0; font-size: 2.5rem; color: #1f77b4;">PromptSuite 2.0</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h3>A Universal Toolkit for Multi-Prompt Evaluation</h3>
        <p style="color: #666;">Create variations of your prompts using template-based transformations</p>
    </div>
    """, unsafe_allow_html=True)

    # Retrieve query parameters
    params = st.query_params
    start_step = int(params.get("step", ["1"])[0])
    debug_mode = params.get("debug", ["False"])[0].lower() == "true"

    # Initialize session state
    initialize_session_state(start_step, debug_mode)

    # Debug mode removed for cleaner interface

    # Total number of pages in the simplified application
    total_pages = 3

    # Display the progress indicator
    current_page = st.session_state.page
    show_progress_indicator(current_page, total_pages)

    # Render the appropriate page
    render_current_page(current_page)


def initialize_session_state(start_step=1, debug_mode=False):
    """Initialize the session state for navigation"""
    defaults = {
        'page': start_step,
        'debug_mode': debug_mode,
        'data_loaded': False,
        'template_ready': False,
        'variations_generated': False,
        'template_suggestions': {
            # Sentiment Analysis Templates
            'sentiment_analysis': {
                'category_name': 'Sentiment Analysis',
                'description': 'Templates for text sentiment classification tasks',
                'templates': [
                    {
                        'name': 'Basic Sentiment Analysis',
                        'template': {
                            INSTRUCTION: 'Classify the sentiment of the following text.',
                            PROMPT_FORMAT: 'Text: "{text}"\nSentiment: {label}',
                            PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION],
                            'text': [TYPOS_AND_NOISE_VARIATION],
                            GOLD_KEY: {
                                'field': 'label',
                                'type': 'value'
                            }
                        },
                        'description': 'Sentiment classification with format structure and noise injection variations',
                        'sample_data': {
                            'text': ['I love this movie!', 'This book is terrible.', 'The weather is nice today.'],
                            'label': ['positive', 'negative', 'neutral']
                        }
                    },
                    {
                        'name': 'Advanced Sentiment with Few-shot',
                        'template': {
                            INSTRUCTION: 'Classify the sentiment of the following text.',
                            PROMPT_FORMAT: 'Text: "{text}"\nSentiment: {label}',
                            PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION],
                            'text': [TYPOS_AND_NOISE_VARIATION, CONTEXT_KEY],
                            GOLD_KEY: {
                                'field': 'label',
                                'type': 'value'
                            },
                            FEW_SHOT_KEY: {
                                'count': 2,
                                'format': 'same_examples__no_variations',
                                'split': 'all'
                            }
                        },
                        'description': 'Sentiment analysis with format structure, noise injection, and context variations',
                        'sample_data': {
                            'text': ['I absolutely love this product!', 'This is the worst service ever!',
                                     'It\'s okay, nothing special', 'Amazing quality!'],
                            'label': ['positive', 'negative', 'neutral', 'positive']
                        }
                    }
                ]
            },

            # Question Answering Templates
            'question_answering': {
                'category_name': 'Question Answering',
                'description': 'Templates for question-answer tasks',
                'templates': [
                    {
                        'name': 'Basic Q&A',
                        'template': {
                            INSTRUCTION: 'Please answer the following question.',
                            PROMPT_FORMAT: 'question: {question}\nanswer: {answer}',
                            PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION],
                            QUESTION_KEY: [TYPOS_AND_NOISE_VARIATION],
                            GOLD_KEY: {
                                'field': 'answer',
                                'type': 'value'
                            }
                        },
                        'description': 'Q&A with format structure and noise injection variations',
                        'sample_data': {
                            'question': ['What is the capital of France?', 'How many days in a week?',
                                         'Who wrote Romeo and Juliet?'],
                            'answer': ['Paris', '7', 'Shakespeare']
                        }
                    },
                    {
                        'name': 'Q&A with Context and Few-shot',
                        'template': {
                            INSTRUCTION: 'Based on the context, answer the question.',
                            INSTRUCTION_VARIATIONS: [PARAPHRASE_WITH_LLM],
                            PROMPT_FORMAT: 'Context: {context}\nQuestion: {question}\nAnswer: {answer}',
                            PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION],
                            QUESTION_KEY: [TYPOS_AND_NOISE_VARIATION],
                            CONTEXT_KEY: [CONTEXT_KEY],
                            GOLD_KEY: {
                                'field': 'answer',
                                'type': 'value'
                            },
                            FEW_SHOT_KEY: {
                                'count': 3,
                                'format': 'same_examples__no_variations',
                                'split': 'all'
                            }
                        },
                        'description': 'Q&A with format structure, noise injection, and context variations',
                        'sample_data': {
                            'question': ['What is 12+8?', 'What is 15-7?', 'What is 6*4?', 'What is 20/5?',
                                         'What is 9*3?'],
                            'answer': ['20', '8', '24', '4', '27'],
                            'context': ['Mathematics', 'Arithmetic', 'Basic math', 'Numbers', 'Calculation']
                        }
                    }
                ]
            },

            # Multiple Choice Templates
            'multiple_choice': {
                'category_name': 'Multiple Choice',
                'description': 'Templates for multiple choice question tasks',
                'templates': [
                    {
                        'name': 'Basic Multiple Choice',
                        'template': {
                            INSTRUCTION: 'The following are multiple choice questions (with answers) about {subject}.',
                            PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
                            PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION],
                            GOLD_KEY: {
                                'field': 'answer',
                                'type': 'index',  # 'index' or 'value'
                                'options_field': 'options'  # Field containing the list to shuffle
                            },
                            'enumerate': {
                                'field': 'options',
                                'type': '1234'
                            }
                        },
                        'description': 'Multiple choice with format structure variations and option shuffling',
                        'sample_data': {
                            'question': ['What is the largest planet?', 'Which element has symbol O?',
                                         'What is the fastest land animal?'],
                            'options': [['Mars', 'Earth', 'Jupiter', 'Venus'], ['Oxygen', 'Gold', 'Silver'], ['Lion', 'Cheetah', 'Horse']],
                            'answer': [2, 0, 1],  # Indices: Jupiter=2, Oxygen=0, Cheetah=1
                            'subject': ['astronomy', 'chemistry', 'biology']
                        }
                    },
                    {
                        'name': 'Multiple Choice with Paraphrased Instruction',
                        'template': {
                            INSTRUCTION: 'The following are multiple choice questions (with answers) about {subject}.',
                            INSTRUCTION_VARIATIONS: [PARAPHRASE_WITH_LLM],
                            PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
                            OPTIONS_KEY: [SHUFFLE_VARIATION],
                            GOLD_KEY: {
                                'field': 'answer',
                                'type': 'index',
                                'options_field': 'options'
                            },
                            'enumerate': {
                                'field': 'options',
                                'type': '1234'
                            }

                        },
                        'description': 'Multiple choice with LLM-paraphrased instruction, format structure, noise injection on question, and option shuffling',
                        'sample_data': {
                            'question': ['What is the largest planet?', 'Which element has symbol O?',
                                         'What is the fastest land animal?'],
                            'options': [['Mars', 'Earth', 'Jupiter', 'Venus'], ['Oxygen', 'Gold', 'Silver'], ['Lion', 'Cheetah', 'Horse']],
                            'answer': [2, 0, 1],
                            'subject': ['astronomy', 'chemistry', 'biology']
                        }
                    },
                    {
                        'name': 'Complex Multiple Choice with Few-shot',
                        'template': {
                            INSTRUCTION: 'The following are multiple choice questions (with answers).',
                            INSTRUCTION_VARIATIONS: [PARAPHRASE_WITH_LLM],
                            PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
                            PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION],
                            OPTIONS_KEY: [SHUFFLE_VARIATION, ENUMERATE_VARIATION],
                            GOLD_KEY: {
                                'field': 'answer',
                                'type': 'index',
                                'options_field': 'options'
                            },
                            FEW_SHOT_KEY: {
                                'count': 2,
                                'format': 'different_examples__different_order_per_variation',
                                'split': 'all'
                            }
                        },
                        'description': 'Multiple choice with LLM-paraphrased instruction, format structure, option shuffling, enumeration, and random per row few-shot examples from train split.',
                        'sample_data': {
                            'question': ['What is the largest planet?', 'Which element has symbol O?',
                                         'What is the fastest land animal?', 'What is the smallest prime number?'],
                            'options': [['Mars', 'Earth', 'Jupiter', 'Venus'], ['Oxygen', 'Gold', 'Silver'], ['Lion', 'Cheetah', 'Horse'],
                                        ['1', '2', '3']],
                            'answer': [2, 0, 1, 1]  # Indices: Jupiter=2, Oxygen=0, Cheetah=1, 2=1
                        }
                    },
                    {
                        'name': 'Multiple Choice with Lettered Enumeration',
                        'template': {
                            INSTRUCTION: 'The following are multiple choice questions (with answers).',
                            PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
                            QUESTION_KEY: [TYPOS_AND_NOISE_VARIATION],
                            GOLD_KEY: {
                                'field': 'answer',
                                'type': 'index',
                                'options_field': 'options'
                            },
                            'enumerate': {
                                'field': 'options',
                                'type': 'ABCD'
                            }
                        },
                        'description': 'Multiple choice with option shuffling and automatic letter enumeration',
                        'sample_data': {
                            'question': ['What is the largest planet?', 'Which element has symbol O?',
                                         'What is the fastest land animal?'],
                            'options': [['Mars', 'Earth', 'Jupiter', 'Venus'], ['Oxygen', 'Gold', 'Silver', 'Hydrogen'],
                                        ['Lion', 'Cheetah', 'Horse', 'Tiger']],
                            'answer': [2, 0, 1]  # Indices: Jupiter=2, Oxygen=0, Cheetah=1
                        }
                    },
                    {
                        'name': 'Multiple Choice with Shuffling and Enumeration',
                        'template': {
                            INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
                            PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
                            OPTIONS_KEY: [SHUFFLE_VARIATION, ENUMERATE_VARIATION],
                            GOLD_KEY: {
                                'field': 'answer',
                                'type': 'index',
                                'options_field': 'options'
                            }
                        },
                        'description': 'Multiple choice with option shuffling and automatic enumeration',
                        'sample_data': {
                            'question': ['What is the largest planet?', 'Which element has symbol O?',
                                         'What is the fastest land animal?'],
                            'options': [['Mars', 'Earth', 'Jupiter', 'Venus'], ['Oxygen', 'Gold', 'Silver'], ['Lion', 'Cheetah', 'Horse']],
                            'answer': [2, 0, 1]
                        }
                    }
                ]
            },

            # Text Classification Templates
            'text_classification': {
                'category_name': 'Text Classification',
                'description': 'Templates for text classification and intent detection tasks',
                'templates': [
                    {
                        'name': 'Basic Text Classification',
                        'template': {
                            INSTRUCTION: 'Classify the following text into a category.',
                            PROMPT_FORMAT: 'Text: "{text}"\nCategory: {category}',
                            'text': [FORMAT_STRUCTURE_VARIATION, TYPOS_AND_NOISE_VARIATION],
                            GOLD_KEY: {
                                'field': 'category',
                                'type': 'value'
                            }
                        },
                        'description': 'Text classification with format structure and noise injection variations',
                        'sample_data': {
                            'text': ['Book a flight to Paris', 'Cancel my subscription', 'What is the weather today?'],
                            'category': ['travel', 'service', 'information']
                        }
                    },
                    {
                        'name': 'Multi-field Text Classification',
                        'template': {
                            INSTRUCTION: 'Classify the following text.',
                            PROMPT_FORMAT: 'Text: "{text}"\nCategory: {category}',
                            'text': [FORMAT_STRUCTURE_VARIATION, TYPOS_AND_NOISE_VARIATION, CONTEXT_KEY],
                            'category': [],  # No variations for output
                            GOLD_KEY: {
                                'field': 'category',
                                'type': 'value'
                            }
                        },
                        'description': 'Text classification with format structure, noise injection, and context variations',
                        'sample_data': {
                            'text': ['Book a flight to Paris', 'Cancel my subscription', 'What is the weather today?'],
                            'category': ['travel', 'service', 'information']
                        }
                    },
                    {
                        'name': 'Text Classification with Few-shot',
                        'template': {
                            INSTRUCTION: 'Classify the following text.',
                            PROMPT_FORMAT: 'Text: "{text}"\nCategory: {category}',
                            'text': [FORMAT_STRUCTURE_VARIATION, TYPOS_AND_NOISE_VARIATION],
                            GOLD_KEY: {
                                'field': 'category',
                                'type': 'value'
                            },
                            FEW_SHOT_KEY: {
                                'count': 3,
                                'format': 'shared_ordered_first_n',
                                'split': 'all'
                            }
                        },
                        'description': 'Text classification with format structure, noise injection, and ordered few-shot examples',
                        'sample_data': {
                            'text': ['Book a flight to Paris', 'Cancel my subscription', 'What is the weather today?',
                                     'Order pizza for dinner', 'Check my account balance'],
                            'category': ['travel', 'service', 'information', 'food', 'banking']
                        }
                    },
                    {
                        'name': 'Text Classification with Unordered Few-shot',
                        'template': {
                            INSTRUCTION: 'Classify the following text.',
                            PROMPT_FORMAT: 'Text: "{text}"\nCategory: {category}',
                            'text': [FORMAT_STRUCTURE_VARIATION, TYPOS_AND_NOISE_VARIATION],
                            GOLD_KEY: {
                                'field': 'category',
                                'type': 'value'
                            },
                            FEW_SHOT_KEY: {
                                'count': 3,
                                'format': 'shared_unordered_random_n',
                                'split': 'all'
                            }
                        },
                        'description': 'Text classification with same random examples but shuffled order for each row',
                        'sample_data': {
                            'text': ['Book a flight to Paris', 'Cancel my subscription', 'What is the weather today?',
                                     'Order pizza for dinner', 'Check my account balance'],
                            'category': ['travel', 'service', 'information', 'food', 'banking']
                        }
                    }
                ]
            },

            # Specialized Augmenters Templates
            'specialized_augmenters': {
                'category_name': 'Specialized Augmenters',
                'description': 'Templates showcasing specialized augmenters for prompt variations',
                'templates': [
                    {
                        'name': 'Format Structure, Shuffle & Enumerate',
                        'template': {
                            INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
                            PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
                            PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION],
                            OPTIONS_KEY: [SHUFFLE_VARIATION, ENUMERATE_VARIATION],
                            GOLD_KEY: {
                                'field': 'answer',
                                'type': 'index',
                                'options_field': 'options'
                            }
                        },
                        'description': 'Semantic-preserving format structure variations with option shuffling and automatic enumeration',
                        'sample_data': {
                            'question': ['What is the capital of France?', 'What is 2+2?'],
                            'options': [['London', 'Berlin', 'Paris', 'Madrid'], ['3', '4', '5', '6']],
                            'answer': [2, 1]  # 0-based indices
                        }
                    },
                    {
                        'name': 'Noise Injection, Shuffle & Enumerate',
                        'template': {
                            INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
                            PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
                            QUESTION_KEY: [TYPOS_AND_NOISE_VARIATION],
                            OPTIONS_KEY: [SHUFFLE_VARIATION, TYPOS_AND_NOISE_VARIATION, ENUMERATE_VARIATION],
                            GOLD_KEY: {
                                'field': 'answer',
                                'type': 'index',
                                'options_field': 'options'
                            }
                        },
                        'description': 'Robustness testing with noise injection on question and options, with option shuffling and automatic enumeration',
                        'sample_data': {
                            'question': ['What is the capital of France?', 'What is 2+2?'],
                            'options': [['London', 'Berlin', 'Paris', 'Madrid'], ['3', '4', '5', '6']],
                            'answer': [2, 1]  # 0-based indices
                        }
                    },
                    {
                        'name': 'Combined Format, Noise, Shuffle & Enumerate',
                        'template': {
                            INSTRUCTION: 'The following are multiple choice questions (with answers) about general knowledge.',
                            PROMPT_FORMAT: 'Question: {question}\nOptions: {options}\nAnswer: {answer}',
                            PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION],
                            QUESTION_KEY: [TYPOS_AND_NOISE_VARIATION],
                            OPTIONS_KEY: [SHUFFLE_VARIATION, TYPOS_AND_NOISE_VARIATION, ENUMERATE_VARIATION],
                            GOLD_KEY: {
                                'field': 'answer',
                                'type': 'index',
                                'options_field': 'options'
                            }
                        },
                        'description': 'Combined format structure and noise injection augmenters on prompt format and question, with option shuffling and automatic enumeration',
                        'sample_data': {
                            'question': ['What is the capital of France?', 'What is 2+2?'],
                            'options': [['London', 'Berlin', 'Paris', 'Madrid'], ['3', '4', '5', '6']],
                            'answer': [2, 1]  # 0-based indices
                        }
                    }
                ]
            },

            # Advanced Templates
            'advanced_examples': {
                'category_name': 'Advanced Examples',
                'description': 'Complex templates showcasing advanced features',
                'templates': [
                    {
                        'name': 'Multi-Variation Classification',
                        'template': {
                            INSTRUCTION: 'Classify the sentiment of the following text.',
                            PROMPT_FORMAT: 'Text: "{text}"\nLabel: {label}',
                            'text': [FORMAT_STRUCTURE_VARIATION, TYPOS_AND_NOISE_VARIATION, CONTEXT_KEY],
                            'label': [],
                            GOLD_KEY: {
                                'field': 'label',
                                'type': 'value'
                            },
                            FEW_SHOT_KEY: {
                                'count': 2,
                                'format': 'shared_ordered_first_n',
                                'split': 'all'
                            }
                        },
                        'description': 'Multiple variations per field with format structure, noise injection, and context',
                        'sample_data': {
                            'text': ['I love this movie!', 'This book is terrible.', 'The weather is nice today.'],
                            'label': ['positive', 'negative', 'neutral']
                        }
                    },
                    {
                        'name': 'Complex Q&A with Ordered Examples',
                        'template': {
                            INSTRUCTION: 'Answer the following question.',
                            PROMPT_FORMAT: 'Question: {question}\nAnswer: {answer}',
                            PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION],
                            QUESTION_KEY: [TYPOS_AND_NOISE_VARIATION, PARAPHRASE_WITH_LLM],
                            'answer': [],
                            GOLD_KEY: {
                                'field': 'answer',
                                'type': 'value'
                            },
                            FEW_SHOT_KEY: {
                                'count': 3,
                                'format': 'shared_ordered_first_n',
                                'split': 'train'
                            }
                        },
                        'description': 'Q&A with format structure, noise injection, and paraphrase variations',
                        'sample_data': {
                            'question': ['What is the capital of France?', 'How many days in a week?',
                                         'Who wrote Romeo and Juliet?'],
                            'answer': ['Paris', '7', 'Shakespeare']
                        }
                    }
                ]
            },

            # Add system prompt support to template suggestions and session state
            INSTRUCTION: {
                'category_name': 'System Prompt',
                'description': 'Templates with a system prompt for the first few-shot example',
                'templates': [
                    {
                        'name': 'Math QA with System Prompt',
                        'template': {
                            INSTRUCTION: 'You are a helpful math assistant. Answer clearly.',
                            PROMPT_FORMAT: 'Question: {question}\nAnswer: {answer}',
                            PROMPT_FORMAT_VARIATIONS: [FORMAT_STRUCTURE_VARIATION],
                            QUESTION_KEY: [TYPOS_AND_NOISE_VARIATION],
                            GOLD_KEY: 'answer',
                            FEW_SHOT_KEY: {
                                'count': 2,
                                'format': 'shared_ordered_first_n',
                                'split': 'all'
                            }
                        },
                        'description': 'Few-shot QA with format structure, noise injection, and system prompt',
                        'sample_data': {
                            'question': ['What is 2+2?', 'What is 3*3?', 'What is 5+3?'],
                            'answer': ['4', '9', '8']
                        }
                    }
                ]
            }
        }
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Debug mode functionality removed for cleaner user experience


def render_current_page(current_page):
    """Render the appropriate page based on the current state"""
    pages = {
        1: upload_data.render,
        2: template_builder.render,
        3: generate_variations.render
    }

    # Add navigation helper
    if current_page > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← Previous Step"):
                st.session_state.page = current_page - 1
                st.rerun()
        with col3:
            # Show next button only if current step is complete
            show_next = False
            if current_page == 1 and st.session_state.get('data_loaded', False):
                show_next = True
            elif current_page == 2 and st.session_state.get('template_ready', False):
                show_next = True
            elif current_page == 3 and st.session_state.get('variations_generated', False):
                show_next = True

            if show_next and current_page < 3:
                if st.button("Next Step →"):
                    st.session_state.page = current_page + 1
                    st.rerun()

    # Call the render function for the current page
    if current_page in pages:
        pages[current_page]()
    else:
        st.error(f"Page {current_page} not found!")


if __name__ == '__main__':
    main()
