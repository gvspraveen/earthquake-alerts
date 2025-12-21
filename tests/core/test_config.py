"""Tests for configuration validation.

Tests the pure validation functions in src/core/config.py.
"""

import pytest

from src.core.config import (
    Config,
    MonitoringRegion,
    ValidationError,
    ValidationResult,
    validate_coordinates,
    validate_bounds,
    validate_poi_references,
    validate_config,
)
from src.core.geo import BoundingBox, PointOfInterest
from src.core.rules import AlertChannel, AlertRule


class TestValidateCoordinates:
    """Tests for validate_coordinates()."""

    def test_valid_coordinates_returns_empty_list(self):
        """Valid coordinates return no errors."""
        errors = validate_coordinates(37.7749, -122.4194, "test")
        assert errors == []

    def test_latitude_out_of_range_returns_error(self):
        """Latitude outside [-90, 90] returns error."""
        errors = validate_coordinates(91.0, 0.0, "test")
        assert len(errors) == 1
        assert "Latitude" in errors[0].message
        assert "out of range" in errors[0].message

    def test_negative_latitude_out_of_range_returns_error(self):
        """Negative latitude outside [-90, 90] returns error."""
        errors = validate_coordinates(-91.0, 0.0, "test")
        assert len(errors) == 1
        assert "Latitude" in errors[0].message

    def test_longitude_out_of_range_returns_error(self):
        """Longitude outside [-180, 180] returns error."""
        errors = validate_coordinates(0.0, 181.0, "test")
        assert len(errors) == 1
        assert "Longitude" in errors[0].message

    def test_both_invalid_returns_two_errors(self):
        """Both invalid coordinates return two errors."""
        errors = validate_coordinates(100.0, 200.0, "test")
        assert len(errors) == 2

    def test_boundary_values_are_valid(self):
        """Boundary values (-90, 90, -180, 180) are valid."""
        assert validate_coordinates(90.0, 180.0, "test") == []
        assert validate_coordinates(-90.0, -180.0, "test") == []


class TestValidateBounds:
    """Tests for validate_bounds()."""

    def test_valid_bounds_returns_empty_list(self):
        """Valid bounding box returns no errors."""
        bounds = BoundingBox(36.0, 38.0, -123.0, -121.0)
        errors = validate_bounds(bounds, "test")
        assert errors == []

    def test_min_greater_than_max_latitude_returns_error(self):
        """min_latitude > max_latitude returns error."""
        bounds = BoundingBox(38.0, 36.0, -123.0, -121.0)  # min > max
        errors = validate_bounds(bounds, "test")
        assert any("min_latitude" in e.message for e in errors)

    def test_min_greater_than_max_longitude_returns_error(self):
        """min_longitude > max_longitude returns error."""
        bounds = BoundingBox(36.0, 38.0, -121.0, -123.0)  # min > max
        errors = validate_bounds(bounds, "test")
        assert any("min_longitude" in e.message for e in errors)

    def test_invalid_coordinates_returns_errors(self):
        """Invalid coordinates in bounds return errors."""
        bounds = BoundingBox(-100.0, 100.0, -200.0, 200.0)  # All out of range
        errors = validate_bounds(bounds, "test")
        assert len(errors) >= 4  # At least 4 coordinate errors


class TestValidatePOIReferences:
    """Tests for validate_poi_references()."""

    def test_all_valid_references_returns_empty(self):
        """All valid POI references return no warnings."""
        pois = [
            PointOfInterest("Office", 37.0, -122.0, 50.0),
            PointOfInterest("Home", 37.5, -122.5, 30.0),
        ]
        errors = validate_poi_references({"Office", "Home"}, pois, "test")
        assert errors == []

    def test_unmatched_reference_returns_warning(self):
        """Unmatched POI reference returns warning."""
        pois = [PointOfInterest("Office", 37.0, -122.0, 50.0)]
        errors = validate_poi_references({"Office", "Unknown"}, pois, "test")

        assert len(errors) == 1
        assert errors[0].severity == "warning"
        assert "Unknown" in errors[0].message
        assert "not found" in errors[0].message

    def test_similar_name_suggests_correction(self):
        """Similar name in POIs suggests correction."""
        pois = [PointOfInterest("San Ramon", 37.0, -122.0, 50.0)]
        errors = validate_poi_references({"San Ramone"}, pois, "test")  # Typo

        assert len(errors) == 1
        assert "Did you mean" in errors[0].message
        assert "San Ramon" in errors[0].message

    def test_empty_references_returns_empty(self):
        """Empty references set returns no errors."""
        pois = [PointOfInterest("Office", 37.0, -122.0, 50.0)]
        errors = validate_poi_references(set(), pois, "test")
        assert errors == []


