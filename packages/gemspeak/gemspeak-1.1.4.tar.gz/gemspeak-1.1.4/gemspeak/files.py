# IMPORTS

import requests
from .data import *

# FILE CLASSES

class LocalInlineImage:
    def __init__(self,
                 path:str
                 ):
        """
        Initalizes the LocalInlineImage class.

        This class is for local image uploads to be used in Gemini requests.
        The file can be up to 20MB. To upload large files, use the `FileUpload` class

        Parameters:
            path (str): The path to the local image file
        """
        self.path = path

        # Extract the file extension
        self.extension = path.strip().split(".")[-1]

        if self.extension not in SUPPORTED_IMAGE_TYPES:
            raise ValueError(f"Unsupported image type: {self.extension}. Supported types are: {SUPPORTED_IMAGE_TYPES}")
        
        # Get the mime type
        self.mime_type = IMAGE_TYPE_TO_MIME_TYPE[self.extension]

    def get(self):
        """
        Returns the image as a bytes object ready to be passed to a `google.genai.Client().models.generate_content()` call.

        Returns:
            The image data as bytes.
        """
        with open(self.path, 'rb') as f:
            image_bytes = f.read()
        
        return types.Part.from_bytes(
            data=image_bytes,
            mime_type=self.mime_type
        )

    def __repr__(self):
        return f"OnlineInlineImage(path={self.path})"

class OnlineInlineImage:
    def __init__(self,
                 url:str,
                 ext:str
                 ):
        """
        Initializes the OnlineInlineImage class.

        This class is for online image uploads to be used in Gemini requests.
        The file can be up to 20MB. To upload large files, use the `FileUpload` class

        Parameters:
            path (str): The online url to the file.
            ext (str): The file extension to use.
        """
        self.path = url
        self.extension = ext

        if self.extension not in SUPPORTED_IMAGE_TYPES:
            raise ValueError(f"Unsupported image type: {self.extension}. Supported types are: {SUPPORTED_IMAGE_TYPES}")

        # Get the mime type
        self.mime_type = IMAGE_TYPE_TO_MIME_TYPE[self.extension]

    def get(self):
        """
        Returns the image as a bytes object ready to be passed to a `google.genai.Client().models.generate_content()` call.

        Returns:
            The image data as bytes.
        """
        image_bytes = requests.get(self.path).content
        
        return types.Part.from_bytes(
            data=image_bytes,
            mime_type=self.mime_type
        )

    def __repr__(self):
        return f"OnlineInlineImage(path={self.path}, ext={self.extension})"

class FileUpload:
    def __init__(self,
                 path:str,
                ):
        """
        Initializes the FileUpload class.

        This class is for file uploads to be used in Gemini requests.
        The file can be up to 20GB, but must be local.
        To upload inline images, use `LocalInlineImage`. To upload online images, use `OnlineInlineImage`

        Parameters:
            path (str): The path to the file.
        """
        self.path = path

    def get(self, client: Client):
        """
        Uploads the file to the Gemini API.

        Parameters:
            client: The Gemini API client.
        """
        return client.files.upload(file=self.path)
    
    def __repr__(self):
        return f"FileUpload(path={self.path})"