
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from webtoepub.epub.writer import EpubFile


class EpubBuilderArguments:
    
    @property
    def starting_chapter(self) -> int:
        return self._starting_chapter
    
    @property
    def ending_chapter(self) -> int:
        return self._ending_chapter

    @property
    def filename(self) -> str:
        return self._filename

    def __init__(self, starting_chapter: int, ending_chapter: int, filename: str) -> None:
        self._starting_chapter = starting_chapter
        self._ending_chapter = ending_chapter
        self._filename = filename

class EpubBuilder:

    def __init__(self, options: EpubBuilderArguments, novel):

        s, e, l = (options.starting_chapter, options.ending_chapter, novel.metadata.num_chapters)

        if s > e:
            raise ValueError(f'Chapter range ({s},{e}) doesn\'t make sense!')
        if e > l:
            raise ValueError(f'Chapter range ({s},{e}) exceeds max chapter: {l}')

        self._options = options
        self._novel = novel
    
    def run(self) -> int:

        with EpubFile(self._novel.metadata, self._options.filename) as epub:
            epub_lock = Lock()

            def fetch_and_add_chapter(idx: int) -> None:

                try:
                    chapter = self._novel.get_chapter(idx)
                except Exception as e:
                    print(f'Failed to fetch chapter#{idx}, skipping. Exception was:\n{e}')
                else:
                    with epub_lock:
                        epub.add_chapter(chapter)

            epub.add_cover(self._novel.get_cover_image())

            with ThreadPoolExecutor() as executor:
                for idx in range(self._options.starting_chapter, self._options.ending_chapter + 1):
                    executor.submit(fetch_and_add_chapter, idx)