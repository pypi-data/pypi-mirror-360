import requests
import pandas as pd


class Contracts:
    def __init__(self, factorial):
        self.factorial = factorial
        self.base_endpoint = '/resources/contracts/contract_versions'

    def get(self,
            ids: list = None,
            employee_ids: list[int] = None,
            date: str = None) -> pd.DataFrame:

        # Use locals() to get all function parameters as a dictionary. Do not move this down since it will include all variables in function scope
        func_params = list(locals().items())
        params = {}
        for param, value in func_params:
            if param != 'self' and value is not None:
                params[param] = value

        has_next_page = True
        result_data = pd.DataFrame()
        while has_next_page:
            response = self.factorial.session.get(url=f'{self.factorial.base_url}{self.base_endpoint}',
                                                  params=params,
                                                  timeout=self.factorial.timeout)
            response.raise_for_status()
            response_data = response.json()
            result_data = pd.concat([result_data, pd.DataFrame(response_data['data'])])
            has_next_page = response_data['meta']['has_next_page']
            if has_next_page:
                params['after_id'] = response_data['meta']['end_cursor']

        return result_data

    def update(self, contract_id: str, data: dict) -> requests.Response:
        response = self.factorial.session.put(url=f'{self.factorial.base_url}{self.base_endpoint}/{contract_id}',
                                              json=data,
                                              timeout=self.factorial.timeout)
        response.raise_for_status()
        return response

    def delete(self, contract_id: str) -> requests.Response:
        response = self.factorial.session.delete(url=f'{self.factorial.base_url}{self.base_endpoint}/{contract_id}', timeout=self.factorial.timeout)
        response.raise_for_status()
        return response

    def create(self, data: dict) -> requests.Response:
        raise NotImplementedError
