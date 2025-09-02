from pathlib import Path
from lxml import etree
import pandas as pd
from os.path import join

FRESH_NAMESPACE_URI = "urn:fresh-enrichment:v1"

def add_sampling_procedure(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Adds SamplingModeFR and SamplingModeEN elements to the XML based on an Excel mapping.

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
            logger.info("Starting sampling mode update for file: %s", xml_file)

        input_path = Path(input_folder) / xml_file
        output_path = Path(output_folder) / xml_file

        if not input_path.exists():
            if logger:
                logger.error("Input file '%s' does not exist. Skipping.", input_path)
            return

        # parse xml
        try:
            tree = etree.parse(str(input_path))
            root = tree.getroot()
        except etree.XMLSyntaxError as e:
            if logger:
                logger.error("Failed to parse '%s': %s", xml_file, e)
            return

        # get file id
        file_id = xml_file.split("_")[0]

        # read excel mapping
        tables_folder = context.get_conversion_tables_folder()
        excel_path = join(tables_folder, 'add-sampling-procedure.xlsx')
        df = pd.read_excel(excel_path, dtype=str).fillna("")

        modes = df[df["ID_PEF"] == file_id]

        if modes.empty:
            if logger:
                logger.info("No sampling modes found for file_id %s", file_id)
        else:
            def make_elem(tag, text=None, attrib=None):
                """Helper to create namespaced element with optional text and attributes"""
                el = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}{tag}", attrib=attrib or {})
                if text:
                    el.text = text
                return el

            for _, row in modes.iterrows():
                # SamplingModeFR
                fr_el = make_elem(
                    "SamplingModeFR", 
                    text=row["ChampFReSH_fr"], 
                    attrib={"uri": row["URI_CESSDA"]} if row["URI_CESSDA"] else {}
                )
                root.append(fr_el)

                # SamplingModeEN
                en_el = make_elem(
                    "SamplingModeEN", 
                    text=row["ChampFReSH_en"], 
                    attrib={"uri": row["URI_CESSDA"]} if row["URI_CESSDA"] else {}
                )
                root.append(en_el)

                # log add
                if changelog is not None:
                    changelog.log_add(
                        task="update_sampling_mode",
                        field="SamplingMode",
                        new_value={
                            "SamplingModeFR": row["ChampFReSH_fr"],
                            "SamplingModeEN": row["ChampFReSH_en"],
                            "URI": row["URI_CESSDA"] if row["URI_CESSDA"] else None,
                        },
                    )

                if logger:
                    logger.info(
                        "Added sampling mode FR='%s', EN='%s' to file %s", 
                        row["ChampFReSH_fr"], row["ChampFReSH_en"], xml_file
                    )

        # save updated xml
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(str(output_path), pretty_print=True, encoding="utf-8", xml_declaration=True)

        if logger:
            logger.info("Successfully updated sampling modes and saved: %s", output_path)

    except Exception as e:
        if logger:
            logger.error("Unexpected error while processing '%s': %s", xml_file, e)
        raise
