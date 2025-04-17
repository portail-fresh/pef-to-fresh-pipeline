# Portail Epidemiologie France (PEF) to FReSH pipeline

## Overview  
The **PEF to FReSH Pipeline** is a Python project designed to reformat and transform metadata references from the [Portail Epidemiologie France (PEF) catalog](https://epidemiologie-france.aviesan.fr/) for integration into the FReSH (France Recherche en Santé Humaine) catalog.

This pipeline automates data cleaning and reformatting tasks, ensuring compatibility with the FReSH metadata schema.

## Data Transformation

Data is transformed step-by-step, with intermediate results saved at each stage to maintain traceability.

Each task is defined by a Python function which solves a specific issue in the original metadata.

The current implementation of the pipeline executes the following tasks:

| Task No. | Step      | Task                                                                                                       | Python Function                          |
| -------- | --------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| 1        | PEF > PEF | Correct XML files by replacing or removing invalid special characters that prevent parsing with `lxml`     | `correct_special_characters.py`          |
| 2        | PEF > PEF | Correct XML files by replacing or removing invalid special characters, that do not prevent correct parsing | `correct_special_characters_optional.py` |
| 3        | PEF > PEF | Format collection dates tags in order to follow a standard format                                          | `process_collection_dates.py`            |
| 4        | PEF > PEF+ | Add `fresh-enrichment` namespace to track custom elements                                        | `add_fresh_enrichment_namespace.py`            |
| 5        | PEF > PEF+ | Add FReSH unique identifier following format _"FRESH-PEFXXXXX"_                                        | `add_fresh_identifier.py`            |

More detailed description of each task is described in the `docs` folder.

### Tasks definition

Tasks are defined respecting the following criteria:

 - Each task should solve a unitary issue with original metadata
 - Each tasks should be idempotent, i.e. a repeated execution of the same task should give the same result
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
   Place the original XML files to be parsed in the designated input folder, without subfolders. This path is specified in the `configs/folders.yaml` file under the `original_ddi_folder` key.


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

