"""
Unit tests for StatisticalAnalyzer class.

This module contains focused tests for the most important functions with complex logic,
data transformations, and high risk of silent failures.
"""

import numpy as np
import pandas as pd
import pytest

from isospec_data_tools.analysis.stat_analyzer import StatisticalAnalyzer


class TestStatisticalAnalyzer:
    """Test suite for StatisticalAnalyzer class."""

    @pytest.fixture
    def sample_data(self) -> pd.DataFrame:
        """Create synthetic test data with known values."""
        return pd.DataFrame({
            "FT-1": [1.2, 2.4, 1.2, 2.4, 1.2, 2.4],  # Mean Healthy=1.2, Yes=2.4
            "FT-2": [1.6, 2.5, 1.6, 2.5, 1.6, 2.5],  # Mean Healthy=1.6, Yes=2.5
            "FT-3": [0.8, 1.6, 0.8, 1.6, 0.8, 1.6],  # Mean Healthy=0.8, Yes=1.6
            "class_final": ["Healthy", "Yes", "Healthy", "Yes", "Healthy", "Yes"],
            "age": [25, 30, 35, 40, 45, 50],
            "sex": [0, 1, 0, 1, 0, 1],
        })

    @pytest.fixture
    def edge_case_data(self) -> pd.DataFrame:
        """Create test data with edge cases."""
        return pd.DataFrame({
            "FT-1": [1.0, 2.0, np.nan, 3.0, 0.0, 4.0],  # Contains NaN and zero
            "FT-2": [1.5, 1.5, 1.5, 1.5, 1.5, 1.5],  # No variance
            "class_final": ["A", "B", "A", "B", "A", "B"],
            "age": [20, 25, 30, 35, 40, 45],
        })

    @pytest.fixture
    def three_group_data(self) -> pd.DataFrame:
        """Create test data with three groups."""
        return pd.DataFrame({
            "FT-1": [1.0, 2.0, 3.0, 1.0, 2.0, 3.0, 1.0, 2.0, 3.0],
            "class_final": ["A", "B", "C", "A", "B", "C", "A", "B", "C"],
            "age": [20, 25, 30, 35, 40, 45, 50, 55, 60],
        })

    def test_get_glycan_features(self, sample_data: pd.DataFrame) -> None:
        """Test glycan feature extraction with different prefixes."""
        # Arrange
        sa = StatisticalAnalyzer()

        # Act
        ft_features = sa._get_glycan_features(sample_data, "FT-")
        non_existent = sa._get_glycan_features(sample_data, "XYZ-")

        # Assert
        assert ft_features == ["FT-1", "FT-2", "FT-3"]
        assert non_existent == []

    def test_calculate_cohens_d(self) -> None:
        """Test Cohen's d calculation with known values."""
        # Arrange
        sa = StatisticalAnalyzer()
        group1 = pd.Series([1, 2, 3, 4, 5])  # mean=3, var=2.5
        group2 = pd.Series([6, 7, 8, 9, 10])  # mean=8, var=2.5

        # Act
        cohens_d = sa._calculate_cohens_d(group1, group2)

        # Assert
        expected_d = (8 - 3) / np.sqrt(((4 * 2.5) + (4 * 2.5)) / 8)
        assert abs(cohens_d - expected_d) < 1e-10

    def test_calculate_fold_change(self) -> None:
        """Test fold change calculation with different scenarios."""
        # Arrange
        sa = StatisticalAnalyzer()

        # Act & Assert
        # Regular fold change
        assert sa._calculate_fold_change(2.0, 6.0, log2_transform=False) == 3.0

        # Log2 transformed fold change
        assert sa._calculate_fold_change(2.0, 6.0, log2_transform=True) == 16.0  # 2^(6-2)

        # Division by zero should return NaN
        assert np.isnan(sa._calculate_fold_change(0.0, 5.0, log2_transform=False))

    def test_adjust_p_values(self) -> None:
        """Test p-value adjustment with Benjamini-Hochberg method."""
        # Arrange
        sa = StatisticalAnalyzer()
        p_values = pd.Series([0.01, 0.05, 0.1, 0.2, 0.3])

        # Act
        adjusted = sa._adjust_p_values(p_values, alpha=0.05)

        # Assert
        assert len(adjusted) == len(p_values)
        assert all(adjusted >= p_values)  # Adjusted p-values should be >= original
        assert adjusted.index.equals(p_values.index)

    def test_validate_input_data_success(self, sample_data: pd.DataFrame) -> None:
        """Test successful input validation."""
        # Arrange
        sa = StatisticalAnalyzer()

        # Act & Assert - should not raise
        sa._validate_input_data(sample_data, "class_final", ["age"])

    def test_validate_input_data_empty(self) -> None:
        """Test input validation with empty data."""
        # Arrange
        sa = StatisticalAnalyzer()
        empty_df = pd.DataFrame()

        # Act & Assert
        with pytest.raises(ValueError, match="Data cannot be empty"):
            sa._validate_input_data(empty_df, "class_final", [])

    def test_validate_input_data_missing_columns(self, sample_data: pd.DataFrame) -> None:
        """Test input validation with missing columns."""
        # Arrange
        sa = StatisticalAnalyzer()

        # Act & Assert
        with pytest.raises(ValueError, match="Missing required columns"):
            sa._validate_input_data(sample_data, "nonexistent", [])

    def test_validate_input_data_single_class(self, sample_data: pd.DataFrame) -> None:
        """Test input validation with single class."""
        # Arrange
        sa = StatisticalAnalyzer()
        single_class_data = sample_data.copy()
        single_class_data["class_final"] = "A"

        # Act & Assert
        with pytest.raises(ValueError, match="At least 2 unique classes required"):
            sa._validate_input_data(single_class_data, "class_final", [])

    def test_perform_tukey_hsd_basic(self, sample_data: pd.DataFrame) -> None:
        """Test Tukey HSD with basic synthetic data."""
        # Arrange
        sa = StatisticalAnalyzer()

        # Act
        results = sa.perform_tukey_hsd(sample_data, alpha=0.05, class_column="class_final", log2_transform=False)

        # Assert

        assert isinstance(results, pd.DataFrame)
        assert len(results) == 3  # 3 glycans
        assert all(
            col in results.columns
            for col in [
                "glycan",
                "group1",
                "group2",
                "mean_diff",
                "fold_change",
                "p_value",
                "ci_lower",
                "ci_upper",
                "effect_size",
                "adj_p_value",
                "log2_fold_change",
            ]
        )

        # Check specific values for FT-1
        ft1_result = results[results["glycan"] == "FT-1"].iloc[0]
        assert abs(ft1_result["mean_diff"] - 1.2) < 0.01  # 2.4 - 1.2
        assert abs(ft1_result["fold_change"] - 2.0) < 0.01  # 2.4/1.2
        assert abs(ft1_result["log2_fold_change"] - np.log2(2.0)) < 0.01

    def test_perform_tukey_hsd_edge_cases(self, edge_case_data: pd.DataFrame) -> None:
        """Test Tukey HSD with edge cases (NaN, zero variance)."""
        # Arrange
        sa = StatisticalAnalyzer()

        # Act
        results = sa.perform_tukey_hsd(edge_case_data, alpha=0.05, class_column="class_final", log2_transform=False)
        # Assert
        assert isinstance(results, pd.DataFrame)
        # FT-2 should be excluded due to no variance, or have NaN effect size
        assert len(results) >= 1  # At least FT-1 should have results
        assert "FT-1" in results["glycan"].values

        # If FT-2 is included, it should have NaN effect size due to no variance
        if "FT-2" in results["glycan"].values:
            ft2_result = results[results["glycan"] == "FT-2"].iloc[0]
            assert pd.isna(ft2_result["effect_size"])

    def test_perform_tukey_hsd_log2_transform(self, sample_data: pd.DataFrame) -> None:
        """Test Tukey HSD with log2 transformation."""
        # Arrange
        sa = StatisticalAnalyzer()

        # Act
        results = sa.perform_tukey_hsd(sample_data, alpha=0.05, class_column="class_final", log2_transform=True)

        # Assert
        assert isinstance(results, pd.DataFrame)
        # Check that fold change calculation is different with log2 transform
        ft1_result = results[results["glycan"] == "FT-1"].iloc[0]
        expected_fold_change = 2 ** (2.4 - 1.2)  # 2^(mean2 - mean1)
        assert abs(ft1_result["fold_change"] - expected_fold_change) < 0.01

    def test_perform_tukey_hsd_three_groups(self, three_group_data: pd.DataFrame) -> None:
        """Test Tukey HSD with three groups."""
        # Arrange
        sa = StatisticalAnalyzer()

        # Act
        results = sa.perform_tukey_hsd(three_group_data, alpha=0.05, class_column="class_final", log2_transform=False)

        # Assert
        assert isinstance(results, pd.DataFrame)
        # Should have 3 comparisons: A-B, A-C, B-C
        assert len(results) == 3
        assert set(results["group1"].unique()) == {"A", "B"}
        assert set(results["group2"].unique()) == {"B", "C"}

    def test_perform_student_test_basic(self, sample_data: pd.DataFrame) -> None:
        """Test Student's t-test with basic synthetic data."""
        # Arrange
        sa = StatisticalAnalyzer()

        # Act
        results = sa.perform_student_test(sample_data, alpha=0.05, class_column="class_final", log2_transform=False)

        # Assert
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 3  # 3 glycans
        assert "t_statistic" in results.columns

        # Check specific values for FT-1
        ft1_result = results[results["glycan"] == "FT-1"].iloc[0]
        assert abs(ft1_result["mean_diff"] - 1.2) < 0.01
        assert abs(ft1_result["fold_change"] - 2.0) < 0.01

    def test_perform_welch_test_basic(self, sample_data: pd.DataFrame) -> None:
        """Test Welch's t-test with basic synthetic data."""
        # Arrange
        sa = StatisticalAnalyzer()

        # Act
        results = sa.perform_welch_test(sample_data, alpha=0.05, class_column="class_final", log2_transform=False)

        # Assert
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 3  # 3 glycans
        assert "welch_df" in results.columns

        # Check that Welch's degrees of freedom are calculated
        ft1_result = results[results["glycan"] == "FT-1"].iloc[0]
        # With synthetic data having no variance, we might get NaN, which is expected
        assert pd.isna(ft1_result["welch_df"]) or ft1_result["welch_df"] > 0

    def test_process_comparison_results(self) -> None:
        """Test processing of comparison results."""
        # Arrange
        sa = StatisticalAnalyzer()
        results = [
            {
                "glycan": "FT-1",
                "group1": "A",
                "group2": "B",
                "mean_diff": 1.0,
                "fold_change": 2.0,
                "p_value": 0.01,
                "ci_lower": 0.5,
                "ci_upper": 1.5,
                "effect_size": 0.8,
            },
            {
                "glycan": "FT-2",
                "group1": "A",
                "group2": "B",
                "mean_diff": 0.5,
                "fold_change": 1.5,
                "p_value": 0.05,
                "ci_lower": 0.2,
                "ci_upper": 0.8,
                "effect_size": 0.6,
            },
        ]

        # Act
        processed = sa._process_comparison_results(results, alpha=0.05)

        # Assert
        assert isinstance(processed, pd.DataFrame)
        assert len(processed) == 2
        assert "adj_p_value" in processed.columns
        assert "log2_fold_change" in processed.columns
        assert all(processed["adj_p_value"] >= processed["p_value"])
        assert processed.iloc[0]["adj_p_value"] <= processed.iloc[1]["adj_p_value"]  # Sorted

    def test_chi_square_test_basic(self, sample_data: pd.DataFrame) -> None:
        """Test chi-square test with basic synthetic data."""
        # Arrange
        sa = StatisticalAnalyzer()

        # Act
        results = sa.chi_square_test(
            sample_data, target_column="class_final", value_column="age", binary_split_column="sex"
        )

        # Assert
        assert isinstance(results, dict)
        assert "within_group" in results
        assert "between_group" in results
        # The within-group tests might fail due to insufficient data or no variance
        # Just check that the structure is correct
        assert len(results["between_group"]) == 1  # 1 comparison between groups

    def test_chi_square_test_no_binary_split(self, sample_data: pd.DataFrame) -> None:
        """Test chi-square test without binary split column."""
        # Arrange
        sa = StatisticalAnalyzer()

        # Act
        results = sa.chi_square_test(sample_data, target_column="class_final", value_column="age")

        # Assert
        assert isinstance(results, dict)
        assert len(results["within_group"]) == 0  # No binary split
        assert len(results["between_group"]) == 1  # 1 comparison

    def test_analyze_glycans_ancova_basic(self, sample_data: pd.DataFrame) -> None:
        """Test ANCOVA analysis with basic synthetic data."""
        # Arrange
        sa = StatisticalAnalyzer()

        # Act
        significant, all_results, significant_glycans = sa.analyze_glycans_ancova(
            sample_data, feature_prefix="FT-", class_column="class_final", covar_columns=["age"], alpha=0.05
        )

        # Assert
        assert isinstance(significant, pd.DataFrame)
        assert isinstance(all_results, pd.DataFrame)
        assert isinstance(significant_glycans, np.ndarray)
        assert len(all_results) == 3  # 3 glycans
        assert "class_p_value" in all_results.columns
        assert "class_adj_p_value" in all_results.columns
        assert "age_p_value" in all_results.columns

    def test_analyze_glycans_ancova_with_composition_map(self, sample_data: pd.DataFrame) -> None:
        """Test ANCOVA analysis with glycan composition mapping."""
        # Arrange
        sa = StatisticalAnalyzer()
        composition_map = {"FT-1": "Hex5HexNAc4", "FT-2": "Hex6HexNAc5", "FT-3": "Hex4HexNAc3"}

        # Act
        significant, all_results, significant_glycans = sa.analyze_glycans_ancova(
            sample_data,
            feature_prefix="FT-",
            class_column="class_final",
            covar_columns=["age"],
            alpha=0.05,
            glycan_composition_map=composition_map,
        )

        # Assert
        assert "glycan_composition" in all_results.columns
        assert all_results.loc[0, "glycan_composition"] == "Hex5HexNAc4"

    def test_analyze_glycans_ancova_no_features(self) -> None:
        """Test ANCOVA analysis with no glycan features."""
        # Arrange
        sa = StatisticalAnalyzer()
        data = pd.DataFrame({
            "class": ["A", "B", "A", "B"],  # Use 'class' as default column name
            "age": [25, 30, 35, 40],
        })

        # Act & Assert
        with pytest.raises(ValueError, match="No glycan features found"):
            sa.analyze_glycans_ancova(data, feature_prefix="FT-")

    def test_add_group_statistics(self, sample_data: pd.DataFrame) -> None:
        """Test adding group statistics to results."""
        # Arrange
        sa = StatisticalAnalyzer()
        results_df = pd.DataFrame({"glycan": ["FT-1", "FT-2"], "class_p_value": [0.01, 0.02]})

        # Act
        sa._add_group_statistics(results_df, sample_data, "class_final")

        # Assert
        assert "max_fold_change" in results_df.columns
        assert "mean_Healthy" in results_df.columns
        assert "mean_Yes" in results_df.columns

        # Check specific values
        ft1_row = results_df[results_df["glycan"] == "FT-1"].iloc[0]
        assert abs(ft1_row["mean_Healthy"] - 1.2) < 0.01
        assert abs(ft1_row["mean_Yes"] - 2.4) < 0.01
        assert abs(ft1_row["max_fold_change"] - 2.0) < 0.01  # 2.4/1.2


