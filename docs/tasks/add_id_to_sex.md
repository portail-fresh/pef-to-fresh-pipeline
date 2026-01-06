## add_id_to_sex

### About
This task enriches sex-related XML elements (`<SexeFR>` and `<SexeEN>`) by attaching standardized URIs and vocabulary identifiers. The mapping between XML values and URIs is defined in an external Excel vocabulary file, allowing consistent referencing of terms across datasets. The sex term is already normalised in the `align_sex.py` task.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to be processed.
- **input_folder** (`str`): Path to the folder containing the input XML file.
- **output_folder** (`str`): Path to the folder where the enriched XML file will be saved.
- **context** (`optional`): Pipeline context providing access to a logger, changelog, and vocabulary folder.

### External Files
- **Sex.xlsx**: Excel vocabulary file containing the following columns:
  - `URI_*`: The URI associated with each term (exact column prefix defines the vocabulary name, e.g., `URI_MeSH` → vocab `"MeSH"`).
  - `label_fr`: French label for the term.
  - `label_en`: English label for the term.

### Output Arguments
This function does not explicitly return a value.  
Its effect is the creation of an enriched XML file written to the output folder, where each `<value>` element inside `<SexeFR>` and `<SexeEN>` may have additional `uri` and `vocab` attributes corresponding to the vocabulary mapping.

### How It Works
1. The function parses the input XML file and extracts `<SexeFR>` and `<SexeEN>` elements.
2. It reads the vocabulary Excel file and constructs normalized lookup tables for French and English labels.
3. Each `<value>` element is normalized (stripped, Unicode-normalized, and lowercased) and matched against the vocabulary.
4. When a match is found, `uri` and `vocab` attributes are added to the XML element.
5. Changes are optionally logged in the pipeline changelog for traceability.
6. The updated XML tree is written to the output folder with proper encoding and formatting.  
   
If a value in the XML does not exist in the vocabulary, a `ValueError` is raised to ensure data consistency.

### Libraries Used
- **pathlib.Path**: Used for platform-independent file path manipulation.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **pandas**: Used to read and process the Excel vocabulary file.
- **unicodedata**: Used to normalize Unicode strings for consistent matching.
