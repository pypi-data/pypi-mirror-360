from brynq_sdk_brynq import BrynQ
import pandas as pd
import requests
from datetime import datetime, date
from typing import Union, List, Dict, Optional, Any, Literal
from .employees import Employees
from .timesheets import Timesheets
from .departments import Departments
from .accounts import Accounts
from .corrections import Corrections
from .events import Events
from .holidays import Holidays
from .locations import Locations
from .logs import Logs
from .open_shifts import OpenShifts
from .required_shifts import RequiredShifts
from .reports import Reports
from .rosters import Rosters
from .shifts import Shifts
from .teams import Teams
from .team_days import TeamDays
from .clock_ips_locations import ClockIpsLocations
from .kiosk import Kiosk
from .users import Users
from .planning import Planning
from .skills import Skills
from .weather import Weather
from .insights import Insights


class Shiftbase(BrynQ):
    """
    This class is meant to be a simple wrapper around the Shiftbase API. In order to start using it, authorize your application in BrynQ.
    You will need to provide a token for the authorization, which can be set up in BrynQ and referred to with a label.
    You can find the Shiftbase API docs here: https://developer.shiftbase.com/
    """
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False):
        super().__init__()
        self.timeout = 3600

        api_type = "API"
        self.base_url = "https://api.shiftbase.com/api/"

        credentials = self.interfaces.credentials.get(system="shiftbase", system_type=system_type)
        self.headers = {
            "Authorization": f"{api_type} {credentials['data']['api_token']}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Initialize session
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Initialize entity classes
        self.employees = Employees(self)
        self.timesheets = Timesheets(self)
        self.departments = Departments(self)
        self.accounts = Accounts(self)
        self.corrections = Corrections(self)
        self.events = Events(self)
        self.holidays = Holidays(self)
        self.locations = Locations(self)
        self.logs = Logs(self)
        self.open_shifts = OpenShifts(self)
        self.required_shifts = RequiredShifts(self)
        self.reports = Reports(self)
        self.rosters = Rosters(self)
        self.shifts = Shifts(self)
        self.teams = Teams(self)
        self.team_days = TeamDays(self)
        self.clock_ips_locations = ClockIpsLocations(self)
        self.kiosk = Kiosk(self)
        self.users = Users(self)
        self.planning = Planning(self)
        self.skills = Skills(self)
        self.weather = Weather(self)
        self.insights = Insights(self)

    def get(self, endpoint: str, filters: Optional[Dict] = None) -> Any:
        """
        Makes a GET request to the Shiftbase API endpoint

        Args:
            endpoint (str): API endpoint to call
            filters (Dict, optional): Query parameters

        Returns:
            Any: Raw response data from the API
        """
        response = self.session.get(
            url=f"{self.base_url}{endpoint}",
            params=filters,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()['data']

    def get_absence(self, filters: dict = None) -> pd.DataFrame:
        """
        This method retrieves the absence data from Shiftbase.
        @deprecated: Use employees.absences.get() instead
        :param filters: A dict with filters. See the Shiftbase API docs for more info: https://developer.shiftbase.com/docs/core/2e1fba402f9bb-list-absentees.
        :return:
        """
        import warnings
        warnings.warn(
            "This method is deprecated. Use employees.absences.get() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        response = requests.get(url=f"{self.base_url}absentees?",
                                headers=self.headers,
                                params=filters,
                                timeout=self.timeout)
        # {"min_date": "2022-01-01", "status": "Approved", "max_date": end_of_next_year})
        response.raise_for_status()
        response_json = response.json()['data']
        absence_data = [absence.get("Absentee") for absence in response_json]

        return pd.DataFrame(absence_data)

    def get_absence_types(self, filters: dict = None) -> pd.DataFrame:
        """
        This method retrieves the get_absence_types data from Shiftbase.
        @deprecated: Use employees.absences.absence_types.get() instead
        :return:
        """
        import warnings
        warnings.warn(
            "This method is deprecated. Use employees.absences.get_types() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        response = requests.get(url=f"{self.base_url}absentee_options?",
                                headers=self.headers,
                                params=filters,
                                timeout=self.timeout)
        response.raise_for_status()
        response_json = response.json()['data']
        absence_type_data = [absence_type.get("AbsenteeOption") for absence_type in response_json]

        return pd.DataFrame(absence_type_data)

    def get_employees(self, filters: dict = None) -> pd.DataFrame:
        """
        This method retrieves the employees from Shiftbase.
        @deprecated: Use employees.get() instead
        :return:
        """
        import warnings
        warnings.warn(
            "This method is deprecated. Use employees.get() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        response = requests.get(url=f"{self.base_url}users?",
                                headers=self.headers,
                                params=filters,
                                timeout=self.timeout)
        response.raise_for_status()
        response_json = response.json()['data']
        employees = [employee.get("User") for employee in response_json]

        return pd.DataFrame(employees)

    def get_mappings(self, employer_id: int) -> pd.DataFrame:
        response = requests.get(url=f"{self.base_url}integrations/map/{employer_id}",
                                headers=self.headers,
                                timeout=self.timeout)
        response.raise_for_status()
        mapping_data = response.json()["data"]["ApiMapping"]["employee_import_mapped_employees"]
        mapping = pd.DataFrame(mapping_data, columns=["internal_id", "external_id"])

        return mapping

    def get_timesheets(self, filters: dict = None) -> pd.DataFrame:
        """
        This method retrieves the timesheets from Shiftbase.
        @deprecated: Use timesheets.get() instead
        :return:
        """
        import warnings
        warnings.warn(
            "This method is deprecated. Use timesheets.get() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        response = requests.get(url=f"{self.base_url}timesheets",
                                headers=self.headers,
                                params=filters,
                                timeout=self.timeout)
        response.raise_for_status()
        response_json = response.json()['data']
        worked_time = [rateblock.get("RateBlock") for rateblock in response_json]
        worked_time_list = [item for sublist in worked_time for item in sublist]
        timesheets_meta = [timesheet.get("Timesheet") for timesheet in response_json]
        worked_time = pd.DataFrame(worked_time_list)
        timesheets_meta = pd.DataFrame(timesheets_meta)
        del timesheets_meta["Rates"]
        timesheets = pd.merge(worked_time, timesheets_meta, how="left", left_on="timesheet_id", right_on="id", suffixes=("", "_meta"))

        return timesheets

    def get_contracts(self, filters: dict = None) -> pd.DataFrame:
        """
        This method retrieves the contracts from Shiftbase.
        @deprecated: Use employees.contracts.get() instead
        :return:
        """
        import warnings
        warnings.warn(
            "This method is deprecated. Use employees.contracts.get() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        response = requests.get(url=f"{self.base_url}contracts",
                                headers=self.headers,
                                params=filters,
                                timeout=self.timeout)
        response.raise_for_status()
        response_json = response.json()['data']
        contracts = [contract.get("Contract") for contract in response_json]

        return pd.DataFrame(contracts)

    def get_contract_types(self, filters: dict = None) -> pd.DataFrame:
        """
        This method retrieves the contract types from Shiftbase.
        @deprecated: Use employees.contracts.contract_types.get() instead
        :return:
        """
        import warnings
        warnings.warn(
            "This method is deprecated. Use contract_types.get() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        response = requests.get(url=f"{self.base_url}contract_types",
                                headers=self.headers,
                                params=filters,
                                timeout=self.timeout)
        response.raise_for_status()
        response_json = response.json()['data']
        contract_types = [contract_type.get("ContractType") for contract_type in response_json]

        return pd.DataFrame(contract_types)

    def get_absentees(self, filters: dict = None) -> pd.DataFrame:
        """
        This method retrieves the absentees from Shiftbase.
        @deprecated: Use employees.absences.get() instead
        :return:
        """
        import warnings
        warnings.warn(
            "This method is deprecated. Use employees.absences.get() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        response = requests.get(url=f"{self.base_url}absentees",
                                headers=self.headers,
                                params=filters,
                                timeout=self.timeout)
        response.raise_for_status()
        response_json = response.json()['data']
        absentees = [absentee.get("Absentee") for absentee in response_json]

        return pd.DataFrame(absentees)

    def get_absentee_options(self, filters: dict = None) -> pd.DataFrame:
        """
        This method retrieves the absentee options from Shiftbase.
        @deprecated: Use employees.absences.absence_types.get instead
        :return:
        """
        import warnings
        warnings.warn(
            "This method is deprecated. Use employees.absences.get_types() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        response = requests.get(url=f"{self.base_url}absentee_options",
                                headers=self.headers,
                                params=filters,
                                timeout=self.timeout)
        response.raise_for_status()
        response_json = response.json()['data']
        absentee_options = [absentee_option.get("AbsenteeOption") for absentee_option in response_json]

        return pd.DataFrame(absentee_options)

    @staticmethod
    def datetime_converter(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")