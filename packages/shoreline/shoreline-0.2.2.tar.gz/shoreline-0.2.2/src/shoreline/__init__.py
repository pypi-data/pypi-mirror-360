"""
NATURESCAPES shoreline analysis package.
"""

import datetime
import os

import geopandas as gpd
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib_scalebar.scalebar import ScaleBar
from shapely import make_valid, reverse
from shapely.geometry import LinearRing, LineString, MultiLineString, Point, Polygon
from shapely.ops import linemerge

from .errors import CrsError, InputError, ShoalBreakError, SlopeError
from .utils.clipping import clip_rays_by_polygon, remove_intersecting_lines
from .utils.perpendicular import calculate_slopes
from .utils.resolution import redistribute_vertices
from .utils.shoal_break import line_of_breaking, line_of_shoaling
from .utils.smoother import (
    cast_snell_rays,
    determine_ray_direction,
)


class ShorelineAnalyzer:
    """
    Shoreline steepness analysis

    Args:
        crs: like "EPSG:25829". CRS must be projected
        shoreline: LineString representing the line of highest astronomical tide (HAT), or its best approximation
        tideline: LineString representing the line of lowest astronomical tide (LAT), or its best approximation
        hat: height of the highest astronomical tide. Should be given as a positive value above mean sea level
        lat: depth of the lowest astronomical tide. Should be given as a positive value below mean sea level
        wave_period: the duration between two waves, in seconds
        wave_height: the height of the wave
        ray_resolution: this will cast a ray from sea to shore every [resolution] meters. 50 by default
        ray_length: distance in meters to ensure that rays intersect the shoreline. 10000 by default
        smoothing_window: window to use for smoothing the ray angle. Values between 250 and 500 will
        suffice for most applications. 250 by default

    Notes:
        The CRS of your input geometries does NOT have to be a projected CRS (i.e. GeoJSON is fine)
        and they do NOT need to match: Input geometries will be re-projected to your specified input CRS

    """

    def __init__(
        self,
        crs,
        shoreline,
        tideline,
        hat,
        lat,
        wave_period,
        wave_height,
        ray_resolution=50.0,
        ray_length=10000,
        smoothing_window=250.0,  # no longer needed, keeping for compat
        origin_angle=0.0,
        origin_distance=1000,
    ):
        """
        Initialize the ShorelineAnalyzer.
        """
        if crs in ["EPSG:3857", "EPSG:4326"]:
            err = "You must use a projected CRS. We're not good at spherical trig"
            raise CrsError(err)
        self.crs = crs
        self.ray_resolution = ray_resolution

        self.shoreline = gpd.read_file(shoreline)
        self.hat_crs = self.shoreline.crs
        self.shoreline.to_crs(crs, inplace=True)

        # populated by _build_lat
        self.lat_crs = None
        # it's set by a call from _built_lat
        self.direction = None
        self.tideline = self._build_lat(tideline)
        self.tideline = redistribute_vertices(self.tideline, self.ray_resolution)

        if hat <= lat:
            err = f"HAT ({hat}) cannot be equal to or lower than LAT ({lat}). The implications for what a shoreline is would be huge"
            raise SlopeError(err)
        if hat <= 0:
            err = "HAT must be a positive value, usually given above MSL"
            raise InputError(err)
        self.hat = hat
        if lat >= 0:
            err = "LAT must be a negative value, usually given below MSL"
            raise InputError(err)
        self.lat = lat
        if wave_period <= 0.0:
            err = f"The wave period must be a positive value in this physical universe. {wave_period} is not"
            raise InputError(err)
        self.wave_period = wave_period
        if wave_height <= 0.0:
            err = "While waves certainly have a subsurface component, we require the height above the sea surface. That is a positive value"
            raise InputError(err)
        self.wave_height = wave_height

        if ray_length <= 0.0:
            err = "Ray length must be positive, in meters"
            raise InputError(err)
        self.ray_length = ray_length
        if smoothing_window <= 0.0:
            err = "The smoothing window should be positive. Try 250.0, unless you're sure you know what you're doing"
            raise InputError(err)
        self.smoothing_window = smoothing_window
        self.origin_angle = origin_angle
        self.origin_distance = origin_distance
        self.log = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc)
            .replace(microsecond=0)
            .isoformat()
        }

        # intermediate products
        self.rays = None
        self.trimmed = None
        self.shoal_line = None
        self.break_line = None
        self.intertidal = None

    def _build_lat(self, isobath):
        geoms = gpd.read_file(isobath)
        self.lat_crs = geoms.crs
        geoms.to_crs(self.crs, inplace=True)
        # Ugh side-effect! But we decompose the gdf so we have to do it here
        self.direction = determine_ray_direction(geoms, self.shoreline)
        isobath = geoms.geometry.union_all()
        if isinstance(isobath, MultiLineString):
            isobath = linemerge(isobath)
        return isobath

    def _cast_rays(self):
        # If direction is "right", rays should go right to left (right=False)
        # If direction is "left", rays should go left to right (right=True)
        if self.direction == "right":
            right = False
        else:
            right = True
        all_rays = cast_snell_rays(
            self.tideline,
            ray_length=self.ray_length,
            origin_distance=self.origin_distance,
            origin_angle=self.origin_angle,
            right=right,
        )
        rays = all_rays[0]
        origins = all_rays[1]
        self.rays = gpd.GeoDataFrame(geometry=[ray for ray in rays], crs=self.crs)
        self.origin_rays = gpd.GeoDataFrame(
            geometry=[ray for ray in origins], crs=self.crs
        )

    def _trim(self):
        self.trimmed = clip_rays_by_polygon(self.rays, self.shoreline)
        self.trimmed["length"] = self.trimmed.geometry.length

    def _remove_intersections(self):
        self.intersections = []
        res = remove_intersecting_lines(self.trimmed)
        self.trimmed = res[0]
        self.intersections = res[1]

    def _assign_depths(self):
        self.trimmed["start_depth"] = self.lat
        self.trimmed["end_depth"] = self.hat

    def _assign_slopes(self):
        self.trimmed["slope"] = (
            self.trimmed["end_depth"] - self.trimmed["start_depth"]
        ) / self.trimmed["length"]
        self.trimmed["slope_degrees"] = calculate_slopes(self.trimmed)
        self.trimmed["slope_radians"] = np.deg2rad(self.trimmed["slope_degrees"])
        self.trimmed["slope_degrees_normalised"] = (
            self.trimmed["slope_degrees"] - np.min(self.trimmed["slope_degrees"])
        ) / np.ptp(self.trimmed["slope_degrees"])

    def _shoaling(self):
        self.shoal_line = line_of_shoaling(self.wave_period, self.trimmed, start=False)

    def _breaking(self):
        self.break_line = line_of_breaking(self.wave_height, self.trimmed)

    def _calculate_point_distances(self):
        """
        Calculate distances from each point in self.trimmed to equivalent points
        on breaking and shoaling lines, and the width between them.
        Also calculate normalized values and geometric mean.
        """
        # Extract coordinates from the shoaling and breaking LineStrings
        shoal_coords = list(self.shoal_line.geometry.iloc[0].coords)
        break_coords = list(self.break_line.geometry.iloc[0].coords)

        # Create GeoDataFrames with Point geometries for vectorized operations
        shoal_points = gpd.GeoDataFrame(
            geometry=[Point(coord) for coord in shoal_coords],
            crs=self.crs,
            index=self.trimmed.index,
        )

        break_points = gpd.GeoDataFrame(
            geometry=[Point(coord) for coord in break_coords],
            crs=self.crs,
            index=self.trimmed.index,
        )

        # Get endpoints of trimmed rays (at HAT) as a GeoSeries
        trimmed_endpoints = self.trimmed.geometry.apply(
            lambda geom: Point(geom.coords[-1])
        )

        # Calculate distances using vectorized operations
        self.trimmed["distance_to_breaking"] = trimmed_endpoints.distance(
            break_points.geometry
        )
        self.trimmed["distance_to_shoaling"] = trimmed_endpoints.distance(
            shoal_points.geometry
        )
        self.trimmed["shoal_break_width"] = shoal_points.geometry.distance(
            break_points.geometry
        )

        # Calculate normalized values (0-1 range using min-max normalization)
        # Invert the normalization - smaller distances = higher scores for impact intensity
        self.trimmed["distance_to_breaking_normalised"] = 1 - (
            (
                self.trimmed["distance_to_breaking"]
                - self.trimmed["distance_to_breaking"].min()
            )
            / (
                self.trimmed["distance_to_breaking"].max()
                - self.trimmed["distance_to_breaking"].min()
            )
        )

        self.trimmed["distance_to_shoaling_normalised"] = 1 - (
            (
                self.trimmed["distance_to_shoaling"]
                - self.trimmed["distance_to_shoaling"].min()
            )
            / (
                self.trimmed["distance_to_shoaling"].max()
                - self.trimmed["distance_to_shoaling"].min()
            )
        )

        self.trimmed["shoal_break_width_normalised"] = 1 - (
            (
                self.trimmed["shoal_break_width"]
                - self.trimmed["shoal_break_width"].min()
            )
            / (
                self.trimmed["shoal_break_width"].max()
                - self.trimmed["shoal_break_width"].min()
            )
        )

        # Calculate geometric mean of the four normalized columns
        # Geometric mean = (a * b * c * d)^(1/4)
        self.trimmed["geom_mean_normalised"] = np.power(
            self.trimmed["distance_to_breaking_normalised"]
            * self.trimmed["distance_to_shoaling_normalised"]
            * self.trimmed["shoal_break_width_normalised"]
            * self.trimmed["slope_degrees_normalised"],
            0.25,
        )

    def _build_score_line(self):
        """
        Build a LineString where each vertex corresponds to a trimmed ray endpoint
        with the geometric mean score as a property.
        """
        # Extract endpoints of trimmed rays
        points = []
        for _, row in self.trimmed.iterrows():
            # Get the endpoint (at HAT)
            endpoint = row.geometry.coords[-1]
            points.append(endpoint)

        # Create LineString from the points
        score_line = LineString(points)

        # Create GeoDataFrame with the score property
        self.score_line = gpd.GeoDataFrame(
            geometry=[score_line],
            crs=self.crs,
            data={"score": [self.trimmed["geom_mean_normalised"].values]},
        )

    def _build_intertidal(self):
        try:
            end = LineString(
                [
                    self.break_line.geometry.iloc[0].coords[-1],
                    self.shoal_line.geometry.iloc[0].coords[-1],
                ]
            )
        except IndexError:
            raise ShoalBreakError(
                "Couldn't get the end points for break or shoal lines!"
            )
        try:
            start = LineString(
                [
                    self.shoal_line.geometry.iloc[0].coords[0],
                    self.break_line.geometry.iloc[0].coords[0],
                ]
            )
        except IndexError:
            raise ShoalBreakError(
                "Couldn't get the start points for shoal or break lines"
            )

        lr = Polygon(
            LinearRing(
                (
                    *start.coords,
                    *self.shoal_line.geometry.iloc[0].coords,
                    *end.coords,
                    *reverse(self.break_line.geometry.iloc[0]).coords,
                )
            )
        )
        # fix it up if necessary
        lr = make_valid(lr)
        self.intertidal = gpd.GeoDataFrame(geometry=[lr], crs=self.crs)

    def evaluate(self):
        """
        Perform the shoreline slope analysis, returning an analysis result object

        The object contains:
        metadata
        lat line
        hat line
        calculated rays containing length and slope data
        shoal line
        break line
        intertidal zone

        """
        self._cast_rays()
        self._trim()
        self._remove_intersections()
        self._assign_depths()
        self._assign_slopes()
        self._shoaling()
        self._breaking()
        self._calculate_point_distances()
        self._build_score_line()
        self._build_intertidal()
        result = AnalysisResult(
            self.crs,
            self.lat_crs,
            self.hat_crs,
            self.lat,
            self.hat,
            self.wave_period,
            self.wave_height,
            self.ray_resolution,
            gpd.GeoDataFrame(geometry=[self.tideline], crs=self.crs),
            self.shoreline,
            self.trimmed,
            self.intersections,
            self.shoal_line,
            self.break_line,
            self.intertidal,
            self.smoothing_window,
            self.origin_rays,
            self.score_line,
        )
        return result


