from pathlib import Path
from lxml import etree

def add_parent_category(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Cleans DomainesDePathologies and DeterminantsDeSante fields by duplicating <value> elements
    containing ':' (keeping also a version truncated before the colon).

    Args:
        xml_file (str): XML file name to process.
        input_folder (str): Folder containing the source XML.
        output_folder (str): Folder where the modified XML will be saved.
        context: Optional pipeline context providing logger and changelog.

    Behavior:
        - For each tag among:
            DomainesDePathologiesFR, DomainesDePathologiesEN,
            DeterminantsDeSanteFR, DeterminantsDeSanteEN
        - If a <value> text contains ':', it duplicates that element but removes the text after ':'.
        - Elements can be anywhere in the XML tree.
        - Logs all changes to changelog (if available).
    """
    try:
        logger = context.get_logger() if context else None
        changelog = context.get_changelog(xml_file) if context else None

        if logger:
            logger.info("Starting Domaines/Determinants cleanup for file: %s", xml_file)

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

        # Lista dei tag da processare
        tags_to_check = [
            "DomainesDePathologiesFR",
            "DomainesDePathologiesEN",
            "DeterminantsDeSanteFR",
            "DeterminantsDeSanteEN"
        ]

        modified = False

        # Cerca in tutto il documento, non solo sotto root
        for tag in tags_to_check:
            for parent in root.findall(f".//{tag}"):
                values = list(parent.findall("value"))  # copia lista per evitare modifiche durante il loop
                for val in values:
                    text = (val.text or "").strip()
                    if ":" in text:
                        before_colon = text.split(":")[0].strip()
                        if before_colon:
                            new_elem = etree.Element("value")
                            new_elem.text = before_colon
                            parent.append(new_elem)
                            modified = True

                            if logger:
                                logger.info("Duplicated value '%s' '%s' in tag %s", text, before_colon, tag)

                            if changelog is not None:
                                changelog.log_add(
                                    task="clean_domaines_and_determinants",
                                    field=tag,
                                    new_value=before_colon,
                                )

        # Salva il risultato
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(str(output_path), pretty_print=True, encoding="utf-8", xml_declaration=True)

        if logger:
            if modified:
                logger.info("File '%s' cleaned and saved to '%s'", xml_file, output_path)
            else:
                logger.info("No modifications found in file '%s'", xml_file)

    except Exception as e:
        logger = context.get_logger() if context else None
        if logger:
            logger.error("Unexpected error while processing '%s': %s", xml_file, e)
        raise
