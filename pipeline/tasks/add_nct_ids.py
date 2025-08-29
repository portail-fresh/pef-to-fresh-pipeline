from os.path import join
from lxml import etree
import logging
import pandas as pd

logger = logging.getLogger(__name__)

FRESH_NAMESPACE_URI = "urn:fresh-enrichment:v1"

def add_nct_identifier(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Adds a <fresh:ID agency="NCT"> element to the <Metadonnees> section of the XML file
    if the PEF ID (taken from the filename) matches an entry in the Excel mapping.
    
    Multiple <fresh:ID> elements can exist; no check is performed for duplicates.
    The file is always written to the output folder, even if no mapping is found.

    Args:
        xml_file: Name of the XML file to modify (e.g., '74131_metadata.xml').
        input_folder: Folder containing the XML file.
        output_folder: Folder to write the updated XML file.
        context (optional): Shared context object containing changelog and other runtime data.

    Returns:
        Path to the updated XML file.
    """
    try:
        logger.info("Processing XML file: %s", xml_file)
        input_path = join(input_folder, xml_file)

        # Get Excel mapping path
        tables_folder = context.get_conversion_tables_folder()
        excel_path = join(tables_folder, 'nct-repartition.xlsx')

        # Extract PEF ID from filename (first part before "_")
        id_pef = xml_file.split("_")[0]

        # Load mapping from Excel
        df = pd.read_excel(excel_path, dtype=str)
        df = df.dropna(subset=["ID_PEF", "ID_NCT"])
        mapping = dict(zip(df["ID_PEF"].str.strip(), df["ID_NCT"].str.strip()))

        # Parse XML
        tree = etree.parse(input_path)
        root = tree.getroot()

        # Prepare namespace map
        nsmap = root.nsmap.copy()
        if "fresh" not in nsmap:
            nsmap["fresh"] = FRESH_NAMESPACE_URI

        # Find <Metadonnees>
        metadonnees = root.find(".//Metadonnees")
        if metadonnees is None:
            raise ValueError("No <Metadonnees> element found in the XML.")

        # If mapping exists, add <fresh:ID>
        if id_pef in mapping:
            nct_value = mapping[id_pef]
            tag_name = f"{{{FRESH_NAMESPACE_URI}}}ID"

            new_id_elem = etree.Element(tag_name, nsmap=nsmap)
            new_id_elem.set("agency", "NCT")
            new_id_elem.text = nct_value
            metadonnees.append(new_id_elem)

            task_name = "add_nct_identifier"
            changelog = context.get_changelog(xml_file) if context else None
            if changelog:
                changelog.log_add(task_name, field="fresh:ID[@agency='NCT']", new_value=nct_value)

            logger.info("Added <fresh:ID agency='NCT'> with value: %s", nct_value)
        else:
            logger.info("No mapping found for ID_PEF=%s, writing file unmodified.", id_pef)

        # Always write output
        output_path = join(output_folder, xml_file)
        tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)
        logger.info("File written to: %s", output_path)

        return output_path

    except Exception as e:
        logger.error("Error while processing file %s: %s", xml_file, e)
        raise
