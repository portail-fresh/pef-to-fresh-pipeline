import os
import datetime
import logging
import inspect
from pathlib import Path
from pipeline.utils.load_config import load_config
from pipeline.tasks import *
from pipeline.utils.logging import setup_logging
from pipeline.utils.XmlChangelog import XmlChangelog  # Assicurati che il path sia corretto

# Setup logging configuration
setup_logging()
logger = logging.getLogger(__name__)


class PipelineContext:
    """
    Context object holding shared resources and paths
    for the current pipeline run, including individual changelogs
    for each XML file.
    """
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.outputs_dir = run_dir / "outputs"
        self.changelogs_dir = run_dir / "changelogs"

        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.changelogs_dir.mkdir(parents=True, exist_ok=True)

        # Will hold XmlChangelog instances per XML file
        self.changelogs = {}

    def get_run_dir(self):
        return self.run_dir

    def get_outputs_dir(self):
        return self.outputs_dir

    def get_changelogs_dir(self):
        return self.changelogs_dir

    def init_changelog_for_file(self, xml_file: str):
        """
        Initialize a changelog object for a given XML file if not already present.
        """
        if xml_file not in self.changelogs:
            self.changelogs[xml_file] = XmlChangelog(
                xml_file=xml_file,
                log_dir=self.changelogs_dir
            )

    def get_changelog(self, xml_file: str):
        """
        Returns the changelog object for the given file.
        """
        return self.changelogs.get(xml_file, None)


def execute_task(task, xml_file, input_folder=None, output_folder=None, context=None, **kwargs):
    """
    Executes a task function with the appropriate parameters based on its signature.
    Only passes arguments that the task function explicitly accepts.
    """
    sig = inspect.signature(task)
    task_args = {}

    if 'xml_file' in sig.parameters:
        task_args['xml_file'] = xml_file
    if 'input_folder' in sig.parameters:
        task_args['input_folder'] = input_folder
    if 'output_folder' in sig.parameters:
        task_args['output_folder'] = output_folder
    if 'context' in sig.parameters:
        task_args['context'] = context

    # Add any additional keyword arguments allowed by the task
    for k, v in kwargs.items():
        if k in sig.parameters:
            task_args[k] = v

    task(**task_args)


def run_pipeline():
    """
    Executes the entire XML modification pipeline.
    """
    logger.info("Starting XML Modification Flow")

    # Load folder configuration
    config = load_config("folders.yaml")
    original_folder = config.get('input_files_folder')
    runs_folder = config.get('runs_folder')

    # Create a unique folder for this run
    datetime_str = "run" + datetime.datetime.now().strftime("-%Y%m%d-%H%M%S")
    run_temp_folder = Path(runs_folder) / datetime_str
    run_temp_folder.mkdir(parents=True, exist_ok=True)

    # Initialize the pipeline context
    context = PipelineContext(run_temp_folder)

    tasks = [
        (correct_special_characters, {}),
        (correct_special_characters_optional, {}),
        (process_collection_dates, {}),
        (add_fresh_enrichment_namespace, {}),
        (add_fresh_identifier, {}),
        #(split_fr_en, {})
    ]

    current_input_folder = Path(original_folder)

    for idx, (task, kwargs) in enumerate(tasks):
        task_name = f"{idx + 1:02d}-{task.__name__}"

        # Each task writes to its own subfolder inside outputs/
        current_output_folder = (
            context.get_outputs_dir() / task_name
            if 'output_folder' in task.__code__.co_varnames
            else None
        )

        if current_output_folder:
            current_output_folder.mkdir(parents=True, exist_ok=True)

        xml_files = get_xml_files(current_input_folder)

        for xml_file in xml_files:
            # Initialize changelog for this file
            context.init_changelog_for_file(xml_file)

            # Execute the task
            execute_task(
                task,
                xml_file,
                input_folder=current_input_folder,
                output_folder=current_output_folder,
                context=context,
                **kwargs
            )

        # Update input folder for the next task
        if current_output_folder:
            current_input_folder = current_output_folder


    logger.info("Pipeline execution completed.")


if __name__ == "__main__":
    run_pipeline()
