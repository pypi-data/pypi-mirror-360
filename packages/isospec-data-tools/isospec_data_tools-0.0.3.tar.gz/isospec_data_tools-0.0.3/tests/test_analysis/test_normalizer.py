"""Tests for the DataWrangler class."""

import numpy as np
import pandas as pd
import pytest

from isospec_data_tools.analysis.normalizer import DataWrangler


class TestDataWrangler:
    """Test cases for DataWrangler class."""

    def test_validate_dataframe_valid(self) -> None:
        """Test that valid DataFrames pass validation."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        # Should not raise any exception
        DataWrangler._validate_dataframe(df)

    def test_validate_dataframe_invalid_type(self) -> None:
        """Test that non-DataFrame inputs raise ValueError."""
        with pytest.raises(TypeError, match="must be a pandas DataFrame"):
            DataWrangler._validate_dataframe([1, 2, 3])

    def test_validate_dataframe_empty(self) -> None:
        """Test that empty DataFrames raise ValueError."""
        df = pd.DataFrame()
        with pytest.raises(ValueError, match="cannot be empty"):
            DataWrangler._validate_dataframe(df)

    def test_get_feature_columns(self) -> None:
        """Test feature column extraction."""
        df = pd.DataFrame({"FT-1": [1, 2], "FT-2": [3, 4], "meta": ["A", "B"]})
        feature_cols = DataWrangler._get_feature_columns(df, "FT-")
        assert feature_cols == ["FT-1", "FT-2"]

    def test_get_feature_columns_no_match(self) -> None:
        """Test feature column extraction with no matches."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        with pytest.raises(ValueError, match="No columns found with prefix"):
            DataWrangler._get_feature_columns(df, "FT-")

    def test_get_numeric_columns(self) -> None:
        """Test numeric column extraction."""
        df = pd.DataFrame({"A": [1, 2], "B": [3.0, 4.0], "C": ["a", "b"]})
        numeric_cols = DataWrangler._get_numeric_columns(df)
        assert set(numeric_cols) == {"A", "B"}

    def test_get_numeric_columns_with_prefix(self) -> None:
        """Test numeric column extraction with prefix."""
        df = pd.DataFrame({"FT-1": [1, 2], "FT-2": [3.0, 4.0], "meta": ["a", "b"]})
        numeric_cols = DataWrangler._get_numeric_columns(df, "FT-")
        assert set(numeric_cols) == {"FT-1", "FT-2"}

    def test_total_abundance_normalization(self) -> None:
        """Test total abundance normalization."""
        df = pd.DataFrame({"FT-1": [10, 20], "FT-2": [5, 15], "meta": ["A", "B"]})
        normalized = DataWrangler.total_abundance_normalization(df, prefix="FT-")

        # Check that metadata is preserved
        assert "meta" in normalized.columns
        assert list(normalized["meta"]) == ["A", "B"]

        # Check normalization (should sum to 1 for each row)
        feature_cols = ["FT-1", "FT-2"]
        row_sums = normalized[feature_cols].sum(axis=1)
        np.testing.assert_allclose(row_sums, [1.0, 1.0])

    def test_total_abundance_normalization_no_prefix(self) -> None:
        """Test total abundance normalization without prefix."""
        df = pd.DataFrame({"A": [10, 20], "B": [5, 15], "meta": ["A", "B"]})
        normalized = DataWrangler.total_abundance_normalization(df)

        # Check that metadata is preserved
        assert "meta" in normalized.columns

        # Check normalization
        numeric_cols = ["A", "B"]
        row_sums = normalized[numeric_cols].sum(axis=1)
        np.testing.assert_allclose(row_sums, [1.0, 1.0])

    def test_median_quotient_normalization(self) -> None:
        """Test median quotient normalization."""
        df = pd.DataFrame({"FT-1": [10, 20, 15], "FT-2": [5, 15, 10], "SampleType": ["QC", "Sample", "QC"]})
        normalized = DataWrangler.median_quotient_normalization(df)

        # Check that metadata is preserved
        assert "SampleType" in normalized.columns
        assert list(normalized["SampleType"]) == ["QC", "Sample", "QC"]

        # Check that features are present
        assert "FT-1" in normalized.columns
        assert "FT-2" in normalized.columns

    def test_filter_data_matrix_samples(self) -> None:
        """Test sample filtering."""
        df = pd.DataFrame({"sample": ["Sample1", "QC1", "Sample2"], "value": [1, 2, 3]})
        filtered = DataWrangler.filter_data_matrix_samples(df)

        # Should filter out QC1
        assert len(filtered) == 2
        assert "QC1" not in filtered["sample"].values

    def test_impute_missing_values(self) -> None:
        """Test missing value imputation."""
        df = pd.DataFrame({"FT1": [1, 2, 1], "FT2": [3, 1, 4], "SampleType": ["QC", "Sample", "QC"]})
        imputed = DataWrangler.impute_missing_values(df, prefix="FT")

        # Check that metadata is preserved
        assert "SampleType" in imputed.columns

        # Check that features are present
        assert "FT1" in imputed.columns
        assert "FT2" in imputed.columns

    def test_join_sample_metadata(self) -> None:
        """Test metadata joining."""
        data_df = pd.DataFrame({"sample": ["A", "B"], "value": [1, 2]})
        meta_df = pd.DataFrame({"SampleID": ["A", "B"], "group": ["G1", "G2"]})

        joined = DataWrangler.join_sample_metadata(data_df, meta_df)

        # Check that all columns are present
        assert "sample" in joined.columns
        assert "value" in joined.columns
        assert "group" in joined.columns

        # Check that metadata was joined correctly
        assert joined.loc[joined["sample"] == "A", "group"].iloc[0] == "G1"
        assert joined.loc[joined["sample"] == "B", "group"].iloc[0] == "G2"

    def test_replace_column_values(self) -> None:
        """Test column value replacement."""
        df = pd.DataFrame({"col": ["A", "B", "A"]})
        result = DataWrangler.replace_column_values(df, "col", mapping={"A": "X"})

        # Check replacement
        assert list(result["col"]) == ["X", "B", "X"]

    def test_log2_transform_numeric(self) -> None:
        """Test log2 transformation."""
        df = pd.DataFrame({"FT1": [1, 2, 4], "FT2": [8, 16, 32], "meta": ["A", "B", "C"]})
        transformed = DataWrangler.log2_transform_numeric(df, prefix="FT")

        # Check that metadata is preserved
        assert "meta" in transformed.columns

        # Check log2 transformation
        assert transformed.loc[0, "FT1"] == 0.0  # log2(1) = 0
        assert transformed.loc[1, "FT1"] == 1.0  # log2(2) = 1
        assert transformed.loc[2, "FT1"] == 2.0  # log2(4) = 2

    def test_encode_categorical_column(self) -> None:
        """Test categorical column encoding."""
        df = pd.DataFrame({"sex": ["M", "F", "M"]})
        result = DataWrangler.encode_categorical_column(df, "sex", {"M": 1, "F": 0})

        # Check that original column is preserved
        assert "sex" in result.columns

        # Check that encoded column is added
        assert "sex_encoded" in result.columns

        # Check encoding
        assert list(result["sex_encoded"]) == [1, 0, 1]

    def test_filter_data_by_column_value(self) -> None:
        """Test data filtering by column value."""
        df = pd.DataFrame({"group": ["A", "B", "A"], "value": [1, 2, 3]})
        filtered = DataWrangler.filter_data_by_column_value(df, "group", "A")

        # Should only keep rows where group == 'A'
        assert len(filtered) == 2
        assert all(filtered["group"] == "A")
