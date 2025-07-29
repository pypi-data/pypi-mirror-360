# IMPORTS

from PIL import Image
from io import BytesIO
import wave

from .data import types, ContentEmbedding

# GEMINI RESPONSE CLASS

class GemSpeakResponse:
    def __init__(self,
                 model:str,
                 text:str="",
                 image:Image.Image | None=None,
                 audio:bytes | None=None,
                 thinking_words:str="",
                 executed_code:str="",
                 code_result:str=""
                 ):
        """
        Initializes the GemSpeakResponse class.

        Parameters:
            model (str): The Gemini model id.
            text (str | None): The text response from the model.
            image (Image.Image | None): An image response from the model.
            audio (bytes | None): The audio response from the model.
            thinking_words (str | None): The thinking words of the model.
            executed_code (str | None): The executed code from the model.
        """
        self.model = model
        self.text = text
        self.image = image
        self.audio = audio
        self.thinking_words = thinking_words
        self.executed_code = executed_code
        self.code_result = code_result

    def save_image(self, path:str):
        """
        Saves the image to the specified path.

        Parameters:
            path (str): The file path where the image will be saved.
        """
        if self.image:
            self.image.save(path)
        else:
            raise ValueError("No image to save.")
        
    def save_audio(self, path:str):
        """
        Saves the audio to the specified path.

        Parameters:
            path (str): The file path where the audio will be saved. Should specify a .wav file
        """
        if self.audio:
            with wave.open(path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(self.audio)
        else:
            raise ValueError("No audio to save.")
        
    def add_part(self, part: types.Part):
        """
        Adds data to the response. This can be text, an image, or audio.

        Parameters:
            data (str | Image.Image | bytes): The data to add to the response.
        """
        # If part.text, the text could be thinking or response.
        # If part.thought, the text is thinking words.
        # Code is part.code_execution.code and result is part.code_execution_result.output.
        if part.text and not part.thought:
            self.text += part.text
        elif part.inline_data:
            # Find which data type to use
            assert isinstance(part.inline_data.mime_type, str)
            if "image" in part.inline_data.mime_type:
                assert isinstance(part.inline_data.data, bytes)
                self.image = Image.open(BytesIO(part.inline_data.data))
            elif "audio" in part.inline_data.mime_type:
                self.audio = part.inline_data.data
        elif part.thought:
            assert isinstance(part.text, str)
            self.thinking_words += part.text
        elif part.executable_code:
            assert isinstance(part.executable_code.code, str)
            self.executed_code += part.executable_code.code
        elif part.code_execution_result:
            assert isinstance(part.code_execution_result.output, str)
            self.code_result += part.code_execution_result.output
        else:
            raise ValueError("Unrecognized part type.")

    def __repr__(self):
        return "Gemini Response from {}:\n{}\n{}\n{}".format(
            self.model,
            self.text,
            f"Image: {self.image.size}" if self.image else "No image",
            f"Audio: {self.audio}" if self.audio else "No audio",
            f"Thinking words: {self.thinking_words}" if self.thinking_words else "No thinking words",
            f"Executed code: {self.executed_code}" if self.executed_code else "No executed code",
            f"Code result: {self.code_result}" if self.code_result else "No code result"
        )
    
class GemSpeakEmbedResponse:
    def __init__(self,
                 model:str,
                 embeddings:list[float]
                 ):
        """
        Initializes the GemSpeakEmbedResponse class.

        Parameters:
            model (str): The Gemini model id.
            embeddings (list): A list with the embedding floats
        """
        self.model = model

        # Convert the embeddings to a list of numbers
        self.embeddings = []

        for embedding in embeddings:
            self.embeddings.append(embedding)

    def __repr__(self):
        return f"Gemini Embedding Response from {self.model}:\n{self.embeddings}"