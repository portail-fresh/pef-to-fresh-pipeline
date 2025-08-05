import pandas as pd
from os import listdir
from os.path import isfile, join
from pipeline.utils.PipelineContext import PipelineContext


def get_xml_files(folder: str, context: PipelineContext):
    """
    Retrieves a list of XML files from the specified folder, excluding files
    whose IDs are listed in the Excel exclusion file.

    Args:
        folder (str): The path to the folder from which to retrieve XML files.
        context (PipelineContext): The pipeline context for logging.

    Returns:
        list: A list of XML file names in the specified folder, excluding files with certain IDs.

    Raises:
        FileNotFoundError: If the specified folder or Excel file does not exist.
        Exception: For other unexpected errors.
    """
    try:
        logger = context.get_logger()
        logger.info("Retrieving XML files from folder: %s", folder)

        # Read the Excel file with the list of IDs to exclude
        exclusion_path = join("files", "utility-files", "id-fiches-exclus-fresh.xlsx")
        df = pd.read_excel(exclusion_path)

        # Extract the list of IDs to exclude (as strings, to match filename format)
        excluded_ids = set(df['ID'].astype(str))

        # Get the list of files in the folder
        all_files = [f for f in listdir(folder) if isfile(join(folder, f))]

        # Filter out files whose first part (before "_") is in the excluded IDs
        xml_files = [
            f for f in all_files
            if f.endswith('.xml') and f.split('_')[0] not in excluded_ids
        ]

        logger.info("Retrieved %d XML files after exclusions", len(xml_files))
        return xml_files

    except FileNotFoundError as fnf_error:
        logger.error("Folder or Excel file not found: %s. Error: %s", folder, fnf_error)
        raise
    except Exception as e:
        logger.error("An error occurred while retrieving XML files: %s", e)
        raise
