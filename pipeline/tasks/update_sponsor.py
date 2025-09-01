from pathlib import Path
from lxml import etree
import pandas as pd
from os.path import join

FRESH_NAMESPACE_URI = "urn:fresh-enrichment:v1"

def update_sponsor(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Adds Sponsor elements to the XML based on the mapping provided in an Excel file.

    Args:
        xml_file (str): XML file name.
        input_folder (str): Directory containing the XML file.
        output_folder (str): Directory to save the transformed XML file.
        excel_path (str): Path to the sponsor Excel mapping.
        context: Optional pipeline context providing logger and changelog.
    """
    try:
        logger = context.get_logger() if context else None
        changelog = context.get_changelog(xml_file) if context else None

        if logger:
            logger.info("Starting sponsor update for file: %s", xml_file)

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

        tables_folder = context.get_conversion_tables_folder()
        excel_path = join(tables_folder, 'OrganismesPEF.xlsx')
        df = pd.read_excel(excel_path, dtype=str).fillna("")

        sponsors = df[df["PEF_ID"] == file_id]

        if sponsors.empty:
            if logger:
                logger.info("No sponsors found for file_id %s", file_id)
        else:
            def make_elem(tag, text=None):
                """Helper to create namespaced element with optional text"""
                el = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}{tag}")
                if text:
                    el.text = text
                return el

            for _, row in sponsors.iterrows():
                sponsor_el = make_elem("Sponsor")

                sponsor_el.append(make_elem("SponsorName", row["FReSH_Organisme"]))
                sponsor_el.append(make_elem("SponsorTypeFR", row["SponsorType_fr"]))
                sponsor_el.append(make_elem("SponsorTypeEN", row["SponsorType_en"]))

                # PID ROR
                if row["ROR"]:
                    pid_el = make_elem("SponsorPID")
                    pid_el.append(make_elem("URL", row["ROR"]))
                    pid_el.append(make_elem("PIDSchema", "ROR"))
                    sponsor_el.append(pid_el)

                # PID SIRET
                if row["SIRET"]:
                    pid_el = make_elem("SponsorPID")
                    pid_el.append(make_elem("URL", row["SIRET"]))
                    pid_el.append(make_elem("PIDSchema", "SIRET"))
                    sponsor_el.append(pid_el)

                # aggiungi sponsor al root
                root.append(sponsor_el)

                # log add
                if changelog is not None:
                    changelog.log_add(
                        task="update_sponsor",
                        field="Sponsor",
                        new_value={
                            "SponsorName": row["FReSH_Organisme"],
                            "SponsorTypeFR": row["SponsorType_fr"],
                            "SponsorTypeEN": row["SponsorType_en"],
                            "ROR": row["ROR"] if row["ROR"] else None,
                            "SIRET": row["SIRET"] if row["SIRET"] else None,
                        },
                    )

                if logger:
                    logger.info("Added sponsor '%s' to file %s", row["FReSH_Organisme"], xml_file)

        # salva
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(str(output_path), pretty_print=True, encoding="utf-8", xml_declaration=True)

        if logger:
            logger.info("Successfully updated sponsors and saved: %s", output_path)

    except Exception as e:
        logger = context.get_logger() if context else None
        if logger:
            logger.error("Unexpected error while processing '%s': %s", xml_file, e)
        raise
