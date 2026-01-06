## add_fresh_identifier

### About
This task enriches an XML file by adding a FReSH-specific identifier element `<fresh:ID>` inside the `<Metadonnees>` section. The identifier uniquely links the XML to the FReSH system.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to modify.
- **input_folder** (`str`): Folder containing the original XML file.
- **output_folder** (`str`): Folder where the updated XML file will be saved.
- **context** (optional): Pipeline context providing logging and changelog utilities.

### Output Arguments
- Returns the path to the updated XML file.

### How It Works
1. Reads the XML file and parses it into an XML tree.
2. Registers the FReSH namespace (`urn:fresh-enrichment:v1`) if it is not already present.
3. Locates the `<Metadonnees>` element in the XML.
4. Retrieves the `<ID>` value from `<Metadonnees>` and constructs a new FReSH ID as `FRESH-PEF<ID>`.
5. Checks if a `<fresh:ID>` element already exists:
   - If not, creates `<fresh:ID>` with the `agency="FReSH"` attribute and sets its text to the constructed value.
   - If it exists, the task skips creation.
6. Logs any additions using the changelog (if available).
7. Writes the updated XML to the output folder, preserving formatting and encoding.

### Notes
- Ensures idempotency: running the task multiple times will not duplicate `<fresh:ID>`.
- Raises an error if `<Metadonnees>` or `<ID>` is missing, as these are required to generate the FReSH ID.
- Fully logs actions and errors for traceability.
- Must be run after the XML has been enriched with the FReSH namespace (e.g., after `add_fresh_enrichment_namespace`).

