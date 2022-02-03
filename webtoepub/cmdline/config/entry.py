

from webtoepub.cmdline.config.objects import ConfigObject, ConfigObjectIdentifier

class StoryEntry(ConfigObject):

    @property
    def coid(self) -> ConfigObjectIdentifier:
        return self._coid

    @property
    def id(self) -> int:
        return self._id

    @property
    def handle(self) -> str:
        return self._handle

    @property
    def title(self) -> str:
        return self._title

    @property
    def last_read(self) -> int:
        return self._last_read

    def toJSON(self):
        return {
            **super().toJSON(),
            'id': self.id,
            'handle': self.handle,
            'title': self.title,
            'last_read': self.last_read
        }
    
    def with_value(self, **kwargs: dict):

        id = kwargs.pop('id', self.id)
        handle = kwargs.pop('handle', self.handle)
        title = kwargs.pop('title', self.title)
        last_read = kwargs.pop('last_read', self.last_read)

        if kwargs not in ({}, None):
            raise ValueError(f'StoryEntry does not have the following fields: {kwargs.keys()}')

        return StoryEntry(id, handle, title, last_read)
    
    def __str__(self) -> str:
        return f'{self.title}<{self.handle}>: id={self.id};last_read={self.last_read}'
    
    def __init__(self, id: int, handle: str, title: str, last_read: int, coid: ConfigObjectIdentifier=None):
        self._id = id
        self._handle = handle
        self._title = title
        self._last_read = last_read
        self._coid = coid or StoryEntryConfigIdentifier()


class StoryEntryConfigIdentifier(ConfigObjectIdentifier):

    @staticmethod
    def _object_type() -> str:
        return "StoryEntry"
    
    def inflate_data(self, data: dict) -> ConfigObject:

        id = data.get('id', None)
        handle = data.get('handle', None)
        title = data.get('title', None)
        last_read = data.get('last_read', None)

        return StoryEntry(id, handle, title, last_read, coid=self)