## update_recruitment_sources

### About
This task aligns recruitment source values in an XML file by replacing PEF terminology with corresponding FReSH terminology. The transformation is applied to `<RecrutementParIntermediaireFR>` nodes using multiple Excel mapping tables, ensuring standardized representation of recruitment sources across the dataset.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to be processed.
- **input_folder** (`str`): Path to the folder containing the input XML file.
- **output_folder** (`str`): Path to the folder where the transformed XML file will be saved.
- **context** (`optional`): Pipeline context providing access to a logger and a changelog for traceability.

### External Files
- **recruitment-sources-regles-migration.xlsx**: Primary Excel mapping table defining the correspondence between PEF and FReSH recruitment source values.
- **recruitment-sources-repartition.xlsx**: Secondary Excel table used for additional transformations and alignment.
- **recruitment-sources-delete.xlsx**: Excel file containing entries that should be removed from the XML as part of cleanup.

### Output Arguments
This function does not explicitly return a value.  
Its effect is the creation of a transformed XML file written to the output folder, with all applied replacements and deletions persisted.

### How It Works
1. The function parses the input XML file and validates its existence.
2. Three consecutive `FieldTransformer` instances are applied:
   - **Primary migration rules**: replace PEF recruitment source values with FReSH equivalents.
   - **Repartition rules**: apply additional transformations to ensure alignment.
   - **Delete rules**: remove values that should no longer be present.
3. Transformations operate in general mode, meaning mappings are applied globally rather than being file-specific.
4. Each modification is optionally recorded in the pipeline changelog.
5. The updated XML tree is written to the output folder with proper encoding and formatting. Any errors encountered during parsing or transformation are raised for pipeline-level handling.

### Libraries Used
- **pathlib.Path**: Used to manage file system paths in a platform-independent way.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **FieldTransformer**: Custom utility responsible for applying field-level transformations based on multiple Excel mapping tables.
