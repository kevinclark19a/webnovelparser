
from typing import List

from webnovelparser.cmdline.config.objects import ConfigObject, ConfigObjectIdentifier
from webnovelparser.cmdline.config.entry import StoryEntry, StoryEntryConfigIdentifier

class Bookshelf(ConfigObject):

    @property
    def coid(self) -> ConfigObjectIdentifier:
        return self._coid

    @property
    def name(self) -> str:
        return self._name

    def get_references(self) -> List[ConfigObjectIdentifier]:
        return self._story_coids[:]

    def add_reference(self, entry: StoryEntry):
        if not entry.coid in self._story_coids:
            self._story_coids.append(entry.coid)
            return True
        return False
    
    def remove_reference(self, entry: StoryEntry):
        if entry.coid in self._story_coids:
            self._story_coids.remove(entry.coid)
            return True
        return False

    def toJSON(self) -> dict:
        return {
            **super().toJSON(),
            "name": self._name,
            "story_coids": [ str(coid) for coid in self._story_coids ]
        }

    def __contains__(self, obj) -> bool:
        return obj in self._story_coids

    def __init__(self, name: str, story_coids: List[ConfigObjectIdentifier], coid: ConfigObjectIdentifier=None) -> None:
        self._coid = coid or BookshelfConfigIdentifer()
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
        
        return Bookshelf(name, story_coids, coid=self)
