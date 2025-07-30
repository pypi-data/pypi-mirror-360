"""Base monitor interface defining common functionality for all monitoring implementations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseMonitor(ABC):
    """Abstract base class for all monitoring implementations."""

    @abstractmethod
    def log_metrics_to_mlflow(
        self, metrics: Dict[str, Any], run_id: Optional[str] = None
    ) -> bool:
        """
        Log metrics to MLflow.

        Args:
            metrics: Dictionary of metrics to log
            run_id: Optional MLflow run ID

        Returns:
            bool: True if metrics were successfully logged
        """
