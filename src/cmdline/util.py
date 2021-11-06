
from typing import Callable

from webtoepub.cmdline.conf import Config, StoryEntry



def story_entry_factory(config: Config) -> Callable[[str], StoryEntry]:
    
    def story_entry(identifier: str) -> StoryEntry:

        id = title = None
        try:
            id = int(identifier)
        except ValueError:
            title = identifier
        
        story = config.fetch_story(id=id, title=title)

        if story is not None:
            return story
        if id is not None:
            return StoryEntry(id, "", 0)
        
        raise ValueError(f'Story "{identifier}" is not tracked, so a story_id must be provided.')

    return story_entry
