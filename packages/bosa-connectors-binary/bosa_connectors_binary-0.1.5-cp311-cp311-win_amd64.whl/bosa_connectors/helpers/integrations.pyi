from _typeshed import Incomplete
from bosa_connectors.auth import ApiKeyAuthenticator as ApiKeyAuthenticator
from bosa_connectors.models.result import ActionResult as ActionResult

class BosaIntegrationHelper:
    """Helper class for BOSA API integrations."""
    OAUTH2_FLOW_ENDPOINT: str
    INTEGRATION_CHECK_ENDPOINT: str
    DEFAULT_TIMEOUT: int
    api_base_url: Incomplete
    auth_scheme: Incomplete
    def __init__(self, api_base_url: str = 'https://api.bosa.id', api_key: str = 'bosa') -> None:
        '''Initializes the BosaIntegrationHelper with the provided API key.

        Args:
            api_base_url (str): The base URL for the BOSA API. Defaults to "https://api.bosa.id".
            api_key (str): The API key for authentication. Defaults to "bosa".
        '''
    def user_has_integration(self, app_name: str, token: str) -> bool:
        """Checks whether or not a user has an integration for a given app in this client.

        Args:
            app_name: The name of the app/connector to use
            token: The BOSA User Token

        Returns:
            True if the user has an integration for the given app
        """
    def initiate_integration(self, app_name: str, token: str, callback_uri: str) -> str:
        """Initiates a 3rd party integration for a user against a certain client.

        Args:
            app_name: The name of the app/connector to use
            token: The BOSA User Token
            callback_uri: The callback URL to be used for the integration

        Returns:
            The integration URL
        """
    def remove_integration(self, app_name: str, token: str) -> ActionResult:
        """Removes a 3rd party integration for a user against a certain client.

        Args:
            app_name: The name of the app/connector to use
            token: The BOSA User Token

        Returns:
            Result that contains an error message (if any), and the success status.
        """
