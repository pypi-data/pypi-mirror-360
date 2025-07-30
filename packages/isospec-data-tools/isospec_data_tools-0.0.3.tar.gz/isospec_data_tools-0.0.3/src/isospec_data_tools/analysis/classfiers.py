"""
Machine learning classification and clustering utilities.

This module provides comprehensive tools for clustering analysis and model training
with cross-validation, hyperparameter tuning, and performance evaluation.
"""

from __future__ import annotations

import logging
from typing import Any, ClassVar, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
    roc_curve,
    silhouette_score,
)
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# Configure logging
logger = logging.getLogger(__name__)

# Type aliases for better readability
ArrayLike = Union[np.ndarray, pd.Series]
DataFrame = pd.DataFrame
Series = pd.Series


class ClusteringError(Exception):
    """Custom exception for clustering-related errors."""

    pass


class ModelTrainingError(Exception):
    """Custom exception for model training-related errors."""

    pass


class ClusterAnalyzer:
    """Handles various clustering algorithms with evaluation and analysis."""

    @staticmethod
    def run_kmeans(
        features: DataFrame,
        max_k: int = 10,
        min_k: int = 2,
        plot: bool = False,
        random_state: int = 42,
    ) -> tuple[np.ndarray, KMeans]:
        """
        Run KMeans clustering with automatic k selection using silhouette analysis.

        Args:
            features: Feature matrix for clustering
            max_k: Maximum number of clusters to try
            min_k: Minimum number of clusters to try
            plot: Whether to plot elbow and silhouette analysis
            random_state: Random state for reproducibility

        Returns:
            Tuple of (cluster_labels, fitted_kmeans_model)

        Raises:
            ClusteringError: If clustering fails or invalid parameters provided
        """
        if min_k >= max_k:
            raise ClusteringError("min_k must be less than max_k")

        if min_k < 2:
            raise ClusteringError("min_k must be at least 2")

        if features.empty:
            raise ClusteringError("Features dataframe cannot be empty")

        distortions = []
        silhouettes = []
        k_range = range(min_k, max_k + 1)

        for k in k_range:
            try:
                kmeans = KMeans(n_clusters=k, random_state=random_state)
                labels = kmeans.fit_predict(features)
                distortions.append(kmeans.inertia_)
                silhouettes.append(silhouette_score(features, labels))
            except Exception as e:
                logger.warning(f"KMeans failed for k={k}: {e}")
                distortions.append(np.inf)
                silhouettes.append(-1)

        if plot:
            ClusterAnalyzer._plot_kmeans_analysis(k_range, distortions, silhouettes)

        best_k_idx = np.argmax(silhouettes)
        best_k = k_range[best_k_idx]
        best_silhouette = silhouettes[best_k_idx]

        logger.info(f"Best k: {best_k}, silhouette score: {best_silhouette:.3f}")

        final_model = KMeans(n_clusters=best_k, random_state=random_state)
        final_labels = final_model.fit_predict(features)

        return final_labels, final_model

    @staticmethod
    def _plot_kmeans_analysis(k_range: range, distortions: list[float], silhouettes: list[float]) -> None:
        """Plot KMeans elbow and silhouette analysis."""
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax2 = ax1.twinx()

        ax1.plot(k_range, distortions, "bo-", label="Inertia (Elbow)")
        ax2.plot(k_range, silhouettes, "go--", label="Silhouette")

        ax1.set_xlabel("k")
        ax1.set_ylabel("Inertia", color="b")
        ax2.set_ylabel("Silhouette Score", color="g")

        plt.title("KMeans Elbow & Silhouette Analysis")
        fig.tight_layout()
        plt.show()

    @staticmethod
    def run_dbscan(features: DataFrame, eps: float = 0.5, min_samples: int = 5) -> tuple[np.ndarray, DBSCAN]:
        """
        Run DBSCAN clustering.

        Args:
            features: Feature matrix for clustering
            eps: Maximum distance between points to be considered neighbors
            min_samples: Minimum number of samples in a neighborhood

        Returns:
            Tuple of (cluster_labels, fitted_dbscan_model)
        """
        if eps <= 0:
            raise ClusteringError("eps must be positive")

        if min_samples < 1:
            raise ClusteringError("min_samples must be at least 1")

        model = DBSCAN(eps=eps, min_samples=min_samples)
        labels = model.fit_predict(features)
        return labels, model

    @staticmethod
    def run_agglomerative_auto(
        features: DataFrame, min_clusters: int = 2, max_clusters: int = 10
    ) -> tuple[np.ndarray, AgglomerativeClustering]:
        """
        Run Agglomerative clustering with automatic cluster number selection.

        Args:
            features: Feature matrix for clustering
            min_clusters: Minimum number of clusters to try
            max_clusters: Maximum number of clusters to try

        Returns:
            Tuple of (cluster_labels, fitted_agglomerative_model)
        """
        if min_clusters >= max_clusters:
            raise ClusteringError("min_clusters must be less than max_clusters")

        best_score = -1
        best_model: Optional[AgglomerativeClustering] = None
        best_labels: Optional[np.ndarray] = None
        best_k = None

        for k in range(min_clusters, max_clusters + 1):
            try:
                model = AgglomerativeClustering(n_clusters=k)
                labels = model.fit_predict(features)

                # Skip if all points are in same cluster or each point is its own cluster
                unique_labels = set(labels)
                if len(unique_labels) < 2 or len(unique_labels) == len(labels):
                    continue

                score = silhouette_score(features, labels)
                if score > best_score:
                    best_score = score
                    best_model = model
                    best_labels = labels
                    best_k = k

            except Exception as e:
                logger.warning(f"Agglomerative clustering failed for k={k}: {e}")
                continue

        if best_model is None or best_labels is None:
            raise ClusteringError("No valid clustering found")

        logger.info(f"[Agglomerative] Best number of clusters: {best_k} (Silhouette = {best_score:.3f})")

        return best_labels, best_model

    @staticmethod
    def evaluate_clustering(features: DataFrame, labels: np.ndarray) -> float:
        """
        Evaluate clustering using silhouette score.

        Args:
            features: Feature matrix used for clustering
            labels: Cluster labels

        Returns:
            Silhouette score, or -1 if evaluation fails
        """
        try:
            if len(set(labels)) > 1:
                score = silhouette_score(features, labels)
                return float(score)
        except Exception as e:
            logger.warning(f"Clustering evaluation failed: {e}")
            return -1.0
        return -1.0

    @staticmethod
    def analyze_clusters(
        cluster_labels: np.ndarray,
        metadata: DataFrame,
        top_n: int = 5,
        imbalance_threshold: float = 0.3,
    ) -> tuple[DataFrame, list[str], list[str]]:
        """
        Analyze cluster characteristics and identify distinguishing features.

        Args:
            cluster_labels: Cluster assignments for each sample
            metadata: Metadata dataframe with sample information
            top_n: Number of top features to return
            imbalance_threshold: Threshold for categorical feature imbalance

        Returns:
            Tuple of (cluster_summary, top_numeric_features, top_categorical_features)
        """
        metadata_copy = metadata.copy()
        metadata_copy["Cluster"] = cluster_labels

        numeric_cols = metadata_copy.select_dtypes(include="number").columns.drop("Cluster", errors="ignore")
        categorical_cols = metadata_copy.select_dtypes(exclude="number").columns

        grouped = metadata_copy.groupby("Cluster")
        numeric_summary = grouped[numeric_cols].mean().round(2)

        categorical_summary = pd.DataFrame()
        max_imbalances = {}

        for col in categorical_cols:
            proportions = grouped[col].value_counts(normalize=True).unstack().fillna(0)
            proportions.columns = pd.Index([f"{col}={val}" for val in proportions.columns])
            max_diff = proportions.max() - proportions.min()
            max_imbalances[col] = max_diff.max()
            proportions = proportions.round(2)
            categorical_summary = pd.concat([categorical_summary, proportions], axis=1)

        summary = pd.concat([numeric_summary, categorical_summary], axis=1)

        # Get top numeric features by standard deviation
        top_numeric = numeric_summary.std().sort_values(ascending=False).head(top_n).index.tolist()

        # Get top categorical features by imbalance
        top_categorical = [col for col, diff in max_imbalances.items() if diff > imbalance_threshold]
        top_categorical = sorted(top_categorical, key=lambda x: max_imbalances[x], reverse=True)[:top_n]

        return summary, top_numeric, top_categorical

    @staticmethod
    def run_clustering_analysis(
        data_matrix: DataFrame,
        selected_metadata: list[str],
        glycans: Optional[list[str]] = None,
        feature_prefix: str = "FT-",
    ) -> dict[str, Any]:
        """
        Run complete clustering analysis with multiple algorithms.

        Args:
            data_matrix: Complete data matrix with features and metadata
            selected_metadata: List of metadata column names
            glycans: List of glycan feature names (if None, uses feature_prefix)
            feature_prefix: Prefix to identify feature columns

        Returns:
            Dictionary containing clustering results and metadata
        """
        if glycans is not None:
            sig_glycans_refined = glycans
        else:
            sig_glycans_refined = [col for col in data_matrix.columns if col.startswith(feature_prefix)]

        if not sig_glycans_refined:
            raise ClusteringError("No features found matching the criteria")

        features = data_matrix[sig_glycans_refined]
        metadata = data_matrix[selected_metadata]

        # Run different clustering algorithms
        kmeans_labels, _ = ClusterAnalyzer.run_kmeans(features, min_k=3, max_k=10)
        dbscan_labels, _ = ClusterAnalyzer.run_dbscan(features, eps=0.5, min_samples=2)
        agglo_labels, _ = ClusterAnalyzer.run_agglomerative_auto(features, min_clusters=3, max_clusters=10)

        # Evaluate clustering quality
        logger.info(f"KMeans Silhouette: {ClusterAnalyzer.evaluate_clustering(features, kmeans_labels):.3f}")
        logger.info(f"DBSCAN Silhouette: {ClusterAnalyzer.evaluate_clustering(features, dbscan_labels):.3f}")
        logger.info(f"Agglomerative Silhouette: {ClusterAnalyzer.evaluate_clustering(features, agglo_labels):.3f}")

        return {
            "features": features,
            "metadata": metadata,
            "kmeans_labels": kmeans_labels,
            "dbscan_labels": dbscan_labels,
            "agglo_labels": agglo_labels,
        }


