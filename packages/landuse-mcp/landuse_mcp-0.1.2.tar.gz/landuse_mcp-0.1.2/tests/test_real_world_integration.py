"""
Real-world integration tests demonstrating landuse-mcp's geospatial utility.

These tests show how the MCP functions work for actual geospatial use cases,
proving the value for AI agents doing environmental and land use analysis.
"""

import pytest

from landuse_mcp.main import get_land_cover, get_landuse_dates, get_soil_type


@pytest.mark.integration
def test_agricultural_land_analysis():
    """Complete workflow: Agricultural land analysis from multiple data sources."""
    print("\n🌾 AGRICULTURAL LAND ANALYSIS WORKFLOW")

    # Test coordinates for Iowa farmland (known agricultural area)
    iowa_farmland_lat, iowa_farmland_lon = 42.0308, -93.6319

    # Step 1: Get soil type for agricultural suitability
    soil_type = get_soil_type(iowa_farmland_lat, iowa_farmland_lon)
    print(f"🌱 Soil type at Iowa farmland: {soil_type}")

    # Step 2: Get available land use dates
    available_dates = get_landuse_dates(iowa_farmland_lat, iowa_farmland_lon)
    if available_dates:
        print(f"📅 Available dates: {len(available_dates)} time periods")
        print(f"   Date range: {available_dates[0]} to {available_dates[-1]}")

    # Step 3: Get land cover for recent period
    if available_dates and len(available_dates) >= 2:
        start_date = available_dates[-2]  # Second to last date
        end_date = available_dates[-1]  # Most recent date

        land_cover = get_land_cover(
            iowa_farmland_lat, iowa_farmland_lon, start_date, end_date
        )
        if land_cover:
            print(f"🗺️ Land cover data structure keys: {list(land_cover.keys())}")

    # This workflow demonstrates how an AI agent would:
    # 1. Identify soil suitability for agriculture
    # 2. Analyze temporal land use patterns
    # 3. Assess current land cover classifications


@pytest.mark.integration
def test_urban_development_analysis():
    """Urban development analysis for city planning."""
    print("\n🏙️ URBAN DEVELOPMENT ANALYSIS")

    # Test coordinates for San Francisco Bay Area
    sf_lat, sf_lon = 37.7749, -122.4194

    # Step 1: Get soil type for construction suitability
    soil_type = get_soil_type(sf_lat, sf_lon)
    print(f"🏗️ Soil type in San Francisco: {soil_type}")

    # Step 2: Analyze historical land use changes
    dates = get_landuse_dates(sf_lat, sf_lon)
    if dates and len(dates) >= 2:
        # Compare early vs recent periods
        early_period = dates[0]
        recent_period = dates[-1]

        print(f"📊 Comparing {early_period} vs {recent_period}")

        # Get land cover for both periods
        early_cover = get_land_cover(sf_lat, sf_lon, early_period, early_period)
        recent_cover = get_land_cover(sf_lat, sf_lon, recent_period, recent_period)

        if early_cover and recent_cover:
            print("🔄 Urban development analysis completed")
            print(f"   Early period data: {type(early_cover)}")
            print(f"   Recent period data: {type(recent_cover)}")


@pytest.mark.integration
def test_environmental_impact_assessment():
    """Environmental impact assessment for protected areas."""
    print("\n🌿 ENVIRONMENTAL IMPACT ASSESSMENT")

    # Test coordinates for Yellowstone National Park
    yellowstone_lat, yellowstone_lon = 44.4280, -110.5885

    # Step 1: Get baseline soil information
    soil_type = get_soil_type(yellowstone_lat, yellowstone_lon)
    print(f"🌍 Soil type in Yellowstone: {soil_type}")

    # Step 2: Get comprehensive land cover data
    dates = get_landuse_dates(yellowstone_lat, yellowstone_lon)
    if dates:
        print(f"📈 Environmental monitoring period: {len(dates)} time points")

        # Get recent land cover
        if len(dates) >= 2:
            recent_date = dates[-1]
            land_cover = get_land_cover(
                yellowstone_lat, yellowstone_lon, recent_date, recent_date
            )

            if land_cover:
                print("🌲 Current land cover classification available")
                print(f"   Data structure: {type(land_cover)}")

    # This demonstrates environmental monitoring capabilities


