import requests
import pandas as pd


class Files:

    def __init__(self, core):
        self.core = core
        self.base_endpoint = '/core/employees'

    def get(self) -> pd.DataFrame:
        response = requests.get(f'{self.core.factorial.base_url_v1}{self.base_endpoint}', timeout=self.factorial.timeout)
        response.raise_for_status()
        return pd.DataFrame(response.json())

    def update(self, employee_id: str, data: dict) -> requests.Response:
        response = requests.put(f'{self.core.factorial.base_url_v1}{self.base_endpoint}/{employee_id}', json=data, timeout=self.factorial.timeout)
        response.raise_for_status()
        return response

    def create(self, data: dict) -> requests.Response:
        raise NotImplementedError