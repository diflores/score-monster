import gspread
import gspread.exceptions as gspExceptions
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict
from time import sleep
from datetime import datetime

QUOTA = 100  # 1s per request to the api


class Worksheet:
    def __init__(self, sheet_url: str, tab_name: str, show_stats: bool):

        # Define the scope of permissions
        scope = ["https://spreadsheets.google.com/feeds"]
        # use creds to create a client to interact with the Google Drive API
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json", scope
        )
        self.client = gspread.authorize(creds)
        self.show_stats = show_stats

        # Private attribute that holds the amount of requests
        self.__requests = 0

        # Find a workbook by name and open the sheet name
        # Make sure you use the right name here.
        self.sheet = self.client.open_by_url(sheet_url).worksheet(tab_name)
        self.requests += 1  # Opening counts as a request

        self.stats = self.client.open_by_url(sheet_url).worksheet("Stats")
        self.requests += 1  # Opening counts as a request

    @property
    def requests(self):
        return self.__requests

    @requests.setter
    def requests(self, value):
        if value >= QUOTA:
            sleep(20)  # Sleep 5 seconds to restrict quota
        self.__requests = value % QUOTA

    def get_hacker_cell(self, hacker: str):
        """
            Finds the hacker username in a worksheet and returns it's cell
        """
        try:
            # The cell found
            cell: gspread.Cell = self.sheet.find(hacker)

            # Increment request counter
            self.requests += 1

            return cell

        except gspread.CellNotFound:
            # If not found, return None
            return None

        except gspExceptions.APIError as e:
            # Raise any other error that may occur
            err_json = e.response.json()
            if e.response.status_code == 400:
                raise PermissionError(err_json["error"]["message"])
            elif (
                e.response.status_code == 429
                and "quota" in err_json["error"]["message"].lower()
            ):
                # Sleep to keep up with quota and call again
                sleep(100)
                return self.get_hacker_cell(hacker)
            else:
                raise ConnectionError(err_json["error"]["message"])

    def _add_value(self, value, *, row: int, col: int):
        """
            Adds or replaces a value of a certain row and column
        """

        try:

            # Try to find the cell in the worksheet and updated
            self.sheet.update_cell(row, col, value)

            # Increment request counter
            self.requests += 1

            # Return true if updated
            return True

        except gspread.CellNotFound:
            # If exception of cell not found is raised
            # Return not added
            return False
        except gspExceptions.APIError as e:
            # Grab the error
            err_json = e.response.json()

            # Check the status code. If known do something specific
            if e.response.status_code == 400:
                raise PermissionError(err_json["error"]["message"])
            elif (
                e.response.status_code == 429
                and "quota" in err_json["error"]["message"].lower()
            ):
                # Sleep to keep up with quota and call again
                sleep(QUOTA + 1)
                self._add_value(value, row=row, col=col)
            else:
                raise ConnectionError(err_json["error"]["message"])

    def update_score(self, hacker: str, score: str, column: int, **kwargs):
        """
            Update a score of hacker in a certain column.
            :param kwargs: It is only there so that hacker data can be
                unpacked without throwing eny errors.
        """
        cell = self.get_hacker_cell(hacker)

        # Increment request counter
        self.requests += 1

        # If hacker is not on the list already append it score at the end
        if not cell:

            # Make a fill of empty cells. Substract one because first column
            # is for the hackerrank username
            fill = ["" for _ in range(column - 1)]

            # Add the hacker username, a fill of empty cells and the score
            # On its corresponding column

            try:

                self.sheet.append_row([hacker] + fill + [score])

                # Increment request counter
                self.requests += 1
                return True
            except gspExceptions.APIError as e:
                # Grab the error
                err_json = e.response.json()

                # Check the status code. If known do something specific
                if e.response.status_code == 400:
                    raise PermissionError(err_json["error"]["message"])
                elif (
                    e.response.status_code == 429
                    and "quota" in err_json["error"]["message"].lower()
                ):
                    # Sleep to keep up with quota and call again
                    sleep(QUOTA + 1)
                    return self.update_score(hacker, score, column, **kwargs)
                else:
                    raise ConnectionError(err_json["error"]["message"])

        # Add one because this function uses indexes starting on 1
        return self._add_value(score, row=cell.row, col=column + 1)

    def update_scores(self, hackers: List[Dict[str, str]], column: int):
        """
            Updates the scores of a list of hackers.
        """
        updated = 0

        # Iterate over every hacker, unpack its data, and add its score
        for hacker in hackers:

            updated += int(self.update_score(column=column, **hacker))

        # If option to show stats is true, update the stats
        if self.show_stats:
            self.update_stats()
            self.requests += 1

        # Return the number of rows affected
        return updated

    def update_stats(self):
        """
            Updates the stats cells
        """
        self.stats.update_cell(2, 1, datetime.now().strftime("%d %b, %Y %H:%M:%S"))
