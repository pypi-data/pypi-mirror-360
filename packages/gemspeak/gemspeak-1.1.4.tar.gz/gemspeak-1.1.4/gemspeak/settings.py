import abc

from .data import *

# SAFETY SETTINGS

class SafetySettings:
    def __init__(self,
                 harrassment=BLOCK_FEW,
                 hate_speech=BLOCK_FEW,
                 sexually_explicit=BLOCK_FEW,
                 dangerous_content=BLOCK_FEW,
                 civic_integrity=BLOCK_FEW
                 ):
        """
        Initializes the SafetySettings class.
        
        Use `gemspeak.data.BLOCK_NONE`, `gemspeak.data.BLOCK_FEW`, `gemspeak.data.BLOCK_SOME`, `gemspeak.data.BLOCK_MOST` to set the safety settings.

        Levels of blocking:
        - `"BLOCK NONE"`: No blocking.
        - `"BLOCK FEW"`: Block a few instances of harmful content.
        - `"BLOCK MORE"`: Block some instances of harmful content.
        - `"BLOCK MOST"`: Block most instances of harmful content.

        Parameters:
            harrassment (str): The level of harassment blocking.
            hate_speech (str): The level of hate speech blocking.
            sexually_explicit (str): The level of sexually explicit content blocking.
            dangerous_content (str): The level of dangerous content blocking.
            civic_integrity (str): The level of civic integrity blocking.
        
        For more information about safety settings, see the Gemini documentation:
        https://ai.google.dev/gemini-api/docs/safety-settings
        """

        self.harrassment = harrassment
        self.hate_speech = hate_speech
        self.sexually_explicit = sexually_explicit
        self.dangerous_content = dangerous_content
        self.civic_integrity = civic_integrity

    def to_settings(self):
        """
        Converts the SafetySettings to a list of `google.genai.types.SafetySetting` objects.
        
        Returns:
            A list of `google.genai.types.SafetySetting` objects with the safety settings.
        """
        return [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=SAFETY_VALUE_TO_GEMINI_VALUE[self.harrassment]
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=SAFETY_VALUE_TO_GEMINI_VALUE[self.hate_speech]
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=SAFETY_VALUE_TO_GEMINI_VALUE[self.sexually_explicit]
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=SAFETY_VALUE_TO_GEMINI_VALUE[self.dangerous_content]
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,
                threshold=SAFETY_VALUE_TO_GEMINI_VALUE[self.civic_integrity]
            )
        ]

    def __repr__(self):
        return f"SafetySettings(harrassment={self.harrassment}, hate_speech={self.hate_speech}, sexually_explicit={self.sexually_explicit}, dangerous={self.dangerous_content}, civic_integrity={self.civic_integrity})"

# BASE SETTINGS CLASS

