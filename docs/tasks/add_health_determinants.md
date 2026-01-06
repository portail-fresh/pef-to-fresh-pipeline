## align_health_determinants

### About
This task aligns and normalizes health determinant values in an XML file by replacing PEF terminology with corresponding FReSH terminology. The transformation is driven by an external Excel mapping table and is applied uniformly to English health determinant nodes within the document.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to be processed.
- **input_folder** (`str`): Path to the folder containing the input XML file.
- **output_folder** (`str`): Path to the folder where the transformed XML file will be saved.
- **context** (`optional`): Pipeline context providing access to a logger and a changelog for traceability.

### External Files
- **align-health-determinants-fr-en.xlsx**: Excel mapping table defining the correspondence between PEF health determinant values and their FReSH equivalents, used in general transformation mode.

### Output Arguments
This function does not explicitly return a value.  
Its effect is the creation of a transformed XML file written to the output folder, with all applied replacements persisted.

### How It Works
The function validates the existence and syntactic correctness of the input XML file, then initializes a field transformation engine using an external Excel mapping table.

The transformation operates in a general mode, meaning that mappings are applied globally rather than being tied to a specific file identifier. All applicable health determinant values found in the XML document are replaced according to the mapping rules defined in the Excel file. Each modification is recorded in the changelog associated with the current file.

Finally, the updated XML document is written to disk with proper formatting and encoding. Any critical issues encountered during processing are logged and raised to ensure pipeline-level visibility.

### Libraries Used
- **pathlib.Path**: Used to manage file system paths in a platform-independent way.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **FieldTransformer**: Custom utility responsible for applying field-level transformations based on an Excel mapping table.
