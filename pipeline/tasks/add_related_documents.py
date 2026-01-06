from os.path import join
from lxml import etree
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def add_related_documents(xml_file: str, input_folder: str, output_folder: str,  context=None):
    """
    Adds <RelatedDocument> elements to an XML file based on data from an Excel file.
    
    For each row in the Excel file where the 'ID' matches the XML's ID, adds:
        <RelatedDocument>
            <DocumentTitle>Description</DocumentTitle>
            <DocumentLink>url</DocumentLink>
        </RelatedDocument>

    Args:
        xml_file: The name of the XML file to modify.
        input_folder: Folder containing the XML file.
        output_folder: Folder to write the updated XML file.
        excel_file: Path to the Excel file containing columns ID, url, Description.
        context (optional): Shared context object containing changelog and other runtime data.

    Returns:
        Path to the updated XML file.
    """
    try:
        logger.info("Processing XML file to add related documents: %s", xml_file)
        input_path = join(input_folder, xml_file)

        # Leggi XML
        tree = etree.parse(input_path)
        root = tree.getroot()

        task_name = "add_related_documents"
        changelog = context.get_changelog(xml_file) if context else None

        # Trova l'ID del documento XML
        xml_id_elem = root.find(".//ID")
        if xml_id_elem is None or not xml_id_elem.text:
            logger.warning("No ID element found in XML: %s", xml_file)
            return join(output_folder, xml_file)
        xml_id = str(xml_id_elem.text).strip()
        logger.info("Found XML ID: %s", xml_id)

        # Leggi Excel
        tables_folder = context.get_conversion_tables_folder()
        excel_file = join(tables_folder, '20251028-liste-autres-liens.xlsx')
        df = pd.read_excel(excel_file, dtype=str).fillna("")
        matches = df[df['ID'] == xml_id]

        if matches.empty:
            logger.info("No matching rows in Excel for ID: %s", xml_id)
        else:
            for _, row in matches.iterrows():
                related_elem = etree.Element("RelatedDocument")
                
                title_elem = etree.Element("DocumentTitle")
                title_elem.text = row['Description']
                related_elem.append(title_elem)
                
                link_elem = etree.Element("DocumentLink")
                link_elem.text = row['url']
                related_elem.append(link_elem)
                
                root.append(related_elem)
                logger.info("Added RelatedDocument with title '%s' and link '%s'", row['Description'], row['url'])
                if changelog:
                    changelog.log_add(task_name, field="RelatedDocument", new_value=f"{row['Description']} | {row['url']}")

        # Scrivi output
        output_path = join(output_folder, xml_file)
        tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)
        logger.info("Successfully wrote updated XML file: %s", output_path)
        return output_path

    except Exception as e:
        logger.error("Error while processing file %s: %s", xml_file, e)
        raise
