from pathlib import Path
from lxml import etree
import pandas as pd
from os.path import join


def update_study_status(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Updates (or creates) EnActiviteFR and EnActiviteEN elements anywhere in the XML tree
    based on an Excel mapping. If not found in the mapping, defaults to 'Inconnu' / 'Unknown'.

    Args:
        xml_file (str): XML file name.
        input_folder (str): Directory containing the XML file.
        output_folder (str): Directory to save the transformed XML file.
        context: Optional pipeline context providing logger and changelog.
    """
    try:
        logger = context.get_logger() if context else None
        changelog = context.get_changelog(xml_file) if context else None

        if logger:
            logger.info("Starting study status update for file: %s", xml_file)

        input_path = Path(input_folder) / xml_file
        output_path = Path(output_folder) / xml_file

        if not input_path.exists():
            if logger:
                logger.error("Input file '%s' does not exist. Skipping.", input_path)
            return

        # parse XML
        try:
            tree = etree.parse(str(input_path))
            root = tree.getroot()
        except etree.XMLSyntaxError as e:
            if logger:
                logger.error("Failed to parse '%s': %s", xml_file, e)
            return

        # extract file ID
        file_id = xml_file.split("_")[0]

        # read Excel mapping
        tables_folder = context.get_conversion_tables_folder()
        excel_path = join(tables_folder, "study-status.xlsx")
        df = pd.read_excel(excel_path, dtype=str).fillna("")

        status_row = df[df["PEF_ID"] == file_id]

        if status_row.empty:
            fr_value = "Inconnu"
            en_value = "Unknown"
            if logger:
                logger.info("No study status found for file_id %s -> using defaults", file_id)
        else:
            row = status_row.iloc[0]
            fr_value = row["ChampFReSH_fr"]
            en_value = row["ChampFReSH_en"]

        # helper to create new elements
        def make_elem(tag, text):
            el = etree.Element(tag)
            el.text = text
            return el

        # find all existing EnActiviteFR/EN anywhere in the XML
        existing_fr = root.xpath(".//EnActiviteFR")
        existing_en = root.xpath(".//EnActiviteEN")

        # update or create FR
        if existing_fr:
            for elem in existing_fr:
                parent = elem.getparent()
                parent.remove(elem)
                parent.append(make_elem("EnActiviteFR", fr_value))
        else:
            # fallback: append to root if none found
            root.append(make_elem("EnActiviteFR", fr_value))

        # update or create EN
        if existing_en:
            for elem in existing_en:
                parent = elem.getparent()
                parent.remove(elem)
                parent.append(make_elem("EnActiviteEN", en_value))
        else:
            root.append(make_elem("EnActiviteEN", en_value))

        # changelog
        if changelog is not None:
            changelog.log_add(
                task="update_study_status",
                field="EnActivite",
                new_value={
                    "EnActiviteFR": fr_value,
                    "EnActiviteEN": en_value,
                },
            )

        # save XML
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(str(output_path), pretty_print=True, encoding="utf-8", xml_declaration=True)

        if logger:
            logger.info("Successfully updated study status and saved: %s", output_path)

    except Exception as e:
        if logger:
            logger.error("Unexpected error while processing '%s': %s", xml_file, e)
        raise
