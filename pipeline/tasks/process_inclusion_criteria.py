from pathlib import Path
from lxml import etree
from pipeline.utils.FieldTransformer import FieldTransformer



def process_inclusion_criteria(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Applies field-level transformations to the given XML file using an Excel mapping
    and logs changes using a changelog system.

    Args:
        xml_file (str): The name of the XML file to process.
        input_folder (str): The directory containing the XML file.
        output_folder (str): The directory where the processed XML file will be saved.
        context (PipelineContext, optional): Shared context providing access to the changelog.
    """
    try:
        logger=context.get_logger()
        logger.info("Starting exclusion criteria transformation for file: %s", xml_file)

        input_path = Path(input_folder) / xml_file
        output_path = Path(output_folder) / xml_file
        
        task_name="process_inclusion_criteria"

        if not input_path.exists():
            logger.error("Input file '%s' does not exist. Skipping.", input_path)
            return

        try:
            tree = etree.parse(str(input_path))
        except etree.XMLSyntaxError as e:
            logger.error("Failed to parse '%s': %s", xml_file, e)
            return

        file_id = xml_file.split('_')[0]

        changelog = context.get_changelog(xml_file) if context else None
        if changelog is None:
            logger.error("No changelog found for '%s'. Skipping.", xml_file)
            return

        # Path to Excel file (assumed to be in working directory)
        excel_path = "new-clusion.xlsx"

        transformer = FieldTransformer(excel_path=excel_path, file_id=file_id, changelog=changelog, task_name=task_name)
        updated_tree = transformer.apply_transformations(tree)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        updated_tree.write(str(output_path), pretty_print=True, encoding="utf-8", xml_declaration=True)

        logger.info("Successfully applied exclusion criteria transformation and saved: %s", output_path)

    except Exception as e:
        logger.error("Unexpected error while processing '%s': %s", xml_file, e)
        raise