import inspect
from pathlib import Path
from pipeline.tasks import *
from pipeline.utils.PipelineContext import PipelineContext


def execute_task(task, xml_file, input_folder=None, output_folder=None, context=None, **kwargs):
    """
    Executes a task function with the appropriate parameters based on its signature.
    Only passes arguments that the task function explicitly accepts.
    """
    sig = inspect.signature(task)
    task_args = {}

    if 'xml_file' in sig.parameters:
        task_args['xml_file'] = xml_file
    if 'input_folder' in sig.parameters:
        task_args['input_folder'] = input_folder
    if 'output_folder' in sig.parameters:
        task_args['output_folder'] = output_folder
    if 'context' in sig.parameters:
        task_args['context'] = context

    # Add any additional keyword arguments allowed by the task
    for k, v in kwargs.items():
        if k in sig.parameters:
            task_args[k] = v

    task(**task_args)


def run_pipeline():
    """
    Executes the entire XML modification pipeline.
    """
    # Initialize the pipeline context
    run_context = PipelineContext()
    logger=run_context.get_logger()
    logger.info("Starting XML Modification Flow")

    tasks = [
        (correct_special_characters, {}),
        #(correct_special_characters_optional, {}),
        #(process_collection_dates, {}),
        #(update_regions, {}),
        #(align_health_determinants, {}),
        #(align_biobank_content, {}),
        #(align_data_types, {}),
        #(align_health_specs, {}),
        #(update_recruitment_sources, {}),
        #(update_population_types, {}),
        #(update_study_categories, {}),
        #(align_study_status,{}),
        (add_fresh_enrichment_namespace, {}),
        #(add_fresh_identifier, {}),
        #(process_inclusion_criteria, {}),
        #(dispatch_data_access, {}),
        #(update_contacts, {}),
        #(add_collection_mode_categories, {}),
        #(add_rare_diseases,{}),
        #(add_nct_identifier, {}),
        #(add_research_type,{}),
        #(add_provenance, {}),
        #(add_pathologies, {}),
        #(add_nations,{}),
        #(add_authorizing_agency,{}),
        #(add_metadata_contributor,{}),
        #(add_third_party_source,{}),
        (add_funding_type,{}),
        #(remove_duplicate_empty, {}),
        
        #(split_fr_en, {})
    ]

    current_input_folder = Path(run_context.get_original_folder())

    for idx, (task, kwargs) in enumerate(tasks):
        task_name = f"{idx + 1:02d}-{task.__name__}"

        # Each task writes to its own subfolder inside outputs/
        current_output_folder = (
            run_context.get_outputs_dir() / task_name
            if 'output_folder' in task.__code__.co_varnames
            else None
        )

        if current_output_folder:
            current_output_folder.mkdir(parents=True, exist_ok=True)

        xml_files = get_xml_files(current_input_folder, context=run_context)

        for xml_file in xml_files:
            # Initialize changelog for this file
            run_context.init_changelog_for_file(xml_file)

            # Execute the task
            execute_task(
                task,
                xml_file,
                input_folder=current_input_folder,
                output_folder=current_output_folder,
                context=run_context,
                **kwargs
            )

        # Update input folder for the next task
        if current_output_folder:
            current_input_folder = current_output_folder


    logger.info("Pipeline execution completed.")


if __name__ == "__main__":
    run_pipeline()
