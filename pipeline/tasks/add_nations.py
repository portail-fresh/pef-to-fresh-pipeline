from pathlib import Path
import pandas as pd
from lxml import etree
from pipeline.utils.FieldTransformer import FieldTransformer
from os.path import join

FRESH_NAMESPACE_URI = "urn:fresh-enrichment:v1"


def add_nations(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Adds <fresh:NationFR> and <fresh:NationEN> elements based on Excel mapping.
    Each Nation has:
      - <fresh:value> from label_fr or label_en
      - <fresh:URI> from ISO

    Args:
        xml_file (str): XML file name.
        input_folder (str): Directory containing the XML file.
        output_folder (str): Directory to save the transformed XML file.
        context: Optional pipeline context providing logger and changelog.
    """
    try:
        logger = context.get_logger() if context else None
        if logger:
            logger.info("Starting add_nations for file: %s", xml_file)

        input_path = Path(input_folder) / xml_file
        output_path = Path(output_folder) / xml_file

        if not input_path.exists():
            if logger:
                logger.error("Input file '%s' does not exist. Skipping.", input_path)
            return

        try:
            tree = etree.parse(str(input_path))
            root = tree.getroot()
        except etree.XMLSyntaxError as e:
            if logger:
                logger.error("Failed to parse '%s': %s", xml_file, e)
            return

        changelog = context.get_changelog(xml_file) if context else None
        if changelog is None:
            if logger:
                logger.error("No changelog found for '%s'. Skipping.", xml_file)
            return

        # file_id = prima parte del nome file
        file_id = xml_file.split('_')[0]
        task_name = "add_nations"

        # carica mapping da Excel
        tables_folder = context.get_conversion_tables_folder()
        excel_path = join(tables_folder, 'add-nations.xlsx')
        df = pd.read_excel(excel_path, dtype=str).fillna("")

        # filtra righe per questo file_id
        df_filtered = df[df["ID_PEF"] == file_id]

        if df_filtered.empty:
            if logger:
                logger.info("No nations found in Excel for file_id=%s", file_id)
        else:
            nsmap = root.nsmap.copy()
            if "fresh" not in nsmap:
                nsmap["fresh"] = FRESH_NAMESPACE_URI

            for _, row in df_filtered.iterrows():
                iso = row["ISO"].strip()
                label_en = row["label_en"].strip()
                label_fr = row["label_fr"].strip()

                # NationFR
                nation_fr = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}NationFR", nsmap=nsmap)
                val_fr = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}value")
                val_fr.text = label_fr
                uri_fr = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}URI")
                uri_fr.text = iso
                nation_fr.extend([val_fr, uri_fr])
                root.append(nation_fr)

                if changelog:
                    changelog.log_add(task_name, field="NationFR.value", new_value=label_fr)
                    changelog.log_add(task_name, field="NationFR.URI", new_value=iso)

                if logger:
                    logger.info("Added NationFR: %s (%s)", label_fr, iso)

                # NationEN
                nation_en = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}NationEN", nsmap=nsmap)
                val_en = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}value")
                val_en.text = label_en
                uri_en = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}URI")
                uri_en.text = iso
                nation_en.extend([val_en, uri_en])
                root.append(nation_en)

                if changelog:
                    changelog.log_add(task_name, field="NationEN.value", new_value=label_en)
                    changelog.log_add(task_name, field="NationEN.URI", new_value=iso)

                if logger:
                    logger.info("Added NationEN: %s (%s)", label_en, iso)

        # salva XML
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(str(output_path), pretty_print=True, encoding="utf-8", xml_declaration=True)

        if logger:
            logger.info("Successfully saved updated XML with nations: %s", output_path)

    except Exception as e:
        logger = context.get_logger() if context else None
        if logger:
            logger.error("Unexpected error while processing '%s': %s", xml_file, e)
        raise
