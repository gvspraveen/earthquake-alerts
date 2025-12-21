"""Tests for Slack webhook client.

Uses the `responses` library to mock HTTP requests.
"""

import pytest
import responses
import requests

from src.shell.slack_client import SlackClient, SlackResponse


WEBHOOK_URL = "https://hooks.slack.com/services/T00/B00/XXX"


class TestSlackClientSendMessage:
    """Tests for SlackClient.send_message()."""

    @responses.activate
    def test_successful_send_returns_success(self):
        """Successful send returns SlackResponse with success=True."""
        responses.add(
            responses.POST,
            WEBHOOK_URL,
            body="ok",
            status=200,
        )

        client = SlackClient()
        result = client.send_message(WEBHOOK_URL, {"text": "Hello"})

        assert result.success is True
        assert result.status_code == 200
        assert result.error is None

    @responses.activate
    def test_sends_json_payload(self):
        """Payload is sent as JSON."""
        responses.add(
            responses.POST,
            WEBHOOK_URL,
            body="ok",
            status=200,
        )

        client = SlackClient()
        payload = {"text": "Test message", "blocks": [{"type": "section"}]}
        client.send_message(WEBHOOK_URL, payload)

        request = responses.calls[0].request
        assert request.headers["Content-Type"] == "application/json"
        assert b'"text": "Test message"' in request.body

    @responses.activate
    def test_non_200_returns_failure(self):
        """Non-200 response returns SlackResponse with success=False."""
        responses.add(
            responses.POST,
            WEBHOOK_URL,
            body="invalid_payload",
            status=400,
        )

        client = SlackClient()
        result = client.send_message(WEBHOOK_URL, {"text": "Hello"})

        assert result.success is False
        assert result.status_code == 400
        assert result.error == "invalid_payload"

    @responses.activate
    def test_rate_limited_returns_failure(self):
        """429 rate limit returns failure with error message."""
        responses.add(
            responses.POST,
            WEBHOOK_URL,
            body="rate_limited",
            status=429,
        )

        client = SlackClient()
        result = client.send_message(WEBHOOK_URL, {"text": "Hello"})

        assert result.success is False
        assert result.status_code == 429
        assert "rate_limited" in result.error

    @responses.activate
    def test_timeout_returns_failure(self):
        """Request timeout returns failure with timeout error."""
        responses.add(
            responses.POST,
            WEBHOOK_URL,
            body=requests.Timeout("Connection timed out"),
        )

        client = SlackClient(timeout=1)
        result = client.send_message(WEBHOOK_URL, {"text": "Hello"})

        assert result.success is False
        assert result.status_code == 0
        assert "timed out" in result.error.lower()

    @responses.activate
    def test_connection_error_returns_failure(self):
        """Connection error returns failure."""
        responses.add(
            responses.POST,
            WEBHOOK_URL,
            body=requests.ConnectionError("Failed to connect"),
        )

        client = SlackClient()
        result = client.send_message(WEBHOOK_URL, {"text": "Hello"})

        assert result.success is False
        assert result.status_code == 0
        assert result.error is not None


class TestSlackClientSendMessages:
    """Tests for SlackClient.send_messages() batch method."""

    @responses.activate
    def test_sends_all_messages(self):
        """All messages are sent successfully."""
        # Add response for each message
        for _ in range(3):
            responses.add(
                responses.POST,
                WEBHOOK_URL,
                body="ok",
                status=200,
            )

        client = SlackClient()
        payloads = [
            {"text": "Message 1"},
            {"text": "Message 2"},
            {"text": "Message 3"},
        ]
        results = client.send_messages(WEBHOOK_URL, payloads, rate_limit_ms=0)

        assert len(results) == 3
        assert all(r.success for r in results)
        assert len(responses.calls) == 3

    @responses.activate
    def test_continues_on_error_by_default(self):
        """Continues sending after error when stop_on_error=False."""
        responses.add(responses.POST, WEBHOOK_URL, body="ok", status=200)
        responses.add(responses.POST, WEBHOOK_URL, body="error", status=500)
        responses.add(responses.POST, WEBHOOK_URL, body="ok", status=200)

        client = SlackClient()
        payloads = [{"text": f"Message {i}"} for i in range(3)]
        results = client.send_messages(WEBHOOK_URL, payloads, rate_limit_ms=0)

        assert len(results) == 3
        assert results[0].success is True
        assert results[1].success is False
        assert results[2].success is True

    @responses.activate
    def test_stops_on_error_when_requested(self):
        """Stops sending after error when stop_on_error=True."""
        responses.add(responses.POST, WEBHOOK_URL, body="ok", status=200)
        responses.add(responses.POST, WEBHOOK_URL, body="error", status=500)
        responses.add(responses.POST, WEBHOOK_URL, body="ok", status=200)

        client = SlackClient()
        payloads = [{"text": f"Message {i}"} for i in range(3)]
        results = client.send_messages(
            WEBHOOK_URL, payloads, rate_limit_ms=0, stop_on_error=True
        )

        # Should stop after the error
        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is False
        # Third message should not have been sent
        assert len(responses.calls) == 2

    @responses.activate
    def test_empty_payloads_returns_empty_list(self):
        """Empty payloads list returns empty results."""
        client = SlackClient()
        results = client.send_messages(WEBHOOK_URL, [])

        assert results == []
        assert len(responses.calls) == 0


class TestSlackResponse:
    """Tests for SlackResponse dataclass."""

    def test_success_response(self):
        """Successful response has correct fields."""
        response = SlackResponse(success=True, status_code=200)

        assert response.success is True
        assert response.status_code == 200
        assert response.error is None

    def test_failure_response(self):
        """Failure response includes error message."""
        response = SlackResponse(
            success=False,
            status_code=500,
            error="Internal error",
        )

        assert response.success is False
        assert response.status_code == 500
        assert response.error == "Internal error"
