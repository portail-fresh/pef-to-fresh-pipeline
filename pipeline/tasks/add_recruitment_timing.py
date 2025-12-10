from os.path import join
from lxml import etree
import logging

logger = logging.getLogger(__name__)

def add_recruitment_timing(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Modifies the XML file by updating recruitment timing based on TypeEnqueteFR/value:

    - If value is "Etudes transversales répétées (hors enquête cas-témoins)" 
      or "Etudes transversales non répétées (hors enquête cas-témoins)", 
      replaces TypeEnqueteFR and TypeEnqueteEN with:
        - RecruitmentTimingFR / RecruitmentTimingEN

    - If value is "Etudes longitudinales (hors cohortes)", deletes TypeEnqueteFR and TypeEnqueteEN.

    Works regardless of the position of TypeEnqueteFR/EN in the XML hierarchy.

    Args:
        xml_file: The name of the XML file to modify.
        input_folder: Folder containing the XML file.
        output_folder: Folder to write the updated XML file.
        context (optional): Shared context object containing changelog and other runtime data.

    Returns:
        Path to the updated XML file.
    """
    try:
        logger.info("Processing XML file for recruitment timing: %s", xml_file)
        input_path = join(input_folder, xml_file)

        tree = etree.parse(input_path)
        root = tree.getroot()

        task_name = "update_recruitment_timing"
        changelog = context.get_changelog(xml_file) if context else None

        # Trova tutti gli elementi TypeEnqueteFR ovunque
        for type_fr in root.xpath(".//TypeEnqueteFR"):
            parent = type_fr.getparent()
            if parent is None:
                continue

            value_elem = type_fr.find("value")
            if value_elem is None or not value_elem.text:
                continue

            value_fr = value_elem.text.strip()
            logger.info("Found TypeEnqueteFR/value: %s", value_fr)

            # Determina azioni solo se è uno dei tre valori target
            if value_fr == "Etudes transversales non répétées (hors enquêtes cas-témoins)":
                replacement_fr = "Etude transversale non répétée"
                replacement_en = "One-time cross-sectional study"
            elif value_fr == "Etudes transversales répétées (hors enquêtes cas-témoins)":
                replacement_fr = "Etude transversale répétée"
                replacement_en = "Repeated cross-sectional study"
            elif value_fr == "Etudes longitudinales (hors cohortes)":
                replacement_fr = None
                replacement_en = None
            else:
                # Nessuna modifica per valori non target
                continue

            # Rimuovi TypeEnqueteFR
            parent.remove(type_fr)
            logger.info("Removed TypeEnqueteFR")
            if changelog:
                changelog.log_delete(task_name, field="TypeEnqueteFR")

            # Rimuovi TypeEnqueteEN nello stesso genitore (se presente)
            type_en = parent.find("TypeEnqueteEN")
            if type_en is not None:
                parent.remove(type_en)
                logger.info("Removed TypeEnqueteEN")
                if changelog:
                    changelog.log_delete(task_name, field="TypeEnqueteEN")

            # Se serve, aggiungi RecruitmentTimingFR e EN
            if replacement_fr:
                elem_fr = etree.Element("RecruitmentTimingFR")
                elem_fr.text = replacement_fr
                parent.append(elem_fr)
                logger.info("Added RecruitmentTimingFR: %s", replacement_fr)
                if changelog:
                    changelog.log_add(task_name, field="RecruitmentTimingFR", new_value=replacement_fr)

                elem_en = etree.Element("RecruitmentTimingEN")
                elem_en.text = replacement_en
                parent.append(elem_en)
                logger.info("Added RecruitmentTimingEN: %s", replacement_en)
                if changelog:
                    changelog.log_add(task_name, field="RecruitmentTimingEN", new_value=replacement_en)

        # Scrivi output
        output_path = join(output_folder, xml_file)
        tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)
        logger.info("Successfully wrote updated XML file: %s", output_path)
        return output_path

    except Exception as e:
        logger.error("Error while processing file %s: %s", xml_file, e)
        raise