@pytest.mark.integration
def test_coastal_zone_management():
    """Coastal zone management and erosion analysis."""
    print("\n🌊 COASTAL ZONE MANAGEMENT")

    # Test coordinates for California coastline
    coastal_lat, coastal_lon = 36.6002, -121.8947  # Monterey Bay area

    # Step 1: Analyze coastal soil types
    soil_type = get_soil_type(coastal_lat, coastal_lon)
    print(f"🏖️ Coastal soil type: {soil_type}")

    # Step 2: Get temporal land use data for erosion analysis
    dates = get_landuse_dates(coastal_lat, coastal_lon)
    if dates:
        print(f"🌊 Coastal monitoring timeline: {len(dates)} observations")

        # Analyze recent coastal changes
        if len(dates) >= 3:
            # Compare three time periods
            early = dates[0]
            mid = dates[len(dates) // 2]
            recent = dates[-1]

            print(f"📊 Analyzing coastal changes: {early} → {mid} → {recent}")

            # Get land cover for recent period
            recent_cover = get_land_cover(coastal_lat, coastal_lon, recent, recent)
            if recent_cover:
                print("🔍 Coastal land cover analysis completed")


@pytest.mark.integration
def test_climate_change_indicators():
    """Climate change impact analysis through land use changes."""
    print("\n🌡️ CLIMATE CHANGE INDICATORS")

    # Test coordinates for Arctic/Northern regions (if available)
    northern_lat, northern_lon = 64.0685, -152.2782  # Fairbanks, Alaska area

    # Step 1: Get soil type in changing climate zones
    soil_type = get_soil_type(northern_lat, northern_lon)
    print(f"❄️ Northern soil type: {soil_type}")

    # Step 2: Analyze long-term land use changes
    dates = get_landuse_dates(northern_lat, northern_lon)
    if dates:
        print(f"📊 Climate monitoring period: {len(dates)} time points")

        # Look for vegetation changes over time
        if len(dates) >= 2:
            earliest = dates[0]
            latest = dates[-1]

            print(f"🌿 Analyzing vegetation changes: {earliest} to {latest}")

            land_cover = get_land_cover(northern_lat, northern_lon, latest, latest)
            if land_cover:
                print("🔬 Climate impact analysis data available")


@pytest.mark.integration
def test_disaster_risk_assessment():
    """Disaster risk assessment for emergency planning."""
    print("\n🚨 DISASTER RISK ASSESSMENT")

    # Test coordinates for wildfire-prone area (California)
    wildfire_lat, wildfire_lon = 38.7223, -122.7581  # Napa Valley area

    # Step 1: Assess soil and terrain suitability
    soil_type = get_soil_type(wildfire_lat, wildfire_lon)
    print(f"🔥 Wildfire zone soil type: {soil_type}")

    # Step 2: Analyze land cover for fire risk
    dates = get_landuse_dates(wildfire_lat, wildfire_lon)
    if dates:
        print(f"📋 Risk assessment timeline: {len(dates)} monitoring points")

        # Get current land cover for risk assessment
        if dates:
            current_date = dates[-1]
            land_cover = get_land_cover(
                wildfire_lat, wildfire_lon, current_date, current_date
            )

            if land_cover:
                print("🛡️ Emergency planning data available")
                print(f"   Risk assessment completed for {current_date}")

    # This demonstrates disaster preparedness applications


@pytest.mark.integration
def test_cross_region_comparative_analysis():
    """Cross-region comparative analysis for policy making."""
    print("\n🌍 CROSS-REGION COMPARATIVE ANALYSIS")

    # Test multiple regions for comparative analysis
    regions = [
        ("Desert", 36.5322649, -116.9325408),  # Death Valley
        ("Forest", 46.8523, -121.7603),  # Mount Rainier
        ("Grassland", 39.8283, -98.5795),  # Kansas
        ("Urban", 40.7128, -74.0060),  # New York City
    ]

    comparative_data = {}

    for region_name, lat, lon in regions:
        print(f"\n📍 Analyzing {region_name} region ({lat}, {lon})")

        # Get soil type for each region
        soil = get_soil_type(lat, lon)

        # Get available dates
        dates = get_landuse_dates(lat, lon)

        # Get recent land cover if available
        land_cover = None
        if dates:
            recent_date = dates[-1]
            land_cover = get_land_cover(lat, lon, recent_date, recent_date)

        comparative_data[region_name] = {
            "soil_type": soil,
            "available_dates": len(dates) if dates else 0,
            "has_land_cover": land_cover is not None,
        }

        print(f"   Soil: {soil}")
        print(f"   Time periods: {len(dates) if dates else 0}")
        print(f"   Land cover data: {'Available' if land_cover else 'Not available'}")

    # Summary analysis
    print("\n📊 COMPARATIVE ANALYSIS SUMMARY")
    for region, data in comparative_data.items():
        print(
            f"   {region}: {data['available_dates']} time periods, "
            f"{'✅' if data['has_land_cover'] else '❌'} land cover"
        )

    # This demonstrates policy-making support capabilities


@pytest.mark.integration
@pytest.mark.slow
def test_comprehensive_geospatial_workflow():
    """Comprehensive geospatial analysis workflow."""
    print("\n🌐 COMPREHENSIVE GEOSPATIAL WORKFLOW")

    # Test coordinate in diverse landscape
    test_lat, test_lon = 39.5501, -105.7821  # Colorado (mountains/plains transition)

    print(f"📍 Analyzing location: {test_lat}, {test_lon}")

    # Step 1: Baseline soil analysis
    soil_type = get_soil_type(test_lat, test_lon)
    print(f"🌱 Soil foundation: {soil_type}")

    # Step 2: Temporal availability assessment
    dates = get_landuse_dates(test_lat, test_lon)
    if dates:
        print(f"📅 Temporal coverage: {len(dates)} time periods")
        print(f"   Range: {dates[0]} to {dates[-1]}")

        # Step 3: Multi-temporal analysis
        if len(dates) >= 3:
            analysis_dates = [dates[0], dates[len(dates) // 2], dates[-1]]
            print(f"🔄 Multi-temporal analysis: {len(analysis_dates)} periods")

            for i, date in enumerate(analysis_dates):
                land_cover = get_land_cover(test_lat, test_lon, date, date)
                status = "✅ Available" if land_cover else "❌ Not available"
                print(f"   Period {i+1} ({date}): {status}")

    print("🎯 Comprehensive geospatial analysis completed")

    # This demonstrates full-stack geospatial intelligence capabilities
