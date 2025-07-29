from ..helpers.azure_search_helper import AzureSearchHelper
from datetime import datetime
import json

class ConversationLogger:
    """
    A logger class for logging user and assistant messages in a conversation.

    This class uses AzureSearchHelper to log messages with metadata such as
    conversation ID, message type, and timestamps.
    """

    def __init__(self):
        """
        Initializes the ConversationLogger instance.

        Sets up the logger using AzureSearchHelper.
        """
        self.logger = AzureSearchHelper().get_conversation_logger()

    def log(self, messages: list):
        """
        Logs a list of messages by calling the appropriate logging methods.

        Args:
            messages (list): A list of message dictionaries to be logged.
        """
        self.log_user_message(messages)
        self.log_assistant_message(messages)

    def log_user_message(self, messages: list):
        """
        Logs user messages from the provided list of messages.

        Extracts the content and metadata from user messages and logs them.

        Args:
            messages (list): A list of message dictionaries to be logged.
        """
        text = ""
        metadata = {}
        for message in messages:
            if message["role"] == "user":
                metadata["type"] = message["role"]
                metadata["conversation_id"] = message.get("conversation_id")
                metadata["created_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                metadata["updated_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                text = message["content"]
        self.logger.add_texts(texts=[text], metadatas=[metadata])

    def log_assistant_message(self, messages: list):
        """
        Logs assistant messages from the provided list of messages.

        Extracts the content and metadata from assistant messages and logs them.
        Also handles messages from tools and extracts source information.

        Args:
            messages (list): A list of message dictionaries to be logged.
        """
        text = ""
        metadata = {}
        try:
            metadata["conversation_id"] = set(
                filter(None, [message.get("conversation_id") for message in messages])
            ).pop()
        except KeyError:
            metadata["conversation_id"] = None
        for message in messages:
            if message["role"] == "assistant":
                metadata["type"] = message["role"]
                metadata["created_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                metadata["updated_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                text = message["content"]
            elif message["role"] == "tool":
                metadata["sources"] = [
                    source["id"]
                    for source in json.loads(message["content"]).get("citations", [])
                ]
        self.logger.add_texts(texts=[text], metadatas=[metadata])