"""Secret Manager Client - Imperative Shell.

This module handles reading secrets from Google Cloud Secret Manager.
All I/O is contained here; configuration logic is in the core module.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from google.cloud import secretmanager


logger = logging.getLogger(__name__)


@dataclass
class SecretManagerConfig:
    """Configuration for Secret Manager client.

    Attributes:
        project_id: GCP project ID (None for default)
    """
    project_id: Optional[str] = None


class SecretManagerClient:
    """Client for reading secrets from Google Cloud Secret Manager.

    This is part of the imperative shell - it handles secret I/O.
    """

    def __init__(self, config: Optional[SecretManagerConfig] = None) -> None:
        """Initialize Secret Manager client.

        Args:
            config: Secret Manager configuration
        """
        self.config = config or SecretManagerConfig()
        self._client: Optional[secretmanager.SecretManagerServiceClient] = None

    @property
    def client(self) -> secretmanager.SecretManagerServiceClient:
        """Lazy initialization of Secret Manager client."""
        if self._client is None:
            self._client = secretmanager.SecretManagerServiceClient()
        return self._client

    def get_secret(
        self,
        secret_name: str,
        version: str = "latest",
        project_id: Optional[str] = None,
    ) -> Optional[str]:
        """Fetch a secret value from Secret Manager.

        This method performs I/O.

        Args:
            secret_name: Name of the secret (not the full resource path)
            version: Version of the secret (default: "latest")
            project_id: GCP project ID (uses config if not provided)

        Returns:
            Secret value as string, or None if not found
        """
        project = project_id or self.config.project_id

        if not project:
            logger.error("No project ID configured for Secret Manager")
            return None

        # Build the resource name
        name = f"projects/{project}/secrets/{secret_name}/versions/{version}"

        try:
            logger.info("Fetching secret: %s", secret_name)
            response = self.client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode("UTF-8")
            logger.info("Successfully fetched secret: %s", secret_name)
            return secret_value

        except Exception as e:
            logger.error("Failed to fetch secret %s: %s", secret_name, str(e))
            return None

    def get_secret_or_env(
        self,
        secret_name: str,
        env_var_name: str,
        fallback_value: Optional[str] = None,
    ) -> Optional[str]:
        """Try to get secret from Secret Manager, fall back to environment variable.

        This is useful for local development where Secret Manager may not be available.

        Args:
            secret_name: Name of the secret in Secret Manager
            env_var_name: Environment variable name to use as fallback
            fallback_value: Final fallback value if both fail

        Returns:
            Secret value, env var value, or fallback value
        """
        import os

        # Try Secret Manager first
        secret_value = self.get_secret(secret_name)
        if secret_value:
            return secret_value

        # Fall back to environment variable
        env_value = os.environ.get(env_var_name)
        if env_value:
            logger.info("Using environment variable %s (Secret Manager unavailable)", env_var_name)
            return env_value

        # Final fallback
        if fallback_value:
            logger.warning("Using fallback value (Secret Manager and env var unavailable)")
            return fallback_value

        return None

    def resolve(self, value: str) -> str:
        """Resolve a value that may contain secret or env var placeholders.

        This method handles the complexity of parsing placeholder syntax,
        pulling complexity down into this module.

        Supports:
        - ${secret:SECRET_NAME} - fetch from Secret Manager
        - ${VAR_NAME} - fetch from environment variable
        - Plain string - return as-is

        Args:
            value: Value to resolve (may contain placeholders)

        Returns:
            Resolved value. Returns original if resolution fails.
        """
        import os

        if not isinstance(value, str):
            return value

        # Check for placeholder syntax: ${...}
        if not (value.startswith("${") and value.endswith("}")):
            return value

        var_spec = value[2:-1]

        # Check if it's a secret reference: ${secret:NAME}
        if var_spec.startswith("secret:"):
            secret_name = var_spec[7:]  # Remove "secret:" prefix
            secret_value = self.get_secret(secret_name)
            if secret_value:
                return secret_value

            # Fall back to environment variable with sanitized name
            env_name = secret_name.upper().replace("-", "_")
            env_value = os.environ.get(env_name)
            if env_value:
                logger.info(
                    "Secret %s not found, using env var %s",
                    secret_name, env_name,
                )
                return env_value

            logger.warning("Secret/env var %s not found", secret_name)
            return value

        # Regular environment variable: ${VAR_NAME}
        env_value = os.environ.get(var_spec)
        if env_value is None:
            logger.warning("Environment variable %s not set", var_spec)
            return value

        return env_value
