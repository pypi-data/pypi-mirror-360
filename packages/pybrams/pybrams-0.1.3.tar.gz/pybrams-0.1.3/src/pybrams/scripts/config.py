from pybrams.utils import Config
import json
import shutil
import os
from rich import print_json


def setup_args(subparsers):
    subparser_config = subparsers.add_parser("config")
    subparser_config_subparsers = subparser_config.add_subparsers(
        dest="config_cmd", required=True
    )

    subparser_config_subparsers.add_parser("show", help="show configuration")
    subparser_config_subparsers.add_parser(
        "copy", help="copy default configuration into current directory"
    )
    subparser_config_subparsers.add_parser(
        "restore", help="Restore the default configuration"
    )

    parser_get = subparser_config_subparsers.add_parser(
        "get", help="get a config value"
    )
    parser_get.add_argument("section", help="config section name")
    parser_get.add_argument("key", help="config key name")

    parser_set = subparser_config_subparsers.add_parser(
        "set", help="set a config value"
    )
    parser_set.add_argument("section", help="config section name")
    parser_set.add_argument("key", help="config key name")
    parser_set.add_argument("value", help="value to set")


def parse_value(value: str):
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def run(args):
    if args.config_cmd == "show":
        print_json(json.dumps(Config._config, indent=4))
    elif args.config_cmd == "copy":
        shutil.copy(Config._default_config_path, Config._user_defined_config_path)
    elif args.config_cmd == "restore":
        try:
            os.remove(Config._user_defined_config_path)
        except FileNotFoundError:
            pass
    elif args.config_cmd == "get":
        try:
            print(Config.get(args.section, args.key))
        except KeyError:
            print(
                f'Unable to retrieve "{args.section}:{args.key}" from the configuration'
            )
    elif args.config_cmd == "set":
        parsed_value = parse_value(args.value)
        Config.set(args.section, args.key, parsed_value)
