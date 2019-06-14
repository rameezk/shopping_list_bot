#!/usr/bin/env python3

import argparse
import pathlib
from sys import exit

from shopping_list_bot import PriceUpdater


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--json",
        dest="client_secret_file",
        required=True,
        help="Google Json file containing secrets.",
    )
    parser.add_argument(
        "--spreadsheet_name",
        "-s",
        dest="spreadsheet_name",
        required=True,
        help="Name of the spreadsheet you want to open.",
    )
    parser.add_argument(
        "--share-with",
        dest="shared",
        help="[email address] Share the spreadsheet with someone via email",
    )
    parser.add_argument(
        "--update",
        dest="update_spreadsheet",
        action="store_true",
        help="Update spreadsheet with new prices.",
    )
    parser.add_argument(
        "--loglevel",
        dest="log_level",
        default="INFO",
        help="log level to use, default [INFO], options [INFO, DEBUG, ERROR]",
    )
    args = vars(parser.parse_args())
    email_list = []
    client_secret = pathlib.Path(args.get("client_secret_file")).absolute()

    if not client_secret.is_file():
        exit(f"File: {client_secret} could not be found!!!")

    if args.get("shared", False):
        email_list.append(args.get("shared"))

    if args.get("log_level", "INFO").lower() == "debug":
        log_level = "DEBUG"
        headless = False
    else:
        log_level = args.get("log_level", "INFO")
        headless = True

    price_updater = PriceUpdater(
        spreadsheet_name=args.get("spreadsheet_name"),
        secrets_json=client_secret,
        share=email_list,
        log_level=log_level,
        headless=headless,
    )

    if args.get("update_spreadsheet", False):
        price_updater.update_spreadsheet()
    else:
        price_updater.process_item_list()


if __name__ == "__main__":
    main()
