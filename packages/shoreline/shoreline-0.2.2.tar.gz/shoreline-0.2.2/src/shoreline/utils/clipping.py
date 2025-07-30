import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, box


def remove_intersecting_lines(gdf):
    # Create spatial index
    spatial_index = gdf.sindex

    # Keep track of indices to drop and processed pairs
    to_drop = set()
    processed_pairs = set()

    # For each geometry, find potential intersections using spatial index
    for idx, geom in gdf.geometry.items():
        if idx in to_drop:
            continue

        # Query spatial index for potential intersections
        possible_matches = list(spatial_index.query(geom))

        # Remove self from matches
        possible_matches.remove(idx)

        # Check actual intersections
        intersecting = gdf.iloc[possible_matches].geometry.intersects(geom)
        if intersecting.any():
            intersecting_idx = intersecting[intersecting].index

            # avoid removing both lines when an intersection is symmetrical:
            # (X, Y), (Y, X)
            for other_idx in intersecting_idx:
                # Create a sorted pair to avoid processing the same intersection twice
                pair = tuple(sorted([idx, other_idx]))

                if pair not in processed_pairs:
                    processed_pairs.add(pair)
                    # Always remove the higher index to maintain consistency
                    to_drop.add(max(idx, other_idx))

    intersections = gdf.iloc[list(to_drop)]
    return (gdf.drop(index=to_drop), intersections)


def clip_rays_by_polygon(
    rays: gpd.GeoDataFrame,
    polygon: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Use clipping and spatial index to speed up new endpoint calculation
    """
    # Get ray bbox, expand it slightly, and clip polygon
    bounds = rays.total_bounds
    buffer = (bounds[2] - bounds[0]) * 0.01
    bbox = box(*bounds).buffer(buffer)
    clipped = polygon.clip(bbox, keep_geom_type=True)

    # Build spatial index of clipped landmask
    sindex = clipped.sindex

    # Extract origins for distance calcs
    origins = np.array([ray.coords[0] for ray in rays.geometry])

    # Process all rays
    new_endpoints = []
    for idx, ray in enumerate(rays.geometry):
        # Query index and get intersection
        matches = list(sindex.intersection(ray.bounds))
        if not matches:
            # we shot the ray all the way but didn't hit anything: don't keep it!
            continue

        intersection = clipped.iloc[matches[0]].geometry.intersection(ray)
        if not intersection or intersection.is_empty:
            # we shot the ray all the way but didn't hit anything: don't keep it!
            continue

        # Get intersection coordinates

        # The hasattr check is actually necessary in GeoPandas/Shapely due to how intersections work:
        # When a LineString intersects a Polygon, the result can be either:
        # A single geometry (Point or LineString) -> no geoms attribute
        # A MultiGeometry (MultiPoint or MultiLineString) -> has geoms attribute

        # The check ensures we handle both cases correctly by either:
        # Iterating through multiple geometries when we get a Multi* result, OR
        # Directly accessing coordinates when we get a single geometry
        intersection_coords = []
        if hasattr(intersection, "geoms"):
            for geom in intersection.geoms:
                intersection_coords.extend(list(geom.coords))
        else:
            intersection_coords = list(intersection.coords)

        # Find nearest point
        points = np.array(intersection_coords)
        distances = np.sqrt(np.sum((points - origins[idx]) ** 2, axis=1))
        new_endpoints.append(tuple(points[np.argmin(distances)]))

    # Create new linestrings
    new_rays = [LineString([orig, end]) for orig, end in zip(origins, new_endpoints)]
    return gpd.GeoDataFrame(geometry=new_rays, crs=rays.crs)
