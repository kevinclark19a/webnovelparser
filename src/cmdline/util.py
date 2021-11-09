
from typing import Callable

from webtoepub.cmdline.conf import Config, StoryEntry
from webtoepub.epub.webnovel import RoyalRoadWebNovel



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

def show_updates(novel: RoyalRoadWebNovel, from_chapter: int, to_chapter: int) -> bool:
    if from_chapter < 0:
        from_chapter += novel.metadata.num_chapters
    if to_chapter < 0:
        to_chapter += novel.metadata.num_chapters

    print(f'Fetching chapters for "{novel.metadata.title}"...')

    if to_chapter < from_chapter:
        print('\tNo chapters found.')
        return False
    
    for idx in range(from_chapter, to_chapter + 1):
        print(f'\tChapter#<{idx + 1}>: "{novel.peek_chapter_title(idx)}"')
    
    return True