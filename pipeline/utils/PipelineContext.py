import logging
import datetime
from pathlib import Path
from pipeline.utils.load_config import load_config
from pipeline.utils.logging import setup_logging
from pipeline.utils.Changelog import Changelog  



class PipelineContext:
    """
    Context object holding shared resources and paths
    for the current pipeline run, including individual changelogs
    for each XML file.
    """
    def __init__(self):
        
        # Load folder configuration
        self.folder_config = load_config("folders.yaml")
        self.original_folder = self.folder_config.get('input_files_folder')
        self.runs_folder = self.folder_config.get('runs_folder')
        self.conversion_tables_folder = self.folder_config.get('conversion_tables_folder')

        # Create a unique folder for this run
        datetime_str = "run" + datetime.datetime.now().strftime("-%Y%m%d-%H%M%S")
        self.run_dir = Path(self.runs_folder) / datetime_str
        self.run_dir.mkdir(parents=True, exist_ok=True)
        
        self.outputs_dir = self.run_dir / "outputs"
        self.changelogs_dir = self.run_dir / "changelogs"

        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.changelogs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging configuration
        setup_logging()
        self.logger = logging.getLogger(__name__)

        # Will hold Changelog instances per XML file
        self.changelogs = {}

    def get_run_dir(self):
        return self.run_dir

    def get_outputs_dir(self):
        return self.outputs_dir

    def get_changelogs_dir(self):
        return self.changelogs_dir
    
    def get_original_folder(self):
        return self.original_folder

    def init_changelog_for_file(self, xml_file: str):
        """
        Initialize a changelog object for a given XML file if not already present.
        """
        if xml_file not in self.changelogs:
            self.changelogs[xml_file] = Changelog(
                xml_file=xml_file,
                log_dir=self.changelogs_dir
            )

    def get_changelog(self, xml_file: str):
        """
        Returns the changelog object for the given file.
        """
        return self.changelogs.get(xml_file, None)
    
    def get_logger(self):
        return self.logger
    
    def get_conversion_tables_folder(self):
        return self.conversion_tables_folder

