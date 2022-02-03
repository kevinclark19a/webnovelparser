
from argparse import ArgumentParser
from typing import Callable

from webtoepub.cmdline.config import Config, bookshelf
from webtoepub.cmdline.config.entry import StoryEntry
from webtoepub.cmdline.util import story_entry_factory, show_updates, get_chapter_bounds
from webtoepub.epub.webnovel import RoyalRoadWebNovel


def command_parser(config: Config, parser_factory: Callable[[], ArgumentParser]):

    parser = parser_factory()
    subparser_factory = parser.add_subparsers()

    __list_parser(config, subparser_factory.add_parser)
    __show_parser(config, subparser_factory.add_parser)
    __create_parser(config, subparser_factory.add_parser)
    __delete_parser(config, subparser_factory.add_parser)
    __add_parser(config, subparser_factory.add_parser)
    __remove_parser(config, subparser_factory.add_parser)

    return lambda _: parser.print_help(), parser

def __list_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):

    def action(_):
        bookshelves = config.bookshelves # Make a copy so we can sort.
        bookshelves.sort(key=lambda shelf: shelf.name)
        print(" ".join(bs.name for bs in bookshelves))

    parser = parser_factory('list')
    parser.set_defaults(run=action)

def __show_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):

    def action(args_namespace):
        for story in config.stories(args_namespace.SHELF_NAME):
            print(story)

    parser = parser_factory('show')
    parser.add_argument('SHELF_NAME', type=str)
    parser.set_defaults(run=action)

def __create_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):
    
    def action(args_namespace):

        if config.create_bookshelf(args_namespace.SHELF_NAME):
            print(f"Created bookshelf '{args_namespace.SHELF_NAME}'.")
        else:
            print(f"Bookshelf '{args_namespace.SHELF_NAME}' already exists!")

    parser = parser_factory('create')
    parser.add_argument('SHELF_NAME', type=str)
    parser.set_defaults(run=action)

def __delete_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):
    
    def action(args_namespace):
        config.delete_bookshelf(args_namespace.SHELF_NAME)

    parser = parser_factory('delete')
    parser.add_argument('SHELF_NAME', type=str)
    parser.set_defaults(run=action)

def __add_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):
    
    def action(args_namespace):

        if bookshelf := config.fetch_bookshelf(args_namespace.SHELF_NAME):
            for entry in args_namespace.STORY_ENTRIES:
                if bookshelf.add_reference(entry):
                    print(f"Added {entry}.")
        else:
            print(f"Bookshelf '{args_namespace.SHELF_NAME}' doesn't exist!")

    parser = parser_factory('add')
    parser.add_argument('SHELF_NAME', type=str)
    parser.add_argument('STORY_ENTRIES', metavar='STORY_IDS',
        nargs="+", type=story_entry_factory(config))
    parser.set_defaults(run=action)

def __remove_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):
    
    def action(args_namespace):
        if bookshelf := config.fetch_bookshelf(args_namespace.SHELF_NAME):
            for entry in args_namespace.STORY_ENTRIES:
                if bookshelf.remove_reference(entry.coid):
                    print(f"Removed {entry}.")
        else:
            print(f"Bookshelf '{args_namespace.SHELF_NAME}' doesn't exist!")
    
    parser = parser_factory('remove')
    parser.add_argument('SHELF_NAME', type=str)
    parser.add_argument('STORY_ENTRIES', metavar='STORY_IDS',
        nargs='+', type=story_entry_factory(config))
    parser.set_defaults(run=action)