## add_id_to_dataaccess

### About
Enriches `<IndividualDataAccessFR>` and `<IndividualDataAccessEN>` elements in an XML file by adding URI and vocabulary attributes from a standardized Excel mapping. The task uses the FReSH namespace and ensures only elements with valid labels and URIs are updated.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process.
- **input_folder** (`str`): Folder containing the original XML file.
- **output_folder** (`str`): Folder where the processed XML file will be saved.
- **context** (optional): Pipeline context providing logger and changelog utilities.

### External Files
- **`IndividualDataAccess.xlsx`**: Excel vocabulary file mapping XML labels to URIs.  
  Contents:
  - `URI_<vocab>`: URI to assign for each label, used as the value for the `uri` attribute.
  - `label_fr`: French labels to match `<IndividualDataAccessFR>` elements.
  - `label_en`: English labels to match `<IndividualDataAccessEN>` elements.  
  This file drives the enrichment of XML elements by supplying the `uri` and `vocab` attributes.

### Output Arguments
- Saves the enriched XML file to the output folder.
- Logs any enrichment changes to the changelog if available.

### How It Works
1. Parses the input XML with `lxml.etree`.
2. Loads the vocabulary Excel file using `pandas` and builds normalized lookup maps for French and English labels.
3. Iterates over `<IndividualDataAccessFR>` and `<IndividualDataAccessEN>` elements within the FReSH namespace.
4. Adds `uri` and `vocab` attributes only if a valid mapping exists.
5. Records the enrichment in the changelog if provided.
6. Writes the updated XML to the output folder with pretty formatting and XML declaration.

### Libraries Used
- **pathlib.Path**: Handles file system paths in a platform-independent manner.
- **lxml.etree**: Parses, manipulates, and writes XML documents.
- **pandas**: Reads Excel files and builds label-to-URI mappings.
- **unicodedata**: Normalizes Unicode text for reliable string comparison.
