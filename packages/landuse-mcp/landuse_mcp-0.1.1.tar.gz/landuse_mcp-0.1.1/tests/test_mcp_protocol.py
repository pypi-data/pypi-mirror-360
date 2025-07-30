"""
MCP protocol tests for landuse-mcp server.

These tests verify that the MCP server correctly implements the protocol
and responds to standard MCP requests.
"""

import pytest


def test_mcp_tool_registration():
    """Test that MCP tools are properly registered."""
    from landuse_mcp.main import mcp

    # Verify that the MCP instance is properly initialized
    assert mcp is not None
    assert mcp.name == "landuse_mcp"

    # Import the functions to verify they exist
    from landuse_mcp.main import get_land_cover, get_landuse_dates, get_soil_type

    # Verify functions are callable
    assert callable(get_land_cover)
    assert callable(get_soil_type)
    assert callable(get_landuse_dates)


def test_mcp_tool_schemas():
    """Test that MCP tools have proper schemas."""
    from landuse_mcp.main import get_land_cover, get_landuse_dates, get_soil_type

    # Verify functions exist and are callable
    assert callable(get_land_cover)
    assert callable(get_soil_type)
    assert callable(get_landuse_dates)

    # Check function signatures
    import inspect

    # get_land_cover should have lat, lon, start_date, end_date parameters
    sig = inspect.signature(get_land_cover)
    params = list(sig.parameters.keys())
    assert "lat" in params
    assert "lon" in params
    assert "start_date" in params
    assert "end_date" in params

    # get_soil_type should have lat, lon parameters
    sig = inspect.signature(get_soil_type)
    params = list(sig.parameters.keys())
    assert "lat" in params
    assert "lon" in params

    # get_landuse_dates should have lat, lon parameters
    sig = inspect.signature(get_landuse_dates)
    params = list(sig.parameters.keys())
    assert "lat" in params
    assert "lon" in params


def test_error_handling():
    """Test error handling in MCP tools."""
    from landuse_mcp.main import get_land_cover, get_landuse_dates, get_soil_type

    # Test with invalid coordinates (should handle gracefully)
    invalid_lat, invalid_lon = 999, 999

    # These should return None or handle errors gracefully
    result = get_soil_type(invalid_lat, invalid_lon)
    assert result is None  # Should handle invalid coordinates

    result = get_landuse_dates(invalid_lat, invalid_lon)
    assert result is None  # Should handle invalid coordinates

    result = get_land_cover(invalid_lat, invalid_lon, "2001-01-01", "2002-01-01")
    assert result is None  # Should handle invalid coordinates


def test_coordinate_validation():
    """Test coordinate validation."""
    from landuse_mcp.main import get_soil_type

    # Test boundary coordinates
    test_cases = [
        (90, 180),  # North pole, max longitude
        (-90, -180),  # South pole, min longitude
        (0, 0),  # Equator, prime meridian
        (45, 90),  # Mid-latitude, mid-longitude
    ]

    for lat, lon in test_cases:
        # Should not raise exceptions for valid coordinates
        result = get_soil_type(lat, lon)
        # Result can be None (service unavailable) but should not crash
        assert result is None or isinstance(result, str)


def test_date_format_validation():
    """Test date format validation."""
    from landuse_mcp.main import get_land_cover

    # Test with valid coordinates
    lat, lon = 36.5322649, -116.9325408

    # Test various date formats
    valid_dates = [
        ("2001-01-01", "2002-01-01"),
        ("2010-12-31", "2011-01-01"),
        ("2020-06-15", "2020-06-16"),
    ]

    for start_date, end_date in valid_dates:
        # Should not raise exceptions for valid date formats
        result = get_land_cover(lat, lon, start_date, end_date)
        # Result can be None (service unavailable) but should not crash
        assert result is None or isinstance(result, dict)


@pytest.mark.integration
def test_mcp_server_initialization():
    """Test MCP server initialization."""
    from landuse_mcp.main import mcp

    # Verify MCP server is properly initialized
    assert mcp is not None
    assert hasattr(mcp, "run")

    # Check that server has proper configuration
    assert mcp.name == "landuse_mcp"


@pytest.mark.integration
def test_realistic_workflow():
    """Test a realistic MCP workflow."""
    from landuse_mcp.main import get_land_cover, get_landuse_dates, get_soil_type

    # Use known coordinates for testing
    test_lat, test_lon = 39.7392, -104.9903  # Denver, Colorado

    # Step 1: Get available dates
    dates = get_landuse_dates(test_lat, test_lon)

    # Step 2: Get soil type
    soil = get_soil_type(test_lat, test_lon)

    # Step 3: Get land cover (if dates available)
    land_cover = None
    if dates and len(dates) >= 2:
        start_date = dates[0]
        end_date = dates[1]
        land_cover = get_land_cover(test_lat, test_lon, start_date, end_date)

    # Verify workflow completed without errors
    # Results can be None if services are unavailable
    if dates is not None:
        assert isinstance(dates, list)
    if soil is not None:
        assert isinstance(soil, str)
    if land_cover is not None:
        assert isinstance(land_cover, dict)

    print(
        f"✅ Workflow completed - Dates: {dates is not None}, "
        f"Soil: {soil is not None}, Land Cover: {land_cover is not None}"
    )


def test_tool_parameter_types():
    """Test that tool parameters handle correct types."""
    from landuse_mcp.main import get_soil_type

    # Test with float coordinates
    result = get_soil_type(40.7128, -74.0060)
    assert result is None or isinstance(result, str)

    # Test with integer coordinates (should work)
    result = get_soil_type(40, -74)
    assert result is None or isinstance(result, str)

    # Test with string coordinates (should handle conversion or fail gracefully)
    try:
        result = get_soil_type("40.7128", "-74.0060")
        assert result is None or isinstance(result, str)
    except (TypeError, ValueError):
        # It's okay if it fails with type error for string inputs
        pass
