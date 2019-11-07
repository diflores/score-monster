# libs
from requests import get as http_get, Response
from json import loads as load_json_str
from typing import List, Union, Dict
from datetime import datetime

# local
from .constants.templates import HACKERRANK_LINK
from .constants.fixed_numbers import LEADERBOARD_LIMIT


class HackerrankAPI:
    """
        An interface for interacting with hackerrank information
    """

    TARGET_KEYS = ["hacker", "score", "time_taken"]

    def __init__(
        self,
        contest: str,
        username_filter: list,
        start_limit: datetime = None,
        end_limit: datetime = None,
    ):

        self.contest = contest
        self.username_filter = username_filter
        self.start_limit = start_limit
        self.end_limit = end_limit

    def render_link(self, offset, limit):
        """
            Renders a links of a contest with a certain offset and limit
        """
        return HACKERRANK_LINK.substitute(
            contest_name=self.contest, offset=offset, limit=limit
        )

    def on_time(self, actual: str):
        """
            Indicates if a date is between the ranges defined on the
            instance of the api. If no limits are specified in any of the
            sides, then it is assumed to be true on that side. For instance
            if no limits are specified, any datetime is on times

        """

        if self.start_limit:
            final_date = datetime.fromtimestamp(
                self.start_limit.timestamp() + float(actual)
            )
        else:
            # Irrelevant if start_limit is not set. Only as a placeholder
            final_date = datetime.now()

        # If the start limit is defined, then compare if it is bigger.
        bottom_limit = self.start_limit <= final_date if self.start_limit else True

        # If the end limit is defined, then compare if it is smaller.
        top_limit = final_date <= self.end_limit if self.end_limit else True

        # Return if it meets bottom limit conditions and top limit conditions
        return bottom_limit and top_limit

    def filter_keys(self, hacker):
        """
            Filters any key that is not wanted from the hacker information.

            Filter is based on TARGET_KEYS defined above.
        """

        # Return a new dictionary with all the information filtered.
        return {K: hacker[K] for K in self.TARGET_KEYS}

    def parse_new_hackers(self, response: Response):
        """
            Parses a json in string format, and extracts all hackers
        """

        # Parse the response into a dictionary
        json_response = load_json_str(response.text)

        # Models contains all the hackers of that pagination
        # Filter only the target keys set above
        return map(self.filter_keys, json_response["models"])

    def filter_on_time(self, hackers: List[Dict[str, str]]):
        return filter(lambda h: self.on_time(h["time_taken"]), hackers)

    def get_leadearboard(self):
        """
        Gets all the hackers from the leaderboard of a certain contest.
        """

        # This list will store all the hackers obtained on the leaderboard.
        all_hackers: List[Dict[str, Union[int, str]]] = []

        # Begin by setting an offset of 0, increment by setting as offset all
        # the added.
        offset = 0

        print(self.render_link(offset, LEADERBOARD_LIMIT))
        # Make initial request
        response = http_get(self.render_link(offset, LEADERBOARD_LIMIT))

        # Make a json from it
        json_response = load_json_str(response.text)

        # Ge the total of hackers
        total = json_response["total"]

        while len(all_hackers) < total:

            # Get the new hackers from the response
            new_hackers = self.parse_new_hackers(response)

            # Add the new hackers to the complete list
            all_hackers.extend(new_hackers)

            # The offset will be all the hackers so far
            offset = len(all_hackers)

            # Request a new set of hackers
            response = http_get(self.render_link(offset, LEADERBOARD_LIMIT))

        # Filter hackers
        if self.username_filter:
            all_hackers = list(
                filter(lambda x: x["hacker"] in self.username_filter, all_hackers)
            )

        # Retrun the complete list of hackers
        return self.filter_on_time(all_hackers)