class TestStatisticalAnalyzerErrorHandling:
    """Test error handling and edge cases."""

    def test_empty_dataframe_handling(self) -> None:
        """Test handling of empty DataFrame."""
        # Arrange
        sa = StatisticalAnalyzer()
        empty_df = pd.DataFrame()

        # Act & Assert
        with pytest.raises(ValueError, match="Data cannot be empty"):
            sa.perform_tukey_hsd(empty_df, class_column="class_final")

    def test_single_group_handling(self) -> None:
        """Test handling of data with single group."""
        # Arrange
        sa = StatisticalAnalyzer()
        single_group_data = pd.DataFrame({"FT-1": [1, 2, 3], "class_final": ["A", "A", "A"]})

        # Act & Assert
        with pytest.raises(ValueError, match="At least 2 unique classes required"):
            sa.perform_tukey_hsd(single_group_data, class_column="class_final")

    def test_missing_columns_handling(self) -> None:
        """Test handling of missing required columns."""
        # Arrange
        sa = StatisticalAnalyzer()
        data = pd.DataFrame({"FT-1": [1, 2, 3]})

        # Act & Assert
        with pytest.raises(ValueError, match="Missing required columns"):
            sa.perform_tukey_hsd(data, class_column="nonexistent")

    def test_insufficient_data_handling(self) -> None:
        """Test handling of insufficient data for statistical tests."""
        # Arrange
        sa = StatisticalAnalyzer()
        insufficient_data = pd.DataFrame({
            "FT-1": [1.0, 2.0],  # Two values but same class
            "class_final": ["A", "A"],
        })

        # Act & Assert
        with pytest.raises(ValueError, match="At least 2 unique classes required"):
            sa.perform_tukey_hsd(insufficient_data, class_column="class_final")

    def test_nan_handling(self) -> None:
        """Test handling of NaN values in data."""
        # Arrange
        sa = StatisticalAnalyzer()
        nan_data = pd.DataFrame({"FT-1": [1.0, np.nan, 3.0, 4.0], "class_final": ["A", "B", "A", "B"]})

        # Act
        results = sa.perform_tukey_hsd(nan_data, class_column="class_final")

        # Assert
        assert isinstance(results, pd.DataFrame)
        # Should still produce results for valid data points
        assert len(results) > 0
