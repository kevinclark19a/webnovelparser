
from argparse import ArgumentParser
from typing import Callable

from webtoepub.cmdline.conf import Config
from webtoepub.cmdline.util import story_entry_factory, show_updates
from webtoepub.epub.webnovel import RoyalRoadWebNovel


def __show_newest_chapters(novel, num_chapters=10):

    return show_updates(novel, -num_chapters)


def command_parser(config: Config, parser_factory: Callable[[], ArgumentParser]):

    def action(args_namespace):

        def process_one(story_entry):

            try:
                novel = RoyalRoadWebNovel(story_entry.id)
            except Exception as e:
                print(f'Failed to fetch web novel, exception was: {e}')
                return

            __show_newest_chapters(novel)
        
        for story_entry in args_namespace.STORY_ENTRIES:
            process_one(story_entry)
    
    parser = parser_factory()
    parser.add_argument('STORY_ENTRIES', metavar='STORY_IDS',
        nargs='+', type=story_entry_factory(config))

    return action, parser