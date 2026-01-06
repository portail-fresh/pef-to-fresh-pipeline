## add_fresh_enrichment_namespace

### About
This task applies an XSLT transformation to an XML file to enrich it with the FReSH enrichment namespace. This ensures that the XML files conform to the FReSH schema and are ready for further processing or validation.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to transform.
- **input_folder** (`str`): Folder containing the original XML file.
- **output_folder** (`str`): Folder where the transformed XML file will be saved.

### Output Arguments
- Returns the path to the transformed XML file.

### How It Works
1. Reads the XML file from the input folder.
2. Loads folder configuration from `folders.yaml` to locate the XSLT file.
3. Executes the XSLT transformation using `execute_xsl_transformation`.
4. Writes the transformed XML content to the output folder.
5. Logs the process start, completion, and any errors encountered.

### Transformation Logic
- The XSLT preserves all existing elements and attributes in the XML (identity transformation).
- Adds a `fresh` namespace (`urn:fresh-enrichment:v1`) to the root element `<FichePortailEpidemiologieFrance>`.
- Ensures that the namespace is declared without modifying the existing content or structure of the XML.
- The transformation is idempotent: running it multiple times will not duplicate the namespace.

### External Files
- **`add-enrichment-namespace.xsl`**: Contains the XSLT logic to add the `fresh` namespace while keeping the XML structure intact.
- **`folders.yaml`**: Configuration file specifying folder paths, including `xslt_files_folder`.

### Notes
- Safe to apply multiple times; it does not change the XML content except for adding the namespace.
- Required for downstream FReSH enrichment steps.
- Fully logs actions and errors for traceability.
