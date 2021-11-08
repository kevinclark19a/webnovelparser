
from argparse import ArgumentParser
from typing import Callable, Optional, Tuple

from webtoepub.cmdline.conf import Config, StoryEntry
from webtoepub.cmdline.util import story_entry_factory, show_updates
from webtoepub.epub.builder import EpubBuilder, EpubBuilderArguments
from webtoepub.epub.webnovel import RoyalRoadWebNovel


def command_parser(config: Config, parser_factory: Callable[[], ArgumentParser]):
    parser = parser_factory()
    subparsers = parser.add_subparsers()

    __one_parser(config, subparsers.add_parser)
    __all_parser(config, subparsers.add_parser)

    return lambda _: parser.print_help(), parser

def __get_chapter_bounds(starting: Optional[int], ending: Optional[int],
    last_read: int, last_update: int) -> Tuple[int, int]:

    if (starting is not None) and (ending is not None):
        # both values provided, use those values.
        return starting, ending

    if starting is not None: # => ending is None
        return starting, last_update

    if ending is not None: # => starting is None
        if ending < 0: # negative index a la python lists
            ending += (last_update + 1)

        if last_read > ending:
            # user is backtracking here, using 
            # last_read would error out later. 
            return 1, ending
        return last_read + 1, ending
    
    # => (starting, ending) is (None, None)
    return last_read, last_update
    

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

        start, end = __get_chapter_bounds(
            args_namespace.STARTING_CHAPTER,
            args_namespace.ENDING_CHAPTER,
            args_namespace.STORY_ENTRY.last_read,
            novel.metadata.num_chapters
        )

        EpubBuilder(EpubBuilderArguments(
            start, end, args_namespace.FILENAME
        ), novel).run()
        
        if end > args_namespace.STORY_ENTRY.last_read:
            config.add_story(args_namespace.STORY_ENTRY.with_value(last_read=end))
    
    
    parser = parser_factory('one')
    parser.add_argument('-s', '--starting-chapter', type=int,
        nargs='?', dest="STARTING_CHAPTER")
    parser.add_argument('-e', '--ending-chapter', type=int,
        nargs='?', dest="ENDING_CHAPTER")
    parser.add_argument('-t', '--title-override', type=str,
        nargs='?', dest="TITLE_OVERRIDE")
    parser.add_argument('STORY_ENTRY', metavar='STORY_ID',
        type=story_entry_factory(config))
    parser.add_argument('FILENAME', type=str)

    parser.set_defaults(run=action)

def __show_update_and_get_confirmation(novel: RoyalRoadWebNovel, last_read: int) -> bool:
    
    if not show_updates(novel, last_read):
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

def __retrieve_and_set_name_override(novel: RoyalRoadWebNovel) -> None:
    try:
        title_override = input('Override eBook title? Enter nothing to use the default. '
            + 'Any instance of $t will be replaced with the default title name.\n')
    except EOFError:
        pass # use title_override = None
    else:
        # empty string is identical to None, don't need to special case it.
        title_override = title_override.replace('$t', novel.metadata.title)
    
    novel.set_name_override(title_override)

def __retrieve_filename() -> Optional[str]:
    try:
        filename = input('eBook filename: ')
    except EOFError:
        print('No filename provided, skipping fetch.')
        return None
    
    return filename


def __all_parser(config: Config, parser_factory: Callable[[str], ArgumentParser]):
    
    def action(_):
        
        def fetch_one(story_entry: StoryEntry):

            try:
                novel = RoyalRoadWebNovel(story_entry.id)
            except Exception as e:
                print(f'Failed to fetch web novel, exception was: {e}')
                return
            
            if not __show_update_and_get_confirmation(novel, story_entry.last_read):
                return
            
            filename = __retrieve_filename()
            if filename is None:
                return

            __retrieve_and_set_name_override(novel)

            EpubBuilder(EpubBuilderArguments(
                story_entry.last_read,
                novel.metadata.num_chapters,
                filename
            ), novel).run()

            config.add_story(story_entry.with_value(last_read=novel.metadata.num_chapters))
    
        for story_entry in config.stories:
            fetch_one(story_entry)

    parser = parser_factory('all')
    parser.set_defaults(run=action)