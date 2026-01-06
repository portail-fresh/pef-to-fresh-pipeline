## align_sex

### About
This task aligns sex categories values in an XML file by replacing PEF terminology with corresponding FReSH terminology. The transformation is applied to relevant sex fields using an external Excel mapping table to ensure standardized representation across the dataset.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to be processed.
- **input_folder** (`str`): Path to the folder containing the input XML file.
- **output_folder** (`str`): Path to the folder where the transformed XML file will be saved.
- **context** (`optional`): Pipeline context providing access to a logger and a changelog for traceability.

### External Files
- **align-sex.xlsx**: Excel mapping table defining the correspondence between PEF sex values and FReSH values, used in general transformation mode.

### Output Arguments
This function does not explicitly return a value.  
Its effect is the creation of a transformed XML file written to the output folder, with all applied replacements persisted.

### How It Works
The function parses the input XML file and validates its existence. A `FieldTransformer` is initialized with the external Excel mapping table, operating in general mode so that all applicable sex values in the XML are replaced according to the mapping. Each transformation is optionally recorded in the pipeline changelog. The updated XML tree is then written to the output folder with proper encoding and formatting. Any critical errors during parsing or transformation are raised to ensure pipeline-level handling.

### Libraries Used
- **pathlib.Path**: Used to manage file system paths in a platform-independent way.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **FieldTransformer**: Custom utility responsible for applying field-level transformations based on an Excel mapping table.