class AnalysisResult:
    """Result of a ShorelineAnalyzer evaluation"""

    def __init__(
        self,
        crs,
        lat_crs,
        hat_crs,
        lat,
        hat,
        period,
        height,
        res,
        lat_line,
        shore_line,
        slopes,
        intersections,
        shoaling,
        breaking,
        intertidal,
        window,
        origins,
        score,
    ):
        super().__init__()
        self.intersections = intersections
        self.metadata = dict()
        self.metadata["timestamp"] = (
            datetime.datetime.now(datetime.timezone.utc)
            .replace(microsecond=0)
            .isoformat()
        )
        self.metadata["analysis_crs"] = crs
        self.metadata["lat"] = lat
        self.metadata["lat_crs"] = lat_crs
        self.metadata["hat"] = hat
        self.metadata["hat_crs"] = hat_crs
        self.metadata["wave_period"] = period
        self.metadata["wave_height"] = height
        self.metadata["ray_resolution"] = res
        self.metadata["smoothing_window"] = window
        self.lat_line = lat_line
        self.shore_line = shore_line
        self.origin_rays = origins
        self.slopes = slopes
        self.shoaling = shoaling
        self.breaking = breaking
        self.intertidal = intertidal
        self.score = score
        self.pcbreaks = [10, 25, 50, 75, 90, 95]
        self.metric_description = [
            "Mean Slope",
            "Median Slope",
            "Std Deviation",
            "Mean Angle (°)",
            "Median Angle (°)",
            "Basic Intertidal Gradient",
            "Basic Intertidal Angle (°)",
            "Weighted Intertidal Gradient",
            "Weighted Intertidal Angle (°)",
            "Mean Segment Gradient",
            "Mean Segment Angle (°)",
            "Area Weighted Gradient",
            "Area Weighted Angle (°)",
            "Slope Variation Coefficient",
        ]
        self.metrics = self._intertidal_gradient_metrics()
        self.friendly_metrics = self._build_metrics_dict()

    def _intertidal_gradient_metrics(self):
        """
        Calculate various intertidal gradient metrics from pre-calculated ray data.

        Parameters
        ----------
        self.slopes : GeoDataFrame
            A GeoDataFrame containing ray information with the following columns:
            - geometry: LineString geometry of each ray
            - length: 2D length of the ray
            - start_depth: depth at the offshore end (LAT)
            - end_depth: depth at the onshore end (HAT)
            - slope: raw slope value
            - slope_degrees: slope in degrees
            - slope_radians: slope in radians

        Returns
        -------
        dict
            Dictionary containing various slope metrics

        References
        ----------
        - Short, A. D., & Wright, L. D. (1983). Physical variability of sandy beaches.
          In Sandy beaches as ecosystems (pp. 133-144). Springer, Dordrecht.
        - Masselink, G., & Short, A. D. (1993). The effect of tide range on beach
          morphodynamics and morphology: a conceptual beach model. Journal of
          Coastal Research, 9(3), 785-800.
        - Masselink, G., & Hegge, B. (1995). Morphodynamics of meso-and macrotidal
          beaches: examples from central Queensland, Australia. Marine Geology, 129(1-2), 1-23.
        - Plant, N. G., Holland, K. T., & Puleo, J. A. (2002). Analysis of the scale of
          errors in nearshore bathymetric data. Marine Geology, 191(1-2), 71-86.
        - Hegge, B., Eliot, I., & Hsu, J. (1996). Sheltered sandy beaches of southwestern
          Australia. Journal of Coastal Research, 12(3), 748-760.

        """
        # Extract relevant data from the GeoDataFrame
        slopes = self.slopes["slope"].values
        slope_angles = self.slopes["slope_degrees"].values
        distances = self.slopes["length"].values

        # Calculate ray lengths in 3D space (using Pythagorean theorem with vertical distance)
        # Note: This assumes start_depth and end_depth are in the same units as length
        vertical_distances = np.abs(
            self.slopes["end_depth"].values - self.slopes["start_depth"].values
        )
        ray_lengths = np.sqrt(distances**2 + vertical_distances**2)

        # Use a common vertical distance for overall metrics
        vert_dist = np.abs(self.metadata["hat"] - self.metadata["lat"])

        # Calculate intertidal gradient metrics

        # 1. Basic intertidal gradient (Short & Wright, 1983 approach)
        basic_intertidal_gradient = vert_dist / np.mean(distances)
        basic_intertidal_angle = np.degrees(np.arctan(basic_intertidal_gradient))

        # 2. Weighted intertidal gradient (Plant et al., 2002 inspired approach)
        # Weight by ray length to give more importance to longer transects
        weighted_intertidal_gradient = vert_dist / np.average(
            distances, weights=ray_lengths
        )
        weighted_intertidal_angle = np.degrees(np.arctan(weighted_intertidal_gradient))

        # 3. Segment-based calculations (Masselink & Hegge, 1995 inspired)
        # In Masselink & Hegge (1995), segment gradients consider local morphology
        # Since we already have pre-calculated slopes, we'll differentiate this by
        # using a distance-normalized calculation that gives more weight to steeper
        # short segments (which is more aligned with their approach)

        # The original differentiation in the literature typically comes from:

        # Mean slope: A simple statistical measure not accounting for spatial relationships
        # Segment gradient: Accounts for how local morphology contributes to overall coastal character

        # The inverse distance weighting approach implemented here is consistent with coastal
        # geomorphology literature, where shorter, steeper segments often indicate important
        # morphological features (like scarps or berms) that have disproportionate influence on
        # processes like wave reflection and erosion.
        # This modification ensures the two metrics will now provide different values, with mean
        # segment gradient giving more emphasis to steep short rays, which is conceptually aligned
        # with the approach described in Masselink & Hegge (1995).
        segment_weights = 1.0 / distances  # Inverse distance weighting
        mean_segment_gradient = np.average(slopes, weights=segment_weights)
        # also apply IDW approach here
        mean_segment_angle = np.average(slope_angles, weights=segment_weights)

        # TODO: revisit this when you aren't exhausted
        # 4. Area-weighted approach
        # Calculate the area between adjacent rays using the constant ray resolution
        #
        # Note on area-weighted metrics with constant ray spacing:
        # Even with constant ray spacing, this approach remains valid and useful because:
        # 1. The areas still vary based on the lengths of adjacent rays
        # 2. It weights coastal segments based on their spatial extent (area)
        # 3. It gives more importance to wider sections of the beach
        # 4. It differs from length-weighted metrics by considering adjacent pairs of rays
        #    rather than individual rays, better representing the actual coastal surface
        #
        # This is particularly relevant for:
        # - Sediment volume considerations
        # - Wave energy distribution calculations
        # - Potential flooding impact assessments
        # - Any analysis where the spatial extent of coastal segments matters
        #
        # Reference: This approach is conceptually similar to area-weighted methods used
        # in Hegge et al. (1996) and later coastal morphology studies that consider the
        # contribution of different beach segments to overall character.

        # Calculate the area between adjacent rays using the (constant!) ray resolution
        # Calculate approximate areas between adjacent rays (trapezoidal)
        areas = []
        for i in range(len(distances) - 1):
            # Calculate trapezoidal area using constant ray resolution
            area = (
                0.5
                * (distances[i] + distances[i + 1])
                * self.metadata["ray_resolution"]
            )
            areas.append(area)
        # Use areas as weights for appropriate segments
        if areas and len(slopes) > 1:  # Ensure we have data
            area_weighted_gradient = np.average(slopes[:-1], weights=areas)
            area_weighted_angle = np.degrees(np.arctan(area_weighted_gradient))
        else:
            area_weighted_gradient = np.nan
            area_weighted_angle = np.nan

        # Calculate various statistical metrics
        metrics = {
            # Basic statistics
            "mean_slope": np.mean(slopes),
            "median_slope": np.median(slopes),
            "std_slope": np.std(slopes),
            "percentiles": np.percentile(slope_angles, self.pcbreaks),
            # Angle-based statistics
            "mean_angle": np.mean(slope_angles),
            "median_angle": np.median(slope_angles),
            "std_angle": np.std(slope_angles),
            # Length-weighted statistics
            "length_weighted_mean_slope": np.average(slopes, weights=ray_lengths),
            "length_weighted_mean_angle": np.average(slope_angles, weights=ray_lengths),
            # Intertidal gradient metrics (various approaches)
            "basic_intertidal_gradient": basic_intertidal_gradient,
            "basic_intertidal_angle": basic_intertidal_angle,
            "weighted_intertidal_gradient": weighted_intertidal_gradient,
            "weighted_intertidal_angle": weighted_intertidal_angle,
            "mean_segment_gradient": mean_segment_gradient,
            "mean_segment_angle": mean_segment_angle,
            "area_weighted_gradient": area_weighted_gradient,
            "area_weighted_angle": area_weighted_angle,
            # Variation metrics
            "slope_variation_coef": np.std(slopes) / np.mean(slopes)
            if np.mean(slopes) > 0
            else np.nan,
            "angle_variation_coef": np.std(slope_angles) / np.mean(slope_angles)
            if np.mean(slope_angles) > 0
            else np.nan,
            # Range metrics
            "max_slope": np.max(slopes),
            "min_slope": np.min(slopes),
            "slope_range": np.max(slopes) - np.min(slopes),
            # Raw data references (for future use)
            "self.slopes_index": self.slopes.index.tolist(),
        }

        return metrics

    def _build_metrics_dict(self):
        """Friendly subset of the full intertidal gradient metric set"""
        return {
            "Metric": self.metric_description,
            "Value": [
                self.metrics["mean_slope"],
                self.metrics["median_slope"],
                self.metrics["std_slope"],
                self.metrics["mean_angle"],
                self.metrics["median_angle"],
                self.metrics["basic_intertidal_gradient"],
                self.metrics["basic_intertidal_angle"],
                self.metrics["weighted_intertidal_gradient"],
                self.metrics["weighted_intertidal_angle"],
                self.metrics["mean_segment_gradient"],
                self.metrics["mean_segment_angle"],
                self.metrics["area_weighted_gradient"],
                self.metrics["area_weighted_angle"],
                self.metrics["slope_variation_coef"],
            ],
        }

    def visualize_coastal_slopes(self, plot_indices=True):
        """
        Visualize analyzed coastal slopes with multiple plots.
        The main plot is a spatial representation of the interaction between LAT and HAT showing
        slope, lines showing computed shoaling and breaking locations and the computed intertidal zone.

        Parameters
        ----------
        plot_indices : bool
            Whether to include a figure showing various gradient indices

        Returns
        -------
        tuple
            (fig1, fig2) containing the generated figures

        """
        # Extract slope data
        slope_angles = self.slopes["slope_degrees"].values

        # Create first figure - coastal profile
        fig1, ax1 = plt.subplots(figsize=(10, 7))

        # Load the PNG logo
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, "assets", "naturescapes.png")
        logo = mpimg.imread(logo_path)  # Path to your PNG file

        # Plot the offshore and onshore lines
        self.shore_line.plot(ax=ax1, color="#B5B5B5", lw=0.25, zorder=6)
        wd = self.slopes.plot(  # noqa: F841
            ax=ax1,
            column="slope_degrees",
            cmap="viridis",
            legend=True,
            legend_kwds={
                "label": "Slope (degrees)",
            },
            zorder=0,
        )

        min_x, max_x, min_y, max_y = self._get_expanded_bounds(4000)
        ax1.set_xlim(min_x, max_x)
        ax1.set_ylim(min_y, max_y)

        self.origin_rays.plot(ax=ax1, color="green", lw=0.5, label="Wave origin")

        latp = self.lat_line.plot(  # noqa: F841
            ax=ax1, linestyle="--", color="#39FF14", lw=1.0, label="LAT"
        )
        shoaling = self.shoaling.plot(  # noqa: F841
            ax=ax1, linestyle="-", color="#FAD02C", lw=0.5, label="Shoaling", zorder=9
        )
        itz = self.intertidal.plot(  # noqa: F841
            ax=ax1,
            color="white",
            fc="#e60995",
            lw=0.1,
            alpha=0.3,
            hatch="///////////",
            zorder=8,
        )
        breaking = self.breaking.plot(  # noqa: F841
            ax=ax1, color="red", lw=0.5, zorder=9, label="Breaking"
        )

        # slope_endpoints = gpd.GeoDataFrame(
        #     geometry=pd.concat(
        #         [self.slopes.geometry.apply(lambda geom: Point(geom.coords[-1]))]
        #     ),
        #     crs=self.slopes.crs,
        # )
        # # slope_endpoints.plot(
        # #     ax=ax1,
        # #     color="blue",
        # #     zorder=0,
        # # )

        if len(self.intersections):
            intersection_endpoints = gpd.GeoDataFrame(
                geometry=pd.concat(
                    [
                        self.intersections.geometry.apply(
                            lambda geom: Point(geom.coords[-1])
                        )
                    ]
                ),
                crs=self.intersections.crs,
            )

            self.intersections.plot(
                ax=ax1,
                # color="#033500",
                color="#8f00ff",
                lw=0.1,
                zorder=9,
                label="Ray intersections",
                legend=True,
                legend_kwds={
                    "Intersecting Lines",
                },
            )

            # Extract endpoints from intersection LineString geometries
            intersection_endpoints.plot(
                ax=ax1,
                color="red",
                markersize=2,
                zorder=10,
                label="Intersection endpoints",
            )

        ax1.set_title(
            f"Inputs (metres, seconds):\nSmoothing Window: {self.metadata['smoothing_window']}, HAT {self.metadata['hat']}, LAT {self.metadata['lat']} , Period: {self.metadata['wave_period']}, Wave height: {self.metadata['wave_height']}",
            fontsize=8,
        )
        ax1.axis("off")
        fig1.patch.set_alpha(1)
        fig1.set_dpi(200)
        ax1.patch.set_alpha(1)
        leg = ax1.legend(loc="best", fontsize=8)
        leg.set_zorder(10)
        for line in leg.get_lines():
            line.set_linewidth(2.0)

        ax1.set_aspect("equal")

        # create logo imagebox
        imagebox = OffsetImage(logo, zoom=0.3)
        # Position in the lower left
        ab = AnnotationBbox(
            imagebox,
            (0.005, -0.05),
            frameon=False,
            box_alignment=(0, 0),
            xycoords="axes fraction",
            zorder=100,
        )
        ax1.add_artist(ab)
        scalebar = ScaleBar(1.0, "m", length_fraction=0.25, loc="upper left")
        ax1.add_artist(scalebar)
        fig1.tight_layout()

        # Create second figure - analysis plots
        if plot_indices:
            fig2, axs = plt.subplots(3, 1)
        else:
            fig2, axs = plt.subplots(1, 1)
            axs = [axs]
        fig2.set_dpi(200)

        elw = 0.4
        # Plot 1: Angle distribution histogram
        axs[0].hist(
            slope_angles,
            histtype="stepfilled",
            bins="auto",
            alpha=0.75,
            edgecolor="#3b3b3b",
            color="#ff4d04",
            linewidth=elw,
        )
        hlw = 1.0
        axs[0].axvline(
            self.metrics["mean_angle"],
            lw=hlw,
            color="#000000",
            linestyle="--",
            label=f"Mean: {self.metrics['mean_angle']:.2f}°",
        )
        axs[0].axvline(
            self.metrics["median_angle"],
            lw=hlw,
            color="#0088FF",
            linestyle="--",
            label=f"Median: {self.metrics['median_angle']:.2f}°",
        )
        axs[0].axvline(
            self.metrics["length_weighted_mean_angle"],
            lw=hlw,
            color="r",
            linestyle="--",
            label=f"Weighted Mean: {self.metrics['length_weighted_mean_angle']:.2f}°",
        )

        axs[0].set_title("Slope Angle Distribution")
        axs[0].set_xlabel("Angle (degrees)")
        axs[0].set_ylabel("Frequency")
        axs[0].legend()

        # Plot 2: Ray distance distribution histogram
        axs[1].hist(
            self.slopes.length,
            histtype="stepfilled",
            bins="auto",
            alpha=0.75,
            edgecolor="#3b3b3b",
            color="#008080",
            linewidth=elw,
        )
        hlw = 1.0
        axs[1].axvline(
            np.mean(self.slopes.length),
            lw=hlw,
            color="#000000",
            linestyle="--",
            label=f"Mean: {np.mean(self.slopes.length):.2f} m",
        )
        axs[1].axvline(
            np.median(self.slopes.length),
            lw=hlw,
            color="#0088FF",
            linestyle="--",
            label=f"Median: {(np.median(self.slopes.length)):.2f} m",
        )
        axs[1].set_title("Ray Length Distribution")
        axs[1].set_xlabel("Length (m)")
        axs[1].set_ylabel("Frequency")
        axs[1].legend()

        if plot_indices:
            # Plot 2: Comparison of different gradient indices
            indices = [
                ("Basic Intertidal", self.metrics["basic_intertidal_angle"]),
                ("Weighted Intertidal", self.metrics["weighted_intertidal_angle"]),
                ("Mean Segment", self.metrics["mean_segment_angle"]),
                ("Area Weighted", self.metrics["area_weighted_angle"]),
            ]

            names = [x[0] for x in indices]
            values = [x[1] for x in indices]

            plt.rcParams["hatch.linewidth"] = 0.1
            axs[2].bar(
                names,
                values,
                ec="#000000",
                color="#90D5FF",  # we could assign them separately in a list if we wanted to
                hatch="///",
                zorder=2,
                linewidth=elw,
            )
            axs[2].set_title("Comparison of Gradient Indices")
            axs[2].set_ylabel("Angle (degrees)")
            axs[2].set_ylim(0, max(values) * 1.2)
            axs[2].grid(axis="y", zorder=1, lw=0.5)
        fig2.tight_layout()

        # for i, v in enumerate(values):
        #     axs[1][0].text(i, v + 0.5, f"{v:.2f}°", ha="center")

        # Show summary statistics table
        print("Summary Statistics:")
        self.summary_stats

        # plt.tight_layout()
        return fig1, fig2

    @property
    def ray_data(self):
        """
        Return the computed ray dataframe containing ray geometries, lengths, and slopes
        """
        return self.slopes

    @property
    def summary_stats(self):
        """
        Return summary statistics for the analysed shoreline
        """
        print(pd.DataFrame(self._build_metrics_dict()).to_string(index=False))
        # Print percentiles separately
        print("\n\t\t\t\tSlope Angle Percentiles (°):")
        for p, v in zip(self.pcbreaks, self.metrics["percentiles"]):
            print(f"\t\t\t{p} %: {v}")
        print("\n\t\t\t\tAnalysis Metadata:")
        for k, v in self.metadata.items():
            print(f"\t\t\t{k}: {v}")

    def _get_expanded_bounds(self, buffer_distance=1000):
        """
        Return a reasonable bounding box for plotting, if lat line and hat line are the inputs
        """
        # Get combined total bounds
        combined_bounds = gpd.GeoDataFrame(
            pd.concat([self.lat_line, self.slopes])
        ).total_bounds

        # Expand by buffer distance
        min_x = combined_bounds[0] - buffer_distance
        min_y = combined_bounds[1] - buffer_distance
        max_x = combined_bounds[2] + buffer_distance
        max_y = combined_bounds[3] + buffer_distance

        return min_x, max_x, min_y, max_y


# Expose main class at package level
__all__ = ["ShorelineAnalyzer"]
