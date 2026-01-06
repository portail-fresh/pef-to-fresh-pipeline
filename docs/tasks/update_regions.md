## update_regions

### About
This task updates region-related fields in an XML file by applying value replacements defined in a global Excel-based mapping table. It is designed to support region migration and normalization across datasets, independently of any specific file identifier, while ensuring all changes are tracked through the pipeline changelog.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to be processed.
- **input_folder** (`str`): Path to the folder containing the input XML file.
- **output_folder** (`str`): Path to the folder where the transformed XML file will be saved.
- **context** (`optional`): Pipeline context providing access to a logger and a changelog used to track field-level transformations.

### Output Arguments
This function does not explicitly return a value.  
Its effect is the creation of an updated XML file written to the output folder, with all applied transformations persisted.

### How It Works
The function loads the XML file and validates its existence and syntactic correctness. It then initializes a field transformation engine configured with a global Excel mapping file that defines how regional values should be migrated.

The transformation operates in a general mode, meaning that mappings are applied uniformly across files rather than being tied to a specific file identifier. Each applicable XML field is updated according to the mapping rules, and all modifications are recorded in the changelog associated with the current file.

After applying the transformations, the updated XML tree is saved to the output directory. Any critical issues encountered during processing cause the task to stop and surface the error for pipeline-level handling.

### Libraries Used
- **pathlib.Path**: Used to manage file system paths in a platform-independent way.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **FieldTransformer**: Custom utility responsible for applying field-level transformations based on an Excel mapping table.
