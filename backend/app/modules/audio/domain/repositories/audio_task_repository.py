from abc import ABC, abstractmethod
from domain.entities.audio_localize.audio_task import AudioTask

class AudioTaskRepository(ABC):
    @abstractmethod
    def create(self, audiotask:AudioTask) -> AudioTask:
        pass

    @abstractmethod
    def update(self, audiotask:AudioTask) -> AudioTask:
        pass

    @abstractmethod
    def delete(self, audiotask:AudioTask) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, audiotask:AudioTask) -> AudioTask:
        pass