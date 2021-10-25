
from argparse import ArgumentParser
from sys import argv
from typing import List

from webtoepub.epub.builder import EpubBuilderArguments, EpubBuilder

def run():
    opts = __from_argv(argv[1:])

    try:
        EpubBuilder(opts).run()
        return 0
    except Exception as e:
        print(e)
        return -1


def __from_argv(argslist: List[str]) -> EpubBuilderArguments:
    parser = ArgumentParser()

    parser.add_argument('-s', '--starting-chapter', type=int,
        nargs='?', dest="STARTING_CHAPTER", default=1)
    parser.add_argument('-e', '--ending-chapter', type=int,
        nargs='?', dest="ENDING_CHAPTER", default=-1)
    parser.add_argument('STORY_ID', type=int)
    parser.add_argument('FILENAME', type=str)

    args = parser.parse_args(argslist)
    
    return EpubBuilderArguments(
        args.STARTING_CHAPTER,
        args.ENDING_CHAPTER,
        args.STORY_ID,
        args.FILENAME
    )