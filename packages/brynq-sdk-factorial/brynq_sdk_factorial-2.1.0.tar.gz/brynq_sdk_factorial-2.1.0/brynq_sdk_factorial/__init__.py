import requests
from typing import List, Union, Optional, Literal
from brynq_sdk_brynq import BrynQ
from .compensations import Compensations
from .employees import Employees
from .companies import Companies
from .contracts import Contracts
from .files import Files
from .costcenter import Costcenter
from .locations import Locations
from .payroll import Payroll
from .teams import Teams
from .workschedules import Workschedules


# Set the base class for Factorial. This class will be used to set the credentials and those will be used in all other classes.
class Factorial(BrynQ):
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False, demo: bool = False):
        """"
        For the documentation of Factorial, see: https://apidoc.factorialhr.com/docs/authentication-1
        """
        super().__init__()
        self.timeout = 3600
        if demo:
            self.base_url = 'https://api.demo.factorial.dev/api/v2/'
            self.base_url_v1 = 'https://api.demo.factorial.dev/api/v1/'
        else:
            self.base_url = 'https://api.factorialhr.com/api/v2/'
            self.base_url_v1 = 'https://api.factorialhr.com/api/v1/'
        headers = self._get_credentials(system_type)
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.employees = Employees(self)
        self.contracts = Contracts(self)
        self.companies = Companies(self)
        self.costcenter = Costcenter(self)
        self.compensations = Compensations(self)
        self.team = Teams(self)
        self.locations = Locations(self)
        self.payroll = Payroll(self)
        self.workschedules = Workschedules(self)
        self.files = Files(self)
        self.debug = debug

    def _get_credentials(self, system_type):
        """
        Sets the credentials for the SuccessFactors API.
        :param label (str): The label for the system credentials.
        :returns: headers (dict): The headers for the API request, including the access token.
        """
        credentials = self.interfaces.credentials.get(system="factorial", system_type=system_type)
        credentials = credentials.get('data')

        headers = {
            'Authorization': f"Bearer {credentials['access_token']}",
            'Content-Type': 'application/json'
        }

        return headers

