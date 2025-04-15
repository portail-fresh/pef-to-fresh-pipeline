from os.path import join
from lxml import etree
import logging


logger = logging.getLogger(__name__)

def correct_special_characters(xml_file: str, input_folder: str, output_folder: str):
    """
    Corrects an XML file by replacing '&' with '&amp;' and removing occurrences of byte '\x01'.
    """
    

    try:
        logger.info("Correcting XML file: %s", xml_file)
        file_path = join(input_folder, xml_file)

        # Step 1: Read the XML file and make replacements
        with open(file_path, 'rb') as fp:
            xml_string = fp.read().replace(b'&', b'&amp;').replace(b'\x01', b'').replace(b'\x02', b'')

        # Step 2: Parse the corrected XML string to ensure it's valid XML
        tree = etree.fromstring(xml_string)

        # Create an ElementTree object from the parsed XML element
        element_tree = etree.ElementTree(tree)

        # Step 3: Define the output file path and save the corrected XML
        output_file_path = join(output_folder, xml_file)
        element_tree.write(output_file_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)

        #logger.info("Successfully corrected and saved XML file: %s", output_file_path)
        return output_file_path  # Prefect traccia automaticamente l'output

    except Exception as e:
        llogger.error("An error occurred while processing the file %s: %s", xml_file, e)
        raise  # Re-raise per mantenere il tracking dell'errore in Prefect UI