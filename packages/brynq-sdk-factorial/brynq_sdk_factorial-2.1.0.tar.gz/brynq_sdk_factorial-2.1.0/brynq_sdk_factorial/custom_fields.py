from typing import Literal, List

import requests
import pandas as pd


class CustomFields:
    def __init__(self, factorial):
        self.factorial = factorial
        self.base_endpoint = '/resources/custom_fields/fields'

    def get(self,
            ids: list = None,
            field_type: str = None,
            label: str = None,
            slug: str = None,
            company_id: int = None
            ) -> pd.DataFrame:

        # Use locals() to get all function parameters as a dictionary. Do not move this down since it will include all variables in function scope
        func_params = locals().items()
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
            params['after_id'] = response_data['meta']['end_cursor']

        return result_data

    def update(self, contract_id: str, data: dict) -> requests.Response:
        response = self.factorial.session.put(url=f'{self.factorial.base_url}{self.base_endpoint}/{self.base_endpoint}',
                                              json=data,
                                              timeout=self.factorial.timeout)
        response.raise_for_status()
        return response

    def delete(self, contract_id: str) -> requests.Response:
        response = self.factorial.session.delete(url=f'{self.factorial.base_url}{self.base_endpoint}/{self.base_endpoint}', timeout=self.factorial.timeout)
        response.raise_for_status()
        return response

    def create(self,
               company_id: int,
               editable: Literal['owned', 'reportees', 'teamleader',  'everybody'] = None,
               visible: Literal['owned', 'reportees', 'teamleader',  'everybody'] = None,
               label: str = None,
               field_type: Literal['text', 'long_text', 'date', 'rating', 'checkbox', 'single_choice', 'multiple_choice', 'money', 'cents'] = None,
               min_value: int = None,
               max_value: int = None,
               required: bool = None,
               options: List[str] = None,
               position: int = None
               ) -> requests.Response:
        # Use locals() to get all function parameters as a dictionary. Do not move this down since it will include all variables in function scope
        func_params = list(locals().items())
        data = {}
        for param, value in func_params:
            if param != 'self' and value is not None:
                data[param] = value

        response = self.factorial.session.post(url=f'{self.factorial.base_url}{self.base_endpoint}/{self.base_endpoint}',
                                               data=data,
                                               timeout=self.factorial.timeout)
        response.raise_for_status()
        return response 
