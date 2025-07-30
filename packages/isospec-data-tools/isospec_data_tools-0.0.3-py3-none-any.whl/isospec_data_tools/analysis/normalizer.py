"""Data normalization and preprocessing utilities.

This module provides a comprehensive set of tools for data wrangling operations
including normalization, filtering, imputation, and transformation of data matrices.
All operations are pure functions with no side effects.
"""

import logging
from typing import Any, Optional, Union

import numpy as np
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)


class DataWrangler:
    """
    A utility class for data normalization and preprocessing operations.

    This class provides static methods for various data wrangling tasks including:
    - Normalization (total abundance, median quotient)
    - Data filtering and imputation
    - Column transformations and encoding
    - Metadata joining and value replacement

    All methods are pure functions that return new DataFrames without modifying
    the original data. The class follows the single responsibility principle
    by focusing solely on data preprocessing operations.
    """

    @staticmethod
    def _validate_dataframe(data: pd.DataFrame, name: str = "data") -> None:
        """
        Validate that input is a non-empty DataFrame.

        Args:
            data: DataFrame to validate
            name: Name of the parameter for error messages

        Raises:
            TypeError: If data is not a DataFrame
            ValueError: If data is empty
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError(f"{name} must be a pandas DataFrame")
        if data.empty:
            raise ValueError(f"{name} cannot be empty")

    @staticmethod
    def _get_feature_columns(data: pd.DataFrame, prefix: str) -> list[str]:
        """
        Get columns that start with the specified prefix.

        Args:
            data: Input DataFrame
            prefix: Column prefix to filter by

        Returns:
            List of column names that start with the prefix

        Raises:
            ValueError: If no columns match the prefix
        """
        feature_cols = [col for col in data.columns if col.startswith(prefix)]
        if not feature_cols:
            raise ValueError(f"No columns found with prefix '{prefix}'")
        return feature_cols

    @staticmethod
    def _get_numeric_columns(data: pd.DataFrame, prefix: Optional[str] = None) -> list[str]:
        """
        Get numeric columns, optionally filtered by prefix.

        Args:
            data: Input DataFrame
            prefix: Optional prefix to filter columns

        Returns:
            List of numeric column names
        """
        numeric_cols = data.select_dtypes(include=["float64", "int64"]).columns.tolist()
        if prefix:
            numeric_cols = [col for col in numeric_cols if col.startswith(prefix)]
        return numeric_cols

    @staticmethod
    def total_abundance_normalization(data: pd.DataFrame, prefix: Optional[str] = None) -> pd.DataFrame:
        """
        Normalize data by total abundance per sample.

        For each sample (row), divides all feature values by the sum of all features
        in that sample. If a prefix is provided, only columns starting with that
        prefix are considered as features.

        Args:
            data: Input DataFrame with samples as rows and features as columns
            prefix: Optional prefix to identify feature columns. If None, only numeric columns are used

        Returns:
            Normalized DataFrame with the same shape as input

        Raises:
            ValueError: If data is invalid or no features found with prefix

        Example:
            >>> df = pd.DataFrame({'FT-1': [10, 20], 'FT-2': [5, 15], 'meta': ['A', 'B']})
            >>> normalized = DataWrangler.total_abundance_normalization(df, prefix='FT-')
            >>> print(normalized)
               FT-1   FT-2 meta
            0   0.67   0.33    A
            1   0.57   0.43    B
        """
        logger.info(f"Performing total abundance normalization with prefix: {prefix}")

        DataWrangler._validate_dataframe(data)
        normalized_data = data.copy()

        if prefix:
            feature_cols = DataWrangler._get_feature_columns(data, prefix)
            # Only use numeric feature columns
            numeric_feature_cols = [col for col in feature_cols if pd.api.types.is_numeric_dtype(data[col])]
            if not numeric_feature_cols:
                raise ValueError(f"No numeric columns found with prefix '{prefix}'")

            column_sums = data[numeric_feature_cols].sum(axis=1)
            # Avoid division by zero
            column_sums = column_sums.replace(0, np.nan)
            normalized_data[numeric_feature_cols] = data[numeric_feature_cols].div(column_sums, axis=0)
        else:
            # When no prefix, only use numeric columns
            numeric_cols = DataWrangler._get_numeric_columns(data)
            if not numeric_cols:
                raise ValueError("No numeric columns found for normalization")

            column_sums = data[numeric_cols].sum(axis=1)
            # Avoid division by zero
            column_sums = column_sums.replace(0, np.nan)
            normalized_data[numeric_cols] = data[numeric_cols].div(column_sums, axis=0)

        logger.info("Total abundance normalization completed successfully")
        return normalized_data

    @staticmethod
    def median_quotient_normalization(
        data: pd.DataFrame,
        prefix: str = "FT-",
        sample_type_col: str = "SampleType",
        qc_samples: list[str] | None = None,
    ) -> pd.DataFrame:
        """
        Normalize data using median quotient normalization.

        This method normalizes features by dividing each feature value by the
        median of that feature across QC samples, then dividing by the median
        of all quotients for each sample.

        Args:
            data: Input DataFrame with samples as rows and features as columns
            prefix: Prefix to identify feature columns
            sample_type_col: Column name containing sample type information
            qc_samples: List of QC sample types. Defaults to ["QC"]

        Returns:
            Normalized DataFrame with the same shape as input

        Raises:
            ValueError: If data is invalid, required columns missing, or no QC samples found

        Example:
            >>> df = pd.DataFrame({
            ...     'FT-1': [10, 20, 15], 'FT-2': [5, 15, 10],
            ...     'SampleType': ['QC', 'Sample', 'QC']
            ... })
            >>> normalized = DataWrangler.median_quotient_normalization(df)
        """
        if qc_samples is None:
            qc_samples = ["QC"]

        logger.info(f"Performing median quotient normalization with QC samples: {qc_samples}")

        DataWrangler._validate_dataframe(data)

        if sample_type_col not in data.columns:
            raise ValueError(f"Sample type column '{sample_type_col}' not found in data")

        feature_cols = DataWrangler._get_feature_columns(data, prefix)
        # Only use numeric feature columns
        numeric_feature_cols = [col for col in feature_cols if pd.api.types.is_numeric_dtype(data[col])]
        if not numeric_feature_cols:
            raise ValueError(f"No numeric columns found with prefix '{prefix}'")

        metadata_cols = data.columns.difference(numeric_feature_cols)

        # Get QC data
        qc_mask = data[sample_type_col].isin(qc_samples)
        qc_data = data[qc_mask]

        if qc_data.empty:
            raise ValueError(f"No QC samples found with types: {qc_samples}")

        # Calculate feature medians from QC samples
        feature_medians = qc_data[numeric_feature_cols].median(axis=0)

        # Avoid division by zero
        feature_medians = feature_medians.replace(0, np.nan)

        # Calculate quotients
        quotients = data[numeric_feature_cols].div(feature_medians, axis=1)
        sample_medians = quotients.median(axis=1)

        # Avoid division by zero
        sample_medians = sample_medians.replace(0, np.nan)

        # Normalize features
        normalized_features = data[numeric_feature_cols].div(sample_medians, axis=0)

        # Combine with metadata
        result = pd.concat([data[metadata_cols], normalized_features], axis=1)

        logger.info("Median quotient normalization completed successfully")
        return result

    @staticmethod
    def filter_data_matrix_samples(
        data_matrix: pd.DataFrame, values_to_filter: list[str] | None = None, column: str = "sample"
    ) -> pd.DataFrame:
        """
        Filter out samples containing specified values in a column.

        Args:
            data_matrix: Input DataFrame
            values_to_filter: List of values to filter out. Defaults to ["MP", "QC"]
            column: Column name to check for filtering values

        Returns:
            Filtered DataFrame with matching rows removed

        Raises:
            ValueError: If data is invalid or column not found

        Example:
            >>> df = pd.DataFrame({'sample': ['Sample1', 'QC1', 'Sample2'], 'value': [1, 2, 3]})
            >>> filtered = DataWrangler.filter_data_matrix_samples(df)
            >>> print(filtered)
                sample  value
            0  Sample1      1
            2  Sample2      3
        """
        if values_to_filter is None:
            values_to_filter = ["MP", "QC"]

        logger.info(f"Filtering samples containing values: {values_to_filter}")

        DataWrangler._validate_dataframe(data_matrix)

        if column not in data_matrix.columns:
            raise ValueError(f"Column '{column}' not found in data")

        # Create filter pattern and apply
        filter_pattern = "|".join(values_to_filter)
        filter_condition = ~data_matrix[column].astype(str).str.contains(filter_pattern, na=False)
        filtered_data = data_matrix[filter_condition]

        logger.info(f"Filtered {len(data_matrix) - len(filtered_data)} samples")
        return filtered_data

    @staticmethod
    def impute_missing_values(
        data_matrix: pd.DataFrame,
        prefix: str = "FT",
        sample_type_col: str = "SampleType",
        qc_samples: list[str] | None = None,
        replacement_value: Union[float, str] = 1,
    ) -> pd.DataFrame:
        """
        Impute missing values using minimum values from QC samples.

        First replaces specified values with NaN, then fills missing values
        with the minimum value from QC samples for each feature.

        Args:
            data_matrix: Input DataFrame
            prefix: Prefix to identify feature columns
            sample_type_col: Column name containing sample type information
            qc_samples: List of QC sample types. Defaults to ["QC", "EQC"]
            replacement_value: Value to replace with NaN before imputation

        Returns:
            DataFrame with imputed missing values

        Raises:
            ValueError: If data is invalid, required columns missing, or no QC samples found

        Example:
            >>> df = pd.DataFrame({
            ...     'FT1': [1, 2, 1], 'FT2': [3, 1, 4],
            ...     'SampleType': ['QC', 'Sample', 'QC']
            ... })
            >>> imputed = DataWrangler.impute_missing_values(df)
        """
        if qc_samples is None:
            qc_samples = ["QC", "EQC"]

        logger.info(f"Imputing missing values with QC samples: {qc_samples}")

        DataWrangler._validate_dataframe(data_matrix)

        if sample_type_col not in data_matrix.columns:
            raise ValueError(f"Sample type column '{sample_type_col}' not found in data")

        data_matrix_processed = data_matrix.copy()
        cols_to_process = DataWrangler._get_feature_columns(data_matrix, prefix)

        # Replace specified values with NaN
        data_matrix_processed[cols_to_process] = data_matrix_processed[cols_to_process].replace(
            replacement_value, np.nan
        )

        # Get QC data
        qc_mask = data_matrix_processed[sample_type_col].isin(qc_samples)
        qc_data = data_matrix_processed[qc_mask]

        if qc_data.empty:
            raise ValueError(f"No QC samples found with types: {qc_samples}")

        # Impute each column with minimum QC value
        for col in cols_to_process:
            min_qc = qc_data[col].min()
            if pd.notna(min_qc):  # Only impute if we have valid QC data
                data_matrix_processed[col] = data_matrix_processed[col].fillna(min_qc)

        logger.info("Missing value imputation completed successfully")
        return data_matrix_processed

    @staticmethod
    def join_sample_metadata(
        data: pd.DataFrame,
        metadata: pd.DataFrame,
        sample_id_col: str = "SampleID",
        sample_join_col: str = "sample",
        metadata_cols: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """
        Join sample metadata with data using specified columns.

        Args:
            data: Main data DataFrame
            metadata: Metadata DataFrame
            sample_id_col: Column in metadata to use as index for joining
            sample_join_col: Column in data to use for joining
            metadata_cols: List of metadata columns to include. If None, includes all

        Returns:
            DataFrame with joined metadata

        Raises:
            ValueError: If data is invalid or required columns missing

        Example:
            >>> data_df = pd.DataFrame({'sample': ['A', 'B'], 'value': [1, 2]})
            >>> meta_df = pd.DataFrame({'SampleID': ['A', 'B'], 'group': ['G1', 'G2']})
            >>> joined = DataWrangler.join_sample_metadata(data_df, meta_df)
        """
        logger.info("Joining sample metadata with data")

        DataWrangler._validate_dataframe(data, "data")
        DataWrangler._validate_dataframe(metadata, "metadata")

        if sample_join_col not in data.columns:
            raise ValueError(f"Sample join column '{sample_join_col}' not found in data")

        if sample_id_col not in metadata.columns:
            raise ValueError(f"Sample ID column '{sample_id_col}' not found in metadata")

        if metadata_cols is None:
            metadata_cols = metadata.columns.tolist()
        else:
            # Validate that all specified columns exist
            missing_cols = set(metadata_cols) - set(metadata.columns)
            if missing_cols:
                raise ValueError(f"Metadata columns not found: {missing_cols}")

        result = data.merge(
            metadata[metadata_cols].set_index(sample_id_col),
            left_on=sample_join_col,
            right_index=True,
            how="left",
            suffixes=("", "_metadata"),
        )

        logger.info("Metadata joining completed successfully")
        return result

    @staticmethod
    def replace_column_values(
        data: pd.DataFrame,
        column: str,
        mapping: Optional[dict[Any, Any]] = None,
        old_value: Optional[Any] = None,
        new_value: Optional[Any] = None,
    ) -> pd.DataFrame:
        """
        Replace values in a specified column.

        Args:
            data: Input DataFrame
            column: Column name to modify
            mapping: Dictionary mapping old values to new values
            old_value: Single old value to replace
            new_value: Single new value to replace with

        Returns:
            DataFrame with replaced values

        Raises:
            ValueError: If data is invalid, column not found, or invalid parameters

        Example:
            >>> df = pd.DataFrame({'col': ['A', 'B', 'A']})
            >>> result = DataWrangler.replace_column_values(df, 'col', mapping={'A': 'X'})
            >>> print(result)
               col
            0   X
            1   B
            2   X
        """
        logger.info(f"Replacing values in column: {column}")

        DataWrangler._validate_dataframe(data)

        if column not in data.columns:
            raise ValueError(f"Column '{column}' not found in data")

        result = data.copy()

        if mapping is not None:
            result[column] = result[column].replace(mapping)
        elif old_value is not None and new_value is not None:
            result[column] = result[column].replace(old_value, new_value)
        else:
            raise ValueError("Must provide either mapping dict or old/new value pair")

        logger.info("Column value replacement completed successfully")
        return result

    @staticmethod
    def log2_transform_numeric(df: pd.DataFrame, prefix: Optional[str] = None) -> pd.DataFrame:
        """
        Apply log2 transformation to numeric columns.

        Args:
            df: Input DataFrame
            prefix: Optional prefix to filter columns. If None, all numeric columns are transformed

        Returns:
            DataFrame with log2-transformed numeric columns

        Raises:
            ValueError: If data is invalid or no numeric columns found

        Example:
            >>> df = pd.DataFrame({'FT1': [1, 2, 4], 'FT2': [8, 16, 32], 'meta': ['A', 'B', 'C']})
            >>> transformed = DataWrangler.log2_transform_numeric(df, prefix='FT')
            >>> print(transformed)
               FT1   FT2 meta
            0  0.0   3.0    A
            1  1.0   4.0    B
            2  2.0   5.0    C
        """
        logger.info(f"Applying log2 transformation with prefix: {prefix}")

        DataWrangler._validate_dataframe(df)

        numeric_cols = DataWrangler._get_numeric_columns(df, prefix)

        if len(numeric_cols) == 0:
            raise ValueError("No numeric columns found for transformation")

        df_logged = df.copy()

        # Handle negative or zero values by adding small constant
        for col in numeric_cols:
            min_val = df_logged[col].min()
            if min_val <= 0:
                offset = abs(min_val) + 1e-10
                df_logged[col] = df_logged[col] + offset
                logger.warning(f"Added offset {offset} to column {col} to handle non-positive values")

        df_logged[numeric_cols] = np.log2(df_logged[numeric_cols])

        logger.info("Log2 transformation completed successfully")
        return df_logged

    @staticmethod
    def encode_categorical_column(
        df: pd.DataFrame, column: str = "sex", mapping: Optional[dict[Any, Any]] = None
    ) -> pd.DataFrame:
        """
        Encode a categorical column using a mapping dictionary.

        Args:
            df: Input DataFrame
            column: Column name to encode
            mapping: Dictionary mapping original values to encoded values

        Returns:
            DataFrame with new encoded column added

        Raises:
            ValueError: If data is invalid, column not found, or mapping is invalid

        Example:
            >>> df = pd.DataFrame({'sex': ['M', 'F', 'M']})
            >>> result = DataWrangler.encode_categorical_column(df, 'sex', {'M': 1, 'F': 0})
            >>> print(result)
               sex  sex_encoded
            0    M            1
            1    F            0
            2    M            1
        """
        logger.info(f"Encoding categorical column: {column}")

        DataWrangler._validate_dataframe(df)

        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in data")

        if mapping is None:
            raise ValueError("Mapping dictionary is required for encoding")

        result = df.copy()
        result[f"{column}_encoded"] = result[column].map(mapping)

        # Check for unmapped values
        unmapped = result[result[f"{column}_encoded"].isna()][column].unique()
        if len(unmapped) > 0:
            logger.warning(f"Unmapped values found in column {column}: {unmapped}")

        logger.info("Categorical encoding completed successfully")
        return result

    @staticmethod
    def filter_data_by_column_value(data: pd.DataFrame, column: str, value: Any) -> pd.DataFrame:
        """
        Filter data to keep only rows where a column equals a specific value.

        Args:
            data: Input DataFrame
            column: Column name to filter on
            value: Value to filter for

        Returns:
            Filtered DataFrame

        Raises:
            ValueError: If data is invalid or column not found

        Example:
            >>> df = pd.DataFrame({'group': ['A', 'B', 'A'], 'value': [1, 2, 3]})
            >>> filtered = DataWrangler.filter_data_by_column_value(df, 'group', 'A')
            >>> print(filtered)
              group  value
            0     A      1
            2     A      3
        """
        logger.info(f"Filtering data where {column} = {value}")

        DataWrangler._validate_dataframe(data)

        if column not in data.columns:
            raise ValueError(f"Column '{column}' not found in data")

        filtered_data: pd.DataFrame = data[data[column] == value]

        logger.info(f"Filtered to {len(filtered_data)} rows")
        return filtered_data

    @staticmethod
    def tan_mqn_pipeline(
        data: pd.DataFrame,
        prefix: str = "FT-",
        sample_type_col: str = "SampleType",
        qc_samples: Optional[list[str]] = None,
        tan_prefix: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Apply Total Abundance Normalization (TAN) followed by Median Quotient Normalization (MQN) sequentially.

        This pipeline first normalizes data by total abundance per sample, then applies
        median quotient normalization using QC samples. This approach is useful for
        metabolomics data preprocessing where both normalizations are needed.

        Args:
            data: Input DataFrame with samples as rows and features as columns
            prefix: Prefix to identify feature columns for MQN (default: "FT-")
            sample_type_col: Column name containing sample type information for MQN
            qc_samples: List of QC sample types for MQN. Defaults to ["QC"]
            tan_prefix: Optional prefix for TAN. If None, uses all numeric columns

        Returns:
            DataFrame normalized by both TAN and MQN sequentially

        Raises:
            ValueError: If data is invalid, required columns missing, or no QC samples found

        Example:
            >>> df = pd.DataFrame({
            ...     'FT-1': [10, 20, 15], 'FT-2': [5, 15, 10],
            ...     'SampleType': ['QC', 'Sample', 'QC']
            ... })
            >>> normalized = DataWrangler.tan_mqn_pipeline(df)
        """
        logger.info("Starting TAN-MQN pipeline normalization")

        # Step 1: Apply Total Abundance Normalization
        logger.info("Step 1: Applying Total Abundance Normalization")
        tan_normalized = DataWrangler.total_abundance_normalization(data=data, prefix=tan_prefix)

        # Step 2: Apply Median Quotient Normalization
        logger.info("Step 2: Applying Median Quotient Normalization")
        final_normalized = DataWrangler.median_quotient_normalization(
            data=tan_normalized, prefix=prefix, sample_type_col=sample_type_col, qc_samples=qc_samples
        )

        logger.info("TAN-MQN pipeline normalization completed successfully")
        return final_normalized
