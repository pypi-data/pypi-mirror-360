"""Implementation of LLM monitoring and evaluation using Evidently."""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd
from evidently import ColumnMapping
from evidently.descriptors import (
    BeginsWith,
    Contains,
    HuggingFaceModel,
    HuggingFaceToxicityModel,
    IncludesWords,
    SemanticSimilarity,
    SentenceCount,
    Sentiment,
    TextLength,
    WordCount,
)
from evidently.metric_preset import TextEvals
from evidently.report import Report
from evidently.test_suite import TestSuite
from evidently.tests import TestColumnValueMax, TestColumnValueMean, TestColumnValueMin

# Optional LLM-as-judge features (requires OpenAI API key)
try:
    from evidently.descriptors import DeclineLLMEval, LLMEval, PIILLMEval
    from evidently.features.llm_judge import BinaryClassificationPromptTemplate

    LLM_JUDGE_AVAILABLE = True
except ImportError:
    LLM_JUDGE_AVAILABLE = False

from ....utils import setup_logger
from ...interfaces.llm_monitor_interface import LLMMonitorInterface

logger = setup_logger(__name__)


class EvidentlyLLMMonitor(LLMMonitorInterface):
    """Implementation of LLM monitoring using Evidently."""

    def __init__(self, mlflow_client=None, evidently_ml_monitor=None):
        """
        Initialize the EvidentlyLLMMonitor.

        Args:
            mlflow_client: MLflowClient instance for logging metrics (optional)
            evidently_ml_monitor: EvidentlyModelMonitor instance for logging metrics (optional)
                If not provided, a new one will be created if mlflow_client is provided
        """
        self.mlflow_client = mlflow_client
        from .evidently_ml_monitor import EvidentlyModelMonitor

        # Use the provided evidently_ml_monitor or create a new one if needed
        self.evidently_ml_monitor = evidently_ml_monitor or (
            EvidentlyModelMonitor(mlflow_client) if mlflow_client else None
        )

    def create_column_mapping(
        self,
        datetime_col: Optional[str] = None,
        prompt_col: str = "prompt",
        response_col: str = "response",
        reference_col: Optional[str] = None,
        categorical_cols: Optional[List[str]] = None,
        datetime_cols: Optional[List[str]] = None,
        numerical_cols: Optional[List[str]] = None,
    ) -> ColumnMapping:
        """
        Create a column mapping for Evidently.

        Args:
            datetime_col: The datetime column for time-based analysis
            prompt_col: Column name for the prompt/question
            response_col: Column name for the model response
            reference_col: Column name for reference/golden response
            categorical_cols: List of categorical feature columns
            datetime_cols: List of datetime feature columns
            numerical_cols: List of numerical feature columns

        Returns:
            ColumnMapping: An Evidently column mapping configuration
        """
        text_features = [prompt_col, response_col]
        if reference_col:
            text_features.append(reference_col)

        return ColumnMapping(
            datetime=datetime_col,
            text_features=text_features,
            categorical_features=categorical_cols or [],
            numerical_features=numerical_cols or [],
            datetime_features=datetime_cols or [],
        )

    def evaluate_text_length(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        reference_data: Optional[pd.DataFrame] = None,
        column_mapping: Optional[ColumnMapping] = None,
        save_html: bool = False,
        output_path: str = "./reports",
    ) -> Report:
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
            Report: The Evidently report object
        """
        logger.info("Evaluating text length metrics")

        report = Report(
            metrics=[
                TextEvals(
                    column_name=response_col,
                    descriptors=[TextLength(), WordCount(), SentenceCount()],
                )
            ]
        )

        report.run(
            reference_data=reference_data,
            current_data=data,
            column_mapping=column_mapping,
        )

        if save_html:
            os.makedirs(output_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(
                output_path, f"text_length_report_{timestamp}.html"
            )
            report.save_html(report_path)
            logger.info("Text length report saved to %s", report_path)

        return report

    def evaluate_content_patterns(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        words_to_check: Optional[List[str]] = None,
        patterns_to_check: Optional[List[str]] = None,
        prefix_to_check: Optional[str] = None,
        reference_data: Optional[pd.DataFrame] = None,
        column_mapping: Optional[ColumnMapping] = None,
        save_html: bool = False,
        output_path: str = "./reports",
    ) -> Report:
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
            Report: The Evidently report object
        """
        logger.info("Evaluating content patterns in responses")

        descriptors = []

        if words_to_check:
            descriptors.append(
                IncludesWords(words_list=words_to_check, display_name="Word Matches")
            )

        if patterns_to_check:
            for i, pattern in enumerate(patterns_to_check):
                descriptors.append(
                    Contains(items=[pattern], display_name=f"Pattern Match {i + 1}")
                )

        if prefix_to_check:
            descriptors.append(
                BeginsWith(prefix=prefix_to_check, display_name="Prefix Match")
            )

        if not descriptors:
            # Add a default pattern check if nothing specified
            descriptors.append(
                IncludesWords(
                    words_list=["yes", "no", "sorry", "thank", "please"],
                    display_name="Common Response Words",
                )
            )

        report = Report(
            metrics=[TextEvals(column_name=response_col, descriptors=descriptors)]
        )

        report.run(
            reference_data=reference_data,
            current_data=data,
            column_mapping=column_mapping,
        )

        if save_html:
            os.makedirs(output_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(
                output_path, f"content_patterns_report_{timestamp}.html"
            )
            report.save_html(report_path)
            logger.info("Content patterns report saved to %s", report_path)

        return report

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
        column_mapping: Optional[ColumnMapping] = None,
        save_html: bool = False,
        output_path: str = "./reports",
    ) -> Optional[Report]:
        """
        Evaluate semantic properties of LLM responses using pre-trained models.

        Args:
            data: Dataset with LLM responses
            response_col: Column name containing model responses
            prompt_col: Column name containing prompts/questions
            check_sentiment: Whether to check sentiment
            check_toxicity: Whether to check toxicity
            check_prompt_relevance: Whether to check semantic similarity between prompt and response
            huggingface_models: List of custom HuggingFace models to use
            reference_data: Reference dataset for comparison
            column_mapping: Column mapping for the dataset
            save_html: Whether to save the report as HTML
            output_path: Directory to save report files

        Returns:
            Report: The Evidently report object
        """
        logger.info("Evaluating semantic properties of responses")

        metrics = []

        # Response semantic properties
        descriptors = []
        if check_sentiment:
            descriptors.append(Sentiment())

        if check_toxicity:
            descriptors.append(HuggingFaceToxicityModel())

        if huggingface_models:
            for model_config in huggingface_models:
                descriptors.append(
                    HuggingFaceModel(
                        model=model_config["model"],
                        params=model_config.get("params", {}),
                        display_name=model_config.get("display_name"),
                    )
                )

        if descriptors:
            metrics.append(TextEvals(column_name=response_col, descriptors=descriptors))

        # Prompt-response similarity
        if check_prompt_relevance and prompt_col and prompt_col in data.columns:
            # Try to use the new format if that's what Evidently expects
            try:
                metrics.append(
                    TextEvals(
                        column_name=response_col,
                        descriptors=[
                            SemanticSimilarity(
                                with_column=prompt_col,
                                display_name="Response-Prompt Relevance",
                            )
                        ],
                    )
                )
            except Exception as e:
                # Fall back to the previous format if an error occurs
                logger.warning(
                    f"Error with new SemanticSimilarity format: {e}. Trying alternate format."
                )
                try:
                    metrics.append(
                        TextEvals(
                            column_name=response_col,
                            descriptors=[
                                SemanticSimilarity(
                                    display_name="Response-Prompt Relevance"
                                ).on([response_col, prompt_col])
                            ],
                        )
                    )
                except Exception as e2:
                    logger.warning(
                        f"Error creating semantic similarity metric: {e2}. Skipping."
                    )

        if not metrics:
            logger.warning("No semantic properties selected for evaluation")
            return None

        report = Report(metrics=metrics)

        report.run(
            reference_data=reference_data,
            current_data=data,
            column_mapping=column_mapping,
        )

        if save_html:
            os.makedirs(output_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(
                output_path, f"semantic_properties_report_{timestamp}.html"
            )
            report.save_html(report_path)
            logger.info("Semantic properties report saved to %s", report_path)

        return report

    def evaluate_llm_as_judge(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        check_pii: bool = True,
        check_decline: bool = True,
        custom_evals: Optional[List[Dict[str, Any]]] = None,
        reference_data: Optional[pd.DataFrame] = None,
        column_mapping: Optional[ColumnMapping] = None,
        save_html: bool = False,
        output_path: str = "./reports",
    ) -> Optional[Report]:
        """
        Evaluate LLM responses using LLM-as-judge (requires OpenAI API key).

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
            Report: The Evidently report object or None if LLM judge is not available
        """
        if not LLM_JUDGE_AVAILABLE:
            logger.warning(
                "LLM-as-judge features not available. Make sure to install required dependencies."
            )
            return None

        if not os.environ.get("OPENAI_API_KEY"):
            logger.warning(
                "OPENAI_API_KEY environment variable not set. LLM-as-judge features require an OpenAI API key."
            )
            return None

        logger.info("Evaluating responses using LLM-as-judge")

        descriptors = []

        if check_decline:
            descriptors.append(DeclineLLMEval())

        if check_pii:
            descriptors.append(PIILLMEval(include_reasoning=True))

        if custom_evals:
            for eval_config in custom_evals:
                descriptors.append(
                    LLMEval(
                        subcolumn="category",
                        template=BinaryClassificationPromptTemplate(
                            criteria=eval_config.get("criteria", ""),
                            target_category=eval_config.get("target", "positive"),
                            non_target_category=eval_config.get(
                                "non_target", "negative"
                            ),
                            uncertainty="uncertain",
                            include_reasoning=True,
                            pre_messages=[
                                ("system", "You are a judge which evaluates text.")
                            ],
                        ),
                        provider="openai",
                        model=eval_config.get("model", "gpt-3.5-turbo"),
                        display_name=eval_config.get("name", "Custom Evaluation"),
                    )
                )

        report = Report(
            metrics=[TextEvals(column_name=response_col, descriptors=descriptors)]
        )

        report.run(
            reference_data=reference_data,
            current_data=data,
            column_mapping=column_mapping,
        )

        if save_html:
            os.makedirs(output_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(
                output_path, f"llm_judge_report_{timestamp}.html"
            )
            report.save_html(report_path)
            logger.info("LLM-as-judge report saved to %s", report_path)

        return report

    def create_test_suite(
        self,
        response_col: str = "response",
        min_response_length: int = 1,
        max_response_length: int = 2000,
        min_sentiment: float = 0.0,
        min_mean_response_length: int = 100,
    ) -> TestSuite:
        """
        Create a test suite for LLM responses with conditions to check.

        Args:
            response_col: Column name containing model responses
            min_response_length: Minimum acceptable response length
            max_response_length: Maximum acceptable response length
            min_sentiment: Minimum acceptable sentiment score
            min_mean_response_length: Minimum acceptable mean response length

        Returns:
            TestSuite: The Evidently test suite object
        """
        test_suite = TestSuite(
            tests=[
                TestColumnValueMin(
                    column_name=TextLength().on(response_col), gt=min_response_length
                ),
                TestColumnValueMax(
                    column_name=TextLength().on(response_col), lte=max_response_length
                ),
                TestColumnValueMean(
                    column_name=TextLength().on(response_col),
                    gt=min_mean_response_length,
                ),
                TestColumnValueMean(
                    column_name=Sentiment().on(response_col), gte=min_sentiment
                ),
            ]
        )

        return test_suite

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
        column_mapping: Optional[ColumnMapping] = None,
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
            reference_col: Column name containing reference/golden responses
            categorical_cols: List of categorical feature columns
            words_to_check: List of words to check for in responses
            run_sentiment: Whether to check sentiment
            run_toxicity: Whether to check toxicity
            run_llm_judge: Whether to run LLM-as-judge (requires OpenAI API key)
            reference_data: Reference dataset for comparison
            column_mapping: Column mapping for the dataset
            save_html: Whether to save the report as HTML
            output_path: Directory to save report files
            artifact_path: MLflow artifact path for logging
            run_id: MLflow run ID

        Returns:
            Dict[str, Any]: Dictionary with all evaluation reports
        """
        if column_mapping is None:
            column_mapping = self.create_column_mapping(
                prompt_col=prompt_col,
                response_col=response_col,
                reference_col=reference_col,
                categorical_cols=categorical_cols,
            )

        evaluation_results = {}

        # 1. Text length metrics
        length_report = self.evaluate_text_length(
            data=data,
            response_col=response_col,
            reference_data=reference_data,
            column_mapping=column_mapping,
            save_html=save_html,
            output_path=output_path,
        )
        evaluation_results["length_metrics"] = length_report

        # 2. Content patterns
        if words_to_check:
            patterns_report = self.evaluate_content_patterns(
                data=data,
                response_col=response_col,
                words_to_check=words_to_check,
                reference_data=reference_data,
                column_mapping=column_mapping,
                save_html=save_html,
                output_path=output_path,
            )
            evaluation_results["content_patterns"] = patterns_report

        # 3. Semantic properties
        semantic_report = self.evaluate_semantic_properties(
            data=data,
            response_col=response_col,
            prompt_col=prompt_col,
            check_sentiment=run_sentiment,
            check_toxicity=run_toxicity,
            check_prompt_relevance=(prompt_col is not None),
            reference_data=reference_data,
            column_mapping=column_mapping,
            save_html=save_html,
            output_path=output_path,
        )
        evaluation_results["semantic_properties"] = semantic_report

        # 4. LLM-as-judge (if enabled)
        if run_llm_judge:
            judge_report = self.evaluate_llm_as_judge(
                data=data,
                response_col=response_col,
                reference_data=reference_data,
                column_mapping=column_mapping,
                save_html=save_html,
                output_path=output_path,
            )
            if judge_report:
                evaluation_results["llm_judge"] = judge_report

        # 5. Test suite for quality conditions
        test_suite = self.create_test_suite(response_col=response_col)
        test_suite.run(
            current_data=data,
            reference_data=reference_data,
            column_mapping=column_mapping,
        )
        evaluation_results["test_suite"] = test_suite

        # Save comprehensive report if requested
        if save_html:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save test suite results
            test_suite_path = os.path.join(
                output_path, f"test_suite_results_{timestamp}.html"
            )
            test_suite.save_html(test_suite_path)

            # Create combined dictionary with results
            combined_results = {
                "timestamp": timestamp,
                "data_size": len(data),
                "metrics": {},
            }

            # Extract metrics from reports
            for key, report in evaluation_results.items():
                if key != "test_suite" and report is not None:
                    combined_results["metrics"][key] = report.as_dict()

            # Add test suite results
            combined_results["test_suite"] = {
                "passed": test_suite.as_dict()["summary"]["success"],
                "total_tests": test_suite.as_dict()["summary"]["total"],
                "results": test_suite.as_dict()["tests"],
            }

            # Save combined results as JSON
            combined_path = os.path.join(
                output_path, f"comprehensive_evaluation_{timestamp}.json"
            )
            with open(combined_path, "w", encoding="utf-8") as f:
                json.dump(combined_results, f, indent=2)

            logger.info("Comprehensive evaluation results saved to %s", combined_path)

            # Generate dashboard and summary reports
            try:
                # Create dashboard visualization
                dashboard_path = self.generate_dashboard(
                    data=data,
                    response_col=response_col,
                    category_col="category" if "category" in data.columns else None,
                    sentiment_col=(
                        "sentiment_score" if "sentiment_score" in data.columns else None
                    ),
                    output_path=output_path,
                    dashboard_name=f"response_dashboard_{timestamp}.png",
                    artifact_path=artifact_path,
                    run_id=run_id,
                )

                if dashboard_path:
                    logger.info(
                        "Response quality dashboard saved to %s", dashboard_path
                    )

                # Generate summary report
                summary_path = self.generate_summary_report(
                    data=data,
                    response_col=response_col,
                    output_path=output_path,
                    report_name=f"evaluation_summary_{timestamp}.html",
                    artifact_path=artifact_path,
                    run_id=run_id,
                )

                if summary_path:
                    logger.info("Summary report saved to %s", summary_path)
            except Exception as e:
                logger.warning(f"Could not generate visualization or summary: {str(e)}")

        return evaluation_results

    def log_metrics_to_mlflow(
        self,
        metrics: Union[Report, TestSuite, Dict[str, Any]],
        run_id: Optional[str] = None,
    ) -> bool:
        """
        Log Evidently report metrics to MLflow.

        Args:
            metrics: The Evidently report, test suite, or metrics dictionary
            run_id: MLflow run ID. If not provided, uses active run

        Returns:
            bool: True if metrics were successfully logged
        """
        if self.evidently_ml_monitor is None:
            logger.warning("Evidently monitor is not initialized. Metrics not logged.")
            return False

        logger.info("Logging LLM metrics to MLflow")

        try:
            # Handle different types of input
            if isinstance(metrics, (Report, TestSuite)):
                # Convert report to dictionary
                report_dict = metrics.as_dict()

                # Extract and flatten metrics for MLflow
                flattened_metrics = {}

                if isinstance(metrics, Report):
                    # Process Report metrics
                    self._extract_textevals_metrics(
                        report_dict, flattened_metrics, "llm_metrics"
                    )
                else:
                    # Process TestSuite metrics
                    self._extract_test_suite_metrics(
                        report_dict, flattened_metrics, "evidently.llm_test_suite."
                    )

                # Use the evidently_ml_monitor to log metrics
                return self.evidently_ml_monitor.log_metrics_to_mlflow(
                    flattened_metrics, run_id
                )
            else:
                # Assume metrics is already a dictionary
                return self.evidently_ml_monitor.log_metrics_to_mlflow(metrics, run_id)

        except (ImportError, ValueError, IOError) as e:
            logger.error("Failed to log metrics to MLflow: %s", str(e))
            return False

    def _extract_textevals_metrics(
        self,
        report_dict: Dict[str, Any],
        flattened_metrics: Dict[str, Any],
        report_type: str,
    ) -> None:
        """Extract TextEvals metrics from the report dictionary."""
        prefix = f"evidently.{report_type}."

        if "metrics" not in report_dict:
            return

        for metric in report_dict["metrics"]:
            if metric.get("metric") == "TextEvals" and "result" in metric:
                column_name = metric.get("column_name", "text")

                for descriptor in metric["result"].get("descriptors", []):
                    descriptor_name = descriptor.get("descriptor", "unknown")

                    if "current" in descriptor:
                        self._extract_current_descriptor(
                            descriptor["current"],
                            f"{prefix}{column_name}.{descriptor_name}",
                            flattened_metrics,
                        )

    def _extract_current_descriptor(
        self, current_metrics: Any, key_prefix: str, flattened_metrics: Dict[str, Any]
    ) -> None:
        """Extract metrics from current descriptor data."""
        if isinstance(current_metrics, dict):
            for k, v in current_metrics.items():
                if isinstance(v, (int, float, bool)):
                    flattened_metrics[f"{key_prefix}.{k}"] = (
                        float(v) if isinstance(v, bool) else v
                    )
        elif isinstance(current_metrics, (int, float, bool)):
            flattened_metrics[key_prefix] = (
                float(current_metrics)
                if isinstance(current_metrics, bool)
                else current_metrics
            )

    def _extract_test_suite_metrics(
        self,
        test_suite_dict: Dict[str, Any],
        flattened_metrics: Dict[str, Any],
        prefix: str = "",
    ) -> None:
        """
        Extract metrics from an Evidently TestSuite and add them to flattened_metrics.

        Args:
            test_suite_dict: The test suite dictionary
            flattened_metrics: Dictionary to populate with flattened metrics
            prefix: Prefix for metric names
        """
        if "summary" in test_suite_dict:
            for k, v in test_suite_dict["summary"].items():
                if isinstance(v, (int, float, bool)):
                    flattened_metrics[f"{prefix}summary.{k}"] = (
                        float(v) if isinstance(v, bool) else v
                    )

        if "tests" in test_suite_dict:
            for i, test in enumerate(test_suite_dict["tests"]):
                test_name = test.get("name", f"test_{i}")
                if "status" in test:
                    flattened_metrics[f"{prefix}tests.{test_name}.passed"] = (
                        1.0 if test["status"] == "SUCCESS" else 0.0
                    )

                if "value" in test and isinstance(test["value"], (int, float)):
                    flattened_metrics[f"{prefix}tests.{test_name}.value"] = test[
                        "value"
                    ]

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
        os.makedirs(output_path, exist_ok=True)

        # Default metrics if none provided
        if metrics is None:
            metrics = ["length", "word_count"]

        # Calculate metrics
        metrics_data = {}

        if "length" in metrics:
            ref_length = reference_data[response_col].str.len().mean()
            cur_length = current_data[response_col].str.len().mean()
            metrics_data["length"] = {
                "reference": ref_length,
                "current": cur_length,
                "diff_pct": (
                    ((cur_length - ref_length) / ref_length * 100)
                    if ref_length > 0
                    else 0
                ),
                "label": "Avg Characters",
            }

        if "word_count" in metrics:
            ref_words = reference_data[response_col].str.split().str.len().mean()
            cur_words = current_data[response_col].str.split().str.len().mean()
            metrics_data["word_count"] = {
                "reference": ref_words,
                "current": cur_words,
                "diff_pct": (
                    ((cur_words - ref_words) / ref_words * 100) if ref_words > 0 else 0
                ),
                "label": "Avg Words",
            }

        if (
            "sentiment_score" in metrics
            and "sentiment_score" in reference_data.columns
            and "sentiment_score" in current_data.columns
        ):
            ref_sentiment = reference_data["sentiment_score"].mean()
            cur_sentiment = current_data["sentiment_score"].mean()
            metrics_data["sentiment_score"] = {
                "reference": ref_sentiment,
                "current": cur_sentiment,
                "diff_pct": (
                    ((cur_sentiment - ref_sentiment) / ref_sentiment * 100)
                    if ref_sentiment > 0
                    else 0
                ),
                "label": "Sentiment Score",
            }

        # Create visualization
        try:
            # Set up bar chart
            models = ["Reference Model", "Current Model"]

            # Setup multipanel figure based on number of metrics
            num_metrics = len(metrics_data)

            if num_metrics <= 2:
                fig, axes = plt.subplots(1, num_metrics, figsize=(7 * num_metrics, 6))
                if num_metrics == 1:
                    axes = [axes]  # Make it iterable for single panel
            else:
                # For 3 or more metrics, use a 2-row layout
                cols = (num_metrics + 1) // 2
                fig, axes = plt.subplots(2, cols, figsize=(7 * cols, 12))
                axes = axes.flatten()

            # Create bar charts for each metric
            for i, (metric_key, metric_data) in enumerate(metrics_data.items()):
                if i < len(axes):
                    ax = axes[i]
                    values = [metric_data["reference"], metric_data["current"]]
                    x = range(len(models))
                    width = 0.6

                    bars = ax.bar(x, values, width, alpha=0.7)

                    # Add value labels on bars
                    for j, v in enumerate(values):
                        ax.text(j, v * 1.05, f"{v:.1f}", ha="center")

                    # Add metric label
                    ax.set_ylabel(metric_data["label"])
                    ax.set_title(f"{metric_data['label']} Comparison")
                    ax.set_xticks(x)
                    ax.set_xticklabels(models)

                    # Add percentage change
                    ax.text(
                        1,
                        values[1] * 0.5,
                        f"{metric_data['diff_pct']:+.1f}%",
                        ha="center",
                        va="center",
                        color="green" if metric_data["diff_pct"] > 0 else "red",
                        bbox=dict(
                            facecolor="white", alpha=0.7, boxstyle="round,pad=0.5"
                        ),
                    )

            plt.tight_layout()

            # Save the plot
            plot_path = os.path.join(output_path, "model_comparison_visualization.png")
            plt.savefig(plot_path, dpi=100, bbox_inches="tight")
            plt.close()

            # Log to MLflow if requested
            if self.mlflow_client and artifact_path:
                try:
                    self.mlflow_client.log_artifact(
                        plot_path, artifact_path, run_id=run_id
                    )
                except Exception as e:
                    logger.warning(f"Could not log visualization to MLflow: {e}")

            return plot_path

        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return ""

    def generate_dashboard(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        category_col: Optional[str] = "category",
        model_col: Optional[str] = "model",
        sentiment_col: Optional[str] = "sentiment_score",
        output_path: str = "./reports",
        dashboard_name: str = "response_quality_dashboard.png",
        artifact_path: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> str:
        """
        Create a dashboard visualization of LLM response data.

        Args:
            data: DataFrame containing the LLM responses
            response_col: Column containing the text responses
            category_col: Column containing response categories
            model_col: Column containing model names
            sentiment_col: Column containing sentiment scores
            output_path: Directory to save the dashboard
            dashboard_name: Filename for the dashboard image
            artifact_path: MLflow artifact path for logging
            run_id: MLflow run ID

        Returns:
            str: Path to the generated dashboard
        """
        os.makedirs(output_path, exist_ok=True)

        try:
            # Create response length column if not exists
            if "response_length" not in data.columns:
                data["response_length"] = data[response_col].str.len()

            # Create word count column if not exists
            if "word_count" not in data.columns:
                data["word_count"] = data[response_col].str.split().str.len()

            # Set up figure
            fig = plt.figure(figsize=(12, 10))

            # Plot 1: Response length distribution
            plt.subplot(2, 2, 1)
            plt.hist(data["response_length"], bins=20, alpha=0.7, color="#4285F4")
            plt.title("Response Length Distribution")
            plt.xlabel("Characters")
            plt.ylabel("Count")
            plt.grid(alpha=0.3)

            # Plot 2: Word count distribution
            plt.subplot(2, 2, 2)
            plt.hist(data["word_count"], bins=15, alpha=0.7, color="#34A853")
            plt.title("Word Count Distribution")
            plt.xlabel("Words")
            plt.ylabel("Count")
            plt.grid(alpha=0.3)

            # Plot 3: Categories distribution (if available)
            plt.subplot(2, 2, 3)
            if category_col and category_col in data.columns:
                category_counts = data[category_col].value_counts()
                plt.pie(
                    category_counts,
                    labels=category_counts.index,
                    autopct="%1.1f%%",
                    colors=[
                        "#4285F4",
                        "#34A853",
                        "#FBBC05",
                        "#EA4335",
                        "#5F6368",
                        "#185ABC",
                    ][: len(category_counts)],
                    startangle=90,
                )
                plt.title("Response Categories")
            else:
                plt.text(
                    0.5, 0.5, "No category data available", ha="center", va="center"
                )
                plt.axis("off")

            # Plot 4: Sentiment distribution (if available) or model distribution
            plt.subplot(2, 2, 4)
            if sentiment_col and sentiment_col in data.columns:
                plt.hist(data[sentiment_col], bins=10, alpha=0.7, color="#FBBC05")
                plt.title("Sentiment Score Distribution")
                plt.xlabel("Sentiment Score")
                plt.ylabel("Count")
                plt.grid(alpha=0.3)
            elif model_col and model_col in data.columns:
                model_counts = data[model_col].value_counts()
                plt.bar(
                    model_counts.index, model_counts.values, alpha=0.7, color="#EA4335"
                )
                plt.title("Models Distribution")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
            else:
                plt.text(
                    0.5,
                    0.5,
                    "No sentiment or model data available",
                    ha="center",
                    va="center",
                )
                plt.axis("off")

            plt.tight_layout()

            # Save the dashboard
            dashboard_path = os.path.join(output_path, dashboard_name)
            plt.savefig(dashboard_path, dpi=100, bbox_inches="tight")
            plt.close()

            # Log to MLflow if requested
            if self.mlflow_client and artifact_path:
                try:
                    self.mlflow_client.log_artifact(
                        dashboard_path, artifact_path, run_id=run_id
                    )
                except Exception as e:
                    logger.warning(f"Could not log dashboard to MLflow: {e}")

            return dashboard_path

        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            return ""

    def generate_summary_report(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        output_path: str = "./reports",
        report_name: str = "evaluation_summary.html",
        include_cols: Optional[List[str]] = None,
        artifact_path: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> str:
        """
        Generate an HTML summary report for LLM responses.

        Args:
            data: DataFrame containing the LLM responses
            response_col: Column containing the text responses
            output_path: Directory to save the report
            report_name: Filename for the HTML report
            include_cols: Additional columns to include in the report
            artifact_path: MLflow artifact path for logging
            run_id: MLflow run ID

        Returns:
            str: Path to the generated report
        """
        os.makedirs(output_path, exist_ok=True)

        if include_cols is None:
            include_cols = ["category", "model", "sentiment_score"]

        # Start building HTML
        summary_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>LLM Evaluation Summary</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                .metric {{ font-weight: bold; }}
                .summary {{
                    background-color: #f9f9f9;
                    border-left: 5px solid #4285f4;
                    padding: 10px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>LLM Evaluation Summary</h1>

                <div class="summary">
                    <h3>Dataset Overview</h3>
                    <p>Analysis of {len(data)} LLM responses</p>
                </div>

                <h2>Key Metrics</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Number of responses</td><td>{len(data)}</td></tr>
                    <tr><td>Average response length</td><td>{data[response_col].str.len().mean():.1f} characters</td></tr>
                    <tr><td>Average word count</td><td>{data[response_col].str.split().str.len().mean():.1f} words</td></tr>
        """

        # Add additional metrics if available
        for col in include_cols:
            if col in data.columns and col != response_col:
                try:
                    if data[col].dtype.kind in "ifc":  # If numeric
                        summary_html += f"<tr><td>Average {col.replace('_', ' ')}</td><td>{data[col].mean():.2f}</td></tr>"
                except (TypeError, ValueError):
                    pass

        summary_html += """
                </table>
        """

        # Add distribution tables for categorical columns
        for col in include_cols:
            if col in data.columns and col != response_col:
                try:
                    # Check if column has categorical-like data (not too many unique values)
                    if data[col].nunique() < 20:
                        value_counts = data[col].value_counts()

                        summary_html += f"""
                <h2>{col.replace('_', ' ').title()} Distribution</h2>
                <table>
                    <tr><th>{col.replace('_', ' ').title()}</th><th>Count</th><th>Percentage</th></tr>
                        """

                        for value, count in value_counts.items():
                            percentage = (count / len(data)) * 100
                            summary_html += f"<tr><td>{value}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>"

                        summary_html += """
                </table>
                        """
                except:
                    pass

        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        summary_html += f"""
                <h2>Report Information</h2>
                <p>Generated on: {timestamp}</p>
            </div>
        </body>
        </html>
        """

        # Save the report
        report_path = os.path.join(output_path, report_name)
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(summary_html)

            # Log to MLflow if requested
            if self.mlflow_client and artifact_path:
                try:
                    self.mlflow_client.log_artifact(
                        report_path, artifact_path, run_id=run_id
                    )
                except Exception as e:
                    logger.warning(f"Could not log report to MLflow: {e}")

            return report_path
        except Exception as e:
            logger.error(f"Error saving summary report: {e}")
            return ""

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
        os.makedirs(output_path, exist_ok=True)

        if metrics_cols is None:
            metrics_cols = []

        # Calculate standard metrics
        ref_length = reference_data[response_col].str.len().mean()
        cur_length = current_data[response_col].str.len().mean()
        length_diff_pct = (
            ((cur_length - ref_length) / ref_length * 100) if ref_length > 0 else 0
        )

        ref_words = reference_data[response_col].str.split().str.len().mean()
        cur_words = current_data[response_col].str.split().str.len().mean()
        words_diff_pct = (
            ((cur_words - ref_words) / ref_words * 100) if ref_words > 0 else 0
        )

        # Build HTML report
        comparison_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Model Comparison Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .container {{ max-width: 900px; margin: 0 auto; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                .metric {{ font-weight: bold; }}
                .highlight {{ background-color: #ffffcc; }}
                .better {{ color: green; }}
                .worse {{ color: red; }}
                .summary {{
                    background-color: #f9f9f9;
                    border-left: 5px solid #4285f4;
                    padding: 10px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>LLM Model Comparison Report</h1>

                <div class="summary">
                    <h3>Summary</h3>
                    <p>
                        This report compares two datasets of LLM responses:
                        <br>- Reference Model: {len(reference_data)} responses
                        <br>- Current Model: {len(current_data)} responses
                    </p>
                </div>

                <h2>Key Metrics Comparison</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Reference Model</th>
                        <th>Current Model</th>
                        <th>Difference</th>
                    </tr>
                    <tr>
                        <td>Average Response Length</td>
                        <td>{ref_length:.1f} chars</td>
                        <td>{cur_length:.1f} chars</td>
                        <td class="{('better' if cur_length > ref_length else 'worse')}">{length_diff_pct:+.1f}%</td>
                    </tr>
                    <tr>
                        <td>Average Word Count</td>
                        <td>{ref_words:.1f} words</td>
                        <td>{cur_words:.1f} words</td>
                        <td class="{('better' if cur_words > ref_words else 'worse')}">{words_diff_pct:+.1f}%</td>
                    </tr>
        """

        # Add additional metrics if available in both dataframes
        for metric in metrics_cols:
            if metric in reference_data.columns and metric in current_data.columns:
                try:
                    ref_value = reference_data[metric].mean()
                    cur_value = current_data[metric].mean()
                    diff_pct = (
                        ((cur_value - ref_value) / ref_value * 100)
                        if ref_value != 0
                        else 0
                    )

                    comparison_html += f"""
                    <tr>
                        <td>{metric.replace('_', ' ').title()}</td>
                        <td>{ref_value:.2f}</td>
                        <td>{cur_value:.2f}</td>
                        <td class="{('better' if cur_value > ref_value else 'worse')}">{diff_pct:+.1f}%</td>
                    </tr>
                    """
                except (TypeError, ValueError):
                    # Skip this metric if calculation fails
                    pass

        comparison_html += """
                </table>
        """

        # Add category distribution comparison if category column is available
        if (
            category_col
            and category_col in reference_data.columns
            and category_col in current_data.columns
        ):
            comparison_html += f"""
                <h2>Category Distribution Comparison</h2>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Reference Model</th>
                        <th>Current Model</th>
                        <th>Difference</th>
                    </tr>
            """

            # Combine categories from both datasets
            all_categories = set(reference_data[category_col].unique()) | set(
                current_data[category_col].unique()
            )

            for category in sorted(all_categories):
                ref_count = reference_data[
                    reference_data[category_col] == category
                ].shape[0]
                ref_pct = (
                    (ref_count / len(reference_data)) * 100
                    if len(reference_data) > 0
                    else 0
                )

                cur_count = current_data[current_data[category_col] == category].shape[
                    0
                ]
                cur_pct = (
                    (cur_count / len(current_data)) * 100
                    if len(current_data) > 0
                    else 0
                )

                diff_pct = cur_pct - ref_pct

                comparison_html += f"""
                        <tr>
                            <td>{category}</td>
                            <td>{ref_count} ({ref_pct:.1f}%)</td>
                            <td>{cur_count} ({cur_pct:.1f}%)</td>
                            <td class="{('highlight' if abs(diff_pct) > 5 else '')}">{diff_pct:+.1f}%</td>
                        </tr>
                """

            comparison_html += """
                </table>
            """

        # Add model distribution comparison if model column is available
        if "model" in reference_data.columns and "model" in current_data.columns:
            comparison_html += f"""
                <h2>Model Distribution</h2>
                <table>
                    <tr>
                        <th>Model</th>
                        <th>Reference Dataset</th>
                        <th>Current Dataset</th>
                    </tr>
            """

            ref_models = reference_data["model"].value_counts().to_dict()
            cur_models = current_data["model"].value_counts().to_dict()
            all_models = set(ref_models.keys()) | set(cur_models.keys())

            for model in sorted(all_models):
                ref_count = ref_models.get(model, 0)
                ref_pct = (
                    (ref_count / len(reference_data)) * 100
                    if len(reference_data) > 0
                    else 0
                )

                cur_count = cur_models.get(model, 0)
                cur_pct = (
                    (cur_count / len(current_data)) * 100
                    if len(current_data) > 0
                    else 0
                )

                comparison_html += f"""
                        <tr>
                            <td>{model}</td>
                            <td>{ref_count} ({ref_pct:.1f}%)</td>
                            <td>{cur_count} ({cur_pct:.1f}%)</td>
                        </tr>
                """

            comparison_html += """
                </table>
            """

        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        comparison_html += f"""
                <h2>Report Information</h2>
                <p>Generated on: {timestamp}</p>
            </div>
        </body>
        </html>
        """

        # Save the report
        report_path = os.path.join(output_path, report_name)
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(comparison_html)

            # Log to MLflow if requested
            if self.mlflow_client and artifact_path:
                try:
                    self.mlflow_client.log_artifact(
                        report_path, artifact_path, run_id=run_id
                    )
                except Exception as e:
                    logger.warning(f"Could not log report to MLflow: {e}")

            return report_path
        except Exception as e:
            logger.error(f"Error saving comparison report: {e}")
            return ""
