import gspread
import gspread.exceptions as gspExceptions
from oauth2client.service_account import ServiceAccountCredentials
from typing import List
from time import sleep

QUOTA = 1  # 1s per request to the api


class Worksheet:
    def __init__(self, *, sheet_url: str, sheet_name: str):

        # Define the scope of permissions
        scope = ['https://spreadsheets.google.com/feeds']
        # use creds to create a client to interact with the Google Drive API
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            'credentials.json', scope)
        self.client = gspread.authorize(creds)

        # Find a workbook by name and open the sheet name
        # Make sure you use the right name here.
        self.sheet = self.client.open_by_url(sheet_url).worksheet(sheet_name)

    def get_student_cell(self, student_number: str):
        '''
            Finds the student number in a worksheet and returns it's cell
        '''
        try:
            # The cell found
            cell: gspread.Cell = self.sheet.find(student_number)
            return cell

        except gspread.CellNotFound:
            # If not found, return None
            return None

        except gspExceptions.APIError as e:
            # Raise any other error that may occur
            err_json = e.response.json()
            if e.response.status_code == 400:
                raise PermissionError(err_json['error']['message'])
            else:
                raise ConnectionError(err_json['error']['message'])

    def _add_value(self, value, *, row: int, col: int):
        '''
            Adds or replaces a value of a certain row and column
        '''

        try:

            # Try to find the cell in the worksheet and updated
            self.sheet.update_cell(row, col, value)
            # Return true if updated
            return True

        except gspread.CellNotFound:
            # If exception of cell not found is raised
            # Return not added
            return False
        except gspExceptions.APIError as e:
            err_json = e.response.json()
            if e.response.status_code == 400:
                raise PermissionError(err_json['error']['message'])
            else:
                raise ConnectionError(err_json['error']['message'])

    def add_students(self, student_list: List[List[str]], section: str,
                     *, index: int):
        '''
        Adds a batch of students to a section.
        The index paramater corresponds to the index of the student item
        where the student number is.
        Returns the number of students added.
        '''
        added = 0
        for student in student_list:
            student_number = student[index]
            added += int(self._add_student(student, student_number, section))
            sleep(QUOTA)
        return added
