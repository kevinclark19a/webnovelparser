
from argparse import ArgumentParser
from typing import Callable

from webtoepub.cmdline.conf import Config
from webtoepub.cmdline.util import story_entry_factory
from webtoepub.epub.stats import EpubViewer, EpubViewerArguments


def command_parser(config: Config, parser_factory: Callable[[], ArgumentParser]):

    def action(args_namespace):

        args = EpubViewerArguments(
            [ entry.id for entry in args_namespace.STORY_ENTRIES ]
        )

        EpubViewer(args).show()
    
    parser = parser_factory()
    parser.add_argument('STORY_ENTRIES', metavar='STORY_IDS',
        nargs='+', type=story_entry_factory(config))

    return action, parser