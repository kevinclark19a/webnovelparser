
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

        def rectify_index(chapter_number):
            if chapter_number < 0:
                return novel.metadata.num_chapters + chapter_number
            return chapter_number - 1
        
        rectified_start = rectify_index(self._options.starting_chapter)
        rectified_end = rectify_index(self._options.ending_chapter)

        if rectified_start > rectified_end:
            raise ValueError(f'Chapter range ({rectified_start},{rectified_end}) doesn\'t make sense!')
        if rectified_end > novel.metadata.num_chapters:
            raise ValueError(f'Chapter range ({rectified_start},{rectified_end}) exceeds max chapter: {novel.metadata.num_chapters}')

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
                for idx in range(rectified_start, rectified_end + 1):
                    executor.submit(fetch_and_add_chapter, idx)