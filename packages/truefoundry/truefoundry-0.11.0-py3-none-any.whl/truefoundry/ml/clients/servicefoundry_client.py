import functools

from truefoundry.common.constants import (
    SERVICEFOUNDRY_CLIENT_MAX_RETRIES,
    VERSION_PREFIX,
)
from truefoundry.common.exceptions import HttpRequestException
from truefoundry.common.request_utils import (
    http_request,
    request_handling,
    requests_retry_session,
)
from truefoundry.common.servicefoundry_client import (
    ServiceFoundryServiceClient as BaseServiceFoundryServiceClient,
)
from truefoundry.common.utils import get_user_agent
from truefoundry.ml.exceptions import MlFoundryException


class ServiceFoundryServiceClient(BaseServiceFoundryServiceClient):
    def __init__(self, tfy_host: str, token: str):
        super().__init__(tfy_host=tfy_host)
        self._token = token

    @functools.cached_property
    def _min_cli_version_required(self) -> str:
        # TODO (chiragjn): read the mlfoundry min cli version from the config?
        return self.python_sdk_config.truefoundry_cli_min_version

    def get_integration_from_id(self, integration_id: str):
        integration_id = integration_id or ""
        session = requests_retry_session(retries=SERVICEFOUNDRY_CLIENT_MAX_RETRIES)
        response = http_request(
            method="get",
            url=f"{self._api_server_url}/{VERSION_PREFIX}/provider-accounts/provider-integrations",
            token=self._token,
            timeout=3,
            params={"id": integration_id, "type": "blob-storage"},
            session=session,
            headers={
                "User-Agent": get_user_agent(),
            },
        )

        try:
            result = request_handling(response)
            assert isinstance(result, dict)
        except HttpRequestException as he:
            raise MlFoundryException(
                f"Failed to get storage integration from id: {integration_id}. Error: {he.message}",
                status_code=he.status_code,
            ) from None
        except Exception as e:
            raise MlFoundryException(
                f"Failed to get storage integration from id: {integration_id}. Error: {str(e)}"
            ) from None

        data = result.get("data", result.get("providerAccounts"))
        # TODO (chiragjn): Parse this using Pydantic
        if data and len(data) > 0 and data[0]:
            return data[0]
        else:
            raise MlFoundryException(
                f"Invalid storage integration id: {integration_id}"
            )
