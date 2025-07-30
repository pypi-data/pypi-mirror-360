from abc import ABC, abstractmethod

from logger_local.MetaLogger import ABCMetaLogger


class OurQueue(ABC, metaclass=ABCMetaLogger):

    @abstractmethod
    def push(self, item):
        """
        Pushes an item to the queue.

        Args:
            item: The item to be pushed to the queue.
        """
        pass

    @abstractmethod
    def get(self):
        """
        Gets an item from the queue and deletes it.

        Returns:
            The item retrieved from the queue.
        """
        pass

    @abstractmethod
    def peek(self):
        """
        Gets the head of the queue without deleting it.

        Returns:
            The item at the head of the queue.
        """
        pass
