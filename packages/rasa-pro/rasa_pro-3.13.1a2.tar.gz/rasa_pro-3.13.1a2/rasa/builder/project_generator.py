"""Service for generating Rasa projects from prompts."""

import json
import os
import shutil
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, List, Optional

import structlog

from rasa.builder import config
from rasa.builder.exceptions import ProjectGenerationError, ValidationError
from rasa.builder.llm_service import get_skill_generation_messages, llm_service
from rasa.builder.validation_service import validate_project
from rasa.cli.scaffold import ProjectTemplateName, create_initial_project
from rasa.shared.core.flows import yaml_flows_io
from rasa.shared.importers.importer import TrainingDataImporter
from rasa.shared.utils.yaml import dump_obj_as_yaml_to_string
from rasa.utils.io import subpath

structlogger = structlog.get_logger()


class ProjectGenerator:
    """Service for generating Rasa projects from skill descriptions."""

    def __init__(self, project_folder: str):
        """Initialize the project generator with a folder for file persistence.

        Args:
            project_folder: Path to the folder where project files will be stored
        """
        self.project_folder = Path(project_folder)
        self.project_folder.mkdir(parents=True, exist_ok=True)

    def init_from_template(self, template: ProjectTemplateName):
        """Create the initial project files."""
        self.cleanup()
        create_initial_project(self.project_folder.as_posix(), template)

    async def generate_project_with_retries(
        self,
        skill_description: str,
        template: ProjectTemplateName,
        max_retries: Optional[int] = None,
    ) -> Dict[str, str]:
        """Generate a Rasa project with retry logic for validation failures.

        Args:
            skill_description: Natural language description of the skill
            rasa_config: Rasa configuration dictionary
            template: Project template to use for the initial project
            max_retries: Maximum number of retry attempts

        Returns:
            Dictionary of generated file contents (filename -> content)

        Raises:
            ProjectGenerationError: If generation fails after all retries
        """
        if max_retries is None:
            max_retries = config.MAX_RETRIES

        self.init_from_template(template)

        project_data = self._get_bot_data_for_llm()

        initial_messages = get_skill_generation_messages(
            skill_description, project_data
        )

        async def _generate_with_retry(
            messages: List[Dict[str, Any]], attempts_left: int
        ):
            try:
                # Generate project data using LLM
                project_data = await llm_service.generate_rasa_project(messages)

                # Update stored bot data
                self._update_bot_files_from_llm_response(project_data)

                bot_files = self.get_bot_files()
                structlogger.info(
                    "project_generator.generated_project",
                    attempts_left=attempts_left,
                    files=list(bot_files.keys()),
                )

                # Validate the generated project
                await self._validate_generated_project()

                structlogger.info(
                    "project_generator.validation_success", attempts_left=attempts_left
                )

                return bot_files

            except ValidationError as e:
                structlogger.error(
                    "project_generator.validation_error",
                    error=str(e),
                    attempts_left=attempts_left,
                )

                if attempts_left <= 0:
                    raise ProjectGenerationError(
                        f"Failed to generate valid Rasa project: {e}", max_retries
                    )

                # Create error feedback for next attempt
                error_feedback_messages = messages + [
                    {
                        "role": "assistant",
                        "content": json.dumps(project_data),
                    },
                    {
                        "role": "user",
                        "content": dedent(f"""
                            Previous attempt failed validation with error: {e}

                            Please fix the issues and generate a valid Rasa project.
                            Pay special attention to:
                            - Proper YAML syntax
                            - Required fields in domain and flows
                            - Consistent naming between flows and domain
                            - Valid slot types and mappings
                        """).strip(),
                    },
                ]

                return await _generate_with_retry(
                    error_feedback_messages, attempts_left - 1
                )

            except Exception as e:
                structlogger.error(
                    "project_generator.generation_error",
                    error=str(e),
                    attempts_left=attempts_left,
                )

                if attempts_left <= 0:
                    raise ProjectGenerationError(
                        f"Failed to generate Rasa project: {e}", max_retries
                    )

                # For non-validation errors, retry with original messages
                return await _generate_with_retry(initial_messages, attempts_left - 1)

        return await _generate_with_retry(initial_messages, max_retries)

    async def _validate_generated_project(self):
        """Validate the generated project using the validation service."""
        importer = self._create_importer()
        validation_error = await validate_project(importer)

        if validation_error:
            raise ValidationError(validation_error)

    def _create_importer(self) -> TrainingDataImporter:
        """Create a training data importer from the current bot files."""
        try:
            return TrainingDataImporter.load_from_config(
                config_path=self.project_folder / "config.yml",
                domain_path=self.project_folder / "domain.yml",
                training_data_paths=[
                    self.project_folder / "data",
                ],
                args={},
            )

        except Exception as e:
            raise ValidationError(f"Failed to create importer: {e}")

    def get_bot_files(self) -> Dict[str, str]:
        """Get the current bot files by reading from disk."""
        bot_files = {}

        for file in self.project_folder.glob("**/*"):
            # Skip directories
            if not file.is_file():
                continue

            relative_path = file.relative_to(self.project_folder)

            # Skip hidden files and directories (any path component starting with '.')
            if any(part.startswith(".") for part in relative_path.parts):
                continue

            # exclude the project_folder / models folder
            if relative_path.parts[0] == "models":
                continue

            # Read file content and store with relative path as key
            bot_files[relative_path.as_posix()] = file.read_text(encoding="utf-8")

        return bot_files

    def _get_bot_data_for_llm(self) -> Dict[str, Any]:
        """Get the current bot data for the LLM."""
        file_importer = self._create_importer()

        # only include data created by the user (or the builder llm)
        # avoid including to many defaults that are not customized
        domain = file_importer.get_user_domain()
        flows = file_importer.get_user_flows()

        return {
            "domain": domain.as_dict(should_clean_json=True),
            "flows": yaml_flows_io.get_flows_as_json(flows, should_clean_json=True),
        }

    def _path_for_flow(self, flow_id: str) -> str:
        """Get the path for a flow."""
        if flow_id.startswith("pattern_"):
            return f"data/patterns/{flow_id}.yml"
        else:
            return f"data/flows/{flow_id}.yml"

    def _update_bot_files_from_llm_response(self, project_data: Dict[str, Any]):
        """Update the bot files with generated data by writing to disk."""
        files = {"domain.yml": dump_obj_as_yaml_to_string(project_data["domain"])}
        # split up flows into one file per flow in the /flows folder
        for flow_id, flow_data in project_data["flows"].get("flows", {}).items():
            flow_file_path = self._path_for_flow(flow_id)
            single_flow_file_data = {"flows": {flow_id: flow_data}}
            files[flow_file_path] = dump_obj_as_yaml_to_string(single_flow_file_data)

        # removes any other flows that the LLM didn't generate
        self._cleanup_flows()
        self.update_bot_files(files)

    def _cleanup_flows(self):
        """Cleanup the flows folder."""
        flows_folder = self.project_folder / "data" / "flows"
        if flows_folder.exists():
            shutil.rmtree(flows_folder)
        flows_folder.mkdir(parents=True, exist_ok=True)

    def update_bot_files(self, files: Dict[str, str]):
        """Update bot files with new content by writing to disk."""
        for filename, content in files.items():
            file_path = Path(subpath(self.project_folder, filename))
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")

    def cleanup(self):
        """Cleanup the project folder."""
        # remove all the files and folders in the project folder resulting
        # in an empty folder
        for filename in os.listdir(self.project_folder):
            file_path = os.path.join(self.project_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                structlogger.error(
                    "project_generator.cleanup_error",
                    error=str(e),
                    file_path=file_path,
                )
