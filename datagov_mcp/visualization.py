"""Visualization and data profiling tools for CKAN datasets."""

import json
from typing import Any

from fastmcp import Context

from datagov_mcp.api import CKANAPIError, ckan_api_call
from datagov_mcp.server import mcp


def infer_field_type(values: list[Any]) -> str:
    """Infer the type of a field from sample values."""
    if not values:
        return "unknown"

    # Remove None values
    non_null = [v for v in values if v is not None]
    if not non_null:
        return "null"

    # Check if numeric
    try:
        numeric_values = [float(v) for v in non_null if v != ""]
        if len(numeric_values) > len(non_null) * 0.8:  # 80% numeric
            # Check if integer
            if all(v == int(v) for v in numeric_values):
                return "integer"
            return "number"
    except (ValueError, TypeError):
        pass

    # Check for lat/lon patterns
    sample_str = str(non_null[0]).lower()
    if any(
        keyword in sample_str
        for keyword in ["lat", "latitude", "lng", "lon", "longitude", "coord"]
    ):
        return "coordinate"

    return "string"


def calculate_stats(values: list[Any], field_type: str) -> dict[str, Any]:
    """Calculate statistics for a field based on its type."""
    stats = {"count": len(values), "null_count": sum(1 for v in values if v is None)}

    non_null = [v for v in values if v is not None]
    if not non_null:
        return stats

    if field_type in ["integer", "number"]:
        try:
            numeric = [float(v) for v in non_null if v != ""]
            if numeric:
                stats.update(
                    {
                        "min": min(numeric),
                        "max": max(numeric),
                        "mean": sum(numeric) / len(numeric),
                    }
                )
        except (ValueError, TypeError):
            pass
    elif field_type == "string":
        # Top values for categorical
        from collections import Counter

        counter = Counter(str(v) for v in non_null)
        stats["unique_count"] = len(counter)
        stats["top_values"] = dict(counter.most_common(5))

    return stats


@mcp.tool()
async def dataset_profile(ctx: Context, resource_id: str, sample_size: int = 100) -> dict:
    """
    Profile a dataset resource to understand its structure and data quality.

    Analyzes a sample of records to infer schema, detect missing values,
    calculate basic statistics, and identify data types.

    Args:
        resource_id: ID of the resource to profile
        sample_size: Number of records to sample (default: 100)

    Returns:
        Profile report with schema, statistics, and data quality metrics
    """
    await ctx.info(f"Profiling resource: {resource_id}")

    try:
        # Fetch sample data
        result = await ckan_api_call(
            "datastore_search",
            params={
                "resource_id": resource_id,
                "limit": sample_size,
            },
        )

        records = result.get("result", {}).get("records", [])
        fields = result.get("result", {}).get("fields", [])

        if not records:
            return {"error": "No records found in resource"}

        # Analyze each field
        field_profiles = []
        for field_info in fields:
            field_name = field_info.get("id") or field_info.get("name", "")
            if field_name == "_id":  # Skip internal ID
                continue

            values = [record.get(field_name) for record in records]
            field_type = infer_field_type(values)
            stats = calculate_stats(values, field_type)

            field_profiles.append(
                {
                    "name": field_name,
                    "type": field_type,
                    "stats": stats,
                    "missingness": stats["null_count"] / stats["count"]
                    if stats["count"] > 0
                    else 0,
                }
            )

        return {
            "resource_id": resource_id,
            "sample_size": len(records),
            "total_fields": len(field_profiles),
            "fields": field_profiles,
        }

    except CKANAPIError as e:
        await ctx.error(f"Failed to profile dataset: {e.message}")
        return {"error": str(e.message)}


