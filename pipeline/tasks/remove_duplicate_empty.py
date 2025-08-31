from os.path import join
from lxml import etree
import logging

logger = logging.getLogger(__name__)

def remove_duplicate_empty(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Cleans the XML file by:
    1. Removing duplicate child elements within the same parent 
       (duplicates = same tag, same text, same attributes).
    2. Recursively removing empty elements. An element is considered empty if it has:
       - no text (or only whitespace),
       - no attributes,
       - no non-empty child elements.

    Args:
        xml_file: Name of the XML file to clean.
        input_folder: Folder containing the XML file.
        output_folder: Folder to write the updated XML file.
        context (optional): Shared context object containing changelog and other runtime data.

    Returns:
        Path to the cleaned XML file.
    """
    try:
        logger.info("Processing XML file for duplicate/empty cleanup: %s", xml_file)
        input_path = join(input_folder, xml_file)

        # Parse XML
        tree = etree.parse(input_path)
        root = tree.getroot()

        task_name = "remove_duplicate_empty"
        changelog = context.get_changelog(xml_file) if context else None

        # Step 1: Remove duplicates
        def remove_duplicates(element):
            seen = set()
            for child in list(element):
                signature = (child.tag, (child.text or "").strip(), frozenset(child.attrib.items()))
                if signature in seen:
                    logger.debug("Removing duplicate element <%s> with text '%s'", child.tag, child.text)
                    element.remove(child)
                    if changelog:
                        changelog.log_delete(task_name, field=child.tag, old_value=child.text)
                else:
                    seen.add(signature)
                    remove_duplicates(child)

        remove_duplicates(root)

        # Step 2: Remove empty elements recursively
        def remove_empty_elements(element):
            for child in list(element):
                remove_empty_elements(child)
            # remove if: no text, no attribs, no children
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

        # Write cleaned XML
        output_path = join(output_folder, xml_file)
        tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)
        logger.info("Successfully wrote cleaned XML file: %s", output_path)

        return output_path

    except Exception as e:
        logger.error("Error while cleaning XML file %s: %s", xml_file, e)
        raise
