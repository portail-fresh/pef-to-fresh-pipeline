from pathlib import Path
import pandas as pd
from lxml import etree
from os.path import join

FRESH_NAMESPACE_URI = "urn:fresh-enrichment:v1"

def add_third_party_source(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Adds <fresh:IsDataIntegration> and optionally <fresh:ThirdPartySource> elements
    based on an Excel mapping of PEF IDs to ChampFReSH values.

    Args:
        xml_file (str): XML file name.
        input_folder (str): Directory containing the XML file.
        output_folder (str): Directory to save the transformed XML file.
        context: Optional pipeline context providing logger and changelog.
    """
    try:
        logger = context.get_logger() if context else None
        if logger:
            logger.info("Starting add_data_integration for file: %s", xml_file)

        input_path = Path(input_folder) / xml_file
        output_path = Path(output_folder) / xml_file

        if not input_path.exists():
            if logger:
                logger.error("Input file '%s' does not exist. Skipping.", input_path)
            return

        try:
            tree = etree.parse(str(input_path))
        except etree.XMLSyntaxError as e:
            if logger:
                logger.error("Failed to parse '%s': %s", xml_file, e)
            return

        root = tree.getroot()

        # nsmap con fresh
        nsmap = root.nsmap.copy()
        if "fresh" not in nsmap:
            nsmap["fresh"] = FRESH_NAMESPACE_URI

        task_name = "add_third_party_source"
        changelog = context.get_changelog(xml_file) if context else None

        # estrai file_id
        file_id = xml_file.split("_")[0]

        tables_folder = context.get_conversion_tables_folder()
        excel_path = join(tables_folder, 'add-third-party-source.xlsx')
        df = pd.read_excel(excel_path, dtype=str)

        df = df.fillna("")  # gestisci eventuali NaN
        df["PEF_ID"] = df["PEF_ID"].astype(str)

        match = df[df["PEF_ID"] == file_id]

        # crea elemento IsDataIntegration
        is_data_integration = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}IsDataIntegration", nsmap=nsmap)
        if not match.empty:
            is_data_integration.text = "true"
        else:
            is_data_integration.text = "false"
        root.append(is_data_integration)
        if logger:
            logger.info("Added IsDataIntegration=%s", is_data_integration.text)
        if changelog:
            changelog.log_add(task_name, field="fresh:IsDataIntegration", new_value=is_data_integration.text)

        # se l'id è nell'excel, aggiungi ThirdPartySource
        if not match.empty:
            row = match.iloc[0]
            third_party = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}ThirdPartySource", nsmap=nsmap)

            elem_fr = etree.SubElement(third_party, f"{{{FRESH_NAMESPACE_URI}}}SourceTypeFR")
            elem_fr.text = row["ChampFReSH_fr"]

            elem_en = etree.SubElement(third_party, f"{{{FRESH_NAMESPACE_URI}}}SourceTypeEN")
            elem_en.text = row["ChampFReSH_en"]

            root.append(third_party)

            if logger:
                logger.info("Added ThirdPartySource with FR='%s' and EN='%s'", row["ChampFReSH_fr"], row["ChampFReSH_en"])
            if changelog:
                changelog.log_add(task_name, field="fresh:ThirdPartySource", new_value=f"{row['ChampFReSH_fr']} / {row['ChampFReSH_en']}")

        # salva
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(str(output_path), pretty_print=True, encoding="utf-8", xml_declaration=True)

        if logger:
            logger.info("Successfully applied add_data_integration and saved: %s", output_path)

    except Exception as e:
        logger = context.get_logger() if context else None
        if logger:
            logger.error("Unexpected error while processing '%s': %s", xml_file, e)
        raise