class ModelTrainer:
    """Handles model training, hyperparameter tuning, and evaluation."""

    DEFAULT_BASE_MODELS: ClassVar[dict[str, BaseEstimator]] = {
        "rf": RandomForestClassifier(random_state=42),
        "svm": SVC(probability=True, random_state=42),
        "lr": LogisticRegression(random_state=42, max_iter=10000),
    }

    DEFAULT_SCORING: ClassVar[dict[str, str]] = {
        "roc_auc": "roc_auc",
        "precision": make_scorer(precision_score, zero_division=0),
        "recall": make_scorer(recall_score, zero_division=0),
        "accuracy": "accuracy",
        "f1": make_scorer(f1_score, zero_division=0),
    }

    MODEL_NAME_MAP: ClassVar[dict[str, str]] = {
        "Random Forest": "rf",
        "SVM": "svm",
        "Logistic Regression": "lr",
    }

    @staticmethod
    def create_cv_splits(
        X: DataFrame,
        y: Series,
        n_splits: int = 3,
        random_state: int = 42,
    ) -> list[tuple[np.ndarray, np.ndarray]]:
        """
        Create cross-validation splits using stratified k-fold.

        Args:
            X: Feature matrix
            y: Target variable
            n_splits: Number of CV folds
            random_state: Random state for reproducibility

        Returns:
            List of (train_indices, test_indices) tuples

        Raises:
            ValueError: If there's only one class in the target variable
        """
        # Check if there's only one class
        if len(y.unique()) < 2:
            raise ValueError("The least populated class in y has only 1 member, which is less than n_splits=3.")

        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        return list(cv.split(X, y))

    @staticmethod
    def tune_model_parameters(
        X: DataFrame,
        y: Series,
        model_type: str,
        cv_splits: list[tuple[np.ndarray, np.ndarray]],
        random_state: int = 42,
        params: Optional[dict[str, Any]] = None,
    ) -> tuple[Pipeline, dict[str, Any], dict[str, Any], int, float]:
        """
        Tune model hyperparameters using randomized search.

        Args:
            X: Feature matrix
            y: Target variable
            model_type: Type of model ('rf', 'svm', 'lr')
            cv_splits: Cross-validation splits
            random_state: Random state for reproducibility
            params: Dictionary containing model parameters

        Returns:
            Tuple of (best_estimator, best_params, cv_results, best_index, best_score)
        """
        if params is None:
            params = {}

        base_models = params.get("base_models", ModelTrainer.DEFAULT_BASE_MODELS)
        scoring = params.get("scoring", ModelTrainer.DEFAULT_SCORING)

        if model_type not in base_models:
            raise ModelTrainingError(f"Model type '{model_type}' not supported")

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("model", base_models[model_type]),
        ])

        param_grid = params.get("param_grids", {}).get(model_type, {})
        pipeline_param_grid = {f"model__{key}": value for key, value in param_grid.items()}

        random_search_params = params.get(
            "random_search_params",
            {
                "n_iter": 20,
                "n_jobs": -1,
                "verbose": 0,
                "refit": "roc_auc",  # Specify which metric to use for refitting
                "return_train_score": True,  # Return training scores for analysis
            },
        )

        random_search = RandomizedSearchCV(
            pipeline,
            pipeline_param_grid,
            cv=cv_splits,
            scoring=scoring,
            random_state=random_state,
            **random_search_params,
        )

        random_search.fit(X, y)

        return (
            random_search.best_estimator_,
            random_search.best_params_,
            random_search.cv_results_,
            int(random_search.best_index_),
            random_search.best_score_,
        )

    @staticmethod
    def _extract_fold_metrics(
        model_cv_results: dict[str, Any],
        best_idx: int,
        fold_idx: int,
    ) -> dict[str, float]:
        """Extract metrics for a specific fold."""
        return {
            "accuracy": model_cv_results[f"split{fold_idx}_test_accuracy"][best_idx],
            "precision": model_cv_results[f"split{fold_idx}_test_precision"][best_idx],
            "recall": model_cv_results[f"split{fold_idx}_test_recall"][best_idx],
            "f1": model_cv_results[f"split{fold_idx}_test_f1"][best_idx],
            "roc_auc": model_cv_results[f"split{fold_idx}_test_roc_auc"][best_idx],
        }

    @staticmethod
    def _calculate_optimal_threshold(y_true: Series, y_prob: np.ndarray) -> float:
        """Calculate optimal classification threshold using ROC curve."""
        fpr, tpr, thresholds = roc_curve(y_true, y_prob[:, 1])
        j_scores = tpr - fpr
        j_best_idx = j_scores.argmax()
        return float(thresholds[j_best_idx])

    @staticmethod
    def _create_model_metrics(
        model_name: str,
        best_score: float,
        model_cv_results: dict[str, Any],
        best_idx: int,
        best_params: dict[str, Any],
        features: list[str],
        model: Pipeline,
    ) -> dict[str, Any]:
        """Create comprehensive metrics dictionary for a model."""
        metrics = {
            "Model": model_name,
            "Best AUC Score": f"{best_score:.3f}",
            "Accuracy": (
                f"{model_cv_results['mean_test_accuracy'][best_idx]:.3f} ± "
                f"{model_cv_results['std_test_accuracy'][best_idx]:.3f}"
            ),
            "Precision": (
                f"{model_cv_results['mean_test_precision'][best_idx]:.3f} ± "
                f"{model_cv_results['std_test_precision'][best_idx]:.3f}"
            ),
            "Recall": (
                f"{model_cv_results['mean_test_recall'][best_idx]:.3f} ± "
                f"{model_cv_results['std_test_recall'][best_idx]:.3f}"
            ),
            "F1 Score": (
                f"{model_cv_results['mean_test_f1'][best_idx]:.3f} ± {model_cv_results['std_test_f1'][best_idx]:.3f}"
            ),
            "ROC AUC": (
                f"{model_cv_results['mean_test_roc_auc'][best_idx]:.3f} ± "
                f"{model_cv_results['std_test_roc_auc'][best_idx]:.3f}"
            ),
            "Train-Test AUC": f"{model_cv_results.get('mean_train_roc_auc', [0])[best_idx] - model_cv_results['mean_test_roc_auc'][best_idx]:.3f}",
            "Best Parameters": best_params,
        }

        # Add feature importances for Random Forest
        if model_name == "Random Forest":
            feature_imp = pd.DataFrame({
                "feature": features,
                "importance": model.named_steps["model"].feature_importances_,
            }).sort_values("importance", ascending=False)
            metrics["Feature Importances"] = feature_imp  # type: ignore[assignment]
        return metrics

    @staticmethod
    def train_evaluate_models(
        X: DataFrame,
        y: Series,
        features: list[str],
        models_to_evaluate: Optional[list[str]] = None,
        params: Optional[dict[str, Any]] = None,
        n_splits: int = 3,
        random_state: int = 42,
    ) -> dict[str, Any]:
        """
        Train and evaluate multiple models with cross-validation.

        Args:
            X: Feature matrix
            y: Target variable
            features: List of feature names to use
            models_to_evaluate: List of model names to evaluate
            params: Model parameters dictionary
            n_splits: Number of CV folds
            random_state: Random state for reproducibility

        Returns:
            Dictionary containing training results and model information
        """
        if models_to_evaluate is None:
            models_to_evaluate = ["Random Forest", "SVM", "Logistic Regression"]

        if params is None:
            params = {}

        X_selected = X[features]
        cv_splits = ModelTrainer.create_cv_splits(X_selected, y, n_splits, random_state)

        models = {}
        best_params = {}
        cv_results = {}
        best_idxs = {}
        best_scores = {}

        for model_name in models_to_evaluate:
            if model_name not in ModelTrainer.MODEL_NAME_MAP:
                raise ModelTrainingError(f"Model {model_name} not supported")

            logger.info(f"Tuning {model_name}...")

            try:
                model, params_result, cv_result, best_idx, best_score = ModelTrainer.tune_model_parameters(
                    X_selected,
                    y,
                    ModelTrainer.MODEL_NAME_MAP[model_name],
                    cv_splits,
                    random_state,
                    params=params,
                )
                models[model_name] = model
                best_params[model_name] = params_result
                cv_results[model_name] = cv_result
                best_idxs[model_name] = best_idx
                best_scores[model_name] = best_score
            except Exception:
                logger.exception("Failed to train %s", model_name)
                continue

        results = []
        fold_data: dict[str, list[dict[str, Any]]] = {}
        best_fold_metrics: Optional[dict[str, float]] = None
        best_fold_idx: Optional[int] = None

        for name, model in models.items():
            model_cv_results = cv_results[name]
            best_idx = best_idxs[name]

            metrics = ModelTrainer._create_model_metrics(
                name, best_scores[name], model_cv_results, best_idx, best_params[name], features, model
            )

            fold_predictions = []
            for i, (_train_idx, test_idx) in enumerate(cv_splits):
                y_true = y.iloc[test_idx]
                y_prob = model.predict_proba(X_selected.iloc[test_idx])

                best_threshold = ModelTrainer._calculate_optimal_threshold(y_true, y_prob)
                y_pred = (y_prob[:, 1] >= best_threshold).astype(int)

                fold_metrics = ModelTrainer._extract_fold_metrics(model_cv_results, best_idx, i)

                if best_fold_metrics is None or fold_metrics["roc_auc"] > best_fold_metrics["roc_auc"]:
                    best_fold_idx = i
                    best_fold_metrics = fold_metrics

                fold_data_dict = {
                    "y_true": y_true,
                    "y_prob": y_prob,
                    "y_pred": y_pred,
                    "metrics": fold_metrics,
                    "estimator": model,
                    "fold_idx": i,
                    "threshold": best_threshold,
                }

                fold_predictions.append(fold_data_dict)

            fold_data[name] = fold_predictions
            results.append(metrics)

        results_df = pd.DataFrame(results)
        best_model = "Logistic Regression"  # Default best model

        return {
            "model_results": results_df,
            "fitted_models": models,
            "best_params": best_params,
            "fold_data": fold_data,
            "best_model": best_model,
            "best_fold_idx": best_fold_idx,
        }

    @staticmethod
    def analyze_best_models(fold_data: dict[str, list[dict[str, Any]]], fold_idx: int = 0) -> dict[str, dict[str, Any]]:
        """
        Analyze performance of best models for a specific fold.

        Args:
            fold_data: Dictionary containing fold predictions for each model
            fold_idx: Index of the fold to analyze

        Returns:
            Dictionary containing detailed analysis results for each model
        """
        detailed_results = {}

        for model_name, folds in fold_data.items():
            if fold_idx >= len(folds):
                logger.warning(f"Fold {fold_idx} not available for {model_name}")
                continue

            fold = folds[fold_idx]
            y_true = fold["y_true"]
            y_pred = fold["y_pred"]

            try:
                report = classification_report(y_true, y_pred, output_dict=True)

                detailed_results[model_name] = {
                    "Classification Report": pd.DataFrame(report).transpose(),
                    "Confusion Matrix": confusion_matrix(y_true, y_pred),
                }
            except Exception:
                logger.exception("Failed to analyze %s", model_name)
                continue

        return detailed_results

    @staticmethod
    def run_modeling(
        data: DataFrame,
        features: list[str],
        target_class: str = "Lung Cancer",
        class_column: str = "class_final",
        models: Optional[list[str]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> tuple[dict[str, dict[str, Any]], dict[str, Any], str]:
        """
        Main function for running complete modeling pipeline.

        Args:
            data: Input data containing features and class labels
            features: List of feature names to use
            target_class: Target class to predict
            class_column: Name of the column containing class labels
            models: List of model names to evaluate
            params: Model parameters dictionary

        Returns:
            Tuple of (detailed_results, training_results, best_model_name)
        """
        if class_column not in data.columns:
            raise ModelTrainingError(f"Class column '{class_column}' not found in data")

        if not features:
            raise ModelTrainingError("No features provided")

        missing_features = [f for f in features if f not in data.columns]
        if missing_features:
            raise ModelTrainingError(f"Missing features: {missing_features}")

        X = data.drop([class_column], axis=1)
        y = (data[class_column] == target_class).astype(int)

        if y.sum() == 0 or y.sum() == len(y):
            raise ModelTrainingError(f"Target class '{target_class}' not found or all samples have same class")

        # Train and evaluate models with parameter tuning
        results = ModelTrainer.train_evaluate_models(X, y, features, models_to_evaluate=models, params=params)

        # Print comprehensive results
        logger.info("\nModel Performance Metrics:")
        logger.info(results["model_results"])

        best_model = results["best_model"]

        # Analyze best models
        logger.info("\nDetailed Analysis of Best Models:")

        detailed_results = ModelTrainer.analyze_best_models(results["fold_data"], fold_idx=results["best_fold_idx"])

        return detailed_results, results, best_model
