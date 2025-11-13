from os.path import join
from lxml import etree
import logging

logger = logging.getLogger(__name__)

def remove_duplicate_empty(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Pulisce un file XML:
      1. Rimuove elementi duplicati (stesso tag e contenuto identico, incluso i figli).
      2. Rimuove ricorsivamente elementi completamente vuoti.
    """
    try:
        logger.info("Processing XML file for duplicate/empty cleanup: %s", xml_file)
        input_path = join(input_folder, xml_file)

        # Parse XML
        tree = etree.parse(input_path)
        root = tree.getroot()

        task_name = "remove_duplicate_empty"
        changelog = context.get_changelog(xml_file) if context else None

        # --- Step 1: Remove duplicates (based on canonical XML) ---
        def remove_duplicates(element):
            seen = set()
            for child in list(element):
                signature = etree.tostring(child, method="c14n")  # full subtree signature
                if signature in seen:
                    logger.debug("Removing duplicate <%s>", child.tag)
                    element.remove(child)
                    if changelog:
                        changelog.log_delete(task_name, field=child.tag, old_value=child.text)
                else:
                    seen.add(signature)
                    remove_duplicates(child)

        remove_duplicates(root)

        # --- Step 2: Remove empty elements ---
        def remove_empty_elements(element):
            for child in list(element):
                remove_empty_elements(child)
            if (
                (not element.text or not element.text.strip())
                and not element.attrib
                and len(element) == 0
            ):
                parent = element.getparent()
                if parent is not None:
                    logger.debug("Removing empty element <%s>", element.tag)
                    parent.remove(element)

        remove_empty_elements(root)

        # --- Write output file ---
        output_path = join(output_folder, xml_file)
        tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)
        logger.info("Cleaned XML written to: %s", output_path)

        return output_path

    except Exception as e:
        logger.error("Error while cleaning XML file %s: %s", xml_file, e)
        raise
