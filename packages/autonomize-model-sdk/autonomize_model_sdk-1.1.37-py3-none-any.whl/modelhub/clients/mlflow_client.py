"""Client for interacting with MLflow."""

import logging
import os
from contextlib import contextmanager
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Union, List
from dotenv import load_dotenv
from modelhub.models.model_card import ModelCardSchema
from urllib.parse import quote_plus

import mlflow

from modelhub.core import BaseClient, ModelhubCredential
from pydantic import BaseModel, Field


load_dotenv()


logger = logging.getLogger(__name__)

class MLflowClient(BaseClient):
    """Client for interacting with MLflow."""

    def __init__(
        self,
        credential: ModelhubCredential,
        client_id: Optional[str] = None,
        copilot_id: Optional[str] = None,
        timeout: int = 10,
        verify_ssl: bool = True,
    ):
        """Initialize the MLflowClient."""
        super().__init__(credential, client_id, copilot_id, timeout, verify_ssl)
        self.configure_mlflow()

    def configure_mlflow(self) -> None:
        """Configure MLflow settings."""
        try:
            response = self.get("mlflow/tracking_uri")
            logger.info(f"MLflow tracking uri: {response}")
            tracking_uri = response.get("tracking_uri")
            if not tracking_uri:
                logger.error("Tracking URI not found in response")
                raise ValueError("Tracking URI not found in response")

            mlflow.set_tracking_uri(tracking_uri)
            logger.debug("Set MLflow tracking URI to: %s", tracking_uri)

            response = self.get("mlflow/credentials")
            username = response.get("username")
            password = response.get("password")

            if username and password:
                mlflow.set_registry_uri(tracking_uri)
                os.environ["MLFLOW_TRACKING_USERNAME"] = username
                os.environ["MLFLOW_TRACKING_PASSWORD"] = password
                logger.debug("Set MLflow credentials")
        except Exception as e:
            logger.error("Failed to configure MLflow: %s", str(e))
            raise

    @contextmanager
    def start_run(
        self,
        run_name: Optional[str] = None,
        nested: bool = False,
        tags: Optional[Dict[str, str]] = None,
        output_path: str = "/tmp",
    ) -> Generator[mlflow.ActiveRun, None, None]:
        """Context manager for starting an MLflow run."""
        logger.info("Starting MLflow run with name: %s", run_name)

        try:
            os.makedirs(output_path, exist_ok=True)
            logger.debug("Created output directory: %s", output_path)
        except OSError as e:
            logger.error(
                "Failed to create output directory '%s': %s", output_path, str(e)
            )
            raise

        try:
            with mlflow.start_run(run_name=run_name, nested=nested, tags=tags) as run:
                run_id = run.info.run_id
                run_id_path = os.path.join(output_path, "run_id")

                try:
                    with open(run_id_path, "w", encoding="utf-8") as f:
                        f.write(run_id)
                    logger.debug("Wrote run_id to: %s", run_id_path)
                except OSError as e:
                    logger.error(
                        "Failed to write run_id to '%s': %s", run_id_path, str(e)
                    )
                    raise

                yield run

        except Exception as e:
            logger.error("Error during MLflow run: %s", str(e))
            raise

    def end_run(self, status: str = "FINISHED") -> None:
        """End the current MLflow run."""
        mlflow.end_run(status=status)
        logger.debug("Ended MLflow run with status: %s", status)

    def get_previous_stage_run_id(self, output_path: str = "/tmp") -> str:
        """Get the run ID of the previous stage."""
        run_id_path = os.path.join(output_path, "run_id")
        try:
            with open(run_id_path, "r", encoding="utf-8") as f:
                run_id = f.read().strip()
            logger.debug("Retrieved previous stage run_id: %s", run_id)
            return run_id
        except FileNotFoundError:
            logger.error("Run ID file not found at: %s", run_id_path)
            raise

    def set_experiment(
        self, experiment_name: Optional[str] = None, experiment_id: Optional[str] = None
    ) -> None:
        """Set the active experiment."""
        mlflow.set_experiment(experiment_name, experiment_id)
        logger.debug("Set experiment: name=%s, id=%s", experiment_name, experiment_id)

    def log_param(self, key: str, value: Any) -> None:
        """Log a parameter."""
        mlflow.log_param(key, value)
        logger.debug("Logged parameter: %s=%s", key, value)

    def log_metric(self, key: str, value: float) -> None:
        """Log a metric."""
        mlflow.log_metric(key, value)
        logger.debug("Logged metric: %s=%f", key, value)

    def log_artifact(
        self,
        local_path: str,
        artifact_path: Optional[str] = None,
        run_id: Optional[str] = None,   
    ) -> None:
        """Log an artifact."""
        mlflow.log_artifact(local_path, artifact_path, run_id)
        logger.debug("Logged artifact: %s", local_path)

    def get_run(self, run_id: str) -> Dict[str, Any]:
        """Get the run details."""
        run = mlflow.get_run(run_id)
        logger.debug("Retrieved run: %s", run_id)
        return run.to_dictionary()

    def load_model(self, model_uri: str) -> Any:
        """Load the model from the specified URI."""
        logger.debug("Loading model from: %s", model_uri)
        return mlflow.pyfunc.load_model(model_uri)

    def save_model(self, model: Any, model_path: str) -> None:
        """Save the model to the specified path."""
        logger.debug("Saving model to: %s", model_path)
        mlflow.pyfunc.save_model(model, model_path)

    def register_model(
        self,
        run_id: str,
        model_name: str,
        model_card_data: Dict[str, Any],
        registered_model_name: Optional[str] = None,
        await_registration_for: int = 300,
        artifact_path: str = "model"
    ) -> Dict[str, Any]:
        """
        Register a model from an MLflow run and create a model card.
        
        Args:
            run_id: The ID of the MLflow run containing the model
            model_name: Name of the model to register
            model_card_data: Dictionary containing required model card fields
            registered_model_name: Optional name to register the model under
            await_registration_for: Number of seconds to wait for model registration
            artifact_path: Path to the model artifacts within the run
            
        Returns:
            Dictionary containing model registration details and model card info
        """
        try:
            # Get the run details
            run = mlflow.get_run(run_id)
            run_data = run.to_dictionary()
            
            # Set the actual model name that will be used
            final_model_name = registered_model_name or model_name
            
            # Get model URI
            model_uri = f"runs:/{run_id}/{artifact_path}"
            
            # Register the model
            logger.info(f"Registering model: {final_model_name} from run: {run_id}")
            model_version = mlflow.register_model(
                model_uri=model_uri,
                name=final_model_name,
                await_registration_for=await_registration_for
            )
            
            # Prepare model registration details
            model_details = {
                "name": model_version.name,
                "version": model_version.version,
                "run_id": model_version.run_id,
                "status": model_version.status,
                "model_uri": model_uri
            }
            
            # Extract metrics and params from run for model card
            metrics = run_data.get('data', {}).get('metrics', {})
            params = run_data.get('data', {}).get('params', {})
            
            # Prepare default performance metrics if not provided
            if 'performance' not in model_card_data:
                model_card_data['performance'] = {
                    'overall': {
                        'precision': metrics.get('precision', 0.0),
                        'recall': metrics.get('recall', 0.0),
                        'f1_score': metrics.get('f1_score', 0.0),
                        'total_count': metrics.get('total_count', 0)
                    }
                }
            
            # Prepare default training data if not provided
            if 'training_data' not in model_card_data:
                model_card_data['training_data'] = {
                    'dataset': params.get('dataset', 'Unknown'),
                    'description': params.get('dataset_description', 'No description provided'),
                    'preprocessing': params.get('preprocessing', 'No preprocessing details'),
                    'split': {
                        'train': int(params.get('train_samples', 0)),
                        'test': int(params.get('test_samples', 0)),
                        'validation': int(params.get('val_samples', 0))
                    }
                }
            

            safe_model_name = quote_plus(model_name.lower())
            endpoint_url = f"http://{safe_model_name}-service:8000/"
            model_card_data.update({
                "name": final_model_name,
                "version": str(model_version.version),
                "inference": {
                    "endpoint": endpoint_url
                }
            })
            
            # Validate and create model card
            validated_card = ModelCardSchema(**model_card_data).dict()
            model_card = self.create_model_card_from_json(validated_card)
            
            return {
                "model_registration": model_details,
                "model_card": model_card
            }
            
        except Exception as e:
            logger.error(f"Model registration failed: {str(e)}")
            raise



    @property
    def mlflow(self) -> mlflow:
        """
        Returns the mlflow module.

        Returns:
            mlflow: The MLflow module instance.
        """
        return mlflow

    def __enter__(self) -> "MLflowClient":
        """Support using client as a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cleanup when exiting context."""
        self.end_run()


    def create_model_card_from_json(self, json_data: Union[Dict, str, Path]) -> Dict:
        """
        Create model card from JSON data or file.

        Args:
            json_data: Either a dictionary, JSON string, or path to JSON file

        Returns:
            Dict: Created model card data
        """
        try:
            if isinstance(json_data, (str, Path)):
                if Path(json_data).exists():
                    with open(json_data, "r") as f:
                        data = json.load(f)
                else:
                    data = json.loads(json_data)
            else:
                data = json_data

            validated = ModelCardSchema(**data).dict()

            return self.request("POST", f"model-card", json=validated)
        except Exception as e:
            logger.error(f"Failed to create model card from JSON: {str(e)}")
            raise

    def update_model_card(self, model_id: str, updates: Dict) -> Dict:
        """
        Update an existing model card.

        Args:
            model_id: ID of the model card to update
            updates: Dictionary of fields to update

        Returns:
            Dict: Updated model card data
        """
        try:
            return self.request("PATCH", f"model-card/{model_id}", json=updates)
        except Exception as e:
            logger.error(f"Failed to update model card {model_id}: {str(e)}")
            raise

    def delete_model_card(self, model_id: str) -> bool:
        """
        Delete a model card.

        Args:
            model_id: ID of the model card to delete

        Returns:
            bool: True if deletion was successful
        """
        try:
            self.request("DELETE", f"model-card/{model_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete model card {model_id}: {str(e)}")
            raise
