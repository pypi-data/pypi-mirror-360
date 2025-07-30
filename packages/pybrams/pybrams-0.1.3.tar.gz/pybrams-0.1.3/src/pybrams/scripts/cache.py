from pybrams.utils import Cache, Config


def setup_args(subparsers):
    subparser_cache = subparsers.add_parser("cache")
    subparser_cache_subparsers = subparser_cache.add_subparsers(
        dest="cache_cmd", required=True
    )

    subparser_cache_subparsers.add_parser("clear", help="clear cache")
    subparser_cache_subparsers.add_parser(
        "status", help="display the status of the cache"
    )
    subparser_cache_subparsers.add_parser("enable", help="enable cache")
    subparser_cache_subparsers.add_parser("disable", help="disable cache")
    subparser_cache_subparsers.add_parser("info", help="display info about cache")


def run(args):
    if args.cache_cmd == "clear":
        Cache.clear()
        print("Cache was cleared")
    elif args.cache_cmd == "status":
        print(
            f'Cache is {"enabled" if Config.get("pybrams.utils.cache", "use") else "disabled"}'
        )
    elif args.cache_cmd == "enable":
        Config.set("pybrams.utils.cache", "use", True)
        print(
            f'Cache is {"enabled" if Config.get("pybrams.utils.cache", "use") else "disabled"}'
        )
    elif args.cache_cmd == "disable":
        Config.set("pybrams.utils.cache", "use", False)
        print(
            f'Cache is {"enabled" if Config.get("pybrams.utils.cache", "use") else "disabled"}'
        )
    elif args.cache_cmd == "info":
        data = Cache.stats()
        print(
            f"""
            Number of files : {data.get("number_of_files")}
            Total size : {data.get("total_size_bytes")} B
            Total size : {data.get("total_size_kb")} KB
            Total size : {data.get("total_size_mb")} MB
        """
        )