class BaseSettings(abc.ABC):
    """
    This is a base class which includes the validate method.
    """
    def all_settings_none(self):
        """
        Sets all of the un-set settings to None for compatibility with the validate method
        """
        self.code_execution = getattr(self, 'code_execution', None)
        self.perform_thinking = getattr(self, 'perform_thinking', None)
        self.perform_grounding = getattr(self, 'perform_grounding', None)
        self.ignore_errors = getattr(self, 'ignore_errors', False)
        
    def validate(self, model:str):
        """
        Ensures that the settings are valid for the specified model.
        """
        if self.ignore_errors:
            return
        
        self.all_settings_none()  # Ensure all settings are set to None if not specified
        
        if model not in ALL_MODELS:
            raise ValueError(f"Model {model} is not a valid Gemini model. Available models: {ALL_MODELS}")
        
        # Get the available features and the selected features
        model_features = MODELS_TO_FEATURES[model]
        selected_features = [
            CODE_EXECUTION_AVAILABLE if self.code_execution else None,
            THINKING_AVAILABLE if self.perform_thinking else None,
            GROUNDING_AVAILABLE if self.perform_grounding else None,

            TEXT_GEN_AVAILABLE if isinstance(self, TextGenSettings) else None,
            IMAGE_GEN_AVAILABLE if isinstance(self, ImageGenSettings) else None,
            TTS_GEN_AVAILABLE if isinstance(self, SingleSpeakerTTSSettings) or isinstance(self, MultiSpeakerTTSSettings) else None,
            TEXT_EMBEDDING_AVAILABLE if isinstance(self, ContentEmbeddingSettings) else None
        ]

        # Gemini 2.5 Pro REQUIRES thinking. Add a special case for that (I will improve this later)
        if model == "gemini-2.5-pro" and not self.perform_thinking:
            raise Exception(f"The model 'gemini-2.5-pro' requires 'perform_thinking' to be enabeled.")

        # Perform the custom thinking mode "AUTO"
        if self.perform_thinking == "AUTO" and THINKING_AVAILABLE in model_features:
            selected_features.append(THINKING_AVAILABLE)

        # Check that all the selected features are available for the model
        for feature in selected_features:
            if feature and feature not in model_features:
                raise ValueError(f"Model {model} does not support {feature}. Available features: {model_features}")
            
        # Check each of the specific features
        if isinstance(self, SingleSpeakerTTSSettings):
            if not self.voice in ALL_TTS_VOICES:
                raise ValueError(f"Voice {self.voice} is not a valid TTS voice. Available voices: {ALL_TTS_VOICES}")
        elif isinstance(self, MultiSpeakerTTSSettings):
            for voice in self.voices:
                if not voice in ALL_TTS_VOICES:
                    raise ValueError(f"Voice {voice} is not a valid TTS voice. Available voices: {ALL_TTS_VOICES}")
                
        # Check for mutually exclusive features
        if model in MUTUALLY_EXCLUSIVE_FEATURE_PAIRS:
            for feature_pair in MUTUALLY_EXCLUSIVE_FEATURE_PAIRS[model]:
                if feature_pair[0] in selected_features and feature_pair[1] in selected_features:
                    raise ValueError(f"Model {model} does not support both {feature_pair[0]} and {feature_pair[1]} at the same time.")

# GEMINI SETTINGS CLASSES

class TextGenSettings(BaseSettings):
    def __init__(self,
                 code_execution:bool=False,
                 perform_thinking:bool | str="AUTO",
                 thinking_budget:int | None=None,
                 perform_grounding:bool=False,
                 grounding_threshold:float | None=False,
                 url_context:bool=False,
                 ignore_errors:bool=False,
                 safety_settings:SafetySettings=SafetySettings()
                 ):
        """
        Initializes the TextGenSettings class.

        Parameters:
            code_execution (bool): Whether to allow code execution.
            perform_thinking (bool): Whether to allow the model to think before generating a response. Set to "AUTO" to enable if available. Only available for Gemini 2.5.
            thinking_budget (int | None): The maximum number of tokens the model can use for thinking. If None, the model will use the default budget.
                Only available for Gemini 2.5 Flash Preview and Gemini 2.5 Pro Preview. (Not experimental versions)
            perform_grounding (bool): Whether to perform google search grounding, e.g., ability to search the web for information.
            grounding_threshold (float): If perform_grounding is set to true, this variable controls the grounding threshold for optional grounding.
                See the Gemini API documentation for more inforamtion.
            ignore_errors (bool): Gemini changes settings frequently, so if the error detection is not up to date, set ignore_errors to True.
                Otherwise, it will raise an error if the settings are not valid for the model.
            safety_settings (SafetySettings): The safety settings to use for the model.

        For more information about text generation, see the Gemini documentation:
        https://ai.google.dev/gemini-api/docs/text-generation
        """
        self.code_execution = code_execution
        self.perform_thinking = perform_thinking
        self.thinking_budget = thinking_budget
        self.perform_grounding = perform_grounding
        self.grounding_threshold = grounding_threshold
        self.url_context = url_context
        self.ignore_errors = ignore_errors
        self.safety_settings = safety_settings

        # If the grounding_threshold param was set but not perform_grounding, enable perform_grounding
        if self.grounding_threshold:
            self.perform_grounding = True

    def to_GenerateContentConfig(self):
        """
        Converts the TextGenSettings to a `google.genai.types.GenerateContentConfig` object.
        
        Returns:
            A `google.genai.types.GenerateContentConfig` object with the settings.
        """

        tools = []

        if self.perform_grounding:
            if self.grounding_threshold:
                tools.append(types.DynamicRetrievalConfig(
                    mode=types.DynamicRetrievalConfigMode.MODE_DYNAMIC,
                    dynamic_threshold=self.grounding_threshold
                ))
            else:
                tools.append(types.Tool(google_search_retrieval=types.GoogleSearchRetrieval()))
        if self.code_execution:
            tools.append(types.Tool(code_execution=types.ToolCodeExecution()))
        if self.url_context:
            tools.append(types.Tool(url_context=types.UrlContext()))
            
        thinking_config = types.ThinkingConfig(
            thinking_budget=self.thinking_budget,
            include_thoughts=True
        ) if self.perform_thinking else None

        return types.GenerateContentConfig(
            tools=tools,
            thinking_config=thinking_config,
            response_modalities=["TEXT"],
            safety_settings=self.safety_settings.to_settings()
        )
    
    def __repr__(self):
        return f"""TextGenSettings(
    code_execution={self.code_execution},
    perform_thinking={self.perform_thinking},
    perform_grounding={self.perform_grounding},
    safety_settings={self.safety_settings},

    ignore_errors={self.ignore_errors}
)"""

