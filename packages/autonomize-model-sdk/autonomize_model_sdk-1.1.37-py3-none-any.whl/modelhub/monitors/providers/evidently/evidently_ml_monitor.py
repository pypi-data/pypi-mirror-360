"""Implementation of model monitoring using Evidently."""

import os
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from evidently import ColumnMapping
from evidently.metric_preset import (
    ClassificationPreset,
    DataDriftPreset,
    DataQualityPreset,
    RegressionPreset,
    TargetDriftPreset,
)
from evidently.metrics import ColumnDriftMetric
from evidently.report import Report

from ....utils import setup_logger
from ...interfaces.model_monitor_interface import ModelMonitorInterface

logger = setup_logger(__name__)


class EvidentlyModelMonitor(ModelMonitorInterface):
    """Implementation of model monitoring using Evidently."""

    REPORT_TYPES = {
        "data_drift": DataDriftPreset,
        "data_quality": DataQualityPreset,
        "target_drift": TargetDriftPreset,
        "regression": RegressionPreset,
        "classification": ClassificationPreset,
    }

    def __init__(self, mlflow_client=None):
        """
        Initialize the EvidentlyModelMonitor.

        Args:
            mlflow_client: MLflowClient instance for logging metrics
        """
        self.mlflow_client = mlflow_client

    def create_column_mapping(
        self,
        target: Optional[str] = None,
        prediction: Optional[str] = None,
        numerical_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        datetime_features: Optional[List[str]] = None,
    ) -> ColumnMapping:
        """
        Create a column mapping for Evidently.

        Args:
            target: The target column name
            prediction: The prediction column name
            numerical_features: List of numerical feature columns
            categorical_features: List of categorical feature columns
            datetime_features: List of datetime feature columns

        Returns:
            ColumnMapping: An Evidently column mapping configuration
        """
        return ColumnMapping(
            target=target,
            prediction=prediction,
            numerical_features=numerical_features or [],
            categorical_features=categorical_features or [],
            datetime_features=datetime_features or [],
        )

    def _infer_column_types(self, reference_data: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Automatically infer column types from a DataFrame.

        Args:
            reference_data: The DataFrame to analyze

        Returns:
            Dictionary with categorized column lists
        """
        column_types = {
            "numerical_features": [],
            "categorical_features": [],
            "datetime_features": [],
        }

        for column in reference_data.columns:
            dtype = reference_data[column].dtype
            if pd.api.types.is_numeric_dtype(dtype):
                # Check if it might actually be categorical
                if reference_data[column].nunique() < 10:
                    column_types["categorical_features"].append(column)
                else:
                    column_types["numerical_features"].append(column)
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                column_types["datetime_features"].append(column)
            else:
                column_types["categorical_features"].append(column)

        logger.info("Inferred column types: %s", column_types)
        return column_types

    def _get_column_mapping(
        self,
        reference_data: pd.DataFrame,
        target_column: Optional[str] = None,
        prediction_column: Optional[str] = None,
        column_mapping: Optional[ColumnMapping] = None,
    ) -> ColumnMapping:
        """
        Get column mapping from parameters or infer from data.

        Args:
            reference_data: Reference dataset
            target_column: Target column name
            prediction_column: Prediction column name
            column_mapping: Explicit column mapping, if provided

        Returns:
            A complete column mapping
        """
        if column_mapping is not None:
            return column_mapping

        column_types = self._infer_column_types(reference_data)
        return self.create_column_mapping(
            target=target_column,
            prediction=prediction_column,
            numerical_features=column_types["numerical_features"],
            categorical_features=column_types["categorical_features"],
            datetime_features=column_types["datetime_features"],
        )

    def _create_report(
        self,
        report_type: str,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        column_mapping: ColumnMapping,
        **kwargs,
    ) -> Report:
        """
        Create a report of the specified type.

        Args:
            report_type: Type of report to create
            reference_data: Reference dataset
            current_data: Current dataset
            column_mapping: Column mapping
            **kwargs: Additional parameters for specific report types

        Returns:
            Evidently Report object
        """
        if report_type == "column_drift" and "column_name" in kwargs:
            column_name = kwargs["column_name"]
            if (
                column_name not in reference_data.columns
                or column_name not in current_data.columns
            ):
                raise ValueError(
                    f"Column '{column_name}' not found in one or both datasets"
                )
            report = Report(metrics=[ColumnDriftMetric(column_name=column_name)])
        elif report_type in self.REPORT_TYPES:
            report = Report(metrics=[self.REPORT_TYPES[report_type]()])
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        report.run(
            reference_data=reference_data,
            current_data=current_data,
            column_mapping=column_mapping if report_type != "column_drift" else None,
        )

        return report

    def generate_report(
        self,
        report_type: str,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        target_column: Optional[str] = None,
        prediction_column: Optional[str] = None,
        column_mapping: Optional[ColumnMapping] = None,
        column_name: Optional[str] = None,
        save_json: bool = False,
        output_path: str = "./reports",
        log_to_mlflow: bool = False,
        artifact_path: str = "reports",
        report_name: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> Tuple[Optional[Report], Dict[str, Any], Optional[str]]:
        """
        Generate a report and extract metrics for a specific analysis type.

        Args:
            report_type: Type of report to generate
            reference_data: Reference dataset
            current_data: Current dataset
            target_column: Target column name
            prediction_column: Prediction column name
            column_mapping: Column mapping specification
            column_name: Column name for column drift reports
            save_json: Whether to save the JSON report
            output_path: Output directory for reports
            log_to_mlflow: Whether to log report to MLflow
            artifact_path: MLflow artifact path
            report_name: Custom name for the report
            run_id: MLflow run ID

        Returns:
            Tuple containing:
            - Report object
            - Dictionary of metrics
            - Path to the saved HTML report (if saved)
        """
        # Validate inputs
        if report_type == "column_drift" and not column_name:
            raise ValueError("column_name must be provided for column_drift report")

        if report_type in ["regression", "classification"] and (
            not target_column or not prediction_column
        ):
            raise ValueError(
                f"target_column and prediction_column must be provided for {report_type} report"
            )

        # Get column mapping
        final_column_mapping = self._get_column_mapping(
            reference_data, target_column, prediction_column, column_mapping
        )

        # Create kwargs for report creation
        create_kwargs = {}
        if report_type == "column_drift":
            create_kwargs["column_name"] = column_name

        # Create report
        try:
            report = self._create_report(
                report_type,
                reference_data,
                current_data,
                final_column_mapping,
                **create_kwargs,
            )

            # Extract metrics
            metrics = self._extract_metrics(report, report_type, **create_kwargs)

            # Save report if requested
            html_path = None
            if save_json or report_name or log_to_mlflow:
                # Create output directory
                os.makedirs(output_path, exist_ok=True)

                # Generate report name if not provided
                if not report_name:
                    from datetime import datetime

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    if report_type == "column_drift" and column_name:
                        report_name = f"{report_type}_{column_name}_{timestamp}"
                    else:
                        report_name = f"{report_type}_{timestamp}"

                # Save report to local filesystem
                if save_json:
                    json_path = os.path.join(output_path, f"{report_name}.json")
                    report.save_json(json_path)
                    logger.info("Report saved to %s", json_path)

                # Create HTML path
                html_path = os.path.join(output_path, f"{report_name}.html")
                report.save_html(html_path)
                logger.info("Report saved to %s", html_path)

                # Log to MLflow if requested
                if log_to_mlflow:
                    self.log_report(report, report_name, artifact_path, run_id)

            return report, metrics, html_path

        except ValueError as e:
            logger.error("Value error generating %s report: %s", report_type, str(e))
            return None, {}, None
        except TypeError as e:
            logger.error("Type error generating %s report: %s", report_type, str(e))
            return None, {}, None
        except ImportError as e:
            logger.error("Import error generating %s report: %s", report_type, str(e))
            return None, {}, None
        except RuntimeError as e:
            logger.error("Runtime error generating %s report: %s", report_type, str(e))
            return None, {}, None

    def log_report(
        self,
        report: Any,  # Evidently Report object
        report_name: str,
        artifact_path: str = "reports",
        run_id: Optional[str] = None,
    ) -> None:
        """
        Log Evidently report as MLflow artifact.

        Args:
            report: Evidently report object
            report_name: Name for the report file (without extension)
            artifact_path: Path for MLflow artifacts folder
            run_id: Optional MLflow run ID
        """
        if self.mlflow_client is None:
            raise ValueError("MLflow client is not initialized")

        # Create a temporary directory
        import shutil
        import tempfile

        temp_dir = tempfile.mkdtemp()
        try:
            # Save report as HTML with custom filename
            html_path = os.path.join(temp_dir, f"{report_name}.html")
            report.save_html(html_path)

            # Save report as JSON with custom filename
            json_path = os.path.join(temp_dir, f"{report_name}.json")
            report.save_json(json_path)

            # Log HTML file to MLflow
            self.mlflow_client.log_artifact(html_path, artifact_path, run_id=run_id)

            # Log JSON file to MLflow
            self.mlflow_client.log_artifact(json_path, artifact_path, run_id=run_id)

            logger.info(
                "Report '%s' logged to MLflow in '%s'", report_name, artifact_path
            )
        except (ValueError, IOError, RuntimeError) as e:
            logger.error("Error logging report to MLflow: %s", str(e))
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)

    def _extract_metrics(
        self, report: Report, report_type: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Extract metrics from an Evidently report.

        Args:
            report: The report to extract metrics from
            report_type: Type of report
            **kwargs: Additional parameters for specific metric extraction

        Returns:
            Dictionary of metrics
        """
        report_dict = report.as_dict()

        # Use dispatch dict pattern instead of if-elif chain
        extractors = {
            "data_drift": self._extract_data_drift_metrics,
            "regression": self._extract_regression_metrics,
            "classification": self._extract_classification_metrics,
            "data_quality": self._extract_quality_metrics,
            "target_drift": self._extract_target_drift_metrics,
        }

        # Handle special case for column_drift
        if report_type == "column_drift" and "column_name" in kwargs:
            return self._extract_column_drift_metrics(
                report_dict, kwargs["column_name"]
            )

        # Use dictionary dispatch for other report types
        if report_type in extractors:
            return extractors[report_type](report_dict)

        # Default case
        logger.warning("No specific extraction method for report type %s", report_type)
        return {"report_type": report_type}

    def _extract_data_drift_metrics(
        self, report_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract metrics from a data drift report."""
        drift_metrics = {}

        if len(report_dict["metrics"]) > 0 and "result" in report_dict["metrics"][0]:
            result = report_dict["metrics"][0]["result"]

            # Extract basic drift metrics if available
            drift_metrics["data_drift_share"] = result.get(
                "share_of_drifted_columns", 0
            )
            drift_metrics["number_of_columns"] = result.get("number_of_columns", 0)
            drift_metrics["number_of_drifted_columns"] = result.get(
                "number_of_drifted_columns", 0
            )

            # Add column-level drift information if available
            column_metrics = {}

            # Check available metrics in different formats
            if "drift_by_columns" in result:
                for column_result in result["drift_by_columns"]:
                    column_name = column_result["column_name"]
                    column_metrics[column_name] = {
                        "drift_detected": column_result.get("drift_detected", False),
                        "drift_score": column_result.get("drift_score"),
                        "column_type": column_result.get("column_type"),
                    }
            elif "column_drift_metrics" in result:
                for column_result in result["column_drift_metrics"]:
                    column_name = column_result.get("column_name", "unknown")
                    column_metrics[column_name] = {
                        "drift_detected": column_result.get("drift_detected", False),
                        "drift_score": column_result.get("drift_score"),
                        "column_type": column_result.get("column_type"),
                    }
            else:
                # Log what keys are available for debugging
                logger.debug("Available keys in result: %s", list(result.keys()))

                # Try to extract column-specific drift information from any available keys
                for key, value in result.items():
                    if isinstance(value, dict) and "drift_detected" in value:
                        column_metrics[key] = {
                            "drift_detected": value.get("drift_detected", False),
                            "drift_score": value.get("drift_score"),
                            "column_type": value.get("column_type", "unknown"),
                        }

            drift_metrics["columns"] = column_metrics

        # If we couldn't extract the metrics with the expected structure,
        # store the entire result for analysis
        if not drift_metrics:
            logger.warning("Could not extract drift metrics with expected structure")
            drift_metrics["raw_result"] = report_dict

        return drift_metrics

    def _extract_regression_metrics(
        self, report_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract metrics from a regression report."""
        metrics_dict = {}

        # Parse metrics from the report JSON
        for metric in report_dict["metrics"]:
            for key, value in metric["result"].items():
                if key != "metrics_matrix":  # Skip the metrics matrix
                    metrics_dict[key] = value

        # Extract common regression metrics
        regression_metrics = {
            "mean_absolute_error": metrics_dict.get("mean_abs_error"),
            "mean_squared_error": metrics_dict.get("mean_sqr_error"),
            "root_mean_squared_error": metrics_dict.get("rmse"),
            "mean_absolute_percentage_error": metrics_dict.get("mean_abs_perc_error"),
            "r2_score": metrics_dict.get("r2_score"),
        }

        return regression_metrics

    def _extract_classification_metrics(
        self, report_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract metrics from a classification report."""
        metrics_dict = {}

        # Parse metrics from the report JSON
        for metric in report_dict["metrics"]:
            metric_results = metric["result"]
            # For overall metrics
            for key, value in metric_results.items():
                if key not in ["class_metrics", "confusion_matrix"]:
                    metrics_dict[key] = value

        # Extract common classification metrics
        classification_metrics = {
            "accuracy": metrics_dict.get("accuracy"),
            "precision": metrics_dict.get("precision"),
            "recall": metrics_dict.get("recall"),
            "f1_score": metrics_dict.get("f1"),
            "roc_auc": metrics_dict.get("roc_auc"),
        }

        return classification_metrics

    def _extract_quality_metrics(self, report_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics from a data quality report."""
        quality_metrics = {}

        # Process DataQualityPreset results
        for metric in report_dict["metrics"]:
            if metric["metric"] == "DataQualityPreset":
                self._extract_quality_preset_metrics(metric, quality_metrics)
            elif metric["metric"] == "DatasetMissingValuesMetric":
                self._extract_missing_values_metrics(metric, quality_metrics)

        return quality_metrics

    def _extract_quality_preset_metrics(
        self, metric: Dict[str, Any], quality_metrics: Dict[str, Any]
    ) -> None:
        """Extract quality preset metrics from a metric dictionary."""
        # Extract overall quality score if available
        if "current" in metric["result"]:
            quality_metrics["current_quality_score"] = metric["result"]["current"].get(
                "quality_score"
            )

        if "reference" in metric["result"]:
            quality_metrics["reference_quality_score"] = metric["result"][
                "reference"
            ].get("quality_score")

        # Extract detailed metrics
        for section in ["reference", "current"]:
            if section in metric["result"]:
                prefix = f"{section}_"
                section_data = metric["result"][section]

                # Extract various quality metrics
                quality_metrics[f"{prefix}missing_values"] = section_data.get(
                    "missing_values", 0
                )
                quality_metrics[f"{prefix}duplicate_rows"] = section_data.get(
                    "duplicate_rows", 0
                )

                # Extract column-level metrics
                self._extract_column_metrics(section_data, section, quality_metrics)

    def _extract_column_metrics(
        self,
        section_data: Dict[str, Any],
        section: str,
        quality_metrics: Dict[str, Any],
    ) -> None:
        """Extract column-level metrics from section data."""
        if "column_metrics" in section_data:
            prefix = f"{section}_"
            for col_name, col_data in section_data["column_metrics"].items():
                col_prefix = f"{prefix}column.{col_name}."
                for metric_name, metric_value in col_data.items():
                    if isinstance(metric_value, (int, float, bool)):
                        quality_metrics[f"{col_prefix}{metric_name}"] = metric_value

    def _extract_missing_values_metrics(
        self, metric: Dict[str, Any], quality_metrics: Dict[str, Any]
    ) -> None:
        """Extract missing values metrics from a metric dictionary."""
        if "current" in metric["result"]:
            quality_metrics["current_missing_cells"] = metric["result"]["current"].get(
                "missing_cells", 0
            )
            quality_metrics["current_missing_cells_ratio"] = metric["result"][
                "current"
            ].get("missing_cells_ratio", 0)

        if "reference" in metric["result"]:
            quality_metrics["reference_missing_cells"] = metric["result"][
                "reference"
            ].get("missing_cells", 0)
            quality_metrics["reference_missing_cells_ratio"] = metric["result"][
                "reference"
            ].get("missing_cells_ratio", 0)

    def _extract_target_drift_metrics(
        self, report_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract metrics from a target drift report."""
        target_drift_metrics = {}

        for metric in report_dict["metrics"]:
            # Assuming the first metric is the target drift preset
            if "target_drift" in metric["result"]:
                target_drift = metric["result"]["target_drift"]
                target_drift_metrics = {
                    "drift_detected": target_drift.get("drift_detected", False),
                    "drift_score": target_drift.get("drift_score"),
                    "stattest_name": target_drift.get("stattest_name"),
                    "p_value": target_drift.get("p_value"),
                    "threshold": target_drift.get("threshold"),
                }
                break

        return target_drift_metrics

    def _extract_column_drift_metrics(
        self, report_dict: Dict[str, Any], column_name: str
    ) -> Dict[str, Any]:
        """Extract metrics from a column drift report."""
        column_drift_metrics = {}

        for metric in report_dict["metrics"]:
            if metric["metric"] == "ColumnDriftMetric":
                column_drift_metrics = {
                    "column_name": column_name,
                    "drift_detected": metric["result"].get("drift_detected", False),
                    "column_type": metric["result"].get("column_type"),
                    "stattest_name": metric["result"].get("stattest_name"),
                    "stattest_threshold": metric["result"].get("threshold"),
                    "drift_score": metric["result"].get("drift_score"),
                    "p_value": metric["result"].get("p_value"),
                }

                # Add distribution details if available
                if "current_small_distribution" in metric["result"]:
                    column_drift_metrics["current_distribution"] = metric["result"][
                        "current_small_distribution"
                    ]
                if "reference_small_distribution" in metric["result"]:
                    column_drift_metrics["reference_distribution"] = metric["result"][
                        "reference_small_distribution"
                    ]

        return column_drift_metrics

    def _flatten_metrics_for_mlflow(
        self, metrics: Dict[str, Any], prefix: str = "evidently."
    ) -> Dict[str, Any]:
        """
        Flatten nested metrics dictionaries for MLflow logging.

        Args:
            metrics: The metrics dictionary to flatten
            prefix: Prefix to add to all metric names

        Returns:
            Flattened metrics dictionary
        """
        flattened_metrics = {}

        def _flatten_dict_helper(d, parent_key=""):
            for key, value in d.items():
                if isinstance(value, dict):
                    _flatten_dict_helper(value, f"{parent_key}{key}" + ".")
                elif isinstance(value, (int, float, bool)) or value is None:
                    # Convert boolean to int for MLflow compatibility
                    if isinstance(value, bool):
                        value = int(value)
                    # Skip None values
                    if value is not None:
                        flattened_metrics[f"{parent_key}{key}"] = value

        _flatten_dict_helper(metrics, prefix)
        return flattened_metrics

    def log_metrics_to_mlflow(
        self, metrics: Dict[str, Any], run_id: Optional[str] = None
    ) -> bool:
        """
        Log Evidently metrics to MLflow.

        Args:
            metrics: Dictionary of metrics to log
            run_id: MLflow run ID. If not provided, uses active run

        Returns:
            bool: True if metrics were successfully logged

        Raises:
            ValueError: If no MLflow client is initialized or if metrics are invalid
        """
        if self.mlflow_client is None:
            raise ValueError("MLflow client is not initialized")

        logger.info("Logging %d metrics to MLflow", len(metrics))

        # Flatten nested dictionaries with dot notation
        flattened_metrics = self._flatten_metrics_for_mlflow(metrics)

        # Log metrics to MLflow
        for key, value in flattened_metrics.items():
            if isinstance(value, (int, float)):
                if run_id:
                    self.mlflow_client.mlflow.log_metric(
                        key=key, value=value, run_id=run_id
                    )
                else:
                    self.mlflow_client.log_metric(key=key, value=value)

        logger.info(
            "Successfully logged %d Evidently metrics to MLflow", len(flattened_metrics)
        )
        return True

    def run_and_log_reports(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        report_types: List[str],
        column_mapping: Optional[ColumnMapping] = None,
        target_column: Optional[str] = None,
        prediction_column: Optional[str] = None,
        report_prefix: str = "",
        output_path: str = "./reports",
        log_to_mlflow: bool = True,
        artifact_path: str = "reports",
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run multiple reports and log them to MLflow with a clean structure.

        Args:
            reference_data: Reference dataset
            current_data: Current dataset
            report_types: List of report types ('data_drift', 'data_quality', etc.)
            column_mapping: Column mapping for the datasets
            target_column: Name of the target column
            prediction_column: Name of the prediction column
            report_prefix: Prefix to add to report names
            output_path: Directory to save report files locally
            log_to_mlflow: Whether to log reports to MLflow
            artifact_path: Path for MLflow artifacts folder
            run_id: Optional MLflow run ID

        Returns:
            Dict[str, Any]: Dictionary with report paths and metrics
        """
        results = {"reports": {}, "metrics": {}}
        prefix = f"{report_prefix}_" if report_prefix else ""

        # Generate requested reports
        for report_type in report_types:
            report_name = f"{prefix}{report_type}"

            # Skip column_drift reports (they need column name)
            if report_type == "column_drift":
                logger.warning(
                    "Column drift reports must be generated individually with a column name"
                )
                continue

            # Generate report
            _, metrics, html_path = self.generate_report(
                report_type=report_type,
                reference_data=reference_data,
                current_data=current_data,
                target_column=target_column,
                prediction_column=prediction_column,
                column_mapping=column_mapping,
                save_json=True,
                output_path=output_path,
                log_to_mlflow=log_to_mlflow,
                artifact_path=artifact_path,
                report_name=report_name,
                run_id=run_id,
            )

            # Store results
            if metrics:
                results["metrics"][report_type] = metrics
            if html_path:
                results["reports"][report_type] = html_path

        return results

    def analyze_column_drift(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        column_name: str,
        save_json: bool = True,
        output_path: str = "./reports",
        log_to_mlflow: bool = True,
        artifact_path: str = "reports",
        report_prefix: str = "",
        run_id: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Analyze drift for a specific column.

        Args:
            reference_data: Reference dataset
            current_data: Current dataset
            column_name: Name of the column to analyze
            save_json: Whether to save JSON output
            output_path: Output directory path
            log_to_mlflow: Whether to log to MLflow
            artifact_path: MLflow artifact path
            report_prefix: Prefix for report name
            run_id: MLflow run ID

        Returns:
            Tuple containing metrics and HTML path
        """
        # Add a leading underscore to match expected test behavior
        prefix = f"{report_prefix}_" if report_prefix else "_"
        report_name = f"{prefix}column_drift_{column_name}"

        _, metrics, html_path = self.generate_report(
            report_type="column_drift",
            reference_data=reference_data,
            current_data=current_data,
            column_name=column_name,
            save_json=save_json,
            output_path=output_path,
            log_to_mlflow=log_to_mlflow,
            artifact_path=artifact_path,
            report_name=report_name,
            run_id=run_id,
        )

        return metrics, html_path

    def save_and_log_report(
        self,
        report: Any,  # Evidently Report object
        report_name: str,
        output_path: str = "./evidently_reports",
        log_to_mlflow: bool = True,
        artifact_path: str = "reports",
        run_id: Optional[str] = None,
    ) -> str:
        """
        Save report locally and log it to MLflow with a clean structure.

        Args:
            report: Evidently Report object
            report_name: Name for the report (without extension)
            output_path: Local directory to save reports
            log_to_mlflow: Whether to log the report to MLflow
            artifact_path: Path for MLflow artifacts folder
            run_id: Optional MLflow run ID

        Returns:
            str: Path to the saved HTML report
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

        # Save HTML report locally
        html_path = os.path.join(output_path, f"{report_name}.html")
        report.save_html(html_path)

        # Save JSON report locally
        json_path = os.path.join(output_path, f"{report_name}.json")
        report.save_json(json_path)

        logger.info("Report saved to: %s", html_path)

        # Log report to MLflow if requested
        if log_to_mlflow and self.mlflow_client is not None:
            try:
                self.log_report(report, report_name, artifact_path, run_id)
            except (ValueError, IOError, RuntimeError) as e:
                logger.warning("Failed to log report to MLflow: %s", str(e))

        return html_path