class TestValidateConfig:
    """Tests for validate_config()."""

    def test_empty_config_warns_no_channels(self):
        """Empty config warns about no alert channels."""
        config = Config()
        result = validate_config(config)

        assert result.valid is True  # Warnings don't make it invalid
        assert len(result.warnings) >= 1
        assert any("No alert channels" in w.message for w in result.warnings)

    def test_valid_config_returns_valid(self):
        """Valid configuration returns valid result."""
        config = Config(
            monitoring_regions=[
                MonitoringRegion(
                    name="Test",
                    bounds=BoundingBox(36.0, 38.0, -123.0, -121.0),
                ),
            ],
            alert_channels=[
                AlertChannel(
                    name="test-channel",
                    channel_type="slack",
                    webhook_url="https://hooks.slack.com/test",
                    rules=AlertRule(min_magnitude=3.0),
                ),
            ],
        )
        result = validate_config(config)

        assert result.valid is True
        assert len(result.critical_errors) == 0

    def test_invalid_region_bounds_returns_error(self):
        """Invalid region bounds return errors."""
        config = Config(
            monitoring_regions=[
                MonitoringRegion(
                    name="Invalid",
                    bounds=BoundingBox(100.0, 38.0, -123.0, -121.0),  # lat out of range
                ),
            ],
        )
        result = validate_config(config)

        assert result.valid is False
        assert len(result.critical_errors) >= 1

    def test_invalid_poi_returns_error(self):
        """Invalid POI coordinates return errors."""
        config = Config(
            points_of_interest=[
                PointOfInterest("Bad", 200.0, -122.0, 50.0),  # lat out of range
            ],
        )
        result = validate_config(config)

        assert result.valid is False

    def test_negative_poi_radius_returns_error(self):
        """Negative POI radius returns error."""
        config = Config(
            points_of_interest=[
                PointOfInterest("Bad", 37.0, -122.0, -50.0),  # negative radius
            ],
        )
        result = validate_config(config)

        assert result.valid is False
        assert any("radius" in e.message.lower() for e in result.critical_errors)

    def test_invalid_magnitude_range_returns_error(self):
        """min_magnitude > max_magnitude returns error."""
        config = Config(
            alert_channels=[
                AlertChannel(
                    name="test",
                    channel_type="slack",
                    webhook_url="https://test.com",
                    rules=AlertRule(min_magnitude=5.0, max_magnitude=3.0),
                ),
            ],
        )
        result = validate_config(config)

        assert result.valid is False
        assert any("min_magnitude" in e.message for e in result.critical_errors)

    def test_unresolved_webhook_placeholder_warns(self):
        """Unresolved webhook placeholder returns warning."""
        config = Config(
            alert_channels=[
                AlertChannel(
                    name="test",
                    channel_type="slack",
                    webhook_url="${secret:unresolved}",  # Still a placeholder
                    rules=AlertRule(min_magnitude=3.0),
                ),
            ],
        )
        result = validate_config(config)

        assert result.valid is True  # Warning, not error
        assert any("placeholder" in w.message.lower() for w in result.warnings)


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_warnings_property(self):
        """warnings property returns only warnings."""
        result = ValidationResult(
            valid=True,
            errors=[
                ValidationError("a", "error", "error"),
                ValidationError("b", "warning", "warning"),
                ValidationError("c", "warning", "warning"),
            ],
        )

        assert len(result.warnings) == 2
        assert all(w.severity == "warning" for w in result.warnings)

    def test_critical_errors_property(self):
        """critical_errors property returns only errors."""
        result = ValidationResult(
            valid=False,
            errors=[
                ValidationError("a", "error", "error"),
                ValidationError("b", "warning", "warning"),
            ],
        )

        assert len(result.critical_errors) == 1
        assert result.critical_errors[0].severity == "error"
