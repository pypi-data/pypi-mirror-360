# IMPORTS

import warnings
import math
from collections.abc import Callable

from google.genai.types import ContentEmbedding

from .data import *
from .settings import TextGenSettings, ImageGenSettings, SingleSpeakerTTSSettings, MultiSpeakerTTSSettings, ContentEmbeddingSettings
from .files import OnlineInlineImage, LocalInlineImage, FileUpload
from .response import GemSpeakResponse, GemSpeakEmbedResponse

# EMBED DISTANCE FUNCTIONS

def pythagorean_distance(
        ar1: list[float | int],
        ar2: list[float | int],
        ):
    """
    Return the pythagorean distance between the two arrays

    Parameters:
        ar1 (list[float | int]): The first point
        ar2 (list[float | int]): The second point

    Returns:
        int: The pythagorean distance
    """
    assert len(ar1) == len(ar2)

    values = []
    for val1, val2 in zip(ar1, ar2):
        values.append((val2 - val1) ** 2)
    
    return math.sqrt(abs(sum(values)))

# CLIENT CLASS

class GemSpeakClient:
    def __init__(self):
        if not API_KEYS:
            raise Exception("No API keys provided! Use `gemspeak.data.add_api_keys` to add API keys. See the documentation for how to get API keys")

    def get_embed_distance(self,
                            model:str,
                            text1:str,
                            text2:str,
                            func:Callable[[list[float | int], list[float | int]], float]=pythagorean_distance,
                            settings:ContentEmbeddingSettings = ContentEmbeddingSettings(),
                            inline_images1: list[OnlineInlineImage | LocalInlineImage]=[],
                            inline_images2: list[OnlineInlineImage | LocalInlineImage]=[],
                            uploaded_files1:list[FileUpload]=[],
                            uploaded_files2:list[FileUpload]=[]
                           ):
        """
        Returns the distance between the two inputs, based on the Gemini embedding model provided.
        By default, distance is calculated with a n-dimensional generalization of the Pythagorean theorem, but you
            can use any function. The inputs are two lists of floats, and the expected output is an integer

        Parameters:
            model (str): The Gemini model id to use for the request.
            text1 (str): The first string to compare.
            text2 (str): The second string to compare.
            func (function): The comparation function to calculate the distance.
            settings (TextGenSettings | ImageGenSettings | SingleSpeakerTTSSettings | MultiSpeakerTTSSettings | ContentEmbeddingSettings):
                An instance of `GemSpeakSettings` to configure the client.
            inline_images1 (list[InlineImage]): A list of inline images to include with the first embedding.
            inline_images2 (list[InlineImage]): A list of inline images to include with the second embedding.
            uploaded_files1 (list[FileUpload]): A list of files to upload with the with the first embedding.
            uploaded_files2 (list[FileUpload]): A list of files to upload with the with the second embedding.

        Returns (in a tuple):
        (
            int: The distance calculated by the distance function
            res1: The `GemSpeakTextEmbedResponse` of text1, inline_images1, and uploaded_files1
            res2: The `GemSpeakTextEmbedResponse` of text2, inline_images2, and uploaded_files2
        )
        """
        res1 = self.embed_content(
            model=model,
            text=text1,
            settings=settings,
            inline_images=inline_images1,
            uploaded_files=uploaded_files1
        )
        res2 = self.embed_content(
            model=model,
            text=text2,
            settings=settings,
            inline_images=inline_images2,
            uploaded_files=uploaded_files2
        )

        return (func(res1.embeddings, res2.embeddings), res1, res2)

    def embed_content(self,
                   model:str,
                   text:str,
                   settings:ContentEmbeddingSettings = ContentEmbeddingSettings(),
                   inline_images: list[OnlineInlineImage | LocalInlineImage]=[],
                   uploaded_files:list[FileUpload]=[]
                   ) -> GemSpeakEmbedResponse:
        """
        Asks the Gemini model a question and returns the response.

        Parameters:
            model (str): The Gemini model id to use for the request.
            text (str):  The text to embed.
            settings (TextGenSettings | ImageGenSettings | SingleSpeakerTTSSettings | MultiSpeakerTTSSettings | ContentEmbeddingSettings):
                An instance of `GemSpeakSettings` to configure the client.
            inline_images (list[InlineImage]): A list of inline images to include in the request.
            uploaded_files (list[FileUpload]): A list of files to upload with the request.

        Returns: 
            A `GemSpeakResponse` object containing the model's response.
        """
        # Prepare the config based on settings type
        settings.validate(model=model)
        config = settings.to_GenerateContentConfig()

        # Iterate through all the API keys
        for key in API_KEYS:
            # Initialize the client
            client = Client(api_key=key)

            # Upload the inline_images and uploaded_files
            files = []
            for image in inline_images:
                files.append(image.get())

            for file in uploaded_files:
                files.append(file.get(client))

            # Try to call the function. If the ResourceExhausted error is raised, it means the API key has exhausted its quota, and continue to the next key.
            try:
                response = client.models.embed_content(
                    model=model,
                    contents=[text, *files],
                    config=config
                )
                # Convert the response to a GemSpeakResponse object
                assert isinstance(response.embeddings, list)
                embeddings = list(response.embeddings)[0].values
                assert isinstance(embeddings, list)
                return GemSpeakEmbedResponse(
                    model=model,
                    embeddings=embeddings
                )

            except ResourceExhausted:
                continue
        else:
            raise ResourceExhausted("All API key's resources are used.")
            
    def ask_gemini(self,
                   model: str,
                   text: str | list,
                   settings:TextGenSettings | ImageGenSettings | SingleSpeakerTTSSettings | MultiSpeakerTTSSettings | ContentEmbeddingSettings = TextGenSettings(),
                   inline_images: list[OnlineInlineImage | LocalInlineImage]=[],
                   uploaded_files:list[FileUpload]=[],
                   ) -> GemSpeakResponse:
        """
        Asks the Gemini model a question and returns the response.

        Parameters:
            model (str): The Gemini model id to use for the request.
            text (str | list): The text to ask the model, or multiple string or types.
            settings (TextGenSettings | ImageGenSettings | SingleSpeakerTTSSettings | MultiSpeakerTTSSettings | ContentEmbeddingSettings):
                An instance of `GemSpeakSettings` to configure the client.
            inline_images (list[InlineImage]): A list of inline images to include in the request.
            uploaded_files (list[FileUpload]): A list of files to upload with the request.

        Returns: 
            A `GemSpeakResponse` object containing the model's response.
        """
        # Prepare the config based on settings type
        settings.validate(model=model)
        config = settings.to_GenerateContentConfig()

        # Iterate through all the API keys
        for key in API_KEYS:
            # Initialize the client
            client = Client(api_key=key)

            # Upload the inline_images and uploaded_files
            files = []
            for image in inline_images:
                files.append(image.get())

            for file in uploaded_files:
                files.append(file.get(client))

            # Try to call the function. If the ResourceExhausted error is raised, it means the API key has exhausted its quota, and continue to the next key.
            try:
                assert isinstance(config, types.GenerateContentConfig)

                response = client.models.generate_content(
                    model=model,
                    contents=[text, *files],
                    config=config,
                )
                # Convert the response to a GemSpeakResponse object
                gemspeak_response = GemSpeakResponse(
                    model=model,
                )

                # Iterate through the response parts, and add them to the gemspeak response
                assert isinstance(response.candidates, list)
                assert isinstance(response.candidates[0].content, types.Content)
                assert isinstance(response.candidates[0].content.parts, list)
                for part in response.candidates[0].content.parts:
                    gemspeak_response.add_part(part)

                return gemspeak_response

            except ResourceExhausted:
                continue
        else:
            raise ResourceExhausted("All API key's resources are exhausted.")

    def create_conversation(self,
                            model:str,
                            system_prompt:str = \
                                "What follows is a conversation between a user, and a helpful, informative AI assistant.",
                            warn_on_unconventional_speaker:bool = True,
                            settings: TextGenSettings | ImageGenSettings = TextGenSettings()
                            ):
        """
        Creates a new conversation instance.

        Parameters:
            model (str): The Gemini model id to use for the conversation.
            system_prompt (str): The system prompt for the conversation.
            warn_on_unconventional_speaker (bool): If True, will warn if the speaker is not "USER", "ASSISTANT", or "SYSTEM".
            settings (TextGenSettings | ImageGenSettings): An instance of `GemSpeakSettings` to configure the conversation.

        Returns:
            A new Conversation instance.
        """
        return Conversation(
            model=model,
            system_prompt=system_prompt,
            warn_on_unconventional_speaker=warn_on_unconventional_speaker,
            client=self,
            settings=settings
        )

