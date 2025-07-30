# pylint: disable=too-few-public-methods

"""
This is the base module for all LLM (Large Language Model) wrappers.
Each specific LLM should extend this base class.
"""

from abc import ABC, abstractmethod
from microllm.llms.message_history import MessageHistory


class BaseLLM(ABC):
    """
    Base class for all Large Language Models. Each specific LLM should extend
    this class.

    Args:
        model (str): The model name used in the LLM class.
    """

    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    async def generate_async(self, message_history: MessageHistory):
        """
        Generates text from the LLM asynchronously.

        Args:
            message_history: A `MessageHistory` object representing the conversation
                history.

        Returns:
            A string representing the generated text.
            A dictionary representing the raw outputs.
            A dictionary representing the model configuration.
        """
