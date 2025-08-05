from pathlib import Path
from lxml import etree
from pipeline.utils.FieldTransformer import FieldTransformer

def update_regions(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Applies general field replacements to the given XML file using an Excel mapping
    file for regional migration. The transformation replaces values in specified XML
    elements based on a global mapping table (not tied to a specific file ID).

    Args:
        xml_file (str): The name of the XML file to process.
        input_folder (str): The directory containing the XML file.
        output_folder (str): The directory where the processed XML file will be saved.
        context (PipelineContext, optional): Shared context providing access to the changelog and logger.
    """
    try:
        logger = context.get_logger()
        logger.info("Starting region mapping transformation for file: %s", xml_file)

        input_path = Path(input_folder) / xml_file
        output_path = Path(output_folder) / xml_file

        task_name = "update_regions"

        if not input_path.exists():
            logger.error("Input file '%s' does not exist. Skipping.", input_path)
            return

        try:
            tree = etree.parse(str(input_path))
        except etree.XMLSyntaxError as e:
            logger.error("Failed to parse '%s': %s", xml_file, e)
            return

        changelog = context.get_changelog(xml_file) if context else None
        if changelog is None:
            logger.error("No changelog found for '%s'. Skipping.", xml_file)
            return

        # Extract file_id anyway but it won't be used in general mode
        file_id = xml_file.split('_')[0]

        excel_path = "regles-migration-regions.xlsx"

        transformer = FieldTransformer(
            excel_path=excel_path,
            file_id=file_id,        # passed but ignored in 'general' mode
            changelog=changelog,
            task_name=task_name,
        )

        updated_tree = transformer.apply_transformations(tree)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        updated_tree.write(str(output_path), pretty_print=True, encoding="utf-8", xml_declaration=True)

        logger.info("Successfully applied region mapping transformation and saved: %s", output_path)

    except Exception as e:
        logger = context.get_logger() if context else None
        if logger:
            logger.error("Unexpected error while processing '%s': %s", xml_file, e)
        raise
