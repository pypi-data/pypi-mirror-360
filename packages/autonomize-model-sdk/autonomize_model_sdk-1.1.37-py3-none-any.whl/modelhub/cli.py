# modelhub/cli.py
import argparse
import json
import os
import sys

from modelhub.clients import PipelineManager
from modelhub.core import ModelhubCredential, ModelHubException


def setup_parsers():
    """Set up argument parsers for the CLI."""
    parser = argparse.ArgumentParser(
        description="ModelHub Pipeline CLI - Manage and execute pipelines"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create the "start" subcommand
    start_parser = subparsers.add_parser("start", help="Start pipeline execution")
    start_parser.add_argument(
        "-f",
        "--file",
        type=str,
        default="pipeline.yaml",
        help="Path to the pipeline YAML file (default: pipeline.yaml)",
    )
    start_parser.add_argument(
        "--mode",
        choices=["local", "cicd"],
        default="local",
        help="Execution mode: 'local' to run with local scripts \
        (and install dependencies using Poetry) \
        or 'cicd' for CI/CD mode",
    )
    # Only relevant in local mode: path to the pyproject.toml file.
    start_parser.add_argument(
        "--pyproject",
        type=str,
        default="pyproject.toml",
        help="Path to the pyproject.toml file (required for local mode)",
    )
    start_parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the pipeline configuration before starting",
    )

    # Create a "validate" subcommand
    validate_parser = subparsers.add_parser(
        "validate", help="Validate pipeline configuration"
    )
    validate_parser.add_argument(
        "-f",
        "--file",
        type=str,
        default="pipeline.yaml",
        help="Path to the pipeline YAML file (default: pipeline.yaml)",
    )
    validate_parser.add_argument(
        "--pyproject",
        type=str,
        default=None,
        help="Path to the pyproject.toml file (optional)",
    )
    validate_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    validate_parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix issues if possible",
    )
    validate_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to save fixed configuration (default: overwrite original)",
    )

    return parser.parse_args()


def get_pipeline_manager():
    """Initialize PipelineManager from environment variables."""
    # Ensure the required environment variables are set
    modelhub_url = os.getenv("MODELHUB_BASE_URL")
    modelhub_client_id = os.getenv("MODELHUB_CLIENT_ID")
    modelhub_client_secret = os.getenv("MODELHUB_CLIENT_SECRET")

    if not modelhub_url:
        raise ValueError("MODELHUB_BASE_URL environment variable is not set.")

    if not modelhub_client_id:
        raise ValueError("MODELHUB_CLIENT_ID environment variable is not set.")

    if not modelhub_client_secret:
        raise ValueError("MODELHUB_CLIENT_SECRET environment variable is not set.")

    # Initialize the credential
    credential = ModelhubCredential(
        modelhub_url=modelhub_url,
        client_id=modelhub_client_id,
        client_secret=modelhub_client_secret,
    )

    # Initialize the PipelineManager with the proper credentials
    return PipelineManager(
        credential=credential,
    )


def print_validation_results(results, format_type):
    """Print validation results in the specified format."""
    if format_type == "json":
        print(json.dumps(results, indent=2))
        return

    # Text format
    if results["valid"]:
        print("✅ Pipeline configuration is valid.")
    else:
        print("❌ Pipeline configuration has errors.")

    if results["warnings"]:
        print("\nWarnings:")
        for i, warning in enumerate(results["warnings"], 1):
            print(f"  {i}. {warning}")

    if results["errors"]:
        print("\nErrors:")
        for i, error in enumerate(results["errors"], 1):
            print(f"  {i}. {error}")


def print_fix_results(fixes):
    """Print the results of fixing pipeline configuration."""
    if not fixes["dependencies_added"]:
        print("\nNo fixes could be applied automatically.")
        return

    print("\nFixed by adding dependencies:")
    for fix in fixes["dependencies_added"]:
        print(
            f"  • Added '{fix['added_dependency']}' as dependency for '{fix['stage']}' "
            f"(needed for artifact '{fix['for_artifact']}')"
        )


def handle_validate_cmd(args, pipeline_manager):
    """Handle the validate subcommand."""
    pipeline_yaml = args.file
    pyproject_path = args.pyproject

    if pyproject_path and not os.path.exists(pyproject_path):
        print(
            f"Warning: pyproject.toml file not found at {pyproject_path}",
            file=sys.stderr,
        )
        pyproject_path = None

    print(f"Validating pipeline configuration: {pipeline_yaml}")
    try:
        results = pipeline_manager.validate_pipeline(pipeline_yaml)
        print_validation_results(results, args.format)

        # Try to fix if requested
        if args.fix and not results["valid"]:
            print("\nAttempting to fix configuration issues...")
            fixes = pipeline_manager.fix_pipeline_configuration(
                pipeline_yaml, args.output
            )

            output_file = args.output or pipeline_yaml
            print_fix_results(fixes)

            # Validate again to check if all issues were fixed
            if fixes["dependencies_added"]:
                results = pipeline_manager.validate_pipeline(output_file)
                if results["valid"]:
                    print(
                        f"\n✅ Pipeline configuration has been fixed and saved to {output_file}"
                    )
                else:
                    print("\n⚠️ Some issues could not be automatically fixed:")
                    for error in results["errors"]:
                        print(f"  • {error}")

        # Exit with appropriate code for validation command
        sys.exit(0 if results["valid"] else 1)

    except (ModelHubException, FileNotFoundError) as e:
        print(f"Error validating pipeline: {e}", file=sys.stderr)
        sys.exit(1)


def validate_before_start(pipeline_yaml, pipeline_manager):
    """Validate the pipeline before starting it."""
    print(f"Validating pipeline configuration: {pipeline_yaml}")
    results = pipeline_manager.validate_pipeline(pipeline_yaml)

    if not results["valid"]:
        print("❌ Pipeline configuration has errors:")
        for error in results["errors"]:
            print(f"  • {error}")
        print("\nPipeline will not be started due to validation errors.")
        sys.exit(1)

    print("✅ Pipeline configuration is valid.")

    if results["warnings"]:
        print("\nWarnings:")
        for warning in results["warnings"]:
            print(f"  • {warning}")
        print()  # Empty line for readability

    return True


def handle_start_cmd(args, pipeline_manager):
    """Handle the start subcommand."""
    pipeline_yaml = args.file
    mode = args.mode
    pyproject_path = args.pyproject if mode == "local" else None

    # Validate first if requested
    if args.validate:
        validate_before_start(pipeline_yaml, pipeline_manager)

    # Check pyproject.toml in local mode
    if mode == "local":
        if not os.path.exists(pyproject_path):
            raise ValueError(f"pyproject.toml file not found at {pyproject_path}")
        print(
            f"Starting pipeline locally using {pipeline_yaml} with pyproject file {pyproject_path} ..."
        )
        # Pass both the YAML file and the pyproject.toml path.
        pipeline = pipeline_manager.start_pipeline(pipeline_yaml, pyproject_path)
        print("Pipeline started:", pipeline)
    else:  # cicd mode
        print(f"Starting pipeline in CI/CD mode using {pipeline_yaml} ...")
        # In CI/CD mode, the Docker image already contains the required files.
        pipeline = pipeline_manager.start_pipeline(pipeline_yaml)
        print("Pipeline started in CI/CD mode:", pipeline)


def main():
    """
    PipelineManager CLI entrypoint.
    """
    args = setup_parsers()

    try:
        pipeline_manager = get_pipeline_manager()

        if args.command == "validate":
            handle_validate_cmd(args, pipeline_manager)
        elif args.command == "start":
            handle_start_cmd(args, pipeline_manager)
    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