# CONVERSATION CLASS

class Conversation(object):
    def __init__(self,
                 model:str,
                 system_prompt:str = \
                    "What follows is a conversation between a user, and a helpful, informative AI assistant.",
                 warn_on_unconventional_speaker:bool = True,
                 client: GemSpeakClient | None = None,
                 settings: TextGenSettings | ImageGenSettings = TextGenSettings()
                 ):
        """
        Initializes the Conversation class.
        
        Parameters:
            model (str): The Gemini model id to use for the conversation.
            system_prompt (str | None): Choose the system prompt for better responses in context.
            warn_on_unconventional_speaker (bool): If True, will warn if the speaker is not "USER", "ASSISTANT", or "SYSTEM".
            client (Client | None): An optional client. If provided, it will be used for generating responses.
                If not provided, a new client must be provided when calling the `generate_response()` method.
        """
        self.model = model
        self.system_prompt = system_prompt
        self.warn_on_unconventional_speaker = warn_on_unconventional_speaker
        self.client = client
        self.settings = settings

        self.as_list = []

        # Add the system prompt to the conversation
        if self.system_prompt:
            self.add_contents("SYSTEM", self.system_prompt)

    # Add input methods

    def add_contents(self, speaker, text):
        """
        Adds input to the conversation.
        Note: If user input is added, this does NOT generate a response.
        Call `generate_response()` to generate a response from the assistant.

        Parameters:
            speaker (str): The speaker of the input, either USER or ASSISTANT.
            text (str): The text of the input.
        """
        if speaker not in ["USER", "ASSISTANT", "SYSTEM"] and self.warn_on_unconventional_speaker:
            warnings.warn(
                "Unconventional speaker: {}. Expected USER, ASSISTANT, or SYSTEM.".format(speaker),
                UserWarning
            )
        self.as_list.append({"SPEAKER": speaker, "CONTENTS": text})

    # Getter functions

    def get_all_ai(self):
        """
        Returns all of the text the AI has generated in the conversation.
        """
        result = ""

        for entry in self.as_list:
            if entry["SPEAKER"] == "ASSISTANT":
                result += "{}\n".format(entry["CONTENTS"].strip())

        return result
    
    def as_content_parts(self):
        parts = []

        for item in self.as_list:
            parts.append(types.Content(role=item["SPEAKER"], parts=[item["CONTENTS"]]))
        
        return parts

    # Generate AI text

    def generate_response(self,
                          client: GemSpeakClient | None=None
                          ):
        """
        Generates the response from the AI model.

        Parameters:
            client (Client | None): The Gemini client to use for the request. If a client was provided with initialization, it will be used.
        """
        if client is None:
            print(type(self.client))
            assert isinstance(self.client, GemSpeakClient), "A GemSpeakClient must be provided to generate a response."
            client = self.client

        # Get self as a string
        conversation_string = self.as_content_parts()

        # Ask gemini for a response
        assert isinstance(client, GemSpeakClient), "A GemSpeakClient must be provided to generate a response."
        response = client.ask_gemini(model=self.model, text=conversation_string, settings=self.settings)

        self.add_contents("ASSISTANT", response.text)

    # Magic methods

    def __str__(self):
        result = ""

        for entry in self.as_list:
            result += "{}: {}\n\n".format(entry["SPEAKER"], entry["CONTENTS"])

        return result

    def __repr__(self):
        return "Conversation with model {}:\n{}".format(
            self.model,
            str(self)
        )