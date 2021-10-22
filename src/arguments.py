
from argparse import ArgumentParser
from typing import List

class WebToEpubArguments:
    
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

    @staticmethod
    def from_argv(argslist: List[str]):
        parser = ArgumentParser()
        
        def pos(val):
            converted = int(val)
            
            if converted < 1:
                raise ValueError(f"Value must be greater than zero, got {converted}")
            
            return converted

        parser.add_argument('-s', '--starting-chapter', type=pos,
            nargs='?', dest="STARTING_CHAPTER", default=1)
        parser.add_argument('-e', '--ending-chapter', type=pos,
            nargs='?', dest="ENDING_CHAPTER", default=1)
        parser.add_argument('STORY_ID', type=int)
        parser.add_argument('FILENAME', type=str)

        args = parser.parse_args(argslist)

        if args.STARTING_CHAPTER > args.ENDING_CHAPTER:
            raise ValueError("Ending chapter number must be past starting chapter number.")
        
        return WebToEpubArguments(
            args.STARTING_CHAPTER,
            args.ENDING_CHAPTER,
            args.STORY_ID,
            args.FILENAME
        )