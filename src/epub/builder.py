
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from webtoepub.epub.writer import EpubFile
from webtoepub.epub.webnovel import RoyalRoadWebNovel



class EpubBuilderArguments:
    
    @property
    def starting_chapter(self) -> int:
        return self._starting_chapter
    
    @property
    def ending_chapter(self) -> int:
        return self._ending_chapter
    
    @property
    def story_id(self) -> int:
        return self._story_id
    
    @property
    def filename(self) -> str:
        return self._filename

    def __init__(self, starting_chapter: int, ending_chapter: int, story_id: int, filename: str) -> None:
        self._starting_chapter = starting_chapter
        self._ending_chapter = ending_chapter
        self._story_id = story_id
        self._filename = filename

class EpubBuilder:

    def __init__(self, options):
        self._options = options
    
    def run(self) -> None:
        try:
            novel = RoyalRoadWebNovel(self._options.story_id)
        except Exception as e:
            print(f'Failed to fetch web novel, exception was: {e}')
            raise

        with EpubFile(novel.metadata, self._options.filename) as epub:
            epub_lock = Lock()

            def fetch_and_add_chapter(idx: int) -> None:

                try:
                    chapter = novel.get_chapter(idx)
                except Exception as e:
                    print(f'Failed to fetch chapter#{idx}, skipping. Exception was:\n{e}')
                else:
                    with epub_lock:
                        epub.add_chapter(chapter)

            epub.add_cover(novel.get_cover_image())

            with ThreadPoolExecutor() as executor:
                for idx in range(self._options.starting_chapter - 1, self._options.ending_chapter):
                    executor.submit(fetch_and_add_chapter, idx)