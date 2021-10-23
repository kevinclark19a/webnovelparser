
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from webtoepub.epub.file.writer import EpubFile
from webtoepub.epub.file.resource import EpubChapter
from webtoepub.epub.web.novel import RoyalRoadWebNovel



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
    
    def run(self):
        novel = RoyalRoadWebNovel(self._options.story_id)

        with EpubFile(novel.metadata, self._options.filename) as epub:
            epub_lock = Lock()

            def fetch_and_add_chapter(idx: int) -> None:
                web_chapter = novel.get_chapter(idx)
                epub_chapter = EpubChapter(idx, web_chapter.source,
                    web_chapter.title, web_chapter.contents)

                with epub_lock:
                    epub.add_chapter(epub_chapter)

            epub.add_cover(novel.get_cover_image())

            with ThreadPoolExecutor() as executor:
                for idx in range(self._options.starting_chapter - 1, self._options.ending_chapter):
                    executor.submit(fetch_and_add_chapter, idx)