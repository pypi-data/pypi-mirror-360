"""
Statistical analysis utilities for glycan data processing.

This module provides comprehensive statistical analysis tools for comparing glycan
abundances across different experimental groups, including ANCOVA, Tukey's HSD,
Student's t-test, Welch's t-test, and chi-square tests.
"""

from typing import Optional, Union

import numpy as np
import pandas as pd
import scipy.stats as stats
from pingouin import ancova
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.multitest import multipletests


class StatisticalAnalyzer:
    """Statistical analysis tools for glycan abundance comparisons."""

    @staticmethod
    def _get_glycan_features(data: pd.DataFrame, feature_prefix: str) -> list[str]:
        """Extract glycan feature column names from data."""
        return [col for col in data.columns if col.startswith(feature_prefix)]

    @staticmethod
    def _calculate_cohens_d(group1_data: pd.Series, group2_data: pd.Series) -> float:
        """Calculate Cohen's d effect size for two groups."""
        n1, n2 = len(group1_data), len(group2_data)
        var1, var2 = float(np.var(group1_data, ddof=1)), float(np.var(group2_data, ddof=1))
        pooled_se = float(np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)))
        return float((np.mean(group2_data) - np.mean(group1_data)) / pooled_se)

    @staticmethod
    def _calculate_fold_change(mean_group1: float, mean_group2: float, log2_transform: bool) -> float:
        """Calculate fold change between two group means."""
        if log2_transform:
            return 2 ** (mean_group2 - mean_group1)
        return mean_group2 / mean_group1 if mean_group1 != 0 else float("nan")

    @staticmethod
    def _adjust_p_values(p_values: pd.Series, alpha: float) -> pd.Series:
        """Adjust p-values using Benjamini-Hochberg method."""
        adjusted_pvalues = multipletests(p_values, alpha=alpha, method="fdr_bh")[1]
        return pd.Series(adjusted_pvalues, index=p_values.index, dtype=float)

    @staticmethod
    def _validate_input_data(data: pd.DataFrame, class_column: str, covar_columns: list[str]) -> None:
        """Validate input data for statistical analysis."""
        if data.empty:
            raise ValueError("Data cannot be empty")

        missing_cols = [col for col in [class_column, *covar_columns] if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        if data[class_column].nunique() < 2:
            raise ValueError(f"At least 2 unique classes required in '{class_column}'")

    @staticmethod
    def analyze_glycans_ancova(
        data: pd.DataFrame,
        feature_prefix: str = "FT-",
        class_column: str = "class",
        covar_columns: Optional[list[str]] = None,
        alpha: float = 0.05,
        glycan_composition_map: Optional[dict[str, str]] = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
        """
        Perform ANCOVA analysis for all glycans and filter for significant class effects.

        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame containing glycan abundances and metadata. Must have columns:
            - Glycan abundance columns starting with feature_prefix
            - class_column: categorical variable for group comparison
            - covar_columns: continuous covariates
        feature_prefix : str, default="FT-"
            Prefix used to identify feature columns
        class_column : str, default="class"
            Name of column containing class labels
        covar_columns : List[str], optional
            List of column names to use as covariates. Defaults to ["age"]
        alpha : float, default=0.05
            Significance level for filtering results
        glycan_composition_map : Dict[str, str], optional
            Dictionary mapping feature IDs to glycan compositions

        Returns:
        --------
        Tuple[pd.DataFrame, pd.DataFrame, np.ndarray]
            - significant_results: DataFrame with significant glycans only
            - all_results: DataFrame with all glycans analyzed
            - significant_glycans: Array of significant glycan names

        Raises:
        -------
        ValueError
            If input data is invalid or missing required columns
        """
        if covar_columns is None:
            covar_columns = ["age"]

        StatisticalAnalyzer._validate_input_data(data, class_column, covar_columns)

        glycan_features = StatisticalAnalyzer._get_glycan_features(data, feature_prefix)
        if not glycan_features:
            raise ValueError(f"No glycan features found with prefix '{feature_prefix}'")

        results = []

        for glycan in glycan_features:
            try:
                # Run ANCOVA
                ancova_result = ancova(data=data, dv=glycan, covar=covar_columns, between=class_column)

                # Extract class effect
                class_effect = ancova_result.loc[ancova_result["Source"] == class_column].iloc[0]

                result_dict = {
                    "glycan": glycan,
                    "class_p_value": class_effect["p-unc"],
                    "class_effect_size": class_effect["np2"],  # partial eta squared
                }

                # Add glycan composition if mapping provided
                if glycan_composition_map and glycan in glycan_composition_map:
                    result_dict["glycan_composition"] = glycan_composition_map[glycan]

                # Add effects for each covariate
                for covar in covar_columns:
                    covar_effect = ancova_result.loc[ancova_result["Source"] == covar].iloc[0]
                    result_dict[f"{covar}_p_value"] = covar_effect["p-unc"]
                    result_dict[f"{covar}_effect_size"] = covar_effect["np2"]

                results.append(result_dict)

            except Exception as e:
                # Log error and continue with other glycans
                print(f"Error analyzing glycan {glycan}: {e}")
                continue

        if not results:
            raise ValueError("No valid ANCOVA results obtained")

        # Convert results to DataFrame
        results_df = pd.DataFrame(results)

        # Adjust p-values for multiple comparisons
        results_df["class_adj_p_value"] = StatisticalAnalyzer._adjust_p_values(results_df["class_p_value"], alpha)

        # Filter for significant class effects
        significant_results = results_df[results_df["class_adj_p_value"] < alpha].sort_values("class_adj_p_value")

        # Add mean abundances and fold changes between classes
        StatisticalAnalyzer._add_group_statistics(significant_results, data, class_column)

        return (
            significant_results,
            results_df,
            significant_results.glycan.unique(),
        )

    @staticmethod
    def _add_group_statistics(results_df: pd.DataFrame, data: pd.DataFrame, class_column: str) -> None:
        """Add group statistics (means, fold changes) to results DataFrame."""
        for glycan in results_df["glycan"]:
            class_means = data.groupby(class_column)[glycan].mean()
            max_fold_change = class_means.max() / class_means.min()

            results_df.loc[results_df["glycan"] == glycan, "max_fold_change"] = max_fold_change

            # Add mean abundance per class as separate columns
            for class_name in data[class_column].unique():
                results_df.loc[
                    results_df["glycan"] == glycan,
                    f"mean_{class_name}",
                ] = data[data[class_column] == class_name][glycan].mean()

    @staticmethod
    def perform_tukey_hsd(
        data: pd.DataFrame,
        prefix: str = "FT-",
        class_column: str = "class_final",
        alpha: float = 0.05,
        log2_transform: bool = False,
    ) -> pd.DataFrame:
        """
        Perform Tukey's HSD test for pairwise comparisons between classes.

        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame containing glycan abundances and metadata
        prefix : str, default='FT-'
            Prefix to filter glycan columns from data
        class_column : str, default="class_final"
            Name of the column containing class labels
        alpha : float, default=0.05
            Significance level for p-value adjustment
        log2_transform : bool, default=False
            Whether the data is log2 transformed

        Returns:
        --------
        pd.DataFrame
            DataFrame containing pairwise comparison results
        """
        StatisticalAnalyzer._validate_input_data(data, class_column, [])

        glycan_features = StatisticalAnalyzer._get_glycan_features(data, prefix)
        if not glycan_features:
            return pd.DataFrame()

        results = []

        for glycan in glycan_features:
            try:
                # Extract data for this glycan and remove any NaN values
                valid_data = pd.DataFrame({"value": data[glycan], "group": data[class_column]}).dropna()

                if len(valid_data) < 3 or valid_data["group"].nunique() < 2:
                    continue

                # Perform Tukey's HSD test
                tukey = pairwise_tukeyhsd(
                    endog=valid_data["value"],
                    groups=valid_data["group"],
                    alpha=alpha,
                )

                # Extract results for each comparison
                if tukey.pvalues is not None and tukey.confint is not None:
                    for idx in range(len(tukey.pvalues)):
                        group1 = tukey.groupsunique[tukey._multicomp.pairindices[0][idx]]
                        group2 = tukey.groupsunique[tukey._multicomp.pairindices[1][idx]]

                        # Get data for both groups
                        group1_data = valid_data[valid_data["group"] == group1]["value"]
                        group2_data = valid_data[valid_data["group"] == group2]["value"]

                        # Calculate statistics
                        mean_group1, mean_group2 = np.mean(group1_data), np.mean(group2_data)
                        cohens_d = StatisticalAnalyzer._calculate_cohens_d(group1_data, group2_data)
                        fold_change = StatisticalAnalyzer._calculate_fold_change(
                            mean_group1, mean_group2, log2_transform
                        )

                        results.append({
                            "glycan": glycan,
                            "group1": group1,
                            "group2": group2,
                            "mean_diff": mean_group2 - mean_group1,
                            "fold_change": fold_change,
                            "p_value": tukey.pvalues[idx],
                            "ci_lower": tukey.confint[idx][0],
                            "ci_upper": tukey.confint[idx][1],
                            "effect_size": cohens_d,
                        })

            except Exception as e:
                print(f"Error in Tukey HSD for glycan {glycan}: {e}")
                continue

        return StatisticalAnalyzer._process_comparison_results(results, alpha)

    @staticmethod
    def perform_student_test(
        data: pd.DataFrame,
        prefix: str = "FT-",
        class_column: str = "class_final",
        alpha: float = 0.05,
        log2_transform: bool = False,
    ) -> pd.DataFrame:
        """
        Perform Student's t-test for pairwise comparisons between classes.

        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame containing glycan abundances and metadata
        prefix : str, default='FT-'
            Prefix to filter glycan columns from data
        class_column : str, default="class_final"
            Name of the column containing class labels
        alpha : float, default=0.05
            Significance level for p-value adjustment
        log2_transform : bool, default=False
            Whether the data is log2 transformed

        Returns:
        --------
        pd.DataFrame
            DataFrame containing pairwise comparison results
        """
        StatisticalAnalyzer._validate_input_data(data, class_column, [])

        glycan_features = StatisticalAnalyzer._get_glycan_features(data, prefix)
        if not glycan_features:
            return pd.DataFrame()

        classes = sorted(data[class_column].unique())
        if len(classes) < 2:
            return pd.DataFrame()

        results = []

        for glycan in glycan_features:
            for i in range(len(classes)):
                for j in range(i + 1, len(classes)):
                    group1, group2 = classes[i], classes[j]

                    try:
                        # Get data for both groups
                        group1_data = data[data[class_column] == group1][glycan].dropna()
                        group2_data = data[data[class_column] == group2][glycan].dropna()

                        if len(group1_data) < 2 or len(group2_data) < 2:
                            continue

                        # Perform t-test
                        t_stat, p_value = stats.ttest_ind(group1_data, group2_data)

                        # Calculate statistics
                        mean_group1, mean_group2 = np.mean(group1_data), np.mean(group2_data)
                        cohens_d = StatisticalAnalyzer._calculate_cohens_d(group1_data, group2_data)
                        fold_change = StatisticalAnalyzer._calculate_fold_change(
                            mean_group1, mean_group2, log2_transform
                        )

                        # Calculate confidence intervals
                        n1, n2 = len(group1_data), len(group2_data)
                        var1, var2 = np.var(group1_data, ddof=1), np.var(group2_data, ddof=1)
                        ci = stats.t.interval(
                            1 - alpha,
                            df=n1 + n2 - 2,
                            loc=mean_group2 - mean_group1,
                            scale=np.sqrt(var1 / n1 + var2 / n2),
                        )

                        results.append({
                            "glycan": glycan,
                            "group1": group1,
                            "group2": group2,
                            "mean_diff": mean_group2 - mean_group1,
                            "fold_change": fold_change,
                            "p_value": p_value,
                            "ci_lower": ci[0],
                            "ci_upper": ci[1],
                            "effect_size": cohens_d,
                            "t_statistic": t_stat,
                        })

                    except Exception as e:
                        print(f"Error in Student's t-test for glycan {glycan}, groups {group1}-{group2}: {e}")
                        continue

        return StatisticalAnalyzer._process_comparison_results(results, alpha)

    @staticmethod
    def perform_welch_test(
        data: pd.DataFrame,
        prefix: str = "FT-",
        class_column: str = "class_final",
        alpha: float = 0.05,
        log2_transform: bool = False,
    ) -> pd.DataFrame:
        """
        Perform Welch's t-test for pairwise comparisons between classes.

        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame containing glycan abundances and metadata
        prefix : str, default='FT-'
            Prefix to filter glycan columns from data
        class_column : str, default="class_final"
            Name of the column containing class labels
        alpha : float, default=0.05
            Significance level for p-value adjustment
        log2_transform : bool, default=False
            Whether the data is log2 transformed

        Returns:
        --------
        pd.DataFrame
            DataFrame containing pairwise comparison results using Welch's t-test
        """
        StatisticalAnalyzer._validate_input_data(data, class_column, [])

        glycan_features = StatisticalAnalyzer._get_glycan_features(data, prefix)
        if not glycan_features:
            return pd.DataFrame()

        classes = sorted(data[class_column].unique())
        if len(classes) < 2:
            return pd.DataFrame()

        results = []

        for glycan in glycan_features:
            for i in range(len(classes)):
                for j in range(i + 1, len(classes)):
                    group1, group2 = classes[i], classes[j]

                    try:
                        # Get data for both groups
                        group1_data = data[data[class_column] == group1][glycan].dropna()
                        group2_data = data[data[class_column] == group2][glycan].dropna()

                        if len(group1_data) < 2 or len(group2_data) < 2:
                            continue

                        # Perform Welch's t-test
                        t_stat, p_value = stats.ttest_ind(group1_data, group2_data, equal_var=False)

                        # Calculate statistics
                        mean_group1, mean_group2 = np.mean(group1_data), np.mean(group2_data)
                        cohens_d = StatisticalAnalyzer._calculate_cohens_d(group1_data, group2_data)
                        fold_change = StatisticalAnalyzer._calculate_fold_change(
                            mean_group1, mean_group2, log2_transform
                        )

                        # Calculate Welch's confidence intervals using Welch-Satterthwaite degrees of freedom
                        n1, n2 = len(group1_data), len(group2_data)
                        var1, var2 = np.var(group1_data, ddof=1), np.var(group2_data, ddof=1)
                        welch_df = ((var1 / n1 + var2 / n2) ** 2) / (
                            (var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1)
                        )
                        ci = stats.t.interval(
                            1 - alpha, df=welch_df, loc=mean_group2 - mean_group1, scale=np.sqrt(var1 / n1 + var2 / n2)
                        )

                        results.append({
                            "glycan": glycan,
                            "group1": group1,
                            "group2": group2,
                            "mean_diff": mean_group2 - mean_group1,
                            "fold_change": fold_change,
                            "p_value": p_value,
                            "ci_lower": ci[0],
                            "ci_upper": ci[1],
                            "effect_size": cohens_d,
                            "t_statistic": t_stat,
                            "welch_df": welch_df,
                        })

                    except Exception as e:
                        print(f"Error in Welch's t-test for glycan {glycan}, groups {group1}-{group2}: {e}")
                        continue

        return StatisticalAnalyzer._process_comparison_results(results, alpha)

    @staticmethod
    def _process_comparison_results(results: list[dict], alpha: float) -> pd.DataFrame:
        """Process and format comparison results with p-value adjustment."""
        if not results:
            return pd.DataFrame()

        results_df = pd.DataFrame(results)

        # Adjust p-values using Benjamini-Hochberg method
        results_df["adj_p_value"] = StatisticalAnalyzer._adjust_p_values(results_df["p_value"], alpha)

        # Calculate log2 fold change
        results_df["log2_fold_change"] = np.log2(results_df["fold_change"])

        # Sort by adjusted p-value
        return results_df.sort_values("adj_p_value")

    @staticmethod
    def chi_square_test(
        data: pd.DataFrame,
        target_column: str = "class_final",
        value_column: str = "age",
        binary_split_column: Optional[str] = "sex",
    ) -> dict[str, list[dict[str, Union[str, float]]]]:
        """
        Perform chi-square test for differences within and between groups.

        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame containing the data to analyze
        target_column : str, default='class_final'
            Column name for the grouping variable
        value_column : str, default='age'
            Column name for the values to compare
        binary_split_column : str, optional
            If provided, will split each group by this binary column (e.g. 'sex')

        Returns:
        --------
        Dict[str, List[Dict]]
            Dictionary containing within-group and between-group test results
        """
        StatisticalAnalyzer._validate_input_data(data, target_column, [])

        if value_column not in data.columns:
            raise ValueError(f"Value column '{value_column}' not found in data")

        if binary_split_column and binary_split_column not in data.columns:
            raise ValueError(f"Binary split column '{binary_split_column}' not found in data")

        results: dict[str, list[dict[str, Union[str, float]]]] = {"within_group": [], "between_group": []}

        # Handle within-group tests if binary split specified
        if binary_split_column:
            results["within_group"] = StatisticalAnalyzer._run_within_group_tests(
                data, target_column, value_column, binary_split_column
            )

        # Handle between-group tests
        results["between_group"] = StatisticalAnalyzer._run_between_group_tests(data, target_column, value_column)

        return results

    @staticmethod
    def _run_within_group_tests(
        data: pd.DataFrame, target_column: str, value_column: str, binary_split_column: str
    ) -> list[dict[str, Union[str, float]]]:
        """Run statistical tests between binary splits within each group."""
        results: list[dict[str, Union[str, float]]] = []
        for group in sorted(data[target_column].unique()):
            group_data = data[data[target_column] == group]
            group_0 = group_data[group_data[binary_split_column] == 0][value_column]
            group_1 = group_data[group_data[binary_split_column] == 1][value_column]

            if len(group_0) == 0 or len(group_1) == 0:
                continue

            try:
                if pd.api.types.is_numeric_dtype(group_0):
                    stat, pval = stats.ttest_ind(group_0, group_1)
                else:
                    contingency = pd.crosstab(group_data[binary_split_column], group_data[value_column])
                    stat, pval = stats.chi2_contingency(contingency)[:2]

                results.append({"group": group, "statistic": stat, "pvalue": pval})
            except Exception as e:
                print(f"Error in within-group test for group {group}: {e}")

        return results

    @staticmethod
    def _run_between_group_tests(
        data: pd.DataFrame, target_column: str, value_column: str
    ) -> list[dict[str, Union[str, float]]]:
        """Run statistical tests between different groups."""
        results: list[dict[str, Union[str, float]]] = []
        groups = sorted(data[target_column].unique())

        for i, group1 in enumerate(groups):
            for group2 in groups[i + 1 :]:
                values1 = data[data[target_column] == group1][value_column]
                values2 = data[data[target_column] == group2][value_column]

                if len(values1) == 0 or len(values2) == 0:
                    continue

                try:
                    if pd.api.types.is_numeric_dtype(values1):
                        stat, pval = stats.ttest_ind(values1, values2)
                    else:
                        mask = data[target_column].isin([group1, group2])
                        contingency = pd.crosstab(mask, data[value_column])
                        stat, pval = stats.chi2_contingency(contingency)[:2]

                    results.append({"group1": group1, "group2": group2, "statistic": stat, "pvalue": pval})
                except Exception as e:
                    print(f"Error in between-group test for groups {group1}-{group2}: {e}")

        return results
