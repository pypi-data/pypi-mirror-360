
import os
from appdirs import user_data_dir

from google.genai import Client, types
from google.api_core.exceptions import ResourceExhausted
from google.genai.types import HarmBlockThreshold, ContentEmbedding
import google.genai

# VARIABLES

# Safety values

BLOCK_NONE = "BLOCK NONE"
BLOCK_FEW = "BLOCK FEW"
BLOCK_MORE = "BLOCK MORE"
BLOCK_MOST = "BLOCK MOST"

SAFETY_VALUE_TO_GEMINI_VALUE = {
    BLOCK_NONE: HarmBlockThreshold.BLOCK_NONE,
    BLOCK_FEW: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    BLOCK_MORE: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    BLOCK_MOST: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
}

# Model info

ALL_MODELS = [
"gemini-2.5-pro",
"gemini-2.5-flash",
"gemini-2.5-flash-lite-preview-06-17",
"gemini-2.5-flash-preview-tts",
"gemini-2.5-pro-preview-tts",

"gemini-2.0-flash",
"gemini-2.0-flash-preview-image-generation",
"gemini-2.0-flash-lite",

"gemini-1.5-flash",
"gemini-1.5-flash-8b",
"gemini-1.5-pro",

"gemma-3-1b-it",
"gemma-3-4b-it",
"gemma-3-12b-it",
"gemma-3-27b-it",
"gemma-3n-e4b-it",

"gemini-embedding-exp-03-07",
"text-embedding-004",
"embedding-001",
]

CODE_EXECUTION_AVAILABLE = "CODE EXECUTION AVAILABLE"
THINKING_AVAILABLE = "THINKING AVAILABLE"
THINKING_BUDGET_AVAILABLE = "THINKING BUDGET AVAILABLE"
GROUNDING_AVAILABLE = "GROUNDING AVAILABLE"
URL_CONTEXT_AVAILABLE = "URL CONTEXT AVAILABLE"

TEXT_GEN_AVAILABLE = "TEXT GENERATION AVAILABLE"
IMAGE_GEN_AVAILABLE = "IMAGE GENERATION AVAILABLE"
TTS_GEN_AVAILABLE = "TEXT-TO-SPEECH GENERATION AVAILABLE"
TEXT_EMBEDDING_AVAILABLE = "TEXT EMBEDDING AVAILABLE"

MODELS_TO_FEATURES = {
"gemini-2.5-pro":
    [TEXT_GEN_AVAILABLE, CODE_EXECUTION_AVAILABLE, THINKING_AVAILABLE, THINKING_BUDGET_AVAILABLE, GROUNDING_AVAILABLE, URL_CONTEXT_AVAILABLE],
"gemini-2.5-flash":
    [TEXT_GEN_AVAILABLE, CODE_EXECUTION_AVAILABLE, THINKING_AVAILABLE, THINKING_BUDGET_AVAILABLE, GROUNDING_AVAILABLE, URL_CONTEXT_AVAILABLE],
"gemini-2.5-flash-lite-preview-06-17":
    [TEXT_GEN_AVAILABLE, CODE_EXECUTION_AVAILABLE, THINKING_AVAILABLE, GROUNDING_AVAILABLE, URL_CONTEXT_AVAILABLE],
"gemini-2.5-flash-preview-tts": [TTS_GEN_AVAILABLE],
"gemini-2.5-pro-preview-tts": [TTS_GEN_AVAILABLE],

"gemini-2.0-flash": [TEXT_GEN_AVAILABLE, CODE_EXECUTION_AVAILABLE, GROUNDING_AVAILABLE, URL_CONTEXT_AVAILABLE],
"gemini-2.0-flash-preview-image-generation": [IMAGE_GEN_AVAILABLE],
"gemini-2.0-flash-lite": [TEXT_GEN_AVAILABLE],

"gemini-1.5-flash": [TEXT_GEN_AVAILABLE, CODE_EXECUTION_AVAILABLE, GROUNDING_AVAILABLE],
"gemini-1.5-flash-8b": [TEXT_GEN_AVAILABLE, CODE_EXECUTION_AVAILABLE, GROUNDING_AVAILABLE],
"gemini-1.5-pro": [TEXT_GEN_AVAILABLE, CODE_EXECUTION_AVAILABLE, GROUNDING_AVAILABLE],

"gemma-3-1b-it": [TEXT_GEN_AVAILABLE],
"gemma-3-4b-it": [TEXT_GEN_AVAILABLE],
"gemma-3-12b-it": [TEXT_GEN_AVAILABLE],
"gemma-3-27b-it": [TEXT_GEN_AVAILABLE],
"gemma-3n-e4b-it": [TEXT_GEN_AVAILABLE],

"gemini-embedding-exp-03-07": [TEXT_EMBEDDING_AVAILABLE],
"text-embedding-004": [TEXT_EMBEDDING_AVAILABLE],
"embedding-001": [TEXT_EMBEDDING_AVAILABLE],
}

