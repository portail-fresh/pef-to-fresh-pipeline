## add_provenance

### About
Enriches an XML file by adding a `<fresh:Provenance>` element to the root. This element specifies the provenance of the data as "Portail Épidémiologie France" (PEF) and is always added, replacing any existing `<fresh:Provenance>` elements.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process.
- **input_folder** (`str`): Folder containing the XML file.
- **output_folder** (`str`): Folder where the updated XML file will be saved.
- **context** (optional): Pipeline context providing logger and changelog utilities.

### External Files
This task does not require external mapping files; the value is fixed within the function.

### Output Arguments
- Writes the updated XML file to the output folder.
- Logs the addition of `<fresh:Provenance>` in the changelog if available.

### How It Works
1. Parses the XML file using `lxml.etree`.
2. Ensures the `fresh` namespace is registered.
3. Removes any existing `<fresh:Provenance>` elements to avoid duplicates.
4. Creates a new `<fresh:Provenance>` element with text `"Portail Épidémiologie France"`.
5. Appends the element to the root of the XML.
6. Logs the addition if a changelog is available.
7. Writes the transformed XML back to the output folder.

### Libraries Used
- **os.path.join**: Constructs platform-independent file paths.
- **lxml.etree**: For parsing, manipulating, and writing XML files.
