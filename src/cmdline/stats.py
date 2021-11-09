
from argparse import ArgumentParser
from typing import Callable

from webtoepub.cmdline.conf import Config
from webtoepub.cmdline.util import story_entry_factory, show_updates
from webtoepub.epub.webnovel import RoyalRoadWebNovel


def __show_newest_chapters(novel, start: int, end: int):

    return show_updates(novel, start, end)


def command_parser(config: Config, parser_factory: Callable[[], ArgumentParser]):

    def action(args_namespace):

        try:
            novel = RoyalRoadWebNovel(args_namespace.STORY_ENTRY.id)
        except Exception as e:
            print(f'Failed to fetch web novel, exception was: {e}')
            return

        __show_newest_chapters(
            novel, args_namespace.STARTING_CHAPTER,
            args_namespace.ENDING_CHAPTER
        )
    
    parser = parser_factory()
    parser.add_argument('-s', '--starting-chapter', type=int,
        nargs='?', dest="STARTING_CHAPTER", default=-10)
    parser.add_argument('-e', '--ending-chapter', type=int,
        nargs='?', dest="ENDING_CHAPTER", default=-1)
    parser.add_argument('STORY_ENTRY', metavar='STORY_ID',
        type=story_entry_factory(config))

    return action, parser