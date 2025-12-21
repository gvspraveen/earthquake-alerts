"""Slack Webhook Client - Imperative Shell.

This module handles HTTP communication with Slack webhooks.
All I/O is contained here; message formatting is in the core module.
"""

import logging
from dataclasses import dataclass
from typing import Any

import requests


logger = logging.getLogger(__name__)


# Default timeout for webhook requests (seconds)
DEFAULT_TIMEOUT = 10


@dataclass
class SlackResponse:
    """Response from Slack webhook.

    Attributes:
        success: Whether the message was sent successfully
        status_code: HTTP status code
        error: Error message if failed
    """
    success: bool
    status_code: int
    error: str | None = None


class SlackClient:
    """Client for sending messages to Slack via webhooks.

    This is part of the imperative shell - it handles HTTP I/O.
    """

    def __init__(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Initialize Slack client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    def send_message(
        self,
        webhook_url: str,
        payload: dict[str, Any],
    ) -> SlackResponse:
        """Send a message to Slack via webhook.

        This method performs HTTP I/O.

        Args:
            webhook_url: Slack incoming webhook URL
            payload: Message payload (from formatter)

        Returns:
            SlackResponse indicating success or failure
        """
        logger.info("Sending message to Slack webhook")

        try:
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                logger.info("Message sent successfully to Slack")
                return SlackResponse(
                    success=True,
                    status_code=response.status_code,
                )
            else:
                error_text = response.text
                logger.warning(
                    "Slack webhook returned non-200: %d - %s",
                    response.status_code,
                    error_text,
                )
                return SlackResponse(
                    success=False,
                    status_code=response.status_code,
                    error=error_text,
                )

        except requests.Timeout:
            logger.error("Slack webhook request timed out")
            return SlackResponse(
                success=False,
                status_code=0,
                error="Request timed out",
            )
        except requests.RequestException as e:
            logger.error("Slack webhook request failed: %s", str(e))
            return SlackResponse(
                success=False,
                status_code=0,
                error=str(e),
            )

    def send_messages(
        self,
        webhook_url: str,
        payloads: list[dict[str, Any]],
        rate_limit_ms: int = 1000,
        stop_on_error: bool = False,
    ) -> list[SlackResponse]:
        """Send multiple messages to Slack with rate limiting.

        This is a deep method that handles:
        - Rate limiting between messages (Slack recommends 1 msg/sec)
        - Optional early termination on error
        - Consistent response collection

        Args:
            webhook_url: Slack incoming webhook URL
            payloads: List of message payloads
            rate_limit_ms: Delay between messages in milliseconds (default: 1000)
            stop_on_error: If True, stop sending on first error

        Returns:
            List of responses for each message (may be shorter if stop_on_error)
        """
        import time

        responses = []

        for i, payload in enumerate(payloads):
            # Rate limit: wait before sending (except for first message)
            if i > 0 and rate_limit_ms > 0:
                time.sleep(rate_limit_ms / 1000.0)

            response = self.send_message(webhook_url, payload)
            responses.append(response)

            # Early termination on error if requested
            if stop_on_error and not response.success:
                logger.warning(
                    "Stopping batch send after error on message %d of %d",
                    i + 1, len(payloads),
                )
                break

        return responses
