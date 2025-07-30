from typing import Any, Optional

import numpy as np
import pandas as pd
import scipy.stats as stats  # type: ignore[import-untyped]
from statsmodels.stats.multitest import multipletests  # type: ignore[import-untyped]


class ConfounderAnalyzer:
    """
    Provides utilities for analyzing confounders in glycan data.
    """

    @staticmethod
    def perform_statistical_tests(
        data: pd.DataFrame,
        target_column: str = "class_final",
        value_column: str = "age",
        binary_split_column: Optional[str] = "sex",
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Perform statistical tests for confounders.

        Args:
            data (pd.DataFrame): Input data containing target, value, and binary split columns.
            target_column (str): Column name for target groups.
            value_column (str): Column name for the value to test.
            binary_split_column (Optional[str]): Column name for binary grouping within target groups.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Results containing within-group and between-group test results.
        """
        results: dict[str, list[dict[str, Any]]] = {"within_group": [], "between_group": []}

        if binary_split_column:
            results["within_group"] = ConfounderAnalyzer._perform_within_group_tests(
                data, target_column, value_column, binary_split_column
            )

        results["between_group"] = ConfounderAnalyzer._perform_between_group_tests(data, target_column, value_column)

        return results

    @staticmethod
    def analyze_confounders(
        data: pd.DataFrame,
        glycan_list: Optional[list[str]] = None,
        glycan_prefix: str = "FT-",
        confounders: Optional[list[str]] = None,
        alpha: float = 0.05,
        correction_method: str = "fdr_bh",
        min_glycans: int = 10,
    ) -> tuple[dict[str, dict[str, list]], list[str]]:
        """
        Analyze relationships between glycans and confounders.

        Args:
            data (pd.DataFrame): Input data containing glycans and confounders.
            glycan_list (Optional[List[str]]): List of specific glycan columns to analyze.
            glycan_prefix (str): Prefix for glycan columns.
            confounders (Optional[List[str]]): List of confounder columns to analyze.
            alpha (float): Significance level for multiple testing correction.
            correction_method (str): Method for multiple testing correction.
            min_glycans (int): Minimum number of significant glycans required for a confounder to be significant.

        Returns:
            Tuple[Dict[str, Dict[str, List]], List[str]]: Results dictionary and list of significant confounders.
        """
        if confounders is None:
            confounders = ["age", "sex", "bmi", "age_cat"]

        glycan_cols = ConfounderAnalyzer._get_glycan_columns(data, glycan_list, glycan_prefix)
        glycan_data = data[glycan_cols]

        results = {}
        significant_confounders = []

        for confounder in confounders:
            if confounder not in data.columns:
                print(f"Warning: {confounder} not found in data")
                continue

            confounder_result = ConfounderAnalyzer._analyze_single_confounder(
                data, glycan_data, confounder, alpha, correction_method
            )

            if confounder_result is not None:
                results[confounder] = confounder_result
                if ConfounderAnalyzer._is_confounder_significant(confounder_result, alpha, min_glycans):
                    significant_confounders.append(confounder)

        return results, significant_confounders

    @staticmethod
    def get_confounded_features(results: dict[str, dict[str, list]], alpha: float = 0.05) -> pd.DataFrame:
        """
        Extract significantly confounded features.

        Args:
            results (Dict[str, Dict[str, List]]): Results from confounder analysis.
            alpha (float): Significance level.

        Returns:
            pd.DataFrame: DataFrame containing significantly confounded features.
        """
        confounded_features = []

        for confounder, res in results.items():
            confounded_features.extend(
                ConfounderAnalyzer._extract_confounded_features_for_confounder(confounder, res, alpha)
            )

        if confounded_features:
            df = pd.DataFrame(confounded_features)
            df["effect_magnitude"] = df.apply(
                lambda row: (abs(row.get("correlation", 0)) if "correlation" in row else row.get("effect_size", 0)),
                axis=1,
            )
            return df.sort_values(["confounder", "p_value"])
        else:
            return pd.DataFrame(
                columns=[
                    "feature",
                    "confounder",
                    "p_value",
                    "effect_magnitude",
                ]
            )

    @staticmethod
    def find_glycan_confounders(glycan_list: list[str], confounder_dict: dict[str, list[str]]) -> dict[str, list[str]]:
        """
        Find which confounders each glycan is associated with.
        Args:
            glycan_list (List[str]): List of glycans to check
            confounder_dict (Dict[str, List[str]]): Dictionary mapping confounders to lists of glycans
        Returns:
            Dict[str, List[str]]: Dictionary mapping each glycan to list of confounders it's found in
        """
        glycan_confounders = {}

        for glycan in glycan_list:
            confounders = []
            for confounder, glycans in confounder_dict.items():
                if glycan in glycans:
                    confounders.append(confounder)
            glycan_confounders[glycan] = confounders

        return glycan_confounders

    @staticmethod
    def filter_significant_glycans(
        results: dict[str, dict[str, list]], alpha: float = 0.05, label_column: str = "Glycan"
    ) -> dict[str, list[str]]:
        """
        Filter glycans with adjusted p-value < alpha for each confounder.
        Args:
            results (Dict[str, Dict[str, List]]): Results from confounder analysis containing
                'glycans' and 'adj_p_values' for each confounder
            alpha (float): Significance threshold for adjusted p-values
            label_column (str): Column name for glycan labels
        Returns:
            Dict[str, List[str]]: Dictionary mapping each confounder to list of significant glycans
        """
        significant_glycans = {}

        for confounder in results:
            df = pd.DataFrame(results[confounder])
            significant_glycans[confounder] = df[df["adj_p_values"] <= alpha][label_column].tolist()

        return significant_glycans

    # --- Private helper methods ---

    @staticmethod
    def _perform_within_group_tests(
        data: pd.DataFrame,
        target_column: str,
        value_column: str,
        binary_split_column: str,
    ) -> list[dict[str, Any]]:
        """
        Perform statistical tests within each target group.
        """
        results = []
        for group in sorted(data[target_column].unique()):
            group_data = data[data[target_column] == group]
            group_0 = group_data[group_data[binary_split_column] == 0][value_column]
            group_1 = group_data[group_data[binary_split_column] == 1][value_column]

            if len(group_0) > 0 and len(group_1) > 0:
                stat, pval = ConfounderAnalyzer._perform_appropriate_test(
                    group_0, group_1, group_data, binary_split_column, value_column
                )
                results.append({"group": group, "statistic": stat, "pvalue": pval})

        return results

    @staticmethod
    def _perform_between_group_tests(data: pd.DataFrame, target_column: str, value_column: str) -> list[dict[str, Any]]:
        """
        Perform statistical tests between target groups.
        """
        results = []
        groups = sorted(data[target_column].unique())

        for i, group1 in enumerate(groups):
            for group2 in groups[i + 1 :]:
                values1 = data[data[target_column] == group1][value_column]
                values2 = data[data[target_column] == group2][value_column]

                if len(values1) > 0 and len(values2) > 0:
                    stat, pval = ConfounderAnalyzer._perform_appropriate_test(
                        values1, values2, data, target_column, value_column, [group1, group2]
                    )
                    results.append({
                        "group1": group1,
                        "group2": group2,
                        "statistic": stat,
                        "pvalue": pval,
                    })

        return results

    @staticmethod
    def _perform_appropriate_test(
        values1: pd.Series,
        values2: pd.Series,
        data: pd.DataFrame,
        group_column: str,
        value_column: str,
        group_filter: Optional[list[Any]] = None,
    ) -> tuple[float, float]:
        """
        Perform appropriate statistical test based on data type.
        """
        if values1.dtype in ["int64", "float64"]:
            result = stats.ttest_ind(values1, values2)
            return (float(result.statistic), float(result.pvalue))
        else:
            filtered_data = data[data[group_column].isin(group_filter)] if group_filter else data
            contingency = pd.crosstab(filtered_data[group_column], filtered_data[value_column])
            result = stats.chi2_contingency(contingency)
            return (float(result[0]), float(result[1]))

    @staticmethod
    def _get_glycan_columns(
        data: pd.DataFrame,
        glycan_list: Optional[list[str]],
        glycan_prefix: str,
    ) -> list[str]:
        """
        Get list of glycan columns to analyze.
        """
        if glycan_list is not None:
            return glycan_list
        return [col for col in data.columns if col.startswith(glycan_prefix)]

    @staticmethod
    def _analyze_single_confounder(
        data: pd.DataFrame,
        glycan_data: pd.DataFrame,
        confounder: str,
        alpha: float,
        correction_method: str,
    ) -> Optional[dict[str, list]]:
        """
        Analyze a single confounder against all glycans.
        """
        confounder_data = data[confounder]
        p_values: list[float] = []
        effect_sizes: list[float] = []
        correlations: list[float] = []

        if ConfounderAnalyzer._is_categorical_confounder(confounder_data):
            p_values, effect_sizes, correlations = ConfounderAnalyzer._analyze_categorical_confounder(
                glycan_data, confounder_data
            )
        else:
            p_values, effect_sizes, correlations = ConfounderAnalyzer._analyze_continuous_confounder(
                glycan_data, confounder_data
            )

        valid_p_values = [p for p in p_values if not np.isnan(p)]
        if len(valid_p_values) == 0:
            return None

        adj_p_values = multipletests(valid_p_values, alpha=alpha, method=correction_method)[1]

        adj_p_values_full = ConfounderAnalyzer._expand_adjusted_p_values(p_values, adj_p_values)

        return {
            "glycans": list(glycan_data.columns),
            "p_values": p_values,
            "adj_p_values": adj_p_values_full,
            "effect_sizes": effect_sizes,
            "correlations": correlations,
        }

    @staticmethod
    def _is_categorical_confounder(confounder_data: pd.Series) -> bool:
        """
        Check if confounder is categorical.
        """
        return confounder_data.dtype == "object" or isinstance(confounder_data.dtype, pd.CategoricalDtype)

    @staticmethod
    def _analyze_categorical_confounder(
        glycan_data: pd.DataFrame, confounder_data: pd.Series
    ) -> tuple[list[float], list[float], list[float]]:
        """
        Analyze categorical confounder using t-tests.
        """
        categories = confounder_data.unique()
        if len(categories) != 2:
            print(f"Warning: Confounder has {len(categories)} categories, but t-test requires exactly 2")
            return [], [], []

        cat1, cat2 = categories
        p_values: list[float] = []
        effect_sizes: list[float] = []
        correlations: list[float] = []

        for glycan in glycan_data.columns:
            group1 = glycan_data.loc[confounder_data == cat1, glycan]
            group2 = glycan_data.loc[confounder_data == cat2, glycan]

            if len(group1) > 0 and len(group2) > 0:
                t_stat, p_val = stats.ttest_ind(group1, group2, nan_policy="omit")
                effect_size = ConfounderAnalyzer._calculate_cohens_d(group1, group2)

                p_values.append(p_val)
                effect_sizes.append(effect_size)
                correlations.append(0.0)
            else:
                p_values.append(np.nan)
                effect_sizes.append(np.nan)
                correlations.append(np.nan)

        return p_values, effect_sizes, correlations

    @staticmethod
    def _analyze_continuous_confounder(
        glycan_data: pd.DataFrame, confounder_data: pd.Series
    ) -> tuple[list[float], list[float], list[float]]:
        """
        Analyze continuous confounder using correlation.
        """
        p_values, effect_sizes, correlations = [], [], []

        for glycan in glycan_data.columns:
            valid_data = pd.DataFrame({"glycan": glycan_data[glycan], "confounder": confounder_data}).dropna()

            if len(valid_data) > 1:
                r, p_val = stats.pearsonr(valid_data["confounder"], valid_data["glycan"])
                p_values.append(p_val)
                effect_sizes.append(0.0)
                correlations.append(r)
            else:
                p_values.append(np.nan)
                effect_sizes.append(np.nan)
                correlations.append(np.nan)

        return p_values, effect_sizes, correlations

    @staticmethod
    def _calculate_cohens_d(group1: pd.Series, group2: pd.Series) -> float:
        """
        Calculate Cohen's d effect size.
        """
        mean1, mean2 = np.mean(group1), np.mean(group2)
        pooled_std = np.sqrt(
            ((len(group1) - 1) * np.var(group1) + (len(group2) - 1) * np.var(group2)) / (len(group1) + len(group2) - 2)
        )
        return abs(mean1 - mean2) / pooled_std if pooled_std != 0 else 0.0

    @staticmethod
    def _expand_adjusted_p_values(original_p_values: list[float], adj_p_values: np.ndarray) -> list[float]:
        """
        Expand adjusted p-values to match original p-values, handling NaN values.
        """
        adj_p_values_full = []
        counter = 0
        for p in original_p_values:
            if np.isnan(p):
                adj_p_values_full.append(np.nan)
            else:
                adj_p_values_full.append(adj_p_values[counter])
                counter += 1
        return adj_p_values_full

    @staticmethod
    def _is_confounder_significant(confounder_result: dict[str, list], alpha: float, min_glycans: int) -> bool:
        """
        Check if a confounder is significant based on adjusted p-values.
        """
        adj_p_values = confounder_result["adj_p_values"]
        significant_count = sum(1 for adj_p in adj_p_values if adj_p is not None and adj_p <= alpha)
        return significant_count >= min_glycans

    @staticmethod
    def _extract_confounded_features_for_confounder(
        confounder: str, res: dict[str, list], alpha: float
    ) -> list[dict[str, Any]]:
        """
        Extract significantly confounded features for a single confounder.
        """
        confounded_features = []
        glycans = res["glycans"]
        adj_p_values = res["adj_p_values"]
        effect_sizes = res["effect_sizes"]
        correlations = res["correlations"]

        for i, (glycan, p_val) in enumerate(zip(glycans, adj_p_values, strict=False)):
            if p_val is not None and p_val <= alpha:
                if abs(correlations[i]) > 0 and not np.isnan(correlations[i]):
                    effect = correlations[i]
                    effect_type = "correlation"
                else:
                    effect = effect_sizes[i]
                    effect_type = "effect_size"

                confounded_features.append({
                    "feature": glycan,
                    "confounder": confounder,
                    "p_value": p_val,
                    effect_type: effect,
                })

        return confounded_features