class ImageGenSettings(BaseSettings):
    def __init__(self,
                 ignore_errors:bool=False,
                 safety_settings:SafetySettings=SafetySettings()
                 ):
        """
        Initializes the ImageGenSettings class.
        
        Parameters:
            ignore_errors (bool): Gemini changes settings frequently, so if the error detection is not up to date, set ignore_errors to True.
                Otherwise, it will raise an error if the settings are not valid for the model.
            safety_settings (SafetySettings): The safety settings to use for the model.

        For more information about image generation, see the Gemini documentation:
        https://ai.google.dev/gemini-api/docs/image-generation
        """
        self.ignore_errors = ignore_errors
        self.safety_settings = safety_settings

    def to_GenerateContentConfig(self):
        """
        Converts the ImageGenSettings to a `google.genai.types.GenerateContentConfig` object.
        
        Returns:
            A `google.genai.types.GenerateContentConfig` object with the settings.
        """
        return types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            safety_settings=self.safety_settings.to_settings()
        )

    def __repr__(self):
        return f"""ImageGenSettings(
    safety_settings={self.safety_settings},

    ignore_errors={self.ignore_errors}
)"""

class SingleSpeakerTTSSettings(BaseSettings):
    def __init__(self,
                 voice:str,
                 ignore_errors:bool=False,
                 safety_settings:SafetySettings=SafetySettings()
                 ):
        """
        Initializes the SingleSpeakerTTSSettings class.
        
        Parameters:
            voice (str): The voice to use for the TTS.
            ignore_errors (bool): Gemini changes settings frequently, so if the error detection is not up to date, set ignore_errors to True.
                Otherwise, it will raise an error if the settings are not valid for the model.
            safety_settings (SafetySettings): The safety settings to use for the model.

        For more information about TTS, see the Gemini documentation:
        https://ai.google.dev/gemini-api/docs/speech-generation
        """
        self.voice = voice
        self.ignore_errors = ignore_errors
        self.safety_settings = safety_settings

    def to_GenerateContentConfig(self):
        """
        Converts the SingleSpeakerTTSSettings to a `google.genai.types.GenerateContentConfig` object.
        
        Returns:
            A `google.genai.types.GenerateContentConfig` object with the settings.
        """
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=self.voice
                    )
                )
            )
        
        return types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=speech_config,
        )

    def __repr__(self):
        return f"""SingleSpeakerTTSSettings(
    voice={self.voice},
    safety_settings={self.safety_settings},

    ignore_errors={self.ignore_errors},
)"""

