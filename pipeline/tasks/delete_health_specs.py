import logging
from os.path import join
from lxml import etree

logger = logging.getLogger(__name__)

def delete_health_specs(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    If a 'no specific medical specialty' value is present in health specialty fields
    (FR or EN), removes all other specialty values and keeps only that one.
    """

    try:
        logger.info("Processing health specialties in XML file: %s", xml_file)
        file_path = join(input_folder, xml_file)
        tree = etree.parse(file_path)
        root = tree.getroot()

        TASK_NAME = "delete_health_specsgit"

        SECTIONS = {
            "DomainesDePathologiesFR": {
                "no_spec_values": {
                    "pas de spécialité médicale spécifique",
                }
            },
            "DomainesDePathologiesEN": {
                "no_spec_values": {
                    "no specific medical specialty",
                }
            }
        }

        def normalize(text: str) -> str:
            return text.strip().lower()

        changelog = context.get_changelog(xml_file) if context else None

        for section_tag, cfg in SECTIONS.items():
            for section in root.xpath(f"//{section_tag}"):

                values = section.xpath("./value")
                if not values:
                    continue

                normalized_map = [
                    (el, normalize(el.text or ""))
                    for el in values
                ]

                no_spec_nodes = [
                    el for el, txt in normalized_map
                    if txt in cfg["no_spec_values"]
                ]

                if not no_spec_nodes:
                    continue

                # Keep the first "no specific specialty" node
                keep_node = no_spec_nodes[0]

                for el in values:
                    if el is keep_node:
                        continue

                    if changelog:
                        changelog.log_delete(
                            TASK_NAME,
                            field=section_tag,
                            old_value=(el.text or "").strip()
                        )

                    section.remove(el)

                logger.info(
                    "Normalized health specialties in section %s (kept '%s')",
                    section_tag,
                    keep_node.text.strip()
                )

        output_file_path = join(output_folder, xml_file)
        tree.write(
            output_file_path,
            encoding="UTF-8",
            xml_declaration=True,
            pretty_print=True
        )

        logger.info("Successfully processed and saved XML file: %s", output_file_path)

    except Exception as e:
        logger.error(
            "An unexpected error occurred while processing health specialties in file %s: %s",
            xml_file,
            e
        )
        raise
