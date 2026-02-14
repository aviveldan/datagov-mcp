"""Tests for visualization and profiling tools."""

import pytest
import respx
from httpx import Response

from datagov_mcp.api import BASE_URL
from datagov_mcp.visualization import chart_generator, dataset_profile, map_generator


class MockContext:
    """Mock Context for testing."""

    def __init__(self):
        self.info_messages = []
        self.error_messages = []

    async def info(self, message: str):
        self.info_messages.append(message)

    async def error(self, message: str):
        self.error_messages.append(message)


@pytest.mark.asyncio
class TestVisualizationTools:
    """Test visualization and profiling tools."""

    @respx.mock
    async def test_dataset_profile(self):
        """Test dataset profiling tool."""
        respx.get(f"{BASE_URL}/action/datastore_search").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "records": [
                            {"_id": 1, "name": "Alice", "age": 30, "city": "Tel Aviv"},
                            {"_id": 2, "name": "Bob", "age": 25, "city": "Jerusalem"},
                            {"_id": 3, "name": "Charlie", "age": 35, "city": "Haifa"},
                        ],
                        "fields": [
                            {"id": "_id", "type": "int"},
                            {"id": "name", "type": "text"},
                            {"id": "age", "type": "int"},
                            {"id": "city", "type": "text"},
                        ],
                    },
                },
            )
        )

        ctx = MockContext()
        result = await dataset_profile.fn(ctx, resource_id="test-resource", sample_size=10)

        assert "fields" in result
        assert result["sample_size"] == 3
        assert len(result["fields"]) == 3  # Excluding _id

        # Check that age is detected as integer
        age_field = next(f for f in result["fields"] if f["name"] == "age")
        assert age_field["type"] == "integer"
        assert "min" in age_field["stats"]
        assert age_field["stats"]["min"] == 25
        assert age_field["stats"]["max"] == 35

        # Check that city is detected as string with top values
        city_field = next(f for f in result["fields"] if f["name"] == "city")
        assert city_field["type"] == "string"
        assert "unique_count" in city_field["stats"]
        assert city_field["stats"]["unique_count"] == 3

    @respx.mock
    async def test_chart_generator_histogram(self):
        """Test chart generation for histogram."""
        respx.get(f"{BASE_URL}/action/datastore_search").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "records": [
                            {"age": 20},
                            {"age": 25},
                            {"age": 30},
                            {"age": 35},
                            {"age": 40},
                        ],
                    },
                },
            )
        )

        ctx = MockContext()
        result = await chart_generator.fn(
            ctx,
            resource_id="test-resource",
            chart_type="histogram",
            x_field="age",
            title="Age Distribution",
        )

        assert "vega_lite_spec" in result
        assert "html" in result

        spec = result["vega_lite_spec"]
        assert spec["mark"] == "bar"
        assert spec["encoding"]["x"]["field"] == "age"
        assert spec["encoding"]["x"]["bin"] is True
        assert "Age Distribution" in spec["title"]

    @respx.mock
    async def test_chart_generator_bar(self):
        """Test chart generation for bar chart."""
        respx.get(f"{BASE_URL}/action/datastore_search").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "records": [
                            {"city": "Tel Aviv", "population": 460000},
                            {"city": "Jerusalem", "population": 936000},
                            {"city": "Haifa", "population": 285000},
                        ],
                    },
                },
            )
        )

        ctx = MockContext()
        result = await chart_generator.fn(
            ctx,
            resource_id="test-resource",
            chart_type="bar",
            x_field="city",
            y_field="population",
        )

        assert "vega_lite_spec" in result
        spec = result["vega_lite_spec"]
        assert spec["mark"] == "bar"
        assert spec["encoding"]["x"]["field"] == "city"
        assert spec["encoding"]["y"]["field"] == "population"

    @respx.mock
    async def test_chart_generator_line(self):
        """Test chart generation for line chart."""
        respx.get(f"{BASE_URL}/action/datastore_search").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "records": [
                            {"year": 2020, "value": 100},
                            {"year": 2021, "value": 150},
                            {"year": 2022, "value": 200},
                        ],
                    },
                },
            )
        )

        ctx = MockContext()
        result = await chart_generator.fn(
            ctx,
            resource_id="test-resource",
            chart_type="line",
            x_field="year",
            y_field="value",
        )

        assert "vega_lite_spec" in result
        spec = result["vega_lite_spec"]
        assert spec["mark"]["type"] == "line"

    @respx.mock
    async def test_map_generator(self):
        """Test map generation from geographic data."""
        respx.get(f"{BASE_URL}/action/datastore_search").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "records": [
                            {
                                "name": "Tel Aviv",
                                "latitude": 32.0853,
                                "longitude": 34.7818,
                                "population": 460000,
                            },
                            {
                                "name": "Jerusalem",
                                "latitude": 31.7683,
                                "longitude": 35.2137,
                                "population": 936000,
                            },
                            {
                                "name": "Haifa",
                                "latitude": 32.7940,
                                "longitude": 34.9896,
                                "population": 285000,
                            },
                        ],
                    },
                },
            )
        )

        ctx = MockContext()
        result = await map_generator.fn(
            ctx,
            resource_id="test-resource",
            lat_field="latitude",
            lon_field="longitude",
            limit=100,
        )

        assert "geojson" in result
        assert "html" in result
        assert result["point_count"] == 3

        geojson = result["geojson"]
        assert geojson["type"] == "FeatureCollection"
        assert len(geojson["features"]) == 3

        # Check first feature
        feature = geojson["features"][0]
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Point"
        assert len(feature["geometry"]["coordinates"]) == 2  # [lon, lat]
        assert "name" in feature["properties"]
        assert "population" in feature["properties"]

        # Check center calculation
        assert "center" in result
        assert abs(result["center"]["lat"] - 32.2159) < 0.1  # Rough average
        assert abs(result["center"]["lon"] - 34.9950) < 0.1

    @respx.mock
    async def test_map_generator_no_valid_coordinates(self):
        """Test map generation with invalid coordinates."""
        respx.get(f"{BASE_URL}/action/datastore_search").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "records": [
                            {"name": "Invalid", "lat": "not-a-number", "lon": "invalid"},
                        ],
                    },
                },
            )
        )

        ctx = MockContext()
        result = await map_generator.fn(
            ctx, resource_id="test-resource", lat_field="lat", lon_field="lon"
        )

        assert "error" in result
        assert "No valid geographic coordinates" in result["error"]

    @respx.mock
    async def test_chart_generator_unsupported_type(self):
        """Test chart generation with unsupported chart type."""
        respx.get(f"{BASE_URL}/action/datastore_search").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "result": {"records": [{"x": 1, "y": 2}]},
                },
            )
        )

        ctx = MockContext()
        result = await chart_generator.fn(
            ctx,
            resource_id="test-resource",
            chart_type="invalid-type",
            x_field="x",
            y_field="y",
        )

        assert "error" in result
        assert "Unsupported chart type" in result["error"]
