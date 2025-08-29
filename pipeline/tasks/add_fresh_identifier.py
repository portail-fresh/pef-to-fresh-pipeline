from os.path import join
from lxml import etree
import logging

logger = logging.getLogger(__name__)

FRESH_NAMESPACE_URI = "urn:fresh-enrichment:v1"

def add_fresh_identifier(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Adds a <fresh:ID agency="FReSH"> element to the <Metadonnees> section of the XML file, 
    if it doesn't already exist. The value is built as 'FRESH-PEF<ID>'.
    
    Args:
        xml_file: The name of the XML file to modify.
        input_folder: Folder containing the XML file.
        output_folder: Folder to write the updated XML file.
        context (optional): Shared context object containing changelog and other runtime data.
    
    Returns:
        Path to the updated XML file.
    """
    try:
        logger.info("Processing XML file to add <fresh:ID>: %s", xml_file)
        input_path = join(input_folder, xml_file)

        # Parse XML
        tree = etree.parse(input_path)
        root = tree.getroot()

        # Register 'fresh' prefix in namespace map if needed
        nsmap = root.nsmap.copy()
        if "fresh" not in nsmap:
            nsmap["fresh"] = FRESH_NAMESPACE_URI

        # Find <Metadonnees>
        metadonnees = root.find(".//Metadonnees")
        if metadonnees is None:
            raise ValueError("No <Metadonnees> element found in the XML.")

        # Get the ID
        id_elem = metadonnees.find("ID")
        if id_elem is None or not id_elem.text:
            raise ValueError("No <ID> element found inside <Metadonnees>.")

        id_value = id_elem.text.strip()
        fresh_id_value = f"FRESH-PEF{id_value}"

        # Check if <fresh:ID> exists
        xpath_expr = f"{{{FRESH_NAMESPACE_URI}}}ID"
        fresh_id_elem = metadonnees.find(xpath_expr)

        task_name = "add_fresh_identifier"
        changelog = context.get_changelog(xml_file) if context else None

        if fresh_id_elem is None:
            # Create <fresh:ID> and append it, adding agency attribute
            fresh_elem = etree.Element(xpath_expr, nsmap=nsmap)
            fresh_elem.set("agency", "FReSH")
            fresh_elem.text = fresh_id_value
            metadonnees.append(fresh_elem)
            logger.info("Added <fresh:ID agency='FReSH'> with value: %s", fresh_id_value)
            if changelog:
                changelog.log_add(task_name, field="fresh:ID[@agency='FReSH']", new_value=fresh_id_value)
        else:
            logger.info("<fresh:ID> already exists, skipping addition.")

        # Write output
        output_path = join(output_folder, xml_file)
        tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)
        logger.info("Successfully wrote updated XML file: %s", output_path)

        return output_path

    except Exception as e:
        logger.error("Error while processing file %s: %s", xml_file, e)
        raise
