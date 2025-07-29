from typing import Callable

import requests


class DataSource:
    """
    Base class for data sources.
    """

    def get(self) -> dict:
        """
        Fetch data from the data source.

        :return: Data fetched from the data source.
        """
        raise NotImplementedError("Subclasses should implement this method.")


class HttpDataSource(DataSource):
    def __init__(self, host: str, endpoint: str):
        self.host = host
        self.endpoint = endpoint

    def get(self):
        """
        Fetch data from the specified host and endpoint using the process function.

        :param host: The base URL of the API.
        :param endpoint: The specific endpoint to fetch data from.
        :return: Processed data from the API.
        """
        response = requests.get(f"{self.host}/{self.endpoint}")
        response.raise_for_status()
        return response.json()


class PythonDataSource(DataSource):
    """
    Class to handle Python data source.
    """

    def __init__(self, python_function: Callable[[], dict]):
        """
        Initialize the PythonDataSource with the data.

        :param data: Data to be used by the PythonDataSource.
        """
        self.python_function = python_function

    def get(self) -> dict:
        """
        Get the data from the PythonFunction.

        :return: The data stored in the PythonFunction.
        """
        return self.python_function()
