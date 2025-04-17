from os.path import join
import logging
from pipeline.utils.xslt_tools import execute_xsl_transformation
from pipeline.utils.load_config import load_config

logger = logging.getLogger(__name__)

def split_fr_en(xml_file: str, input_folder: str, output_folder: str):
    try:
        logger.info("Applying XSLT transformation to XML file: %s", xml_file)
        input_path = join(input_folder, xml_file)

        config = load_config("folders.yaml")
        xslt_files_folder = config.get('xslt_files_folder')

        id_value = xml_file.split('_')[0]

        # Francese
        fr_xsl_file = join(xslt_files_folder, 'split-fr.xsl')
        fr_result = execute_xsl_transformation(input_path, fr_xsl_file)
        fr_output_file = join(output_folder, f"{id_value}-fr.xml")
        with open(fr_output_file, "w", encoding="utf-8") as f:
            f.write(fr_result)

        # Inglese
        en_xsl_file = join(xslt_files_folder, 'split-en.xsl')
        en_result = execute_xsl_transformation(input_path, en_xsl_file)
        en_output_file = join(output_folder, f"{id_value}-en.xml")
        with open(en_output_file, "w", encoding="utf-8") as f:
            f.write(en_result)

        logger.info("Successfully wrote French output to: %s", fr_output_file)
        logger.info("Successfully wrote English output to: %s", en_output_file)

        return fr_output_file, en_output_file

    except Exception as e:
        logger.error("An error occurred while transforming the file %s: %s", xml_file, e)
        raise
