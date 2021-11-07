

from concurrent.futures.thread import ThreadPoolExecutor
from io import StringIO
from os import linesep
from threading import Lock
from typing import List

from webtoepub.epub.webnovel import RoyalRoadWebNovel


class EpubViewerArguments:

    @property
    def story_ids(self) -> int:
        return self._story_ids
    
    def __init__(self, story_ids: List[int]):
        self._story_ids = story_ids

class EpubViewer:

    def __init__(self, options: EpubViewerArguments):

        self._novels = []

        write_lock = Lock()
        def fetch_story_metadata(story_id):
            try:
                novel = RoyalRoadWebNovel(story_id)
            except Exception as e:
                print(f'Failed to fetch web novel, exception was: {e}')
            else:
                latest_chapter_title = novel.peek_chapter_title(novel.metadata.num_chapters - 1)

                with write_lock:
                    self._novels.append({
                        'title': novel.metadata.title,
                        'latest_chapter': {
                            'title': latest_chapter_title,
                            'index': novel.metadata.num_chapters
                        }
                    })
        
        with ThreadPoolExecutor() as executor:
            for story_id in options.story_ids:
                executor.submit(fetch_story_metadata, story_id)
    
    @property
    def titles(self) -> List[str]:
        return [ novel['title'] for novel in self._novels ]

    def show(self):
        for novel in self._novels:
            print(f'{novel["title"]}:')
            print(f'\tLatest Chapter<{novel["latest_chapter"]["index"]}>: "{novel["latest_chapter"]["title"]}"')
    