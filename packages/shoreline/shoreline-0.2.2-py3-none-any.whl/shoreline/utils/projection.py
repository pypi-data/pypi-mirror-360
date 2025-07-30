def wgs84_to_utm_epsg(latitude: float, longitude: float) -> str:
    """
    Convert WGS84 coordinates to the appropriate UTM zone EPSG code.

    Args:
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)

    Returns:
        String with EPSG code in the format "EPSG:XXXX"

    """
    # Ensure longitude is in the range [-180, 180]
    longitude = ((longitude + 180) % 360) - 180

    # Calculate the UTM zone number
    zone_number = int((longitude + 180) / 6) + 1

    # Handle special cases for Norway and Svalbard
    if 56 <= latitude < 64 and 3 <= longitude < 12:
        zone_number = 32

    if 72 <= latitude < 84 and longitude >= 0:
        if longitude < 9:
            zone_number = 31
        elif longitude < 21:
            zone_number = 33
        elif longitude < 33:
            zone_number = 35
        elif longitude < 42:
            zone_number = 37

    # Determine if northern or southern hemisphere
    epsg_code = 32600 + zone_number if latitude >= 0 else 32700 + zone_number

    return f"EPSG:{epsg_code}"
