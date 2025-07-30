################################################################################
# landuse_mcp/main.py
# This module provides a FastMCP wrapper for geolocation tools
# Updated to use nmdc-geoloc-tools instead of rasterio for land use data
################################################################################
from fastmcp import FastMCP
from nmdc_geoloc_tools import fao_soil_type, landuse, landuse_dates


def get_land_cover(
    lat: float, lon: float, start_date: str = "2001-01-01", end_date: str = "2002-01-01"
) -> dict | None:
    """
    Get land use data for a given latitude and longitude using nmdc-geoloc-tools.

    Args:
        lat: latitude of the point (-90 to 90)
        lon: longitude of the point (-180 to 180)
        start_date: start date in YYYY-MM-DD format
        end_date: end date in YYYY-MM-DD format

    Returns:
        dict: Land use data with classification systems and ENVO terms
        or None if things go wrong
    """
    try:
        data = landuse((lat, lon), start_date, end_date)
        return data
    except Exception as e:
        print(f"Error processing point ({lat}, {lon}): {e}")
        return None


def get_soil_type(lat: float, lon: float) -> str | None:
    """
    Get FAO soil type for a given latitude and longitude.

    Args:
        lat: latitude of the point (-90 to 90)
        lon: longitude of the point (-180 to 180)

    Returns:
        str: FAO soil classification (e.g., "Cambisols", "Water")
        or None if things go wrong
    """
    try:
        soil = fao_soil_type((lat, lon))
        return soil
    except Exception as e:
        print(f"Error getting soil type for point ({lat}, {lon}): {e}")
        return None


def get_landuse_dates(lat: float, lon: float) -> list[str] | None:
    """
    Get available dates for land use data at a given latitude and longitude.

    Args:
        lat: latitude of the point (-90 to 90)
        lon: longitude of the point (-180 to 180)

    Returns:
        list: Available dates in YYYY-MM-DD format
        or None if things go wrong
    """
    try:
        dates = landuse_dates((lat, lon))
        return dates
    except Exception as e:
        print(f"Error getting landuse dates for point ({lat}, {lon}): {e}")
        return None


# MAIN SECTION
# Create the FastMCP instance
mcp: FastMCP = FastMCP("landuse_mcp")

# Register all tools
mcp.tool(get_land_cover)
mcp.tool(get_soil_type)
mcp.tool(get_landuse_dates)


def main():
    """Main entry point for the application."""
    mcp.run()


if __name__ == "__main__":
    main()
