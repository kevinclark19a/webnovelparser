
from argparse import ArgumentParser
from os.path import expanduser

from webtoepub.cmdline.conf import Config
from webtoepub.cmdline.fetch import command_parser as fetch_command_parser
from webtoepub.cmdline.story import command_parser as story_command_parser

_CONFIG_FILE_LOCATION = expanduser('~/.config/webtoepub.json')

def run():
    try:
        with Config(_CONFIG_FILE_LOCATION) as config:
            arg_parser = __arg_parser_factory(config)
            args = arg_parser.parse_args()

            args.run(args)
    except KeyboardInterrupt:
        print()
        return -1
    except Exception as e:
        print(f'Internal Error: {e}')
        return -1
    else:
        return 0

def __arg_parser_factory(config: Config) -> ArgumentParser:
    parser = ArgumentParser()
    parser.set_defaults(run=lambda args: parser.print_help())
    subparser_factory = parser.add_subparsers()

    story_action, story_parser = story_command_parser(config, lambda: subparser_factory.add_parser('story'))
    story_parser.set_defaults(run=story_action)

    fetch_action, fetch_parser = fetch_command_parser(config, lambda: subparser_factory.add_parser('fetch'))
    fetch_parser.set_defaults(run=fetch_action)

    return parser
    
