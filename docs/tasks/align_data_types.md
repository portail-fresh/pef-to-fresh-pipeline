## align_data_types

### About
This task aligns and normalizes data type values in an XML file by replacing PEF terminology with corresponding FReSH terminology. The transformation is applied to `<TypeDonneesRecueilliesFR>` nodes using multiple Excel mapping tables, supporting consistent representation of data types across the dataset.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to be processed.
- **input_folder** (`str`): Path to the folder containing the input XML file.
- **output_folder** (`str`): Path to the folder where the transformed XML file will be saved.
- **context** (`optional`): Pipeline context providing access to a logger and a changelog for traceability.

### External Files
- **data-types-regles-migration.xlsx**: Primary Excel mapping table defining the correspondence between PEF data type values and FReSH values.
- **data-types-repartition.xlsx**: Secondary Excel table used to apply additional data type transformations to specific XML files.

### Output Arguments
This function does not explicitly return a value.  
Its effect is the creation of a transformed XML file written to the output folder, with all applied replacements persisted.

### How It Works
The function validates the input XML file and parses it into a tree structure. It initializes a transformation engine (`FieldTransformer`) twice: first with the primary mapping table, then with the secondary repartition table. Both transformations operate in general mode, meaning mappings are applied globally rather than being file-specific. 

All applicable `<TypeDonneesRecueilliesFR>` values are replaced according to the Excel mappings, and all modifications are optionally logged in the pipeline changelog. Finally, the updated XML document is written to the output folder with proper formatting and encoding. Any errors encountered during parsing or transformation are raised for pipeline-level handling.

### Libraries Used
- **pathlib.Path**: Used to manage file system paths in a platform-independent way.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **FieldTransformer**: Custom utility responsible for applying field-level transformations based on Excel mapping tables.
