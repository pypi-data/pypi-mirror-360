from pathlib import Path
from typing import List

from vito.sas.air import logger

from cams_ncp_client._base import BaseClient
from cams_ncp_client.utils.request_utils import download_file


class CamsFileClient(BaseClient):
    """
    Client for managing CAMS nc files.

    Example usage:
    >>> from cams_ncp_client.client import CamsNcpApiClient
    >>>
    >>> client = CamsNcpApiClient(base_url="http://localhost:8080")
    >>> cams_file_client = client.cams_file
    >>> cams_file_path = cams_file_client.download_cams_file(year=2025, month=5, day=1, pollutant='PM25', cams_model='CAMS_CHIMERE', forecast_days=4, output_path='./cams_data')
    """

    def upload_cams_file(self,
                         year: int,
                         month: int,
                         day: int,
                         pollutant: str,
                         cams_model: str,
                         forecast_days: int,
                         file_path: Path):
        """
        Upload CAMS data file to the API.

        Args:
            year: The year of the CAMS data
            month: The month of the CAMS data (1-12)
            day: The day of the CAMS data (1-31)
            pollutant: The pollutant type
            cams_model: The CAMS model name
            forecast_days: The number of forecasted days
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
        url = self._build_url_private_api(f"/cams/{year}/{month}/{day}")

        # Prepare form data
        form_data = {
            "pollutant": pollutant,
            "cams_model": cams_model,
            "forecast_days": forecast_days
        }

        # Prepare file
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f)}
            response = self._exec_post(url, data=form_data, files=files)

        # Raise exception for HTTP errors
        logger.debug(f"upload_cams() url: {url} response code: {response.status_code}, json: {response.json()}")
        response.raise_for_status()


    def download_cams_file(self,
                           year: int,
                           month: int,
                           day: int,
                           pollutant: str,
                           cams_model: str,
                           forecast_days: int,
                           output_path: Path | str) -> Path:
        """
        Download CAMS data file from the API.

        Args:
            year: The year of the CAMS data (>1900, <=2200)
            month: The month of the CAMS data (1-12)
            day: The day of the CAMS data (1-31)
            pollutant: The pollutant type
            cams_model: The CAMS model name
            forecast_days: The number of forecasted days
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
        url = self._build_url_public_api(f"/cams/{year}/{month}/{day}")

        # Prepare query parameters
        params = {
            "pollutant": pollutant,
            "cams_model": cams_model,
            "forecast_days": forecast_days
        }

        # Send the request with stream=True to handle large files efficiently
        response = self._exec_get(url, params=params, stream=True)
        return download_file(response, output_path)


    def list_cams_files(self, year: int, month: int, day: int) -> List[str]:
        """
        List all CAMS files for a given date.

        Args:
            year: The year of the CAMS data
            month: The month of the CAMS data (1-12)
            day: The day of the CAMS data (1-31)

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

        url = self._build_url_public_api(f"/cams/{year}/{month}/{day}/files")
        response = self._exec_get(url)
        response.raise_for_status()

        # Parse JSON response
        string_list: List[str] = response.json()
        assert isinstance(string_list, list), "Expected a list of strings"
        for item in string_list:
            assert isinstance(item, str), f"Expected a string, got {type(item)}"
        return string_list