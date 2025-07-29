import pytest
from unittest.mock import patch, mock_open
import pandas as pd
import os

from toolkit.main import Toolkit
from toolkit.template import Template

@pytest.fixture
def toolkit():
    return Toolkit()

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "model": ["Sex"],
        "pid": ["001"],
        "event_id": ["E001"],
        "value": ["M"],
        "age": [30],
        "value_datatype": ["xsd:string"],
        "valueIRI": ["http://example.org/sex/male"],
        "activity": [None],
        "unit": [None],
        "input": [None],
        "target": [None],
        "protocol_id": [None],
        "frequency_type": [None],
        "frequency_value": [None],
        "agent": [None],
        "startdate": ["2021-01-01"],
        "enddate": [None],
        "comments": [None]
    })

# _find_matching_files

def test_find_matching_files(toolkit, mocker):
    mocker.patch("os.listdir", return_value=["Sex.csv"])
    result = toolkit._find_matching_files("/toolkit/data")
    assert result == [os.path.join("/toolkit/data/Sex.csv")]

def test_find_matching_files_no_csv(toolkit, mocker):
    mocker.patch("os.listdir", return_value=["README.txt", "data.json"])
    result = toolkit._find_matching_files("/toolkit/data")
    assert result == []

# import_your_data_from_csv

def test_import_your_data_from_csv_success(toolkit, sample_df, mocker):
    mocker.patch("builtins.open", mock_open(read_data="model,pid,event_id,value"))
    mocker.patch("pandas.read_csv", return_value=sample_df)
    df = toolkit.import_your_data_from_csv("somefile.csv")
    assert df is not None

def test_import_your_data_from_csv_empty(toolkit, mocker):
    mocker.patch("builtins.open", mock_open(read_data="model,pid,event_id,value"))
    mocker.patch("pandas.read_csv", return_value=pd.DataFrame())
    df = toolkit.import_your_data_from_csv("empty.csv")
    assert df.empty

def test_import_your_data_from_csv_fail(toolkit, mocker):
    mocker.patch("pandas.read_csv", side_effect=Exception("Error"))
    df = toolkit.import_your_data_from_csv("badfile.csv")
    assert df is None

# check_status_column_names

def test_check_status_column_names_valid(toolkit, sample_df):
    df = sample_df.reindex(columns=Toolkit.columns, fill_value=None)
    result = toolkit.check_status_column_names(df.copy())
    assert all(col in result.columns for col in Toolkit.columns)

def test_check_status_column_names_adds_missing_columns(toolkit, sample_df):
    df = sample_df.copy().drop(columns=["model"])
    result = toolkit.check_status_column_names(df)
    assert "model" in result.columns
    assert all(col in result.columns for col in Toolkit.columns)

def test_check_status_column_names_invalid(toolkit, sample_df):
    df = sample_df.copy()
    df["unexpected"] = "value"
    with pytest.raises(ValueError):
        toolkit.check_status_column_names(df)

def test_check_status_column_names_extra_columns(toolkit, sample_df):
    df = sample_df.copy()
    df["extra_column"] = "unexpected"
    with pytest.raises(ValueError):
        toolkit.check_status_column_names(df)

# value_edition

def test_value_edition(toolkit, sample_df):
    df = sample_df.reindex(columns=Toolkit.columns, fill_value=None)
    edited = toolkit.value_edition(df.copy())
    assert "value_string" in edited.columns
    assert edited.loc[0, "value_string"] == "M"
    assert edited.loc[0, "attribute_type"] == "http://example.org/sex/male"

# time_edition

def test_time_edition(toolkit, sample_df):
    df = sample_df.reindex(columns=Toolkit.columns, fill_value=None)
    edited = toolkit.time_edition(df.copy())
    assert edited.loc[0, "enddate"] == "2021-01-01"

def test_time_edition_enddate_none(toolkit, sample_df):
    df = sample_df.reindex(columns=Toolkit.columns, fill_value=None)
    df.loc[0, "enddate"] = None
    df.loc[0, "startdate"] = "2020-12-31"
    edited = toolkit.time_edition(df.copy())
    assert edited.loc[0, "enddate"] == "2020-12-31"

def test_time_edition_missing_dates(toolkit, sample_df):
    df = sample_df.reindex(columns=Toolkit.columns, fill_value=None)
    df.loc[0, "startdate"] = None
    df.loc[0, "enddate"] = None
    edited = toolkit.time_edition(df.copy())
    assert edited.loc[0, "enddate"] is None

# clean_empty_rows

def test_clean_empty_rows(toolkit, sample_df):
    df = sample_df.reindex(columns=Toolkit.columns, fill_value=None)
    cleaned = toolkit.clean_empty_rows(df.copy(), "fake.csv")
    assert len(cleaned) == 1

def test_clean_empty_rows_all_empty(toolkit):
    df = pd.DataFrame([{col: None for col in Toolkit.columns}])
    cleaned = toolkit.clean_empty_rows(df.copy(), "fake.csv")
    assert len(cleaned) == 0

# delete_extra_columns

def test_delete_extra_columns(toolkit, sample_df):
    df = sample_df.copy()
    df["extra"] = "something"
    deleted = toolkit.delete_extra_columns(df)
    for col in Toolkit.drop_columns:
        assert col not in deleted.columns

def test_delete_extra_columns_drops_specified(toolkit, sample_df):
    df = sample_df.copy()
    df["to_be_dropped"] = "drop me"
    Toolkit.drop_columns.append("to_be_dropped")
    deleted = toolkit.delete_extra_columns(df.copy())
    assert "to_be_dropped" not in deleted.columns
    Toolkit.drop_columns.remove("to_be_dropped")

# unique_id_generation

def test_unique_id_generation(toolkit, sample_df):
    df = sample_df.reindex(columns=Toolkit.columns, fill_value=None)
    result = toolkit.unique_id_generation(df.copy())
    uniqid_value = result.loc[0, "uniqid"]
    assert isinstance(uniqid_value, str)
    assert uniqid_value.isdigit()
    assert len(uniqid_value) == 20

# whole_method

def test_whole_method(toolkit, sample_df, mocker):
    mocker.patch.object(Toolkit, "_find_matching_files", return_value=["CARE.csv"])
    mocker.patch.object(Toolkit, "_process_file", return_value=sample_df.reindex(columns=Toolkit.columns, fill_value=None))
    mock_to_csv = mocker.patch("pandas.DataFrame.to_csv")
    toolkit.whole_method("/toolkit/data")
    mock_to_csv.assert_called_once()
