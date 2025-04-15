import logging
from os import listdir
from os.path import isfile, join

# Create a logger for this module
logger = logging.getLogger(__name__)


def get_xml_files(folder: str):
    """
    Retrieves a list of XML files from the specified folder.

    Args:
        folder (str): The path to the folder from which to retrieve XML files.

    Returns:
       
        xml_files (list): A list of XML file names in the specified folder.
    
    Raises:
        FileNotFoundError: If the specified folder does not exist.
        Exception: For other unexpected errors.
    """
    try:
        logger.info("Retrieving XML files from folder: %s", folder)

        # Get the list of files in the specified folder
        xml_files = [f for f in listdir(folder) if isfile(join(folder, f))]

        #logger.info("Retrieved %d XML files: %s", len(xml_files), xml_files)
        
        return xml_files

    except FileNotFoundError as fnf_error:
        logger.error("Folder not found: %s. Error: %s", folder, fnf_error)
        raise  # Re-raise the exception after logging
    except Exception as e:
        logger.error("An error occurred while retrieving XML files: %s", e)
        raise  # Re-raise the exception after logging