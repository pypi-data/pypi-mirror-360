"""Interface for LLM monitoring and evaluation functionality."""

from abc import abstractmethod
from typing import Any, Dict, List, Optional

import pandas as pd

from .base_monitor import BaseMonitor


class LLMMonitorInterface(BaseMonitor):
    """Abstract interface for LLM monitoring implementations."""

    @abstractmethod
    def create_column_mapping(
        self,
        datetime_col: Optional[str] = None,
        prompt_col: str = "prompt",
        response_col: str = "response",
        reference_col: Optional[str] = None,
        categorical_cols: Optional[List[str]] = None,
        datetime_cols: Optional[List[str]] = None,
        numerical_cols: Optional[List[str]] = None,
    ) -> Any:
        """
        Create a column mapping for LLM evaluation.

        Args:
            datetime_col: The datetime column for time-based analysis
            prompt_col: Column name for the prompt/question
            response_col: Column name for the model response
            reference_col: Column name for reference/golden response
            categorical_cols: List of categorical feature columns
            datetime_cols: List of datetime feature columns
            numerical_cols: List of numerical feature columns

        Returns:
            Any: Column mapping configuration
        """

    @abstractmethod
    def evaluate_text_length(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        reference_data: Optional[pd.DataFrame] = None,
        column_mapping: Optional[Any] = None,
        save_html: bool = False,
        output_path: str = "./reports",
    ) -> Any:
        """
        Evaluate text length metrics for LLM responses.

        Args:
            data: Dataset with LLM responses
            response_col: Column name containing model responses
            reference_data: Reference dataset for comparison
            column_mapping: Column mapping for the dataset
            save_html: Whether to save the report as HTML
            output_path: Directory to save report files

        Returns:
            Any: The report object
        """

    @abstractmethod
    def evaluate_content_patterns(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        words_to_check: Optional[List[str]] = None,
        patterns_to_check: Optional[List[str]] = None,
        prefix_to_check: Optional[str] = None,
        reference_data: Optional[pd.DataFrame] = None,
        column_mapping: Optional[Any] = None,
        save_html: bool = False,
        output_path: str = "./reports",
    ) -> Any:
        """
        Evaluate content patterns in LLM responses.

        Args:
            data: Dataset with LLM responses
            response_col: Column name containing model responses
            words_to_check: List of words to check for in responses
            patterns_to_check: List of patterns to check for in responses
            prefix_to_check: Prefix to check for in responses
            reference_data: Reference dataset for comparison
            column_mapping: Column mapping for the dataset
            save_html: Whether to save the report as HTML
            output_path: Directory to save report files

        Returns:
            Any: The report object
        """

    @abstractmethod
    def create_comparison_visualization(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        output_path: str = "./reports",
        response_col: str = "response",
        metrics: Optional[List[str]] = None,
        artifact_path: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> str:
        """
        Create visualizations comparing reference and current data.

        Args:
            reference_data: Reference dataset
            current_data: Current dataset
            output_path: Directory to save visualization files
            response_col: Column name containing the response text
            metrics: List of metrics to visualize
            artifact_path: MLflow artifact path for logging
            run_id: MLflow run ID

        Returns:
            str: Path to the saved visualization file
        """

    @abstractmethod
    def evaluate_semantic_properties(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        prompt_col: Optional[str] = "prompt",
        check_sentiment: bool = True,
        check_toxicity: bool = True,
        check_prompt_relevance: bool = True,
        huggingface_models: Optional[List[Dict[str, Any]]] = None,
        reference_data: Optional[pd.DataFrame] = None,
        column_mapping: Optional[Any] = None,
        save_html: bool = False,
        output_path: str = "./reports",
    ) -> Any:
        """
        Evaluate semantic properties of LLM responses.

        Args:
            data: Dataset with LLM responses
            response_col: Column name containing model responses
            prompt_col: Column name containing prompts/questions
            check_sentiment: Whether to check sentiment
            check_toxicity: Whether to check toxicity
            check_prompt_relevance: Whether to check prompt-response relevance
            huggingface_models: List of custom HuggingFace models to use
            reference_data: Reference dataset for comparison
            column_mapping: Column mapping for the dataset
            save_html: Whether to save the report as HTML
            output_path: Directory to save report files

        Returns:
            Any: The report object
        """

    @abstractmethod
    def evaluate_llm_as_judge(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        check_pii: bool = True,
        check_decline: bool = True,
        custom_evals: Optional[List[Dict[str, Any]]] = None,
        reference_data: Optional[pd.DataFrame] = None,
        column_mapping: Optional[Any] = None,
        save_html: bool = False,
        output_path: str = "./reports",
    ) -> Optional[Any]:
        """
        Evaluate LLM responses using LLM-as-judge.

        Args:
            data: Dataset with LLM responses
            response_col: Column name containing model responses
            check_pii: Whether to check for PII in responses
            check_decline: Whether to check if responses decline to answer
            custom_evals: List of custom evaluation criteria
            reference_data: Reference dataset for comparison
            column_mapping: Column mapping for the dataset
            save_html: Whether to save the report as HTML
            output_path: Directory to save report files

        Returns:
            Any: The report object or None if LLM judge is not available
        """

    @abstractmethod
    def generate_comparison_report(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        response_col: str = "response",
        category_col: Optional[str] = "category",
        metrics_cols: Optional[List[str]] = None,
        output_path: str = "./reports",
        report_name: str = "model_comparison_report.html",
        artifact_path: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> str:
        """
        Generate an HTML report comparing two datasets of LLM responses.

        Args:
            reference_data: Reference dataset
            current_data: Current dataset
            response_col: Column containing the text responses
            category_col: Column containing response categories
            metrics_cols: Additional numerical columns to include in comparison
            output_path: Directory to save the report
            report_name: Filename for the HTML report
            artifact_path: MLflow artifact path for logging
            run_id: MLflow run ID

        Returns:
            str: Path to the generated report
        """

    @abstractmethod
    def run_comprehensive_evaluation(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        prompt_col: Optional[str] = "prompt",
        reference_col: Optional[str] = None,
        categorical_cols: Optional[List[str]] = None,
        words_to_check: Optional[List[str]] = None,
        run_sentiment: bool = True,
        run_toxicity: bool = True,
        run_llm_judge: bool = False,
        reference_data: Optional[pd.DataFrame] = None,
        column_mapping: Optional[Any] = None,
        save_html: bool = False,
        output_path: str = "./reports",
        artifact_path: str = "llm_evaluation",
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run a comprehensive evaluation of LLM responses.

        Args:
            data: Dataset with LLM responses
            response_col: Column name containing model responses
            prompt_col: Column name containing prompts/questions
            reference_col: Column name containing reference responses
            categorical_cols: List of categorical feature columns
            words_to_check: List of words to check for in responses
            run_sentiment: Whether to check sentiment
            run_toxicity: Whether to check toxicity
            run_llm_judge: Whether to run LLM-as-judge
            reference_data: Reference dataset for comparison
            column_mapping: Column mapping for the dataset
            save_html: Whether to save the report as HTML
            output_path: Directory to save report files
            artifact_path: MLflow artifact path for logging
            run_id: MLflow run ID

        Returns:
            Dict[str, Any]: Dictionary with all evaluation reports
        """
