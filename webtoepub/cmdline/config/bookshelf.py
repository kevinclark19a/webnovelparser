
from typing import List

from webtoepub.cmdline.config.objects import ConfigObject, ConfigObjectIdentifier
from webtoepub.cmdline.config.entry import StoryEntryConfigIdentifier

class Bookshelf(ConfigObject):

    @property
    def coid(self) -> ConfigObjectIdentifier:
        return self._coid

    def get_references(self) -> List[ConfigObjectIdentifier]:
        return self._story_coids[:]

    def add_reference(self, coid: ConfigObjectIdentifier):
        if not coid in self._story_coids:
            self._story_coids.append(coid)
    
    def remove_reference(self, coid: ConfigObjectIdentifier):
        if coid in self._story_coids:
            self._story_coids.remove(coid)

    def toJSON(self) -> dict:
        return {
            **super().toJSON(),
            "name": self._name,
            "story_coids": self._story_coids
        }

    def __contains__(self, obj) -> bool:
        return obj in self._story_coids

    def __init__(self, coid: ConfigObjectIdentifier, name: str, story_coids: List[ConfigObjectIdentifier]) -> None:
        
        self._coid = coid
        self._name = name
        self._story_coids = story_coids

class BookshelfConfigIdentifer(ConfigObjectIdentifier):

    @staticmethod
    def _object_type() -> str:
        return "Bookshelf"

    def inflate_data(self, data: dict) -> ConfigObject:
        
        name = data.get('name', None)
        story_coids = []

        for coid in data.get('story_coids', []):
            if StoryEntryConfigIdentifier.matches(coid):
                story_coids.append(StoryEntryConfigIdentifier(coid))
        
        return Bookshelf(self, name, story_coids)
