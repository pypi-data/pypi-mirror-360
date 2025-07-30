

from cams_ncp_client._base import BaseClient


class HealthClient(BaseClient):
    """
    Client for the /health endpoint of the CAMS NCP API.

    Example usage:
    >>> from cams_ncp_client.client import CamsNcpApiClient
    >>>
    >>> client = CamsNcpApiClient(base_url="http://localhost:8080")
    >>> health_client = client.health
    >>> readiness: dict = health_client.readiness()
    """

    def readiness(self) -> dict:
        """
        Get the readiness status of the API.
        """
        url = self._build_url_public_api("health/readiness")
        return self._exec_get(url).json()