@mcp.tool()
async def chart_generator(
    ctx: Context,
    resource_id: str,
    chart_type: str,
    x_field: str,
    y_field: str = "",
    title: str = "",
    limit: int = 100,
) -> dict:
    """
    Generate a Vega-Lite chart specification for dataset visualization.

    Creates interactive chart specifications that can be rendered in compatible viewers.
    Supports common chart types: histogram, bar, line, and scatter plots.

    Args:
        resource_id: ID of the resource to visualize
        chart_type: Type of chart ('histogram', 'bar', 'line', 'scatter')
        x_field: Field name for X-axis
        y_field: Field name for Y-axis (not needed for histogram)
        title: Chart title (optional)
        limit: Maximum number of records to visualize (default: 100)

    Returns:
        Vega-Lite specification (JSON) and optional HTML rendering
    """
    await ctx.info(f"Generating {chart_type} chart for resource: {resource_id}")

    try:
        # Fetch data
        result = await ckan_api_call(
            "datastore_search",
            params={
                "resource_id": resource_id,
                "limit": limit,
            },
        )

        records = result.get("result", {}).get("records", [])

        if not records:
            return {"error": "No records found in resource"}

        # Base Vega-Lite specification
        spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "title": title or f"{chart_type.capitalize()} Chart",
            "data": {"values": records},
            "width": 600,
            "height": 400,
        }

        # Chart-specific configurations
        if chart_type == "histogram":
            spec["mark"] = "bar"
            spec["encoding"] = {
                "x": {"field": x_field, "bin": True, "title": x_field},
                "y": {"aggregate": "count", "title": "Count"},
            }
        elif chart_type == "bar":
            spec["mark"] = "bar"
            spec["encoding"] = {
                "x": {"field": x_field, "title": x_field},
                "y": {"field": y_field, "type": "quantitative", "title": y_field},
            }
        elif chart_type == "line":
            spec["mark"] = {"type": "line", "point": True}
            spec["encoding"] = {
                "x": {"field": x_field, "title": x_field},
                "y": {"field": y_field, "type": "quantitative", "title": y_field},
            }
        elif chart_type == "scatter":
            spec["mark"] = "point"
            spec["encoding"] = {
                "x": {"field": x_field, "type": "quantitative", "title": x_field},
                "y": {"field": y_field, "type": "quantitative", "title": y_field},
            }
        else:
            return {"error": f"Unsupported chart type: {chart_type}"}

        # Generate HTML rendering
        html = f"""
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
</head>
<body>
  <div id="vis"></div>
  <script type="text/javascript">
    var spec = {json.dumps(spec)};
    vegaEmbed('#vis', spec);
  </script>
</body>
</html>
"""

        return {"vega_lite_spec": spec, "html": html}

    except CKANAPIError as e:
        await ctx.error(f"Failed to generate chart: {e.message}")
        return {"error": str(e.message)}


@mcp.tool()
async def map_generator(
    ctx: Context, resource_id: str, lat_field: str, lon_field: str, limit: int = 500
) -> dict:
    """
    Generate an interactive map from geographic data.

    Creates a GeoJSON representation and an HTML map visualization
    for datasets with latitude/longitude coordinates.

    Args:
        resource_id: ID of the resource to map
        lat_field: Field name containing latitude values
        lon_field: Field name containing longitude values
        limit: Maximum number of points to map (default: 500)

    Returns:
        GeoJSON feature collection and HTML map with Leaflet
    """
    await ctx.info(f"Generating map for resource: {resource_id}")

    try:
        # Fetch data
        result = await ckan_api_call(
            "datastore_search",
            params={
                "resource_id": resource_id,
                "limit": limit,
            },
        )

        records = result.get("result", {}).get("records", [])

        if not records:
            return {"error": "No records found in resource"}

        # Convert to GeoJSON
        features = []
        for record in records:
            try:
                lat = float(record.get(lat_field, 0))
                lon = float(record.get(lon_field, 0))

                if lat and lon:  # Skip invalid coordinates
                    feature = {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [lon, lat]},
                        "properties": {k: v for k, v in record.items() if k not in [lat_field, lon_field]},
                    }
                    features.append(feature)
            except (ValueError, TypeError):
                continue

        if not features:
            return {"error": "No valid geographic coordinates found"}

        geojson = {"type": "FeatureCollection", "features": features}

        # Calculate bounds for map centering
        lats = [f["geometry"]["coordinates"][1] for f in features]
        lons = [f["geometry"]["coordinates"][0] for f in features]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)

        # Generate HTML map
        html = f"""
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    #map {{ height: 600px; width: 100%; }}
  </style>
</head>
<body>
  <div id="map"></div>
  <script>
    var map = L.map('map').setView([{center_lat}, {center_lon}], 10);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      attribution: '© OpenStreetMap contributors'
    }}).addTo(map);
    
    var geojson = {json.dumps(geojson)};
    L.geoJSON(geojson, {{
      onEachFeature: function(feature, layer) {{
        if (feature.properties) {{
          var popup = Object.entries(feature.properties)
            .map(([k,v]) => `<b>${{k}}</b>: ${{v}}`)
            .join('<br>');
          layer.bindPopup(popup);
        }}
      }}
    }}).addTo(map);
  </script>
</body>
</html>
"""

        return {
            "geojson": geojson,
            "html": html,
            "point_count": len(features),
            "center": {"lat": center_lat, "lon": center_lon},
        }

    except CKANAPIError as e:
        await ctx.error(f"Failed to generate map: {e.message}")
        return {"error": str(e.message)}
