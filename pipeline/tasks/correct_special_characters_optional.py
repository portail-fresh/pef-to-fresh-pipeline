from os.path import join
from lxml import etree
import logging
import html

logger = logging.getLogger(__name__)

def correct_special_characters_optional(xml_file: str, input_folder: str, output_folder: str):
    """
    Cleans an XML file by replacing specific special characters, like '&#13;', 
    with readable alternatives and decoding HTML entities.
    """
    # Create a logger for this module
    
    
    try:
        logger.info("Cleaning XML file: %s", xml_file)
        file_path = join(input_folder, xml_file)

        # Parse the XML file
        tree = etree.parse(file_path)
        root = tree.getroot()

        def clean_text(text):
            if text:
                return html.unescape(text.replace("&#13;", "\n"))
            return text

        # Clean each element's text and tail content
        for elem in root.iter():
            elem.text = clean_text(elem.text)
            elem.tail = clean_text(elem.tail)

        # Save the cleaned XML
        output_file_path = join(output_folder, xml_file)
        tree.write(output_file_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)

        logger.info("Successfully cleaned and saved XML file: %s", output_file_path)
        return output_file_path  # Prefect traccia automaticamente l'output

    except Exception as e:
        logger.error("An error occurred while processing the file %s: %s", xml_file, e)
        raise  # Re-raise per il tracking dell'errore in Prefect UI