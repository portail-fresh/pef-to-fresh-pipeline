from pathlib import Path
from lxml import etree
from pipeline.utils.FieldTransformer import FieldTransformer

def add_pathologies(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Applies general field replacements for biobank content in the given XML file
    using 'align-biobank-content-en.xlsx' as mapping table. This replaces PEF values
    with FReSH values inside <ContenuBiothequeFR> nodes.

    Args:
        xml_file (str): XML file name.
        input_folder (str): Directory containing the XML file.
        output_folder (str): Directory to save the transformed XML file.
        context: Optional pipeline context providing logger and changelog.
    """
    try:
        logger = context.get_logger() if context else None
        if logger:
            logger.info("Starting adding rare diseases boolean for file: %s", xml_file)

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

        changelog = context.get_changelog(xml_file) if context else None
        if changelog is None:
            if logger:
                logger.error("No changelog found for '%s'. Skipping.", xml_file)
            return

        # file_id non utilizzato in modalità general
        file_id = xml_file.split('_')[0]

        excel_path = "pathologies.xlsx"
        task_name = "add_pathologies"

        transformer = FieldTransformer(
            excel_path=excel_path,
            file_id=file_id,
            changelog=changelog,
            task_name=task_name,
        )

        updated_tree = transformer.apply_transformations(tree)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        updated_tree.write(str(output_path), pretty_print=True, encoding="utf-8", xml_declaration=True)

        if logger:
            logger.info("Successfully applied rare diseases and saved: %s", output_path)

    except Exception as e:
        logger = context.get_logger() if context else None
        if logger:
            logger.error("Unexpected error while processing '%s': %s", xml_file, e)
        raise
