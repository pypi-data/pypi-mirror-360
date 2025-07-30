from pybrams.utils.interval import Interval
from rich.console import Console
from rich.table import Table
from rich import box
from pybrams.utils.interval import Interval
from pybrams.brams.file import availability as file_availability
from pybrams.brams.adsb import availability as adsb_availability


def availability_color_bool(value):
    return "green" if value else "dark_red"


def availability_color(value):
    if value == 1.0:
        return "green"
    elif value >= 0.8:
        return "bright_green"
    elif value >= 0.6:
        return "yellow"
    elif value >= 0.4:
        return "dark_orange"
    elif value >= 0.2:
        return "orange3"
    elif value > 0:
        return "red"
    else:
        return "dark_red"


def setup_args(subparsers):
    subparser_availability = subparsers.add_parser("availability")
    subparser_availability_subparsers = subparser_availability.add_subparsers(
        dest="availability_cmd", required=True
    )

    subparser_availability_brams = subparser_availability_subparsers.add_parser(
        "brams", help="check the BRAMS data availability"
    )
    subparser_availability_adsb = subparser_availability_subparsers.add_parser(
        "adsb", help="check the ADSB data availability"
    )

    subparser_availability_brams.add_argument(
        "interval", type=str, help="datetime interval in ISO 8601 format"
    )
    subparser_availability_adsb.add_argument(
        "interval", type=str, help="datetime interval in ISO 8601 format"
    )


def run(args):
    console = Console()
    if args.availability_cmd == "brams":
        interval: Interval = Interval.from_string(args.interval)
        table = Table(
            title=f"Availability from {interval.start} to {interval.end}",
            show_lines=True,
        )
        table.add_column("System", style="bold", no_wrap=True, overflow="fold")
        table.add_column("Availability", no_wrap=True, overflow="fold")
        for system_code, data in file_availability(interval).items():
            blocks = "".join(
                f"[{availability_color(value)}]█[/{availability_color(value)}]"
                for value in data.values()
            )
            table.add_row(system_code, blocks)

        console.print(table)
    elif args.availability_cmd == "adsb":
        interval: Interval = Interval.from_string(args.interval)
        table = Table(
            title=f"Availability from {interval.start} to {interval.end}",
            show_lines=True,
        )
        table.add_column("ADSB Receiver", style="bold", no_wrap=True, overflow="fold")
        table.add_column("Availability", no_wrap=True, overflow="fold")
        blocks = "".join(
            f"[{availability_color_bool(availability)}]█[/{availability_color_bool(availability)}]"
            for availability in adsb_availability(interval).values()
        )

        table.add_row("BEUCCL", blocks)

        console.print(table)
