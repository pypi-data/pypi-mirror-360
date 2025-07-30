import gc
import time
import warnings

import matplotlib.pyplot as plt
import numpy as np
import psutil
import rasterio
from matplotlib import colors
from pykrige.ok import OrdinaryKriging
from rasterio.transform import from_origin
from scipy.interpolate import griddata
from scipy.spatial import ConvexHull
from shapely.geometry import Point, Polygon
from sklearn.model_selection import KFold
from tqdm import tqdm

# Suppress warnings from PyKrige
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def optimize_kriging_parameters(
    gdf,
    output_prefix,
    attribute="depth",
    cell_size=10,
    max_points=1000,
    test_area_size=0.2,
):
    """
    Optimize kriging parameters by testing on a smaller subset of the data.

    Parameters
    ----------
    gdf : GeoDataFrame
        GeoDataFrame with point geometries and attribute values
    output_prefix : str
        Prefix for output files
    attribute : str
        Column name containing the values to interpolate
    cell_size : float
        Size of output cells in coordinate units
    max_points : int
        Maximum number of points to use for optimization
    test_area_size : float
        Size of test area as a fraction of the full extent

    Returns
    -------
    dict : Dictionary of recommended parameters

    """
    # Extract a smaller area for testing
    x = np.array([geom.x for geom in gdf.geometry])
    y = np.array([geom.y for geom in gdf.geometry])

    x_min, y_min, x_max, y_max = np.min(x), np.min(y), np.max(x), np.max(y)

    # Define a smaller test area
    x_center = (x_max + x_min) / 2
    y_center = (y_max + y_min) / 2

    x_range = (x_max - x_min) * test_area_size / 2
    y_range = (y_max - y_min) * test_area_size / 2

    # Filter points in test area
    idx = (
        (x >= x_center - x_range)
        & (x <= x_center + x_range)
        & (y >= y_center - y_range)
        & (y <= y_center + y_range)
    )

    test_gdf = gdf.iloc[idx].copy()

    # Further subsample if still too many points
    if len(test_gdf) > max_points:
        test_gdf = test_gdf.sample(max_points, random_state=42)

    print(f"Using {len(test_gdf)} points for parameter optimization")

    # Test different variogram models
    variogram_models = ["spherical", "exponential", "gaussian", "linear"]
    anisotropy_ratios = [1, 3, 5, 10]

    best_score = float("inf")
    best_params = {}

    # Use cross-validation to evaluate models

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    test_coords = np.array([(geom.x, geom.y) for geom in test_gdf.geometry])
    test_values = np.array(test_gdf[attribute])

    results = []

    for vm in variogram_models:
        for ar in anisotropy_ratios:
            scores = []

            for train_idx, test_idx in kf.split(test_coords):
                train_x = test_coords[train_idx, 0]
                train_y = test_coords[train_idx, 1]
                train_z = test_values[train_idx]

                test_x = test_coords[test_idx, 0]
                test_y = test_coords[test_idx, 1]
                test_z = test_values[test_idx]

                try:
                    # Train kriging model
                    ok = OrdinaryKriging(
                        train_x,
                        train_y,
                        train_z,
                        variogram_model=vm,
                        verbose=False,
                        enable_plotting=False,
                        anisotropy_scaling=ar,
                    )

                    # Predict at test locations
                    z_pred, ss_pred = ok.execute("points", test_x, test_y)

                    # Calculate RMSE
                    rmse = np.sqrt(np.mean((z_pred - test_z) ** 2))
                    scores.append(rmse)

                except Exception as e:
                    print(f"Error with {vm}, ratio={ar}: {e!s}")
                    scores.append(float("inf"))

            # Average score across folds
            avg_score = np.mean(scores)
            results.append(
                {"variogram_model": vm, "anisotropy_ratio": ar, "rmse": avg_score}
            )

            print(f"Model: {vm}, Anisotropy: {ar}, RMSE: {avg_score:.3f}")

            if avg_score < best_score:
                best_score = avg_score
                best_params = {
                    "variogram_model": vm,
                    "anisotropy_ratio": ar,
                    "rmse": avg_score,
                }

    # Sort results by RMSE
    results.sort(key=lambda x: x["rmse"])

    print("\nParameter optimization results (sorted by RMSE):")
    for r in results:
        print(
            f"Variogram: {r['variogram_model']}, "
            f"Anisotropy: {r['anisotropy_ratio']}, "
            f"RMSE: {r['rmse']:.3f}"
        )

    print("\nRecommended parameters:")
    print(f"Variogram model: {best_params['variogram_model']}")
    print(f"Anisotropy ratio: {best_params['anisotropy_ratio']}")
    print(f"Estimated RMSE: {best_params['rmse']:.3f}")

    return best_params


