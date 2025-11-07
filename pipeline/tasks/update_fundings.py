from pathlib import Path
from lxml import etree
import pandas as pd
from os.path import join

FRESH_NAMESPACE_URI = "urn:fresh-enrichment:v1"

def update_fundings(xml_file: str, input_folder: str, output_folder: str, context=None):
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
        excel_path = join(tables_folder, 'OK-Financeurs.xlsx')
        df = pd.read_excel(excel_path, dtype=str).fillna("")

        sponsors = df[df["ID"] == file_id]

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
                sponsor_el = make_elem("FundingAgent")

                sponsor_el.append(make_elem("FundingAgentName", row["FinanceurNorm"]))
                sponsor_el.append(make_elem("FundingAgentTypeFR", row["Statut_FR"]))
                sponsor_el.append(make_elem("FundingAgentTypeEN", row["Statut_EN"]))

                # PID ROR
                if row["ROR"]:
                    pid_el = make_elem("FundingAgentPID")
                    pid_el.append(make_elem("URL", row["ROR"]))
                    pid_el.append(make_elem("PIDSchema", "ROR"))
                    sponsor_el.append(pid_el)

                # PID SIRET
                if row["SIREN"]:
                    pid_el = make_elem("FundingAgentPID")
                    pid_el.append(make_elem("URL", row["SIREN"]))
                    pid_el.append(make_elem("PIDSchema", "SIREN"))
                    sponsor_el.append(pid_el)

                # aggiungi sponsor al root
                root.append(sponsor_el)

                # log add
                if changelog is not None:
                    changelog.log_add(
                        task="update_funding",
                        field="FundingAgent",
                        new_value={
                            "FundingAgentName": row["FinanceurNorm"],
                            "FundingAgentTypeFR": row["Statut_FR"],
                            "FundingAgentTypeEN": row["Statut_EN"],
                            "ROR": row["ROR"] if row["ROR"] else None,
                            "SIRET": row["SIREN"] if row["SIREN"] else None,
                        },
                    )

                if logger:
                    logger.info("Added funding '%s' to file %s", row["FinanceurNorm"], xml_file)

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
