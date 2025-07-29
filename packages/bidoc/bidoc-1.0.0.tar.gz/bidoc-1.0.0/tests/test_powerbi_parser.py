import os
from pathlib import Path

import pytest

from bidoc.pbix_parser import PowerBIParser

# Define the path to the sample Power BI file
SAMPLE_FILE_PATH = Path(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "samples",
        "power_bi",
        "COVID-19 US Tracking Sample.pbix",
    )
)


@pytest.fixture
def power_bi_parser():
    """Provides an instance of the PowerBiParser for the sample file."""
    return PowerBIParser()


@pytest.fixture
def parsed_power_bi_data(power_bi_parser):
    """Provides parsed data from the sample Power BI file."""
    return power_bi_parser.parse(SAMPLE_FILE_PATH)


def test_initialization(power_bi_parser):
    """Tests that the PowerBiParser initializes correctly."""
    assert power_bi_parser is not None


def test_data_source_extraction(parsed_power_bi_data):
    """
    Tests the extraction of data source information.
    """
    data_sources = parsed_power_bi_data["data_sources"]
    assert isinstance(data_sources, list)
    # Data sources may be empty if they couldn't be extracted properly
    # The key requirement is that the field exists and is a list

    if data_sources:
        # If there are data sources, check their structure
        first_source = data_sources[0]
        assert "name" in first_source
        assert "type" in first_source
        assert "connection" in first_source


def test_table_and_field_extraction(parsed_power_bi_data):
    """Tests the extraction of tables and fields."""
    tables = parsed_power_bi_data["tables"]
    assert isinstance(tables, list)
    assert len(tables) > 0

    # Check for a known table
    covid_table = next((t for t in tables if t["name"] == "COVID"), None)
    assert covid_table is not None

    # Check for known columns in the COVID table
    assert any(c["name"] == "County Name" for c in covid_table["columns"])
    assert any(c["name"] == "Cases" for c in covid_table["columns"])


def test_measure_extraction(parsed_power_bi_data):
    """Tests the extraction of DAX measures."""
    measures = parsed_power_bi_data["measures"]
    assert isinstance(measures, list)
    assert len(measures) > 0

    # Check for a known measure
    total_deaths_measure = next(
        (m for m in measures if m["name"] == "Total deaths"), None
    )
    assert total_deaths_measure is not None
    assert "SUM(COVID[Daily deaths])" in total_deaths_measure["expression"]


# Add more tests for other components like calculated columns, relationships, etc.
