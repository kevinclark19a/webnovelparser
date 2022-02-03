
from argparse import ArgumentParser
from typing import Callable

from webtoepub.cmdline.config import Config
from webtoepub.cmdline.config.entry import StoryEntry
from webtoepub.cmdline.util import story_entry_factory, show_updates, get_chapter_bounds
from webtoepub.epub.webnovel import RoyalRoadWebNovel


def command_parser(config: Config, parser_factory: Callable[[], ArgumentParser]):

    parser = parser_factory()
    subparser_factory = parser.add_subparsers()

    __list_parser(config, subparser_factory.add_parser)
    __show_parser(config, subparser_factory.add_parser)
    __add_parser(config, subparser_factory.add_parser)
    __remove_parser(config, subparser_factory.add_parser)

    return lambda _: parser.print_help(), parser

def __list_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):
    def action(args_namespace):
        stories = config.stories() # Make a copy so we can sort.
        stories.sort(key=lambda entry: entry.title)

        def for_each_story(f):
            for story in stories:
                f(story)
            
        if args_namespace.NAME_ONLY:
            for_each_story(lambda s: print(s.handle))
        else:
            for_each_story(lambda s: print(s))

    parser = parser_factory('list')
    parser.add_argument('--name-only', dest='NAME_ONLY', action='store_true')
    parser.set_defaults(run=action)

def __show_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):

    def action(args_namespace):
        print(args_namespace.STORY_ENTRY)
        
        try:
            novel = RoyalRoadWebNovel(args_namespace.STORY_ENTRY.id)
        except Exception as e:
            print(f'Failed to fetch web novel, exception was: {e}')
            return
        
        start, end = get_chapter_bounds(
            args_namespace.STARTING_CHAPTER,
            args_namespace.ENDING_CHAPTER,
            args_namespace.STORY_ENTRY.last_read,
            novel.metadata.num_chapters
        )
        
        show_updates(novel, start, end, flag_entries=(args_namespace.STORY_ENTRY.last_read,))

    parser = parser_factory('show')
    parser.add_argument('-s', '--starting-chapter', type=int,
        nargs='?', dest="STARTING_CHAPTER", default=-10)
    parser.add_argument('-e', '--ending-chapter', type=int,
        nargs='?', dest="ENDING_CHAPTER", default=-1)
    parser.add_argument('STORY_ENTRY', metavar='STORY_ID',
        type=story_entry_factory(config))
    parser.set_defaults(run=action)

def __add_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):
    
    def action(args_namespace):

        try:
            novel = RoyalRoadWebNovel(args_namespace.STORY_ID)
        except Exception as e:
            print(f'Failed to fetch web novel, exception was: {e}')
            return

        if args_namespace.LAST_CHAPTER < 0:
            args_namespace.LAST_CHAPTER += (novel.metadata.num_chapters + 1)
        
        handle = args_namespace.HANDLE
        if handle is None:
            handle = str(args_namespace.STORY_ID)
        
        entry = StoryEntry(
            args_namespace.STORY_ID,
            handle,
            novel.metadata.title,
            args_namespace.LAST_CHAPTER
        )

        config.add_story(entry)
        print(entry)

    parser = parser_factory('add')
    parser.add_argument('-l', '--last-chapter', type=int,
        nargs='?', dest='LAST_CHAPTER', default=0)
    parser.add_argument('-n', '--handle', type=str,
        nargs='?', dest='HANDLE')
    parser.add_argument('STORY_ID', type=int)
    parser.set_defaults(run=action)

def __remove_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):
    
    def action(args_namespace):
        for entry in args_namespace.STORY_ENTRIES:
            config.remove_story(id=entry.id, handle=entry.handle, title=entry.title)
    
    parser = parser_factory('remove')
    parser.add_argument('STORY_ENTRIES', metavar='STORY_IDS',
        nargs='+', type=story_entry_factory(config))
    parser.set_defaults(run=action)