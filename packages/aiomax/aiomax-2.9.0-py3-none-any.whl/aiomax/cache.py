from .types import Message


class MessageCache:
    def __init__(self, max_size: int = 10000):
        """
        New message cache.

        :param max_size: Maximum number of messages to store
        """
        self.max_size: int = max_size
        self.messages: dict[str, Message] = {}

    def get_message(self, id: str) -> "Message | None":
        """
        Returns a message by ID. None if message wasnt cached

        :param id: Message ID
        """
        return self.messages.get(id, None)

    def add_message(self, message: Message):
        """
        Caches a message.

        :param message: Message
        """
        self.messages[message.id] = message

        while len(self.messages) > self.max_size:
            (k := next(iter(self.messages)), self.messages.pop(k))
