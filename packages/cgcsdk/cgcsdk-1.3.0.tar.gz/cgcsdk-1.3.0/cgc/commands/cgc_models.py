from abc import ABC, abstractmethod


class CGCEntityList(ABC):
    """Base class for other lists"""

    @staticmethod
    @abstractmethod
    def load_data() -> list[str]:
        pass

    @classmethod
    def get_list(cls) -> list[str]:
        try:
            return [el for el in cls.load_data()]
        except TypeError:
            return []
