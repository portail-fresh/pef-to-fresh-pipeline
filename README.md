# Portail Epidemiologie France (PEF) to FReSH pipeline

## Overview  
The **PEF to FReSH Pipeline** is a Python project designed to reformat and transform metadata references from the [Portail Epidemiologie France (PEF) catalog](https://epidemiologie-france.aviesan.fr/) for integration into the FReSH (France Recherche en Santé Humaine) catalog.

This pipeline automates data cleaning and reformatting tasks, ensuring compatibility with the [FReSH metadata schema](https://github.com/portail-fresh/fresh-metadata-schema).

## Source Data

The Portail Epidémiologie France (PEF) catalog includes **1,099** bilingual records (French and English). Of these, **22** were excluded from the migration to the FReSH catalog: **20** belong to the medico-administrative domain and fall outside the scope of FReSH, while **2** are duplicates of other published studies in PEF.

PEF contributors were asked to update their metadata records by **May 26, 2025**. Updates submitted after this date were not considered in the migration process.



## Data Transformation Pipeline

The data is transformed through a step-by-step process, with intermediate outputs saved at each stage to ensure traceability.

Each transformation task is implemented as a Python function designed to address a specific issue in the original metadata.

### Transformation stages

The transformation workflow is organized into three main stages:

- **PEF>PEF**: Content transformation of specific PEF elements. These operations modify only the content of elements without altering the PEF metadata schema. Typical tasks in this step include content normalization and alignment with controlled vocabularies adopted by the FReSH catalog.

- **PEF>PEF+**: Content transformation involving changes to the PEF metadata schema. In this step, the content of certain PEF elements is redistributed across different elements, and custom elements may be added to prepare the metadata for schema mapping to the FReSH schema.

- **PEF+>FReSH**: Schema mapping from the customized PEF+ metadata schema to the FReSH metadata schema.

 
![Graphical representation of the PEF to FReSH transformation steps.](docs/img/pef-transformation-steps.png)

### Tasks list

The current implementation of the pipeline executes the following tasks:

| Task No. | Step     | Task                                                                                                       | Python Function                          |
| -------- | -------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| 1        | PEF>PEF  | Correct XML files by replacing or removing invalid special characters that prevent parsing with `lxml`     | `correct_special_characters.py`          |
| 2        | PEF>PEF  | Correct XML files by replacing or removing invalid special characters, that do not prevent correct parsing | `correct_special_characters_optional.py` |
| 3        | PEF>PEF  | Format collection dates tags in order to follow a standard format                                          | `process_collection_dates.py`            |
| 4        | PEF>PEF  | Update french regions' names                                                                               | `update_regions.py`                      |
| 5        | PEF>PEF  | Update health determinants categories                                                                      | `align_health_determinants.py`           |
| 6        | PEF>PEF  | Update biobank content categories                                                                          | `align_biobank_content.py`               |
| 7        | PEF>PEF  | Align data types                                                                                           | `align_data_types.py`                    |
| 8        | PEF>PEF  | Align health specialties categories                                                                        | `align_health_specs.py`                  |
| 9        | PEF>PEF  | Update recruitment sources categories                                                                      | `update_recruitment_sources.py`          |
| 10       | PEF>PEF  | Update population categories, adding people with disabilities                                              | `update_population_types.py`          |
| 11       | PEF>PEF+ | Add `fresh-enrichment` namespace to track custom elements                                                  | `add_fresh_enrichment_namespace.py`      |
| 12       | PEF>PEF+ | Add FReSH unique identifier following format _"FRESH-PEFXXXXX"_                                            | `add_fresh_identifier.py`                |
| 13       | PEF>PEF+ | Separate inclusion and exclusion criteria                                                                  | `process_inclusion_criteria.py`          |
| 14       | PEF>PEF+ | Dispatch data access information from one to multiple custom fields                                        | `dispatch_data_access.py`                |
| 15       | PEF>PEF+ | Add CESSDA categories for collection mode                                                                  | `add_collection_mode_categories.py`      |


More detailed description of each task is described in the `docs/` folder.

### Tasks definition

Tasks are defined respecting the following criteria:

 - Each task should solve a unitary issue with original metadata
 - Each modification on an input XML file should produce a copy of the modified XML file as output.

Tasks are implemented following as much as possible a common coding style and structure.

Task functions generally share three common default input arguments:

 - `xml_file`: the filename of the XML file to be processed
 - `input_folder`: the input folder where the XML file to be processed is stored
 - `output_folder`: the output folder where to store the copy of the XML file after the processing

Depending the task, they might miss one or more default input arguments and need some other extra and/or optional arguments.

Task function usually don't return, but just store the processed XML files in the designated output folder.

Tasks functions are stored in the `pipeline/tasks` folder and exported through the `pipeline/tasks/__init__.py` file:

```python
# __init__.py

from .get_xml_files import get_xml_files
from .correct_special_characters import correct_special_characters
from .correct_special_characters_optional import correct_special_characters_optional
...

# Define __all__ to specify the public API of the tasks module
__all__ = [
    "get_xml_files",
    "correct_special_characters",
    "correct_special_characters_optional",
    ...
]

```

### Pipeline execution

The pipeline execution is defined in the `main.py` file.

Tasks functions are imported from the `pipeline/tasks` folder and the execution order is defined in the `tasks` list of the `run_pipeline()` function in `main.py` file.

```python
# main.py

...
from pipeline.tasks import * 

...
def run_pipeline():
  ...
  tasks = [
        (correct_special_characters, {}),
        (correct_special_characters_optional, {}),
        (process_collection_dates, {}),
    ]
  ...

```

Tasks should be added in the `tasks` list as tuples containing the function names as first item, and a dictionnary containing extra arguments (for defaults ones, see section: [Tasks definition](#tasks-definition)).

## Setup and usage

 1. **Install Dependencies**  
   Ensure that all required packages are installed. To install the dependencies, create a python venv or a conda env and run:
     ```bash
    pip install -r requirements.txt
    ```

2. **Prepare Input Data**  
   Place the original XML files to be parsed in the designated input folder, without subfolders. This path is specified in the `configs/folders.yaml` file under the `input_files_folder` key.


3. **Run the Pipeline**  
   To execute the main pipeline, run:
   ```bash
   python main.py
   ```



## References

- **Portail Epidemiologie France (PEF)**  
  The Portail Epidemiologie France catalog provides access to French health-related data sources for research and public health. More information can be found at:  
  [https://epidemiologie-france.aviesan.fr/](https://epidemiologie-france.aviesan.fr/)

- **lxml Library**  
  `lxml` is a Python library for XML and HTML parsing that supports XPath and XSLT. This project uses `lxml` to process XML files. Library documentation:  
  [https://lxml.de/](https://lxml.de/)

- **saxonche Library**  
  `saxonche` is a Python library that provides a Python interface to SaxonC, enabling XML and XSLT processing capabilities. It is based on the Saxon-HE processor. Library documentation:  
  [https://www.saxonica.com/saxon-c/index.xml](https://www.saxonica.com/saxon-c/index.xml)

- **pipreqs Library**  
  The `pipreqs` library was used to automatically generate a `requirements.txt` file with the dependencies of the project:  
  [https://github.com/bndr/pipreqs](https://github.com/bndr/pipreqs)