# Mutually exclusive feature pairs. These are feature that cannot be used together in the same request.
MUTUALLY_EXCLUSIVE_FEATURE_PAIRS = {
    "gemini-2.5-pro": [
        (CODE_EXECUTION_AVAILABLE, THINKING_AVAILABLE),
    ],
    "gemini-2.5-flash": [
        (CODE_EXECUTION_AVAILABLE, THINKING_AVAILABLE),
    ],
    "gemini-2.0-flash": [
        (CODE_EXECUTION_AVAILABLE, GROUNDING_AVAILABLE),
        (CODE_EXECUTION_AVAILABLE, URL_CONTEXT_AVAILABLE),
    ],

    "gemini-1.5-flash": [
        (CODE_EXECUTION_AVAILABLE, GROUNDING_AVAILABLE),
    ],
    "gemini-1.5-pro": [
        (CODE_EXECUTION_AVAILABLE, GROUNDING_AVAILABLE),
    ],
    "gemini-1.5-flash-8b": [
        (CODE_EXECUTION_AVAILABLE, GROUNDING_AVAILABLE),
    ],
}

assert len(MODELS_TO_FEATURES.keys()) == len(ALL_MODELS), "Models and features mismatch. Please check the models and features."

# Supported file types

SUPPORTED_IMAGE_TYPES = [
    "png",
    "jpeg",
    "jpg",
    "webp",
]

IMAGE_TYPE_TO_MIME_TYPE = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "webp": "image/webp"
}

ALL_SUPPORTED_FILE_TYPES = [
    "c", "cpp", "py", "java", "php", "sql", "html",
    "doc", "docx", "pdf", "rtf", "dot", "dotx", "hwp", "hwpx",
    "gdoc",
    "txt",
    "pptx",
    "gslides",
    "xls", "xlsx",
    "gsheet",
    "csv", "tsv"
]

ALL_TTS_VOICES = [
    "Zephyr", "Puck", "Charon",
    "Kore", "Fenrir", "Leda",
    "Orus", "Aoede", "Callirrhoe",
    "Autonoe", "Enceladus", "Iapetus",
    "Umbriel", "Algieba", "Despina",
    "Erinome", "Algenib", "Rasalgethi",
    "Laomedeia", "Achernar", "Alnilam",
    "Schedar", "Gacrux", "Pulcherrima",
    "Achird", "Zubenelgenubi", "Vindemiatrix",
    "Sadachbia", "Sadaltager", "Sulafat"
]

# Text constants

USER = "USER"
ASSISTANT = "ASSISTANT"

# Rate limits

APP_NAME = "gemspeak"
BASE_DIR = user_data_dir(APP_NAME)
API_KEYS_PATH = os.path.join(BASE_DIR, "api_keys.txt")

# API keys

# Read the API keys from the file
if not os.path.exists(API_KEYS_PATH):
    # Create the directory if it doesn't exist
    os.makedirs(BASE_DIR, exist_ok=True)
    # Create the file with an empty list
    with open(API_KEYS_PATH, "w") as file:
        file.write("")
with open(API_KEYS_PATH, "r") as file:
    API_KEYS = file.read().strip().split("\n")

# FUNCTIONS

def add_api_keys(api_keys:list):
    """
    Adds API keys to the API keys file.
    param api_keys: A list of API keys to add.
    """
    with open(API_KEYS_PATH, "a") as file:
        for key in api_keys:
            file.write(f"{key.strip()}\n")
