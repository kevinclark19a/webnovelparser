
from sys import argv
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from webtoepub.arguments import WebToEpubArguments
from webtoepub.web.novel import RoyalRoadWebNovel
from webtoepub.epub.chapter import EpubChapter
from webtoepub.epub.writer import EpubFile

def run():
    opts = WebToEpubArguments.from_argv(argv[1:])
    return WebToEpub(opts).run()


class WebToEpub:

    def __init__(self, options):
        self._options = options
    
    def run(self):
        novel = RoyalRoadWebNovel(self._options.story_id)

        with EpubFile(novel.metadata, self._options.filename) as epub:
            epub_lock = Lock()

            def fetch_and_add_chapter(idx: int) -> None:
                web_chapter = novel.get_chapter(idx)
                epub_chapter = EpubChapter(idx, web_chapter.source, web_chapter.title, web_chapter.contents)

                with epub_lock:
                    epub.add_chapter(epub_chapter)

            epub.add_cover(novel.get_cover_image())

            with ThreadPoolExecutor() as executor:
                for idx in range(self._options.starting_chapter - 1, self._options.ending_chapter):
                    executor.submit(fetch_and_add_chapter, idx)