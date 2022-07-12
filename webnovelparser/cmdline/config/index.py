
from typing import Dict, List
from webnovelparser.cmdline import config

from webnovelparser.cmdline.config.entry import StoryEntry, StoryEntryConfigIdentifier
from webnovelparser.cmdline.config.objects import ConfigObject, ConfigObjectIdentifier


class StoryIndex(ConfigObject):

    @property
    def coid(self):
        return self._coid

    @property
    def stories(self) -> List[StoryEntry]:
        return list(self._stories.values())

    def fetch_story(self, coid: ConfigObjectIdentifier) -> StoryEntry:
        return self._stories.get(coid, None)
    
    def add_story(self, story: StoryEntry):
        self._stories[story.coid] = story
    
    def remove_story(self, entry: StoryEntry):
        if entry is None:
            return
            
        if entry.coid in self._stories:
            del self._stories[entry.coid]
    
    def toJSON(self) -> Dict:
        return {
            **super().toJSON(),
            "stories": [ story.toJSON() for story in self._stories.values() ]
        }
    
    def __contains__(self, obj) -> bool:
        if not isinstance(obj, StoryEntry):
            return False
        return obj.coid in self._stories

    
    def __init__(self, coid: ConfigObjectIdentifier=None, stories: Dict[ConfigObjectIdentifier, StoryEntry]=None) -> None:
        self._coid = coid or StoryIndexConfigIdentifier()
        self._stories = stories or {}


class StoryIndexConfigIdentifier(ConfigObjectIdentifier):
    
    @staticmethod
    def _object_type() -> str:
        return "StoryIndex"

    def inflate_data(self, data: dict) -> ConfigObject:
        
        stories = {}

        for story in data.get('stories', []):
            generic_coid = story.get('__coid', "")
            if StoryEntryConfigIdentifier.matches(generic_coid):
                story_entry_coid = StoryEntryConfigIdentifier(generic_coid)
                stories[story_entry_coid] = story_entry_coid.inflate_data(story)
        
        return StoryIndex(self, stories)

