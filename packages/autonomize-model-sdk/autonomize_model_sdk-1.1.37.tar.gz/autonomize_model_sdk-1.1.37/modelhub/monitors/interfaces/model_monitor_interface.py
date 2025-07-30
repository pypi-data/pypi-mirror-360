"""Interface for model monitoring functionality."""

from abc import abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .base_monitor import BaseMonitor


class ModelMonitorInterface(BaseMonitor):
    """Abstract interface for model monitoring implementations."""

    @abstractmethod
    def create_column_mapping(
        self,
        target: Optional[str] = None,
        prediction: Optional[str] = None,
        numerical_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        datetime_features: Optional[List[str]] = None,
    ) -> Any:
        """
        Create a column mapping for monitoring.

        Args:
            target: The target column name
            prediction: The prediction column name
            numerical_features: List of numerical feature columns
            categorical_features: List of categorical feature columns
            datetime_features: List of datetime feature columns

        Returns:
            Any: A column mapping configuration
        """

    @abstractmethod
    def generate_report(
        self,
        report_type: str,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        target_column: Optional[str] = None,
        prediction_column: Optional[str] = None,
        column_mapping: Optional[Any] = None,
        column_name: Optional[str] = None,
        save_json: bool = False,
        output_path: str = "./reports",
        log_to_mlflow: bool = False,
        artifact_path: str = "reports",
        report_name: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> Tuple[Optional[Any], Dict[str, Any], Optional[str]]:
        """
        Generate a monitoring report.

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

    @abstractmethod
    def run_and_log_reports(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        report_types: List[str],
        column_mapping: Optional[Any] = None,
        target_column: Optional[str] = None,
        prediction_column: Optional[str] = None,
        report_prefix: str = "",
        output_path: str = "./reports",
        log_to_mlflow: bool = True,
        artifact_path: str = "reports",
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run multiple reports and log them to MLflow.

        Args:
            reference_data: Reference dataset
            current_data: Current dataset
            report_types: List of report types
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

    @abstractmethod
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

    @abstractmethod
    def save_and_log_report(
        self,
        report: Any,
        report_name: str,
        output_path: str = "./reports",
        log_to_mlflow: bool = True,
        artifact_path: str = "reports",
        run_id: Optional[str] = None,
    ) -> str:
        """
        Save report locally and log it to MLflow.

        Args:
            report: Report object
            report_name: Name for the report (without extension)
            output_path: Local directory to save reports
            log_to_mlflow: Whether to log the report to MLflow
            artifact_path: Path for MLflow artifacts folder
            run_id: Optional MLflow run ID

        Returns:
            str: Path to the saved HTML report
        """
