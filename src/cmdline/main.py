
from argparse import ArgumentParser
from os.path import expanduser
from typing import Callable

from webtoepub.cmdline.conf import Config, StoryEntry
from webtoepub.epub.builder import EpubBuilderArguments, EpubBuilder
from webtoepub.epub.stats import EpubViewerArguments, EpubViewer

_CONFIG_FILE_LOCATION = expanduser('~/.config/webtoepub.json')

def run():
    try:
        with Config(_CONFIG_FILE_LOCATION) as config:
            arg_parser = __arg_parser_factory(config)
            args = arg_parser.parse_args()

            args.run(args)
    except Exception as e:
        print(f'Internal Error: {e}')
        return -1
    else:
        return 0

def __arg_parser_factory(config: Config) -> ArgumentParser:
    parser = ArgumentParser()
    parser.set_defaults(run=lambda args: parser.print_help())
    subparser_factory = parser.add_subparsers()

    story_action, story_parser = __story_command_parser(config, lambda: subparser_factory.add_parser('story'))
    story_parser.set_defaults(run=story_action)

    view_action, view_parser = __stats_command_parser(config, lambda: subparser_factory.add_parser('stats'))
    view_parser.set_defaults(run=view_action)

    build_action, build_parser = __build_command_parser(config, lambda: subparser_factory.add_parser('fetch'))
    build_parser.set_defaults(run=build_action)

    return parser

def __story_command_parser(config: Config, parser_factory: Callable[[], ArgumentParser]):

    parser = parser_factory()
    subparser_factory = parser.add_subparsers()

    #############################################
    #                  story list               #
    #############################################

    list_story_parser = subparser_factory.add_parser('list')
    list_story_parser.set_defaults(run=lambda _: config.show_stories())

    #############################################
    #                  story add                #
    #############################################

    def add_story_action(args_namespace):
        args = EpubViewerArguments([ args_namespace.STORY_ID ])

        titles = [ args_namespace.TITLE_OVERRIDE ] + EpubViewer(args).titles
        title = next((t for t in titles if t is not None), None)
        if title:
            config.add_story(StoryEntry(
                args_namespace.STORY_ID, title,
                args_namespace.LAST_CHAPTER
            ))

    add_story_parser = subparser_factory.add_parser('add')
    add_story_parser.add_argument('-l', '--last-chapter', type=int,
        nargs='?', dest='LAST_CHAPTER', default=0)
    add_story_parser.add_argument('-t', '--title-override', type=str,
        nargs='?', dest='TITLE_OVERRIDE')
    add_story_parser.add_argument('STORY_ID', type=int)
    add_story_parser.set_defaults(run=add_story_action)

    #############################################
    #                story remove               #
    #############################################
    
    def remove_story_action(args_namespace):
        for entry in args_namespace.STORY_ENTRIES:
            config.remove_story(id=entry.id, title=entry.title)
    
    remove_story_parser = subparser_factory.add_parser('remove')
    remove_story_parser.add_argument('STORY_ENTRIES', metavar='STORY_IDS',
        nargs='+', type=__story_entry_factory(config))
    remove_story_parser.set_defaults(run=remove_story_action)

    #############################################
    #############################################

    return lambda _: parser.print_help(), parser

def __stats_command_parser(config: Config, parser_factory: Callable[[], ArgumentParser]):

    def view_action(args_namespace):

        args = EpubViewerArguments(
            [ entry.id for entry in args_namespace.STORY_ENTRIES ]
        )

        EpubViewer(args).run()
    
    parser = parser_factory()
    parser.add_argument('STORY_ENTRIES', metavar='STORY_IDS',
        nargs='+', type=__story_entry_factory(config))

    return view_action, parser


def __build_command_parser(config: Config, parser_factory: Callable[[], ArgumentParser]):
    
    def build_action(args_namespace):

        starting_chapter = args_namespace.STARTING_CHAPTER
        if starting_chapter is None:
            starting_chapter = 1
            if args_namespace.STORY_ENTRY.last_read < args_namespace.ENDING_CHAPTER:
                starting_chapter += args_namespace.STORY_ENTRY.last_read
        
        args = EpubBuilderArguments(
            starting_chapter,
            args_namespace.ENDING_CHAPTER,
            args_namespace.TITLE_OVERRIDE,
            args_namespace.STORY_ENTRY.id,
            args_namespace.FILENAME
        )

        last_read = EpubBuilder(args).run()
        if last_read > args_namespace.STORY_ENTRY.last_read:
            config.add_story(args_namespace.STORY_ENTRY.with_value(last_read=last_read))
    
    parser = parser_factory()
    parser.add_argument('-s', '--starting-chapter', type=int,
        nargs='?', dest="STARTING_CHAPTER")
    parser.add_argument('-e', '--ending-chapter', type=int,
        nargs='?', dest="ENDING_CHAPTER", default=-1)
    parser.add_argument('-t', '--title-override', type=str,
        nargs='?', dest="TITLE_OVERRIDE")
    parser.add_argument('STORY_ENTRY', metavar='STORY_ID',
        type=__story_entry_factory(config))
    parser.add_argument('FILENAME', type=str)

    return build_action, parser


def __story_entry_factory(config: Config) -> Callable[[str], StoryEntry]:
    
    def story_entry(identifier: str) -> StoryEntry:

        id = title = None
        try:
            id = int(identifier)
        except ValueError:
            title = identifier
        
        story = config.fetch_story(id=id, title=title)

        if story is not None:
            return story
        if id is not None:
            return StoryEntry(id, "", 0)
        
        raise ValueError(f'Story "{identifier}" is not tracked, so a story_id must be provided.')

    return story_entry