def memory_usage():
    """Return memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)


def create_surface(
    gdf,
    output_path,
    attribute="depth",
    resolution=100,
    cell_size=5,
    method="cubic",
    diagnostic=True,
    clip_to_hull=True,
    percentile_clip=(2, 98),
):
    """
    Create a continuous surface from point data and write to GeoTIFF. Uses simple interpolation

    Parameters
    ----------
    gdf : GeoDataFrame
        GeoDataFrame with point geometries and attribute values
    output_path : str
        Path to save the output GeoTIFF
    attribute : str
        Column name containing the values to interpolate
    resolution : int
        Number of cells in x and y direction
    cell_size: int
        cell size for grid dimensions
    method : str
        Interpolation method ('linear', 'cubic', 'nearest')
    diagnostic : bool
        If True, save a diagnostic plot showing the interpolation
    clip_to_hull : bool
        If True, clip the interpolation to the convex hull of input points
    percentile_clip : tuple
        Lower and upper percentiles for clipping outliers

    Returns
    -------
    str : Path to the created raster

    """
    # Validate input data
    if gdf.empty:
        raise ValueError("GeoDataFrame is empty")

    if attribute not in gdf.columns:
        raise ValueError(f"Attribute '{attribute}' not found in GeoDataFrame")

    # Drop rows with NaN in attribute or geometry
    gdf = gdf.dropna(subset=[attribute, "geometry"])

    # Print basic statistics about the data
    if diagnostic:
        print(f"Number of points: {len(gdf)}")
        print(
            f"{attribute} stats: min={gdf[attribute].min()}, max={gdf[attribute].max()}, "
            f"mean={gdf[attribute].mean()}, median={gdf[attribute].median()}"
        )

    # Extract coordinates and values
    x = np.array([geom.x for geom in gdf.geometry])
    y = np.array([geom.y for geom in gdf.geometry])
    z = np.array(gdf[attribute], dtype=np.float64)

    # Handle outliers if needed using percentile clipping
    if percentile_clip:
        low, high = np.percentile(z, percentile_clip)
        z = np.clip(z, low, high)
        if diagnostic:
            print(f"Clipped values to range: {low} to {high}")

    # Define grid bounds based on the actual data points
    x_min, y_min, x_max, y_max = np.min(x), np.min(y), np.max(x), np.max(y)

    # Add a small buffer to avoid edge effects
    buffer_x = (x_max - x_min) * 0.05
    buffer_y = (y_max - y_min) * 0.05
    x_min -= buffer_x
    x_max += buffer_x
    y_min -= buffer_y
    y_max += buffer_y

    # Determine appropriate resolution based on data density
    # For bathymetric data with tracklines, we need higher resolution
    if resolution == "auto":
        # Estimate point density
        area = (x_max - x_min) * (y_max - y_min)
        point_density = len(gdf) / area
        # Adjust resolution based on density
        resolution = int(np.sqrt(len(gdf) / 10))  # Heuristic
        resolution = min(max(resolution, 100), 1000)  # Between 100 and 1000

    # # Calculate cell size - ensure it's square
    # cell_size_x = (x_max - x_min) / resolution
    # cell_size_y = (y_max - y_min) / resolution
    # cell_size = min(cell_size_x, cell_size_y)
    cell_size = 5

    # Recalculate grid dimensions to maintain square cells
    cols = int(np.ceil((x_max - x_min) / cell_size))
    rows = int(np.ceil((y_max - y_min) / cell_size))

    if diagnostic:
        print(f"Grid dimensions: {rows} rows x {cols} columns")
        print(f"Cell size: {cell_size}")

    # Create coordinate grids for interpolation
    x_grid = np.linspace(x_min, x_max, cols)
    y_grid = np.linspace(y_max, y_min, rows)  # Note: top to bottom for raster
    xi_grid, yi_grid = np.meshgrid(x_grid, y_grid)

    # Create a mask for points inside the convex hull
    mask = np.ones((rows, cols), dtype=bool)
    if clip_to_hull and len(gdf) > 3:  # Need at least 3 points for a hull
        try:
            points = np.column_stack([x, y])
            hull = ConvexHull(points)
            hull_polygon = Polygon(
                [(points[i, 0], points[i, 1]) for i in hull.vertices]
            )

            # Create a more efficient hull masking using vectorized operations
            grid_points = np.column_stack([xi_grid.flatten(), yi_grid.flatten()])

            # Use a less computationally intensive approximation
            # Test points in batches to avoid memory issues
            batch_size = 10000
            num_points = grid_points.shape[0]
            mask_flat = np.zeros(num_points, dtype=bool)

            for i in range(0, num_points, batch_size):
                end = min(i + batch_size, num_points)
                batch_points = [Point(p) for p in grid_points[i:end]]
                mask_flat[i:end] = [hull_polygon.contains(p) for p in batch_points]

            mask = mask_flat.reshape(rows, cols)

            if diagnostic:
                print(
                    f"Created convex hull mask: {np.sum(mask)} of {mask.size} cells are inside hull"
                )

        except Exception as e:
            print(f"Warning: Could not create convex hull mask: {e!s}")
            print("Continuing without masking")

    # Interpolate values
    zi_grid = griddata((x, y), z, (xi_grid, yi_grid), method=method)

    # Fill any NaN values with nearest neighbor interpolation
    if np.any(np.isnan(zi_grid)):
        zi_nn = griddata((x, y), z, (xi_grid, yi_grid), method="nearest")
        zi_grid = np.where(np.isnan(zi_grid), zi_nn, zi_grid)

    # Apply mask to set values outside hull to nodata
    if clip_to_hull and "mask" in locals():
        zi_grid = np.where(mask, zi_grid, np.nan)

    # Create diagnostic visualization
    if diagnostic:
        fig, ax = plt.subplots(figsize=(10, 8))

        # For bathymetric data, use a blue colormap
        # Reverse the colormap for depth (darker blue = deeper)
        cmap = plt.cm.Blues_r

        # Create a normalized colormap
        vmin, vmax = np.nanmin(zi_grid), np.nanmax(zi_grid)
        norm = colors.Normalize(vmin=vmin, vmax=vmax)

        # Plot the interpolated surface with proper colormap
        im = ax.imshow(
            zi_grid,
            extent=[x_min, x_max, y_min, y_max],
            origin="upper",
            cmap=cmap,
            norm=norm,
        )

        # Plot a subset of the original points (if too many)
        max_points = 5000
        if len(x) > max_points:
            idx = np.random.choice(len(x), max_points, replace=False)
            scatter_x, scatter_y, scatter_z = x[idx], y[idx], z[idx]
        else:
            scatter_x, scatter_y, scatter_z = x, y, z

        # Plot points with the same colormap
        ax.scatter(
            scatter_x,
            scatter_y,
            c=scatter_z,
            cmap=cmap,
            norm=norm,
            edgecolor="black",
            s=20,
            alpha=0.5,
        )

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, label=f"{attribute} (m)")

        # Set title and labels
        ax.set_title(f"Interpolated {attribute} Surface")
        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")

        # Save diagnostic plot
        diag_path = output_path.replace(".tif", "_diagnostic.png")
        plt.savefig(diag_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Diagnostic image saved to: {diag_path}")

    # Ensure proper data type for raster
    zi_grid = zi_grid.astype(np.float32)

    # Create raster transform (from upper left corner)
    transform = from_origin(x_min, y_max, cell_size, cell_size)

    # Write to raster
    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=rows,
        width=cols,
        count=1,
        dtype=zi_grid.dtype,
        crs=gdf.crs,
        transform=transform,
        nodata=np.nan,
    ) as dst:
        dst.write(zi_grid, 1)

    if diagnostic:
        print(f"GeoTIFF written to: {output_path}")
        print(f"Output shape: {zi_grid.shape}")
        print(f"Output range: {np.nanmin(zi_grid)} to {np.nanmax(zi_grid)}")

    return output_path


def create_robust_surface(
    gdf,
    output_path,
    attribute="depth",
    cell_size=5,
    anisotropy_angle=0,
    anisotropy_ratio=5.0,
    tile_size=400,
    overlap=40,
    diagnostic=True,
    max_points=2000,
    method="cubic",
):
    """
    Create a surface using a robust hybrid approach that combines kriging with
    other interpolation methods when kriging fails.

    Parameters
    ----------
    gdf : GeoDataFrame
        GeoDataFrame with point geometries and attribute values
    output_path : str
        Path to save the output GeoTIFF
    attribute : str
        Column name containing the values to interpolate
    cell_size : float
        Size of output cells in coordinate units
    anisotropy_angle : float
        Angle (in degrees) of anisotropy
    anisotropy_ratio : float
        Ratio of anisotropy (values > 1 indicate stronger anisotropy)
    tile_size : int
        Size of tiles in pixels
    overlap : int
        Overlap between tiles in pixels
    diagnostic : bool
        If True, save a diagnostic plot showing the interpolation
    max_points : int
        Maximum number of points to use for kriging per tile
    method : str
        Fallback interpolation method ('cubic', 'linear', 'nearest')

    Returns
    -------
    str : Path to the created raster

    """
    start_time = time.time()
    initial_memory = memory_usage()

    if diagnostic:
        print(f"Initial memory usage: {initial_memory:.1f} MB")
        print(f"Using robust hybrid approach: kriging + {method} interpolation")

    # Validate input data
    if gdf.empty:
        raise ValueError("GeoDataFrame is empty")

    if attribute not in gdf.columns:
        raise ValueError(f"Attribute '{attribute}' not found in GeoDataFrame")

    # Drop rows with NaN in attribute or geometry
    gdf = gdf.dropna(subset=[attribute, "geometry"])

    # Print basic statistics about the data
    if diagnostic:
        print(f"Number of points: {len(gdf)}")
        print(
            f"{attribute} stats: min={gdf[attribute].min()}, max={gdf[attribute].max()}, "
            f"mean={gdf[attribute].mean()}, median={gdf[attribute].median()}"
        )

    # Extract coordinates and values
    x = np.array([geom.x for geom in gdf.geometry])
    y = np.array([geom.y for geom in gdf.geometry])
    z = np.array(gdf[attribute], dtype=np.float64)

    # Define grid bounds based on the actual data points
    x_min, y_min, x_max, y_max = np.min(x), np.min(y), np.max(x), np.max(y)

    # Calculate total grid dimensions based on cell size
    width = int(np.ceil((x_max - x_min) / cell_size))
    height = int(np.ceil((y_max - y_min) / cell_size))

    if diagnostic:
        print(f"Full grid dimensions: {height} rows x {width} columns")
        print(
            f"Cell size: {cell_size} (approximately {width * height / 1_000_000:.1f} million cells)"
        )

    # Initialize output arrays - use float32 to save memory
    z_grid = np.full((height, width), np.nan, dtype=np.float32)
    method_grid = np.full(
        (height, width), 0, dtype=np.int8
    )  # 0=none, 1=kriging, 2=fallback

    # Calculate number of tiles
    n_tiles_x = int(np.ceil(width / (tile_size - overlap)))
    n_tiles_y = int(np.ceil(height / (tile_size - overlap)))
    total_tiles = n_tiles_x * n_tiles_y

    if diagnostic:
        print(f"Processing {total_tiles} tiles ({n_tiles_x} x {n_tiles_y})")
        print(f"Anisotropy angle: {anisotropy_angle}°, ratio: {anisotropy_ratio}")

    # Process each tile
    with tqdm(total=total_tiles, disable=not diagnostic) as pbar:
        for ty in range(n_tiles_y):
            for tx in range(n_tiles_x):
                tile_start_time = time.time()

                # Calculate tile bounds in pixel coordinates
                # Ensure overlap between tiles
                if tx > 0:
                    px_start = tx * (tile_size - overlap)
                else:
                    px_start = 0

                if ty > 0:
                    py_start = ty * (tile_size - overlap)
                else:
                    py_start = 0

                px_end = min(px_start + tile_size, width)
                py_end = min(py_start + tile_size, height)

                # Calculate tile bounds in world coordinates
                x_start = x_min + px_start * cell_size
                y_start = y_min + py_start * cell_size
                x_end = x_min + px_end * cell_size
                y_end = y_min + py_end * cell_size

                # Add buffer to include points just outside tile
                buffer = cell_size * max(10, overlap)
                x_buffer_start = max(x_min, x_start - buffer)
                y_buffer_start = max(y_min, y_start - buffer)
                x_buffer_end = min(x_max, x_end + buffer)
                y_buffer_end = min(y_max, y_end + buffer)

                if diagnostic:
                    print(
                        f"\nProcessing tile {tx},{ty} at pixel coords {px_start}:{px_end}, {py_start}:{py_end}"
                    )
                    print(
                        f"World coordinates: {x_start:.1f}:{x_end:.1f}, {y_start:.1f}:{y_end:.1f}"
                    )

                # Filter points within buffered tile
                idx = (
                    (x >= x_buffer_start)
                    & (x <= x_buffer_end)
                    & (y >= y_buffer_start)
                    & (y <= y_buffer_end)
                )

                x_tile = x[idx]
                y_tile = y[idx]
                z_tile = z[idx]

                # Skip tile if not enough points
                if len(x_tile) < 5:
                    if diagnostic:
                        print(
                            f"Skipping tile {tx},{ty} - not enough points ({len(x_tile)})"
                        )
                    pbar.update(1)
                    continue

                if diagnostic:
                    print(f"Tile {tx},{ty} has {len(x_tile)} points")

                # Sample points if too many
                if len(x_tile) > max_points:
                    if diagnostic:
                        print(f"Sampling {max_points} of {len(x_tile)} points")
                    sidx = np.random.choice(len(x_tile), max_points, replace=False)
                    x_tile = x_tile[sidx]
                    y_tile = y_tile[sidx]
                    z_tile = z_tile[sidx]

                # Create tile grid coordinates
                grid_x = np.linspace(x_start, x_end, px_end - px_start)
                grid_y = np.linspace(y_start, y_end, py_end - py_start)

                # Create coordinate meshgrid
                xi_grid, yi_grid = np.meshgrid(grid_x, grid_y)

                # First try kriging
                kriging_success = False
                try:
                    if diagnostic:
                        print(f"Attempting kriging for tile {tx},{ty}...")

                    # Initialize kriging object with simplified parameters
                    krig = OrdinaryKriging(
                        x_tile,
                        y_tile,
                        z_tile,
                        variogram_model="spherical",
                        verbose=False,
                        enable_plotting=False,
                        anisotropy_angle=anisotropy_angle,
                        anisotropy_scaling=anisotropy_ratio,
                        nlags=10,
                        weight=False,
                    )

                    # Override the variogram parameters with sensible defaults
                    range_val = (
                        np.sqrt((x_max - x_min) ** 2 + (y_max - y_min) ** 2) / 10
                    )
                    sill = np.var(z_tile)
                    nugget = sill * 0.1  # 10% of sill
                    krig.variogram_model_parameters = [nugget, sill - nugget, range_val]

                    # Execute kriging
                    if diagnostic:
                        print("Executing kriging...")

                    z_krig, _ = krig.execute("grid", grid_x, grid_y)

                    # Check if kriging was successful
                    if not np.all(np.isnan(z_krig)):
                        kriging_success = True

                        # Insert kriging result into full grid
                        for i in range(py_end - py_start):
                            for j in range(px_end - px_start):
                                if not np.isnan(z_krig[i, j]):
                                    z_grid[py_start + i, px_start + j] = z_krig[i, j]
                                    method_grid[py_start + i, px_start + j] = (
                                        1  # 1 = kriging
                                    )

                except Exception as e:
                    print(f"Kriging failed for tile {tx},{ty}: {e!s}")
                    kriging_success = False

                finally:
                    # Clean up kriging resources
                    if "krig" in locals():
                        del krig
                    if "z_krig" in locals():
                        del z_krig
                    gc.collect()

                # If kriging failed, use fallback interpolation
                if not kriging_success:
                    if diagnostic:
                        print(
                            f"Using {method} interpolation as fallback for tile {tx},{ty}"
                        )

                    # Use scipy's griddata for interpolation
                    z_interp = griddata(
                        (x_tile, y_tile), z_tile, (xi_grid, yi_grid), method=method
                    )

                    # Fill any NaN values with nearest
                    if np.any(np.isnan(z_interp)):
                        z_nearest = griddata(
                            (x_tile, y_tile),
                            z_tile,
                            (xi_grid, yi_grid),
                            method="nearest",
                        )
                        z_interp = np.where(np.isnan(z_interp), z_nearest, z_interp)

                    # Insert interpolation result into full grid
                    for i in range(py_end - py_start):
                        for j in range(px_end - px_start):
                            if (
                                np.isnan(z_grid[py_start + i, px_start + j])
                                or method_grid[py_start + i, px_start + j] == 0
                            ):
                                z_grid[py_start + i, px_start + j] = z_interp[i, j]
                                method_grid[py_start + i, px_start + j] = (
                                    2  # 2 = fallback
                                )

                    # Clean up
                    del z_interp
                    if "z_nearest" in locals():
                        del z_nearest
                    gc.collect()

                # Update progress
                pbar.update(1)

                # Report tile completion
                tile_time = time.time() - tile_start_time
                if diagnostic:
                    print(
                        f"Tile {tx},{ty} finished in {tile_time:.1f} seconds "
                        f"({'kriging' if kriging_success else f'{method} interpolation'})"
                    )

                    # Report progress percentage
                    tiles_done = ty * n_tiles_x + tx + 1
                    percent_done = tiles_done / total_tiles * 100
                    print(
                        f"Progress: {percent_done:.1f}% ({tiles_done}/{total_tiles} tiles)"
                    )

    # Flip the grid to match GeoTIFF convention (origin at top-left)
    z_grid = np.flipud(z_grid)
    method_grid = np.flipud(method_grid)

    # Calculate statistics on the methods used
    kriging_cells = np.sum(method_grid == 1)
    fallback_cells = np.sum(method_grid == 2)
    total_cells = width * height
    if diagnostic:
        print("\nInterpolation method statistics:")
        print(
            f"Kriging: {kriging_cells} cells ({kriging_cells / total_cells * 100:.1f}%)"
        )
        print(
            f"Fallback {method}: {fallback_cells} cells ({fallback_cells / total_cells * 100:.1f}%)"
        )
        print(
            f"Empty: {total_cells - kriging_cells - fallback_cells} cells ({(total_cells - kriging_cells - fallback_cells) / total_cells * 100:.1f}%)"
        )

    # Create diagnostic visualization if requested
    if diagnostic:
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))

        # For bathymetric data, use a blue colormap
        # Reverse the colormap for depth (darker blue = deeper)
        cmap = plt.cm.Blues_r

        # Create a normalized colormap for the surface
        vmin, vmax = np.nanmin(z_grid), np.nanmax(z_grid)
        norm = colors.Normalize(vmin=vmin, vmax=vmax)

        # Plot the interpolated surface
        im0 = axes[0].imshow(
            z_grid,
            extent=[x_min, x_max, y_min, y_max],
            origin="upper",
            cmap=cmap,
            norm=norm,
        )

        # Plot a subset of the original points
        max_plot_points = 2000
        if len(x) > max_plot_points:
            idx = np.random.choice(len(x), max_plot_points, replace=False)
            plot_x, plot_y, plot_z = x[idx], y[idx], z[idx]
        else:
            plot_x, plot_y, plot_z = x, y, z

        axes[0].scatter(
            plot_x,
            plot_y,
            c=plot_z,
            cmap=cmap,
            norm=norm,
            edgecolor="black",
            s=5,
            alpha=0.5,
        )

        # Add colorbar
        cbar0 = plt.colorbar(im0, ax=axes[0], label=f"{attribute} (m)")

        # Set title and labels
        axes[0].set_title(f"Hybrid Interpolated {attribute} Surface")
        axes[0].set_xlabel("X Coordinate")
        axes[0].set_ylabel("Y Coordinate")

        # Plot the method map
        cmap_method = colors.ListedColormap(["white", "green", "yellow"])
        bounds = [-0.5, 0.5, 1.5, 2.5]
        norm_method = colors.BoundaryNorm(bounds, cmap_method.N)

        im1 = axes[1].imshow(
            method_grid,
            extent=[x_min, x_max, y_min, y_max],
            origin="upper",
            cmap=cmap_method,
            norm=norm_method,
        )

        # Add colorbar
        cbar1 = plt.colorbar(im1, ax=axes[1], ticks=[0, 1, 2])
        cbar1.set_ticklabels(["None", "Kriging", f"{method.capitalize()}"])

        # Set title and labels
        axes[1].set_title("Interpolation Method Used")
        axes[1].set_xlabel("X Coordinate")
        axes[1].set_ylabel("Y Coordinate")

        # Adjust layout
        plt.tight_layout()

        # Save diagnostic plot
        diag_path = output_path.replace(".tif", "_diagnostic.png")
        plt.savefig(diag_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Diagnostic image saved to: {diag_path}")

    # Create raster transform (from upper left corner)
    transform = from_origin(x_min, y_max, cell_size, cell_size)

    # Write surface to raster
    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=np.float32,
        crs=gdf.crs,
        transform=transform,
        nodata=np.nan,
    ) as dst:
        dst.write(z_grid.astype(np.float32), 1)

    # Write method grid to raster for reference
    method_path = output_path.replace(".tif", "_method.tif")
    with rasterio.open(
        method_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=np.int8,
        crs=gdf.crs,
        transform=transform,
        nodata=0,
    ) as dst:
        dst.write(method_grid, 1)

    # Final memory report
    if diagnostic:
        final_memory = memory_usage()
        print(
            f"Final memory usage: {final_memory:.1f} MB "
            f"(change: {final_memory - initial_memory:.1f} MB)"
        )
        print(f"GeoTIFF written to: {output_path}")
        print(f"Method map written to: {method_path}")
        print(f"Total processing time: {time.time() - start_time:.1f} seconds")

    return output_path
