# Libs
from os import path
from json import load as load_json_file
from typing import Dict, Any, List
from datetime import datetime

# Local
from .gsheets import Worksheet
from .hackerrank import HackerrankAPI


class Mediator:
    def __init__(self):

        # Ensure the needed files are there.
        assert path.exists("credentials.json"), (
            "Credentials are missing."
            " Please add or rename your"
            " credentials file "
            "to credentials.json"
        )
        assert path.exists("collect.json"), "The collect.json file is missing."

        # Open the configuration file
        with open("collect.json", encoding="utf-8") as fp:
            # Store all the options on a variable
            options: Dict[str, Any] = load_json_file(fp)

        # Ensure that there is a sheets parameter
        if not options.get("sheets"):
            raise SyntaxError("Collection JSON does not have a sheets option.")

        # Store all the sheets information
        self.sheets: List[Dict[str, Any]] = options["sheets"]

        # Store wanted usernames
        self.filter = [] if not options.get("filter") else options["filter"]

    def begin_collection(self):
        """
            Begins the collection of scores from the json.
        """

        # First, the sheets are enumerated, and iterated over
        for i, sheet_opts in enumerate(self.sheets):
            # Ensure the json has the necessary data.
            assert sheet_opts.get("sheetUrl"), (
                f"There is no sheetUrl" f" for the worksheet {i}"
            )
            assert sheet_opts.get("tabName"), (
                f"There is tabName" f" to be used for the" f" worksheet {i}"
            )
            assert sheet_opts.get("contests"), (
                f"There are no contests" f" for the worksheet {i}"
            )

            # Extract the data needed from the json
            sheet_url = sheet_opts["sheetUrl"]
            tab_name = sheet_opts["tabName"]
            contests = sheet_opts["contests"]

            # If no param of showStats is found, then stats
            # won't be shown for that sheet
            show_stats = bool(sheet_opts.get("showStats"))

            # Instantiate the worksheet with all the data
            sheet = Worksheet(sheet_url, tab_name, show_stats)

            # Enumerate and iterate over the contests, begin in one,
            # as the first column is for the usernames
            for j, contest_info in enumerate(contests, 1):
                # Ensure there is a link
                assert contest_info.get("link"), (
                    f"There is no link for the"
                    f" contest {j-1} on the"
                    f" worksheet {i}."
                )
                # Get the existing data
                link = contest_info["link"]
                # If no start limit or end limit is given.
                # It is assumed to be none.
                start_limit = (
                    datetime(*contest_info["startLimit"])
                    if contest_info.get("startLimit")
                    else None
                )
                end_limit = (
                    datetime(*contest_info["endLimit"])
                    if contest_info.get("endLimit")
                    else None
                )

                # Instantiate the hackerrank application
                hackerrank_API = HackerrankAPI(
                    link, self.filter, start_limit, end_limit
                )
                hackers = hackerrank_API.get_leadearboard()

                # Update the scores
                sheet.update_scores(hackers, column=j)
