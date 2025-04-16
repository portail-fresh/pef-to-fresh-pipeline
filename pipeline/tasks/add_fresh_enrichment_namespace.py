from os.path import join
import logging
from pipeline.utils.xslt_tools import execute_xsl_transformation
from pipeline.utils.load_config import load_config

logger = logging.getLogger(__name__)

def add_fresh_enrichment_namespace(xml_file: str, input_folder: str, output_folder: str):
    """
    Applies an XSLT transformation to an XML file.
    
    Args:
        xml_file: The name of the XML file to transform.
        input_folder: Folder containing the XML file.
        output_folder: Folder where the transformed output will be saved.
        xsl_file: Path to the XSL file to apply.
    
    Returns:
        The path to the transformed output file.
    """
    try:
        logger.info("Applying XSLT transformation to XML file: %s", xml_file)
        input_path = join(input_folder, xml_file)
        
        config = load_config("folders.yaml")

        # Configuring API URL and key
        input_files_folder=config.get('xslt_files_folder')
        
        xsl_file=join(input_files_folder,'add-enrichment-namespace.xsl')

        # Execute the transformation
        transformed_output = execute_xsl_transformation(input_path, xsl_file)

        # Define and write to output file
        output_path = join(output_folder, f"{xml_file}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transformed_output)

        logger.info("Successfully wrote transformed file: %s", output_path)
        return output_path

    except Exception as e:
        logger.error("An error occurred while transforming the file %s: %s", xml_file, e)
        raise