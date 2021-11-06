
from argparse import ArgumentParser
from typing import Callable


from webtoepub.cmdline.conf import Config, StoryEntry
from webtoepub.cmdline.util import story_entry_factory
from webtoepub.epub.stats import EpubViewerArguments, EpubViewer


def command_parser(config: Config, parser_factory: Callable[[], ArgumentParser]):

    parser = parser_factory()
    subparser_factory = parser.add_subparsers()

    __list_parser(config, subparser_factory.add_parser)
    __add_parser(config, subparser_factory.add_parser)
    __remove_parser(config, subparser_factory.add_parser)

    return lambda _: parser.print_help(), parser

def __list_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):
    def action(_):
        stories = config.stories # Make a copy so we can sort.
        stories.sort(key=lambda entry: entry.title)

        for story in stories:
            print(f'{story.title}<{story.id}>: last_read={story.last_read}')

    parser = parser_factory('list')
    parser.set_defaults(run=action)

def __add_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):
    
    def action(args_namespace):
        args = EpubViewerArguments([ args_namespace.STORY_ID ])

        titles = [ args_namespace.TITLE_OVERRIDE ] + EpubViewer(args).titles
        title = next(filter(lambda t: t is not None, titles), None)
        if title:
            config.add_story(StoryEntry(
                args_namespace.STORY_ID, title,
                args_namespace.LAST_CHAPTER
            ))

    parser = parser_factory('add')
    parser.add_argument('-l', '--last-chapter', type=int,
        nargs='?', dest='LAST_CHAPTER', default=0)
    parser.add_argument('-t', '--title-override', type=str,
        nargs='?', dest='TITLE_OVERRIDE')
    parser.add_argument('STORY_ID', type=int)
    parser.set_defaults(run=action)

def __remove_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):
    
    def action(args_namespace):
        for entry in args_namespace.STORY_ENTRIES:
            config.remove_story(id=entry.id, title=entry.title)
    
    parser = parser_factory('remove')
    parser.add_argument('STORY_ENTRIES', metavar='STORY_IDS',
        nargs='+', type=story_entry_factory(config))
    parser.set_defaults(run=action)