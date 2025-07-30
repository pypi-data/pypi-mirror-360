from pathlib import Path
from typing import List

from vito.sas.air import logger

from cams_ncp_client._base import BaseClient
from cams_ncp_client.utils.request_utils import download_file


class ChimereFileClient(BaseClient):
    """
    Client for managing chimere nc files.

    Example usage:
    >>> from cams_ncp_client.client import CamsNcpApiClient
    >>>
    >>> client = CamsNcpApiClient(base_url="http://localhost:8080")
    >>> chimere_file_client = client.chimere_file
    >>> chimere_file_path = chimere_file_client.download_chimere_file(year=2025, month=5, day=1, chimere_model='CHIMERE_EMAP3_V2023', night_version=True,  output_path='./chimere_data')
    """

    def upload_chimere_file(self,
                         year: int,
                         month: int,
                         day: int,
                         chimere_model: str,
                         night_version: bool,
                         file_path: Path):
        """
        Upload a Chimere data file to the API.

        Args:
            year: The year of the chimere data
            month: The month of the chimere data (1-12)
            day: The day of the chimere data (1-31)
            chimere_model: The chimere model name
            night_version: Whether the file is the night version
            file_path: Path to the file to upload

        Returns:
            Response from the API as a dictionary

        Raises:
            ValueError: If parameters are invalid
            FileNotFoundError: If the file doesn't exist
            requests.RequestException: For API communication errors
        """
        # Validate parameters
        if not 1900 < year <= 2200:
            raise ValueError(f"{year} is not a valid year. Year must be between 1900 and 2200")
        if not 1 <= month <= 12:
            raise ValueError("Month must be between 1 and 12")
        if not 1 <= day <= 31:
            raise ValueError("Day must be between 1 and 31")
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Prepare the endpoint URL
        url = self._build_url_private_api(f"/chimere/{year}/{month}/{day}")

        # Prepare form data
        form_data = {
            "chimere_model": chimere_model,
            "night_version": night_version
        }

        # Prepare file
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f)}
            response = self._exec_post(url, data=form_data, files=files)

        # Raise exception for HTTP errors
        logger.debug(f"upload_chimere() url: {url} response code: {response.status_code}, json: {response.json()}")
        response.raise_for_status()


    def download_chimere_file(self,
                           year: int,
                           month: int,
                           day: int,
                           chimere_model: str,
                           night_version: bool,
                           output_path: Path | str) -> Path:
        """
        Download the Chimere data file from the API.

        Args:
            year: The year of the chimere data (>1900, <=2200)
            month: The month of the chimere data (1-12)
            day: The day of the chimere data (1-31)
            chimere_model: The chimere model name
            night_version: Whether the file is the night version
            output_path: Output directory or file path where the downloaded file will be saved.

        Returns:
            Path object pointing to the downloaded file

        Raises:
            ValueError: If parameters are invalid
            requests.RequestException: For API communication errors
            IOError: If the output file cannot be written
        """
        # Validate parameters
        if not 1900 < year <= 2200:
            raise ValueError("Year must be between 2001 and 3000")
        if not 1 <= month <= 12:
            raise ValueError("Month must be between 1 and 12")
        if not 1 <= day <= 31:
            raise ValueError("Day must be between 1 and 31")

        if not isinstance(output_path, Path):
            output_path = Path(output_path)

        # Prepare the endpoint URL - note using different base URL for public endpoint
        # Assuming public route is at the same base but without the /private part
        url = self._build_url_public_api(f"/chimere/{year}/{month}/{day}")

        # Prepare query parameters
        params = {
            "chimere_model": chimere_model,
            "night_version": night_version
        }

        # Send the request with stream=True to handle large files efficiently
        response = self._exec_get(url, params=params, stream=True)

        # Raise exception for HTTP errors
        response.raise_for_status()
        return download_file(response, output_path)


    def list_chimere_files(self, year: int, month: int, day: int) -> List[str]:
        """
        List all chimere files for a given date.

        Args:
            year: The year of the chimere data
            month: The month of the chimere data (1-12)
            day: The day of the chimere data (1-31)

        Returns:
            List of file names

        Raises:
            ValueError: If parameters are invalid
            requests.RequestException: For API communication errors
        """
        # Validate parameters
        if not 1900 < year <= 2200:
            raise ValueError("Year must be between 1900 and 2200")
        if not 1 <= month <= 12:
            raise ValueError("Month must be between 1 and 12")
        if not 1 <= day <= 31:
            raise ValueError("Day must be between 1 and 31")

        url = self._build_url_public_api(f"/chimere/{year}/{month}/{day}/files")
        response = self._exec_get(url)
        response.raise_for_status()

        # Parse JSON response
        string_list: List[str] = response.json()
        assert isinstance(string_list, list), "Expected a list of strings"
        for item in string_list:
            assert isinstance(item, str), f"Expected a string, got {type(item)}"
        return string_list