class MultiSpeakerTTSSettings(BaseSettings):
    def __init__(self,
                 speaker_names:list[str],
                 voices:list[str],
                 ignore_errors:bool=False,
                 safety_settings:SafetySettings=SafetySettings()
                 ):
        """
        Initializes the MultiSpeakerTTSSettings class.

        Note: Currently, the number of speakers is limited to 2, and the voices must be prebuilt voices.
        
        Parameters:
            speaker_names (list[str]): The speaker names to use for the TTS; the names that are used in the input text.
            voices (list[str]): The voices to use for the TTS.
            ignore_errors (bool): Gemini changes settings frequently, so if the error detection is not up to date, set ignore_errors to True.
                Otherwise, it will raise an error if the settings are not valid for the model.
            safety_settings (SafetySettings): The safety settings to use for the model.

        For more information about TTS, see the Gemini documentation:
        https://ai.google.dev/gemini-api/docs/speech-generation
        """
        self.speaker_names = speaker_names
        self.voices = voices
        self.ignore_errors = ignore_errors
        self.safety_settings = safety_settings

    def to_GenerateContentConfig(self):
        """
        Converts the MultiSpeakerTTSSettings to a `google.genai.types.GenerateContentConfig` object.
        
        Returns:
            A `google.genai.types.GenerateContentConfig` object with the settings.
        """
        speech_config = types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker=self.speaker_names[0],
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=self.voices[0],
                            )
                        )
                    ),
                    types.SpeakerVoiceConfig(
                        speaker=self.speaker_names[1],
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=self.voices[1],
                            )
                        )
                    ),
                ]
            )
        )
        return types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=speech_config,
            safety_settings=self.safety_settings.to_settings()
        )

    def __repr__(self):
        return f"""MultiSpeakerTTSSettings(
    speaker_names={self.speaker_names},
    voices={self.voices},
    safety_settings={self.safety_settings},

    ignore_errors={self.ignore_errors}
)"""

class ContentEmbeddingSettings(BaseSettings):
    def __init__(self,
                 classification:str="SEMANTIC_SIMILARITY",
                 ignore_errors:bool=False,
                 safety_settings:SafetySettings=SafetySettings()
                 ):
        """
        Initializes the ContentEmbeddingSettings class.
        
        Parameters:
            classification (str): The type of text embedding to use.
            Options are "SEMANTIC_SIMILARITY", "CLASSIFICATION", "CLUSTERING",
                "RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY", "QUESTION_ANSWERING", "FACT_VERIFICATION", and "CODE_RETRIEVAL_QUERY"
                Defaults to "SEMANTIC_SIMILARITY".
            ignore_errors (bool): Gemini changes settings frequently, so if the error detection is not up to date, set ignore_errors to True.
                Otherwise, it will raise an error if the settings are not valid for the model.
            safety_settings (SafetySettings): The safety settings to use for the model.

        For more information about text embedding, see the Gemini documentation:
        https://ai.google.dev/gemini-api/docs/embeddings
        """
        self.classification = classification
        self.ignore_errors = ignore_errors
        self.safety_settings = safety_settings

    def to_GenerateContentConfig(self):
        """
        Converts the ContentEmbeddingSettings to a `google.genai.types.EmbedContentConfig` object.
        The name is for polymorphism convenience.

        Returns:
            A `google.genai.types.EmbedContentConfig` object with the settings.
        """
        return types.EmbedContentConfig(
            task_type=self.classification,
        )

    def __repr__(self):
        return f"""ContentEmbeddingSettings(
    classification={self.classification},
    safety_settings={self.safety_settings},

    ignore_errors={self.ignore_errors}
)"""