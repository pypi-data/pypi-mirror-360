""" This module contains the PipelineManager class for creating and managing pipelines. """

import httpx
import yaml

from modelhub.core import ModelHubAPIException, ModelHubResourceNotFoundException

from ..core import BaseClient
from ..models import PipelineCreateRequest, SubmitPipelineRequest
from ..utils import encode_file, setup_logger

logger = setup_logger(__name__)


class PipelineManager(BaseClient):
    """Manager for creating and managing pipelines."""

    def _process_stage_defaults(self, stage):
        """Process default values for a stage."""
        # Ensure depends_on is a list
        if "depends_on" not in stage:
            stage["depends_on"] = []
        elif stage["depends_on"] is None:
            stage["depends_on"] = []

        # Ensure other fields have proper defaults
        stage["params"] = stage.get("params", {})
        stage["tolerations"] = stage.get("tolerations", [])
        stage["node_selector"] = stage.get("node_selector", {})

    def _process_stage_script_requirements(self, stage):
        """Process script and requirements for a stage."""
        # Handle script encoding
        if "script" in stage and stage["script"]:
            stage["script"] = encode_file(stage["script"])

        # Handle requirements encoding
        if "requirements" in stage and stage["requirements"]:
            stage["requirements"] = encode_file(stage["requirements"])

    def _validate_blob_storage_config(self, stage):
        """Validate blob storage configuration for a stage."""
        if "blob_storage_config" in stage and stage["blob_storage_config"]:
            blob_storage_config = stage["blob_storage_config"]
            required_fields = ["container", "blob_url", "mount_path"]

            if not all(key in blob_storage_config for key in required_fields):
                raise ModelHubAPIException(
                    f"Invalid blob_storage_config for stage {stage['name']}. "
                    "It must include 'container', 'blob_url', and 'mount_path'."
                )

    def _initialize_artifacts(self, stage):
        """Initialize artifacts structure for a stage."""
        if "artifacts" not in stage:
            return

        # Ensure structure is correct
        if not isinstance(stage["artifacts"], dict):
            raise ModelHubAPIException(
                f"Invalid artifacts configuration for stage {stage['name']}"
            )

        # Initialize inputs/outputs if not present
        if "inputs" not in stage["artifacts"]:
            stage["artifacts"]["inputs"] = []
        if "outputs" not in stage["artifacts"]:
            stage["artifacts"]["outputs"] = []

    def _validate_artifact_config(self, stage):
        """Validate artifact configuration for a stage."""
        if "artifacts" not in stage:
            return

        # Validate artifact configurations
        for artifact_type in ["inputs", "outputs"]:
            if not isinstance(stage["artifacts"][artifact_type], list):
                stage["artifacts"][artifact_type] = []

            for artifact in stage["artifacts"][artifact_type]:
                if (
                    not isinstance(artifact, dict)
                    or "name" not in artifact
                    or "path" not in artifact
                ):
                    raise ModelHubAPIException(
                        f"Invalid artifact configuration in {artifact_type} for stage {stage['name']}"
                    )

                # Set default archive option if not specified (for outputs)
                if artifact_type == "outputs" and "archive" not in artifact:
                    artifact["archive"] = {"none": {}}

    def load_config(self, config_path, pyproject_path=None):
        """
        Loads the pipeline configuration from a YAML file.

        Args:
            config_path (str): Path to the configuration file.
            pyproject_path (str, optional): Path to the pyproject.toml file.

        Returns:
            PipelineCreateRequest: The parsed pipeline request object.

        Raises:
            ModelHubAPIException: If the configuration is invalid.
        """
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if pyproject_path is not None:
            config["pyproject"] = encode_file(pyproject_path)

        # Process each stage
        for stage in config["stages"]:
            self._process_stage_defaults(stage)
            self._process_stage_script_requirements(stage)
            self._validate_blob_storage_config(stage)
            self._initialize_artifacts(stage)
            self._validate_artifact_config(stage)

        pipeline_request = PipelineCreateRequest(**config)

        return pipeline_request

    def _build_artifact_maps(self, pipeline_request):
        """
        Build artifact output map (stage_name -> [artifact_names]).

        Args:
            pipeline_request: The pipeline request object

        Returns:
            dict: A mapping of stage names to lists of artifact names
        """
        artifact_outputs = {}
        for stage in pipeline_request.stages:
            if stage.artifacts and stage.artifacts.outputs:
                artifact_outputs[stage.name] = [
                    artifact.name for artifact in stage.artifacts.outputs
                ]
            else:
                artifact_outputs[stage.name] = []

        return artifact_outputs

    def validate_pipeline(self, config_path=None, pipeline_request=None):
        """
        Validates a pipeline configuration to ensure all artifact dependencies are correctly set up.

        Args:
            config_path (str, optional): Path to pipeline YAML file.
            pipeline_request (PipelineCreateRequest, optional): Pipeline request object.

        Returns:
            dict: Validation results with any warnings or errors.
        """
        if config_path and not pipeline_request:
            pipeline_request = self.load_config(config_path)

        if not pipeline_request:
            raise ValueError("Either config_path or pipeline_request must be provided")

        validation_results = {"valid": True, "warnings": [], "errors": []}

        # Build artifact output map (stage_name -> [artifact_names])
        artifact_outputs = self._build_artifact_maps(pipeline_request)

        # Validate each stage
        for stage in pipeline_request.stages:
            # Skip if no artifacts
            if not stage.artifacts or not stage.artifacts.inputs:
                continue

            # For each input artifact, check if it's provided by a dependency
            self._validate_stage_artifacts(stage, artifact_outputs, validation_results)

        return validation_results

    def _validate_stage_artifacts(self, stage, artifact_outputs, validation_results):
        """
        Validate that a stage's input artifacts are correctly provided by dependencies.

        Args:
            stage: The stage to validate
            artifact_outputs: Mapping of stage names to their output artifacts
            validation_results: Dictionary to collect validation results
        """
        for input_artifact in stage.artifacts.inputs:
            artifact_found = False
            direct_dependency_found = False

            # Check if any direct dependency provides this artifact
            for dep_name in stage.depends_on:
                if (
                    dep_name in artifact_outputs
                    and input_artifact.name in artifact_outputs[dep_name]
                ):
                    artifact_found = True
                    direct_dependency_found = True
                    break

            # If not found in direct dependencies, check if it's available somewhere else
            if not artifact_found:
                for other_stage_name, outputs in artifact_outputs.items():
                    if input_artifact.name in outputs:
                        artifact_found = True
                        validation_results["warnings"].append(
                            f"Stage '{stage.name}' requires artifact '{input_artifact.name}' which is produced by "
                            f"stage '{other_stage_name}', but '{other_stage_name}' is not in the dependencies."
                        )
                        break

            # If artifact isn't produced anywhere
            if not artifact_found:
                validation_results["errors"].append(
                    f"Stage '{stage.name}' requires artifact '{input_artifact.name}' but no stage produces it."
                )
                validation_results["valid"] = False

            # If artifact is found but not from a direct dependency
            elif not direct_dependency_found:
                validation_results["errors"].append(
                    f"Stage '{stage.name}' requires artifact '{input_artifact.name}' but doesn't depend on "
                    f"the stage that produces it."
                )
                validation_results["valid"] = False

    def start_pipeline(self, config_path, pyproject_path=None, validate_only=False):
        """
        Starts a pipeline based on the configuration file.

        Args:
            config_path (str): The path to the YAML configuration file.
            pyproject_path (str, optional): The path to the pyproject. Defaults to None.
            validate_only (bool, optional): Only validate, don't submit. Defaults to False.

        Returns:
            dict: The response from the API or validation results.
        """
        pipeline_request = self.load_config(config_path, pyproject_path)

        # Always validate
        validation_results = self.validate_pipeline(pipeline_request=pipeline_request)

        # If validation failed, or only validating, return results
        if not validation_results["valid"] or validate_only:
            return validation_results

        # Otherwise, continue with pipeline creation and submission
        pipeline = self.create_or_update(config_path, pyproject_path)
        return self.submit(pipeline["pipeline_id"])

    def fix_pipeline_configuration(self, config_path, output_path=None):
        """
        Fixes pipeline configuration by automatically adding missing dependencies
        based on artifact requirements.

        Args:
            config_path (str): Path to pipeline YAML file.
            output_path (str, optional): Path to save the fixed configuration.
                                        If None, modifies the original file.

        Returns:
            dict: Information about fixes made.
        """
        if not output_path:
            output_path = config_path

        # Load YAML directly to preserve formatting and comments
        with open(config_path, "r", encoding="utf-8") as f:
            pipeline_yaml = yaml.safe_load(f)

        # Build artifact output map (stage_name -> [artifact_names])
        artifact_outputs = {}
        for stage in pipeline_yaml["stages"]:
            artifacts = stage.get("artifacts", {})
            if artifacts and artifacts.get("outputs"):
                artifact_outputs[stage["name"]] = [
                    artifact["name"] for artifact in artifacts["outputs"]
                ]
            else:
                artifact_outputs[stage["name"]] = []

        # Track fixes made
        fixes = {"dependencies_added": []}

        # Fix each stage
        self._fix_stage_dependencies(pipeline_yaml, artifact_outputs, fixes)

        # Save the modified configuration
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(pipeline_yaml, f, default_flow_style=False, sort_keys=False)

        return fixes

    def _fix_stage_dependencies(self, pipeline_yaml, artifact_outputs, fixes):
        """Fix dependencies for each stage in the pipeline."""
        for stage in pipeline_yaml["stages"]:
            artifacts = stage.get("artifacts", {})
            if not artifacts or not artifacts.get("inputs"):
                continue

            # Ensure depends_on is a list
            if "depends_on" not in stage:
                stage["depends_on"] = []

            # For each input artifact, check if the dependency is missing
            for input_artifact in artifacts.get("inputs", []):
                artifact_name = input_artifact["name"]
                dependency_found = False

                # Check if any direct dependency provides this artifact
                for dep_name in stage.get("depends_on", []):
                    if (
                        dep_name in artifact_outputs
                        and artifact_name in artifact_outputs[dep_name]
                    ):
                        dependency_found = True
                        break

                # If not found, find who provides it and add dependency
                if not dependency_found:
                    self._add_missing_dependency(
                        stage, artifact_name, artifact_outputs, fixes
                    )

    def _add_missing_dependency(self, stage, artifact_name, artifact_outputs, fixes):
        """Add a missing dependency to a stage."""
        for provider_name, outputs in artifact_outputs.items():
            if artifact_name in outputs and provider_name != stage["name"]:
                if provider_name not in stage["depends_on"]:
                    stage["depends_on"].append(provider_name)
                    fixes["dependencies_added"].append(
                        {
                            "stage": stage["name"],
                            "added_dependency": provider_name,
                            "for_artifact": artifact_name,
                        }
                    )

    def create_or_update(self, config_path, pyproject_path=None):
        """
        Creates or updates a pipeline based on the configuration file.

        Args:
            config_path (str): The path to the YAML configuration file.
            pyproject_path (str, optional): The path to the pyproject. Defaults to None.

        Returns:
            dict: The response from the API.
        """
        pipeline_request = self.load_config(config_path, pyproject_path)
        existing_pipeline = self.search_pipeline(pipeline_request.name)
        if existing_pipeline:
            return self.put(
                f"pipelines/{existing_pipeline['pipeline_id']}",
                json=pipeline_request.dict(),
            )
        else:
            return self.post("pipelines", json=pipeline_request.dict())

    def search_pipeline(self, name):
        """
        Searches for a pipeline by name.

        Args:
            name (str): The name of the pipeline to search for.

        Returns:
            dict: The existing pipeline if found, None otherwise.
        """
        try:
            existing_pipeline = self.get(f"pipelines/search?name={name}")
            return existing_pipeline
        except ModelHubResourceNotFoundException:
            return None
        except httpx.HTTPError as e:
            raise ModelHubAPIException(f"Server error: {e}") from e

    def submit(self, pipeline_id):
        """
        Submits a pipeline for execution.

        Args:
            pipeline_id (str): The ID of the pipeline to submit.

        Returns:
            dict: The response from the API.
        """
        # Get base URL, client ID and client secret from credential
        base_url = getattr(self.credential, "_modelhub_url", None)
        client_id = getattr(self.credential, "_client_id", None)
        client_secret = getattr(self.credential, "_client_secret", None)

        submit_request = SubmitPipelineRequest(
            modelhub_base_url=base_url,
            modelhub_client_id=client_id,
            modelhub_client_secret=client_secret,
        )
        return self.post(f"pipelines/{pipeline_id}/submit", json=submit_request.dict())
