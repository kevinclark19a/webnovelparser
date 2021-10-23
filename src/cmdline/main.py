
from argparse import ArgumentParser
from sys import argv
from typing import List

from webtoepub.epub.builder import EpubBuilderArguments, EpubBuilder

def run():
    opts = __from_argv(argv[1:])
    return EpubBuilder(opts).run()


def __from_argv(argslist: List[str]) -> EpubBuilderArguments:
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
    
    return EpubBuilderArguments(
        args.STARTING_CHAPTER,
        args.ENDING_CHAPTER,
        args.STORY_ID,
        args.FILENAME
    )