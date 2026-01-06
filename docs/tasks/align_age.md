## align_age

### About
This task aligns age-related values in an XML file by replacing PEF terminology with corresponding FReSH terminology. The transformation is applied using an external Excel mapping table to standardize all age fields across the dataset.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to be processed.
- **input_folder** (`str`): Path to the folder containing the input XML file.
- **output_folder** (`str`): Path to the folder where the transformed XML file will be saved.
- **context** (`optional`): Pipeline context providing access to a logger and a changelog for traceability.

### External Files
- **align-age.xlsx**: Excel mapping table defining the correspondence between PEF age values and FReSH values, used in general transformation mode.

### Output Arguments
This function does not explicitly return a value.  
Its effect is the creation of a transformed XML file written to the output folder, with all applied replacements persisted.

### How It Works
The function parses the input XML file and validates its existence. It then initializes a `FieldTransformer` with the external Excel mapping table in general mode. All applicable age values in the XML document are replaced according to the mapping rules. Each modification is optionally recorded in the pipeline changelog. Finally, the updated XML tree is written to the output folder with proper formatting and encoding. Any critical errors encountered during parsing or transformation are raised for pipeline-level handling.

### Libraries Used
- **pathlib.Path**: Used to manage file system paths in a platform-independent way.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **FieldTransformer**: Custom utility responsible for applying field-level transformations based on an Excel mapping table.
