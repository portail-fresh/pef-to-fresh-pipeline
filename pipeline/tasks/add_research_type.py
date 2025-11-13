from os.path import join
from lxml import etree
import logging

logger = logging.getLogger(__name__)

FRESH_NAMESPACE_URI = "urn:fresh-enrichment:v1"

def add_research_type(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Adds two elements <fresh:ResearchTypeFR> and <fresh:ResearchTypeEN> 
    to the root of the XML file, with fixed values:
      - ResearchTypeFR: "Observationnelle"
      - ResearchTypeEN: "Observational Study"
    These elements are always added, regardless of existing content.
    
    Args:
        xml_file: The name of the XML file to modify.
        input_folder: Folder containing the XML file.
        output_folder: Folder to write the updated XML file.
        context (optional): Shared context object containing changelog and other runtime data.
    
    Returns:
        Path to the updated XML file.
    """
    try:
        logger.info("Processing XML file to add research type elements: %s", xml_file)
        input_path = join(input_folder, xml_file)

        # Parse XML
        tree = etree.parse(input_path)
        root = tree.getroot()

        # Register 'fresh' prefix in namespace map if needed
        nsmap = root.nsmap.copy()
        if "fresh" not in nsmap:
            nsmap["fresh"] = FRESH_NAMESPACE_URI

        task_name = "add_research_type"
        changelog = context.get_changelog(xml_file) if context else None

        # Define tags
        tag_fr = f"{{{FRESH_NAMESPACE_URI}}}ResearchTypeFR"
        tag_en = f"{{{FRESH_NAMESPACE_URI}}}ResearchTypeEN"

        # Create and append <fresh:ResearchTypeFR>
        elem_fr = etree.Element(tag_fr, nsmap=nsmap)
        elem_fr.text = "Etude observationnelle"
        root.append(elem_fr)
        logger.info("Added <fresh:ResearchTypeFR> with value 'Etude observationnelle'")
        if changelog:
            changelog.log_add(task_name, field="fresh:ResearchTypeFR", new_value="Etude observationnelle")

        # Create and append <fresh:ResearchTypeEN>
        elem_en = etree.Element(tag_en, nsmap=nsmap)
        elem_en.text = "Observational Study"
        root.append(elem_en)
        logger.info("Added <fresh:ResearchTypeEN> with value 'Observational Study'")
        if changelog:
            changelog.log_add(task_name, field="fresh:ResearchTypeEN", new_value="Observational Study")

        # Write output
        output_path = join(output_folder, xml_file)
        tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)
        logger.info("Successfully wrote updated XML file: %s", output_path)

        return output_path

    except Exception as e:
        logger.error("Error while processing file %s: %s", xml_file, e)
        raise
