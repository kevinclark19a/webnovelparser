
from argparse import ArgumentParser
from typing import Callable, Optional

from webnovelparser.cmdline.config import Config
from webnovelparser.cmdline.config.entry import StoryEntry
from webnovelparser.cmdline.util import compute_chapter_info, story_entry_factory, show_updates, get_chapter_bounds
from webnovelparser.epub.builder import EpubBuilder, EpubBuilderArguments
from webnovelparser.epub.webnovel import RoyalRoadWebNovel


def command_parser(config: Config, parser_factory: Callable[[], ArgumentParser]):
    parser = parser_factory()
    subparsers = parser.add_subparsers()

    __one_parser(config, subparsers.add_parser)
    __multi_parser(config, subparsers.add_parser)

    return lambda _: parser.print_help(), parser

def __show_update_and_get_confirmation(novel: RoyalRoadWebNovel,
    from_chapter: int, to_chapter: int) -> bool:
    
    if not show_updates(novel, from_chapter, to_chapter):
        return False

    try:
        confirmation = input('Continue with fetch? (Y/n) ')
    except EOFError:
        return False
    else:
        while True:
            if confirmation in ('N', 'n'):
                return False
            if confirmation in ('Y', 'y', ''):
                return True

            print(f'Invalid input provided: "{confirmation}". Use either "y" or "n". ')
            try:
                confirmation = input('Continue with fetch? (Y/n) ')
            except EOFError:
                return False

def __retrieve_and_set_name_override(novel: RoyalRoadWebNovel, start: Optional[int]=None, end: Optional[int]=None) -> None:
    try:
        title_override = input('Override eBook title? Enter nothing to use the default.\n'
            + 'Any instance of $t will be replaced with the novel\'s title name.\n'
            + 'Book Title: ')
    except EOFError:
        pass # use title_override = None

    # A saner default includes chapter info (if present), so let's do that here.
    if title_override in ("", None):
        title_override = f'$t{compute_chapter_info(novel, start, end)}'
    
    title_override = title_override.replace('$t', novel.metadata.title)

    novel.set_name_override(title_override)

def __one_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):

    def action(args_namespace):

        try:
            novel = RoyalRoadWebNovel(
                args_namespace.STORY_ENTRY.id,
                args_namespace.TITLE_OVERRIDE
            )
        except Exception as e:
            print(f'Failed to fetch web novel, exception was: {e}')
            raise

        start, end = get_chapter_bounds(
            args_namespace.STARTING_CHAPTER,
            args_namespace.ENDING_CHAPTER,
            args_namespace.STORY_ENTRY.last_read,
            novel.metadata.num_chapters
        )

        show_updates(novel, start, end)

        if args_namespace.TITLE_OVERRIDE is None:
            __retrieve_and_set_name_override(novel, start, end)

        if args_namespace.FILENAME is None:
            args_namespace.FILENAME = f"./{args_namespace.STORY_ENTRY.handle}_{start+1}_{end+1}.epub"

        EpubBuilder(EpubBuilderArguments(
            start, end, args_namespace.FILENAME
        ), novel).run()
        
        if end + 1 > args_namespace.STORY_ENTRY.last_read:
            config.add_story(args_namespace.STORY_ENTRY.with_value(last_read=end+1))
    
    
    parser = parser_factory('one')
    parser.add_argument('-s', '--starting-chapter', type=int,
        nargs='?', dest="STARTING_CHAPTER")
    parser.add_argument('-e', '--ending-chapter', type=int,
        nargs='?', dest="ENDING_CHAPTER")
    parser.add_argument('-t', '--title-override', type=str,
        nargs='?', dest="TITLE_OVERRIDE")
    parser.add_argument('-o', '--filename', type=str,
        nargs='?', dest="FILENAME")
    parser.add_argument('STORY_ENTRY', metavar='STORY_ID',
        type=story_entry_factory(config))

    parser.set_defaults(run=action)

def __multi_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):

    def fetch_one(story_entry: StoryEntry):

        try:
            novel = RoyalRoadWebNovel(story_entry.id)
        except Exception as e:
            print(f'Failed to fetch web novel, exception was: {e}')
            return

        start, end = get_chapter_bounds(
            None, None,
            story_entry.last_read,
            novel.metadata.num_chapters
        )

        if not __show_update_and_get_confirmation(novel, start, end):
            return
        
        filename = f"{story_entry.handle}_{start+1}_{end+1}.epub"
        __retrieve_and_set_name_override(novel, start, end)

        EpubBuilder(EpubBuilderArguments(
            start,
            end,
            filename
        ), novel).run()

        config.add_story(story_entry.with_value(last_read=novel.metadata.num_chapters))
    
    def bookshelf(args_namespace):
        stories = config.stories(shelf_name=args_namespace.BOOKSHELF)
        stories.sort(key=lambda story: story.handle)

        for story_entry in stories:
            fetch_one(story_entry)
    
    def all(_):
        for story_entry in config.stories():
            fetch_one(story_entry)

    parser = parser_factory('all')
    parser.set_defaults(run=all)

    parser = parser_factory('bookshelf')
    parser.add_argument('BOOKSHELF', type=str)
    parser.set_defaults(run=bookshelf)