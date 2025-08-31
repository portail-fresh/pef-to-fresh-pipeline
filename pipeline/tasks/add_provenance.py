from os.path import join
from lxml import etree

FRESH_NAMESPACE_URI = "urn:fresh-enrichment:v1"


def add_provenance(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Adds an element <fresh:Provenance> to the root of the XML file,
    with fixed value "PEF". This element is always added, regardless
    of existing content.
    
    Args:
        xml_file: The name of the XML file to modify.
        input_folder: Folder containing the XML file.
        output_folder: Folder to write the updated XML file.
        context (optional): Shared context object containing changelog, logger, etc.
    
    Returns:
        Path to the updated XML file.
    """
    logger = context.get_logger() if context else None
    try:
        if logger:
            logger.info("Processing XML file to add provenance element: %s", xml_file)

        input_path = join(input_folder, xml_file)

        # Parse XML
        tree = etree.parse(input_path)
        root = tree.getroot()

        # Register 'fresh' prefix in namespace map if needed
        nsmap = root.nsmap.copy()
        if "fresh" not in nsmap:
            nsmap["fresh"] = FRESH_NAMESPACE_URI

        task_name = "add_provenance"
        changelog = context.get_changelog(xml_file) if context else None

        # Define tag
        tag_prov = f"{{{FRESH_NAMESPACE_URI}}}Provenance"

        # Create and append <fresh:Provenance>
        elem_prov = etree.Element(tag_prov, nsmap=nsmap)
        elem_prov.text = "PEF"
        root.append(elem_prov)

        if logger:
            logger.info("Added <fresh:Provenance> with value 'PEF'")
        if changelog:
            changelog.log_add(task_name, field="fresh:Provenance", new_value="PEF")

        # Write output
        output_path = join(output_folder, xml_file)
        tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)

        if logger:
            logger.info("Successfully wrote updated XML file: %s", output_path)

        return output_path

    except Exception as e:
        if logger:
            logger.error("Error while processing file %s: %s", xml_file, e)
        raise
