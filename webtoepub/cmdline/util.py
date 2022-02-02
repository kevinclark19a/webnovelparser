
from typing import Callable, Optional, Tuple

from webtoepub.cmdline.conf import Config, StoryEntry
from webtoepub.epub.webnovel import RoyalRoadWebNovel


def get_chapter_bounds(starting: Optional[int], ending: Optional[int],
    last_read: int, last_update: int) -> Tuple[int, int]:

    if last_update < 0:
        raise ValueError('Argument last_update must be positive!')

    def rectify_index(value: Optional[int]) -> int:        
        if value is None:
            return None

        if value < 0:
            return value + last_update
        
        return value - 1
    
    starting, ending, last_read, last_update = map(rectify_index, [
        starting, ending, last_read, last_update
    ])

    if (starting is not None) and (ending is not None):
        # both values provided, use those values.
        return starting, ending

    if starting is not None: # => ending is None
        return starting, last_update

    if ending is not None: # => starting is None
        if last_read > ending:
            # user is backtracking here, using 
            # last_read would error out later. 
            return 1, ending
        return last_read + 1, ending
    
    # => (starting, ending) is (None, None)
    return last_read + 1, last_update


def story_entry_factory(config: Config) -> Callable[[str], StoryEntry]:
    
    def story_entry(identifier: str) -> StoryEntry:

        id = handle = title = None
        try:
            id = int(identifier)
        except ValueError:
            title = handle = identifier
        
        # No way to tell the two strings apart, try to treat identifier
        # as a handle first. 
        story = config.fetch_story(id=id, handle=handle)
        if story is not None:
            return story

        # Follow up with trying the identifier as a title.
        story = config.fetch_story(id=id, title=title)
        if story is not None:
            return story
        
        if id is not None:
            return StoryEntry(id, "", "", 0)
        
        raise ValueError(f'Story "{identifier}" is not tracked, so a story_id must be provided.')

    return story_entry

def show_updates(novel: RoyalRoadWebNovel,
    from_chapter: int, to_chapter: int,
    flag_entries: Tuple[int]=()) -> bool:
    
    print(f'Fetching chapters for "{novel.metadata.title}"...')

    if to_chapter < from_chapter:
        print('\tNo chapters found.')
        return False
    
    for idx in range(from_chapter, to_chapter + 1):
        output = f'Chapter#<{idx + 1}>: "{novel.peek_chapter_title(idx)}"'

        if (idx + 1) in flag_entries:
            print(f'[+]\t{output}')
        else:
            print(f'\t{output}')
    
    return True