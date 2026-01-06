from pathlib import Path
from lxml import etree
from pipeline.utils.FieldTransformer import FieldTransformer

def update_recruitment_sources(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Aligns recruitment sources values in the given XML file by applying general field
    replacements defined in 'recruitment-sources-regles-migration.xlsx'. 

    This task replaces PEF values with their corresponding FReSH values 
    inside <RecrutementParIntermediaireFR> nodes.

    Args:
        xml_file (str): Name of the XML file to process.
        input_folder (str): Directory containing the input XML file.
        output_folder (str): Directory where the transformed XML file will be saved.
        context: Optional pipeline context providing logger and changelog.
    """
    try:
        logger = context.get_logger() if context else None
        if logger:
            logger.info("Starting recruitment sources alignment for file: %s", xml_file)

        input_path = Path(input_folder) / xml_file
        output_path = Path(output_folder) / xml_file

        if not input_path.exists():
            if logger:
                logger.error("Input file '%s' does not exist. Skipping.", input_path)
            return

        # Parse the XML file
        try:
            tree = etree.parse(str(input_path))
        except etree.XMLSyntaxError as e:
            if logger:
                logger.error("Failed to parse '%s': %s", xml_file, e)
            return

        # Retrieve changelog from context
        changelog = context.get_changelog(xml_file) if context else None
        if changelog is None:
            if logger:
                logger.error("No changelog found for '%s'. Skipping.", xml_file)
            return

        # file_id is unused in 'general' mode, but still provided for compatibility
        file_id = xml_file.split('_')[0]

        migration_rules_excel_path = "recruitment-sources-regles-migration.xlsx"
        
        task_name = "update_recruitment_sources"

        # Apply transformations using FieldTransformer
        transformer = FieldTransformer(
            excel_path=migration_rules_excel_path,
            file_id=file_id,
            changelog=changelog,
            task_name=task_name,
        )

        updated_tree = transformer.apply_transformations(tree)
        
        
        repartition_file="recruitment-sources-repartition.xlsx"
        # Apply transformations using FieldTransformer
        transformer = FieldTransformer(
            excel_path=repartition_file,
            file_id=file_id,
            changelog=changelog,
            task_name=task_name,
        )

        updated_tree = transformer.apply_transformations(updated_tree)
        
        delete_file="recruitment-sources-delete.xlsx"
        # Apply transformations using FieldTransformer
        transformer = FieldTransformer(
            excel_path=delete_file,
            file_id=file_id,
            changelog=changelog,
            task_name=task_name,
        )

        updated_tree = transformer.apply_transformations(updated_tree)

        # Save the updated XML
        output_path.parent.mkdir(parents=True, exist_ok=True)
        updated_tree.write(str(output_path), pretty_print=True, encoding="utf-8", xml_declaration=True)

        if logger:
            logger.info("Successfully aligned recruitment sources and saved: %s", output_path)

    except Exception as e:
        logger = context.get_logger() if context else None
        if logger:
            logger.error("Unexpected error while processing '%s': %s", xml_file, e)
        raise
