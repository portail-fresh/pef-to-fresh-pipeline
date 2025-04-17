import os
import datetime
from pipeline.utils.load_config import load_config
from pipeline.tasks import *
import logging
import pandas as pd
from pipeline.utils.logging import setup_logging
# Setup logging configuration
setup_logging()

# Create a logger for this module
logger = logging.getLogger(__name__)

def execute_task(task, xml_file, input_folder=None, output_folder=None, **kwargs):
    """
    Executes a task function with the appropriate parameters based on its signature.
    
    Parameters:
    - task (function): The task function to execute.
    - xml_file (str): The XML file being processed.
    - input_folder (str, optional): Folder path where the XML file is read from.
    - output_folder (str, optional): Folder path where the XML file will be saved.
    - **kwargs: Additional keyword arguments specific to the task.
    """
    if 'input_folder' in task.__code__.co_varnames and 'output_folder' in task.__code__.co_varnames:
        task(xml_file, input_folder=input_folder, output_folder=output_folder, **kwargs)
    elif 'input_folder' in task.__code__.co_varnames:
        task(xml_file, input_folder=input_folder, **kwargs)
    elif 'output_folder' in task.__code__.co_varnames:
        task(xml_file, output_folder=output_folder, **kwargs)
    else:
        task(xml_file, **kwargs)

def run_pipeline():
    """
    Executes the entire XML modification pipeline.

    This function orchestrates the execution of multiple tasks in sequence, where each task
    modifies XML files in a specified order. The pipeline processes XML files from a given 
    input folder and outputs the results to dynamically generated subfolders based on the 
    current date and time. A separate subfolder is created for each execution of the pipeline 
    to ensure that results from different runs do not overlap.

    Steps:
    1. Load configuration settings from a YAML file.
    2. Create a unique temporary folder based on the current date and time for storing 
       the results of each task.
    3. Sequentially execute each task from the task list, passing the appropriate folders 
       (input and output) to the task function.
    4. For each task that requires output, create an output folder inside the run's temporary 
       folder.
    5. The input folder for each task is updated to the output folder of the previous task 
       if applicable.

    Raises:
    - Exception: If any task encounters an error during execution, it is raised to halt the 
      pipeline.
    """
    logger.info("Starting XML Modification Flow")
    
    config = load_config("folders.yaml")
    original_folder = config.get('original_ddi_folder')
    temp_folder = config.get('temp_folder')

    # Generate a datetime-based folder name for each pipeline run
    datetime_str = "run" + datetime.datetime.now().strftime("-%Y%m%d-%H%M%S")
    run_temp_folder = os.path.join(temp_folder, datetime_str)
    os.makedirs(run_temp_folder, exist_ok=True)
    
    # Initialize error log
    #error_log_path = os.path.join(run_temp_folder, "error_log.csv")
    #error_records = []
    
    tasks = [
        (correct_special_characters, {}),
        (correct_special_characters_optional, {}),
        (process_collection_dates, {}),
        (add_fresh_enrichment_namespace,{}),
        (add_fresh_identifier,{}),
        (split_fr_en,{})
    ]
    
    current_input_folder = original_folder  # Start with the original folder
    for idx, (task, kwargs) in enumerate(tasks):
        task_name = "{}-{}".format(idx + 1, task.__name__)
        current_output_folder = os.path.join(run_temp_folder, task_name) if 'output_folder' in task.__code__.co_varnames else None
        
        if current_output_folder:
            os.makedirs(current_output_folder, exist_ok=True)
        
        xml_files = get_xml_files(current_input_folder)
        for xml_file in xml_files:
            execute_task(task, xml_file, input_folder=current_input_folder, output_folder=current_output_folder, **kwargs)
            
        
        if current_output_folder:
            current_input_folder = current_output_folder
    
    # Save errors to CSV if there are any
    #if error_records:
    #    df = pd.DataFrame(error_records)
    #    df.to_csv(error_log_path, index=False)
    #    logger.info("Errors logged to %s", error_log_path)
    
    logger.info("Pipeline execution completed.")


if __name__ == "__main__":
    run_pipeline()
