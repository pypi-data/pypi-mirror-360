from typing import Generator
from abc import ABC, abstractmethod

class BaseSTTModel(ABC):
    def __init__(self,
                 model: str) -> None:
        """
        Initializes the BaseSTTModel with a model name.
        Args:
            model (str): The name of the speech model to use.
        """
        self.model = model

    @abstractmethod
    def speech_to_text(self, audio_bytes: bytes) -> str:
        """
        An abstract method to convert speech audio bytes to text.

        Args:
            audio_bytes (bytes): The audio bytes to convert to text.

        Returns:
            str: The text transcription of the audio data.
        """
        raise NotImplementedError
    
    @abstractmethod
    def stream_speech_to_text(self, audio_bytes: bytes) -> Generator[str, None, None]:
        """
        An abstract method to stream speech audio bytes to text.

        Args:
            audio_bytes (bytes): The audio bytes to convert to text.

        Returns:
            Generator[str, None, None]: A generator that yields text transcriptions of the audio data.
        """
        raise NotImplementedError
    
class BaseTTSModel(ABC):
    """
    An abstract base class for text-to-speech models.
    
    ## Methods:
        `text_to_speech()`: An abstract method to convert text to speech.
    """
    def __init__(self,
                 model: str) -> None:
        """
        Initializes the BaseTTSModel with a model name.
        
        Args:
            model (str): The name of the text-to-speech model to use.
        """
        self.model = model

    @abstractmethod
    def text_to_speech(
        self, 
        text: str,
    ) -> bytes:
        """
        Convert text to speech audio bytes.

        Args:
            text (str): The text to convert to speech.

        Returns:
            bytes: The audio bytes of the spoken text.
        """
        raise NotImplementedError
    
    @abstractmethod
    def stream_text_to_speech(
        self, 
        text: str,
    ) -> Generator[bytes, None, None]:
        """
        Stream text to speech audio bytes.

        Args:
            text (str): The text to convert to speech.

        Returns:
            Generator[bytes, None, None]: A generator that yields audio bytes of the spoken text.
        """
        raise NotImplementedError