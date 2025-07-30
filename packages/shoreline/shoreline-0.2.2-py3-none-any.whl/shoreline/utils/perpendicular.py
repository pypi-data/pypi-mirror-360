import numpy as np
from shapely.geometry import LineString, Point


def cast_perpendicular_rays(
    line1: LineString, window: float = 500, ray_length=1000, right: bool = False
) -> list[Point]:
    """
    Casts rays perpendicular to each line segment at its vertices.
    Rays are cast leftward by default, or rightward if right=True.

    Note: window parameter is included for API compatibility but not used.
    """
    # Convert to numpy array and explicitly get x,y coordinates
    coords = np.array([(p[0], p[1]) for p in line1.coords])
    rays = []

    for i, vertex in enumerate(coords):
        # Skip last point as we need a next point to determine direction
        if i == len(coords) - 1:
            continue

        # Now these are proper numpy arrays that can be subtracted
        segment_vec = coords[i + 1] - coords[i]  # noqa: PLR1736

        # Perpendicular vector, direction based on right parameter
        perp_vec = (
            np.array([segment_vec[1], -segment_vec[0]])
            if right
            else np.array([-segment_vec[1], segment_vec[0]])
        )

        # Normalize to unit vector
        perp_vec = perp_vec / np.linalg.norm(perp_vec)

        ray = LineString([vertex, vertex + perp_vec * ray_length])
        rays.append(ray)

    return rays


# TODO: it's not clear that this is useful / better than cast_perpendicular
def get_westward_intersections(
    line1: LineString, line2: LineString, ray_length=1000
) -> list[Point]:
    """ "
    Will cast rays due westward. Note that grid north / west won't be the same as true north / east due
    to meridional convergence, but it should be accurate enough for our purposes
    """
    coords = np.array(line1.coords)
    west_vector = np.array([-1.0, 0.0])  # UTM west
    intersections = []
    for coord in coords:
        ray = LineString([coord, coord + west_vector * ray_length])
        if ray.intersects(line2):
            intersections.append((ray, ray.intersection(line2)))
    return intersections


def calculate_slopes(gdf):
    """Calculate slope angles in degrees.

    Args:
        gdf: GeoDataFrame with start_depth and end_depth in meters (negative down)
             and length (horizontal distance) in meters

    """
    # For rise: remember negative is down, so end - start gives us the rise
    rise = gdf.end_depth - gdf.start_depth  # Will be positive for upward slopes
    run = gdf.length
    return np.degrees(np.arctan2(rise, run))
