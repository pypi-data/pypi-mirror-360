from pathlib import Path

from vito.sas.air import logger

from cams_ncp_client._base import BaseClient
from cams_ncp_client.utils.request_utils import download_file


class EcmwfFileClient(BaseClient):
    """
    Client for managing ECMWF requests.

    Example usage:
    >>> from cams_ncp_client.client import CamsNcpApiClient
    >>>
    >>> client = CamsNcpApiClient(base_url="http://localhost:8080")
    >>> ecmwf_file_client = client.ecmwf_file
    >>> request = {'stream': 'oper', 'class': 'od', 'type': 'fc', 'levtype': 'sfc', 'levelist': 'off', 'param': '167.128/159.128', 'expver': '1', 'time': '00', 'step': '0/to/120/by/3', 'grid': '0.125/0.125', 'area': '52.0/2.5/49.0/6.5'}
    >>> ecmwf_file_path = ecmwf_file_client.ecmwf_request(year=2025, month=6, day=20, request=request, output_path='./')
    """


    def ecmwf_request(self,
            year: int,
            month: int,
            day: int,
            request: dict,
            output_path: Path | str,
            service_name: str = 'mars' ) -> Path | str:
        """
        Trigger an ECMWF request to download a file for a specific date and parameters.
        If the file does not exist, it will be downloaded in the background and this method will return 'PENDING'.

        Args:
            year: The year of the CAMS data (>1900, <=2200)
            month: The month of the CAMS data (1-12)
            day: The day of the CAMS data (1-31)
            request: Dictionary containing the ECMWF request parameters
            service_name: The ECMWF service to use (default is 'mars')
            output_path: Output directory or file path where the downloaded file will be saved.

        Returns:
            Path object pointing to the downloaded file or 'PENDING' if the download is in progress.

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

        # Prepare the endpoint URL - note using different base URL for public endpoint
        # Assuming public route is at the same base but without the /private part
        url = self._build_url_private_api(f"/ecmwf/{year}/{month}/{day}")

        # Prepare query parameters
        params = {
            "service_name": service_name
        }

        # Send the request with stream=True to handle large files efficiently
        response = self._exec_post(url, params=params, stream=True, json=request)

        # Raise exception for HTTP errors
        response.raise_for_status()
        if response.status_code == 202:
            logger.info("ECMWF request is being processed. Please check back later.")
            return "PENDING"

        return download_file(response, output_path)

    def ecmwf_request_and_wait(self,
            year: int,
            month: int,
            day: int,
            request: dict,
            output_path: Path | str,
            service_name: str = 'mars',
            timeout: int = 60 * 60  # Default timeout of 60 minutes
        ) -> Path:
        """
        Trigger an ECMWF request and wait for the file to be available.
        Args:
            year: The year of the CAMS data (>1900, <=2200)
            month: The month of the CAMS data (1-12)
            day: The day of the CAMS data (1-31)
            request: Dictionary containing the ECMWF request parameters
            service_name: The ECMWF service to use (default is 'mars')
            output_path: Output directory or file path where the downloaded file will be saved.
            timeout: Maximum time to wait for the file to be available (in seconds)
        """
        from time import sleep
        from datetime import datetime, timedelta
        start_time = datetime.now()
        while True:
            result = self.ecmwf_request(year, month, day, request, output_path, service_name)
            if result != "PENDING":
                return Path(result)
            # Check if timeout has been reached
            if datetime.now() - start_time > timedelta(seconds=timeout):
                raise TimeoutError(f"ECMWF request timed out after {timeout} seconds.")
            # Wait 30 seconds before checking again
            sleep(30)