"""Tests for USGS API client.

Uses the `responses` library to mock HTTP requests.
"""

import pytest
import responses
from datetime import datetime, timezone

from src.shell.usgs_client import USGSClient, USGSQueryParams, USGS_API_BASE
from src.core.geo import BoundingBox


class TestUSGSClientFetchEarthquakes:
    """Tests for USGSClient.fetch_earthquakes()."""

    @responses.activate
    def test_successful_fetch_returns_geojson(self):
        """Successful API call returns parsed GeoJSON."""
        mock_response = {
            "type": "FeatureCollection",
            "metadata": {"count": 2},
            "features": [
                {"id": "eq1", "properties": {"mag": 4.5}},
                {"id": "eq2", "properties": {"mag": 3.2}},
            ],
        }
        responses.add(
            responses.GET,
            USGS_API_BASE,
            json=mock_response,
            status=200,
        )

        client = USGSClient()
        result = client.fetch_earthquakes(USGSQueryParams())

        assert result["type"] == "FeatureCollection"
        assert result["metadata"]["count"] == 2
        assert len(result["features"]) == 2

    @responses.activate
    def test_includes_bounds_in_request(self):
        """Bounding box parameters are included in request."""
        responses.add(
            responses.GET,
            USGS_API_BASE,
            json={"type": "FeatureCollection", "metadata": {"count": 0}, "features": []},
            status=200,
        )

        client = USGSClient()
        bounds = BoundingBox(
            min_latitude=36.0,
            max_latitude=38.0,
            min_longitude=-123.0,
            max_longitude=-121.0,
        )
        client.fetch_earthquakes(USGSQueryParams(bounds=bounds))

        # Check that bounds were included in query params
        request = responses.calls[0].request
        assert "minlatitude=36.0" in request.url
        assert "maxlatitude=38.0" in request.url
        assert "minlongitude=-123.0" in request.url
        assert "maxlongitude=-121.0" in request.url

    @responses.activate
    def test_includes_magnitude_filter(self):
        """Minimum magnitude is included in request."""
        responses.add(
            responses.GET,
            USGS_API_BASE,
            json={"type": "FeatureCollection", "metadata": {"count": 0}, "features": []},
            status=200,
        )

        client = USGSClient()
        client.fetch_earthquakes(USGSQueryParams(min_magnitude=3.5))

        request = responses.calls[0].request
        assert "minmagnitude=3.5" in request.url

    @responses.activate
    def test_server_error_raises_exception(self):
        """500 error from USGS raises exception."""
        responses.add(
            responses.GET,
            USGS_API_BASE,
            json={"error": "Internal Server Error"},
            status=500,
        )

        client = USGSClient()

        with pytest.raises(Exception):
            client.fetch_earthquakes(USGSQueryParams())

    @responses.activate
    def test_timeout_raises_exception(self):
        """Request timeout raises exception."""
        import requests

        responses.add(
            responses.GET,
            USGS_API_BASE,
            body=requests.Timeout("Connection timed out"),
        )

        client = USGSClient(timeout=1)

        with pytest.raises(requests.Timeout):
            client.fetch_earthquakes(USGSQueryParams())

    @responses.activate
    def test_empty_response_returns_empty_features(self):
        """Empty response from USGS returns empty features list."""
        mock_response = {
            "type": "FeatureCollection",
            "metadata": {"count": 0},
            "features": [],
        }
        responses.add(
            responses.GET,
            USGS_API_BASE,
            json=mock_response,
            status=200,
        )

        client = USGSClient()
        result = client.fetch_earthquakes(USGSQueryParams())

        assert result["features"] == []
        assert result["metadata"]["count"] == 0


class TestUSGSClientFetchRecent:
    """Tests for USGSClient.fetch_recent() convenience method."""

    @responses.activate
    def test_calculates_time_window(self):
        """Time window is calculated correctly."""
        responses.add(
            responses.GET,
            USGS_API_BASE,
            json={"type": "FeatureCollection", "metadata": {"count": 0}, "features": []},
            status=200,
        )

        client = USGSClient()
        client.fetch_recent(hours=2)

        request = responses.calls[0].request
        # Should have starttime and endtime params
        assert "starttime=" in request.url
        assert "endtime=" in request.url

    @responses.activate
    def test_passes_bounds_and_magnitude(self):
        """Bounds and magnitude are passed through."""
        responses.add(
            responses.GET,
            USGS_API_BASE,
            json={"type": "FeatureCollection", "metadata": {"count": 0}, "features": []},
            status=200,
        )

        client = USGSClient()
        bounds = BoundingBox(36.0, 38.0, -123.0, -121.0)
        client.fetch_recent(bounds=bounds, min_magnitude=2.5, hours=1)

        request = responses.calls[0].request
        assert "minlatitude=36.0" in request.url
        assert "minmagnitude=2.5" in request.url
