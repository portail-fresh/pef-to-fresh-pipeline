## process_collection_dates

### About
This task normalizes collection date fields in an XML file by converting heterogeneous year or date expressions into a standardized ISO-like format (`YYYY-01-01`). It also removes date elements that indicate ongoing or undetermined collections, while optionally recording all transformations in a structured changelog for traceability within the pipeline.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to be processed.
- **input_folder** (`str`): Path to the folder containing the input XML file.
- **output_folder** (`str`): Path to the folder where the processed XML file will be saved.
- **context** (`optional`): Pipeline context object providing access to a changelog interface used to record updates and deletions.

### Output Arguments
This function does not explicitly return a value.  
Its effect is the creation of a processed XML file written to the output folder.  
If a context with a changelog is provided, transformations are recorded there as a side effect.

### How It Works
The function parses the XML document and targets a predefined set of elements representing collection start and end years in multiple languages. For each of these elements, it:

1. Skips empty values.
2. Detects textual markers indicating ongoing or undetermined collections and removes the corresponding XML elements.
3. Attempts to parse the date using a generic date parser to extract the year.
4. Falls back to a predefined mapping for known unstructured or ambiguous date formats.
5. Raises an error if the date cannot be interpreted by either strategy.
6. Normalizes valid years into the format `YYYY-01-01`.

Whenever a value is updated or removed, the change is optionally logged into a changelog provided by the pipeline context. Finally, the modified XML is written back to disk with proper formatting and encoding.

### Libraries Used
- **lxml.etree**: Used to parse, navigate, modify, and write XML documents.
- **dateutil.parser**: Used to flexibly parse heterogeneous date strings and extract year information.
- **datetime**: Used to provide default date values during parsing.
