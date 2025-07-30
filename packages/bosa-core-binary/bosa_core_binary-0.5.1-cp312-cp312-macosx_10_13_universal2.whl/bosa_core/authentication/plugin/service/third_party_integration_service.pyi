from _typeshed import Incomplete
from bosa_core.authentication.plugin.repository.base_repository import BaseRepository as BaseRepository
from bosa_core.authentication.plugin.repository.models import ThirdPartyIntegrationAuth as ThirdPartyIntegrationAuth
from uuid import UUID

class ThirdPartyIntegrationService:
    """Third-party integration service."""
    third_party_integration_repository: Incomplete
    def __init__(self, third_party_integration_repository: BaseRepository) -> None:
        """Initialize the service.

        Args:
            third_party_integration_repository (BaseRepository): The third-party integration repository
        """
    def has_integration(self, client_id: UUID, user_id: UUID, connector: str) -> bool:
        """Returns whether the user has a third-party integration for the specified connector.

        Args:
            client_id (UUID): Client ID.
            user_id (UUID): User ID.
            connector (str): Connector name.

        Returns:
            bool: True if the user has a third-party integration for the specified connector, False otherwise.
        """
    def get_integration(self, client_id: UUID, user_id: UUID, connector: str) -> ThirdPartyIntegrationAuth | None:
        """Returns the third-party integration for the specified connector.

        Args:
            client_id (UUID): Client ID.
            user_id (UUID): User ID.
            connector (str): Connector name.

        Returns:
            ThirdPartyIntegrationAuth: Third-party integration, or None if not found.
        """
    def get_integrations(self, client_id: UUID, user_id: UUID) -> list[ThirdPartyIntegrationAuth]:
        """Returns all the third-party integrations for the specified client and user.

        Args:
            client_id (UUID): Client ID.
            user_id (UUID): User ID.

        Returns:
            list[ThirdPartyIntegrationAuth]: List of third-party integrations.
        """
    def create_integration(self, integration: ThirdPartyIntegrationAuth):
        """Creates a third-party integration.

        Args:
            integration (ThirdPartyIntegrationAuth): Third-party integration.

        Returns:
            ThirdPartyIntegrationAuth: Created third-party integration.
        """
    def delete_integration(self, client_id: UUID, user_id: UUID, connector: str) -> None:
        """Deletes a third-party integration.

        Args:
            client_id (UUID): Client ID.
            user_id (UUID): User ID.
            connector (str): Connector name.
        """
