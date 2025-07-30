import json

from pybrams.utils import Cache
from pybrams.brams.location import Location
from pybrams import brams
from pybrams.brams import system as system
from pybrams.event.meteor import Meteor
from pybrams.utils.interval import Interval


def extract_file_data(args, file):
    meteor = Meteor()
    meteor.extract_infos(args.interval.start, args.interval.end, file, args.plot)

    return {
        "location": file.location,
        "meteor": meteor,
    }


def get_brams_data(args):
    if not hasattr(args, "interval"):
        args.interval = Interval.from_string(args.interval_str)

    cached_data = Cache.get(f"meteors_{args.key}")
    files_data = {}

    if not args.system:
        args.system = [
            system.system_code
            for system in system.all().values()
            if system.antenna == 1
        ]

    if not cached_data or args.recompute_meteors:
        try:
            print("Fetching BRAMS files...")

            files = brams.file.get(args.interval, args.system, clean=True)

            print("Extracting meteor information...")

            for system_code, file_list in files.items():
                if len(file_list) == 1:
                    file_to_extract = file_list[0]
                elif len(file_list) == 2:
                    file_to_extract = file_list[0] + file_list[1]

                files_data[system_code] = extract_file_data(args, file_to_extract)

        except TypeError as e:
            print(f"Error extracting files: {e}")
            return

    else:
        cached_json = json.loads(cached_data)
        cached_system_code = cached_json.keys()

        for system_code in cached_system_code:
            entry = cached_json[system_code]
            files_data[system_code] = {
                "location": Location(*entry["location"].values()),
                "meteor": Meteor(*entry["meteor"].values()),
            }

        other_system_code = list(set(args.system) - set(cached_system_code))

        if other_system_code:
            try:
                print("Fetching BRAMS files...")

                files = brams.file.get(args.interval, other_system_code, clean=True)

                print("Extracting meteor information...")

                for system_code, file_list in files.items():
                    if len(file_list) == 1:
                        file_to_extract = file_list[0]
                    elif len(file_list) == 2:
                        file_to_extract = file_list[0] + file_list[1]
                    files_data[system_code] = extract_file_data(args, file_to_extract)

            except Exception as e:
                pass

        if files_data is None:
            print(f"No BRAMS files data.")
            return

    json_meteors = {
        outer_key: {
            inner_key: inner_value.json()
            for inner_key, inner_value in inner_dict.items()
        }
        for outer_key, inner_dict in files_data.items()
    }

    Cache.cache(f"meteors_{args.key}", json.dumps(json_meteors, indent=4))

    brams_data = {
        system_code: entry
        for system_code, entry in files_data.items()
        if system_code in args.system
    }

    if not any(
        entry["meteor"].v_pseudo_pre_t0 is not None
        for entry in brams_data.values()
        if entry is not None
    ):
        print("No pre-t0 information in the BRAMS data.")
        return

    return brams_data
