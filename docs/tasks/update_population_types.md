## update_population_types

### About
This task aligns population type values in an XML file by replacing PEF terminology with corresponding FReSH terminology. The transformation is applied to `<PopulationFR>` nodes using multiple Excel mapping tables, ensuring standardized representation of population types across the dataset.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to be processed.
- **input_folder** (`str`): Path to the folder containing the input XML file.
- **output_folder** (`str`): Path to the folder where the transformed XML file will be saved.
- **context** (`optional`): Pipeline context providing access to a logger and a changelog for traceability.

### External Files
- **population-types-regles-migration.xlsx**: Primary Excel mapping table defining the correspondence between PEF and FReSH population type values.
- **population-types-repartition.xlsx**: Secondary Excel table used for additional transformations and alignment.

### Output Arguments
This function does not explicitly return a value.  
Its effect is the creation of a transformed XML file written to the output folder, with all applied replacements persisted.

### How It Works
1. The function validates and parses the input XML file.
2. Two consecutive `FieldTransformer` instances are applied:
   - **Primary migration rules**: replace PEF population type values with FReSH equivalents.
   - **Repartition rules**: apply additional transformations to ensure alignment.
3. Transformations operate in general mode, meaning mappings are applied globally rather than being file-specific.
4. Each modification is optionally recorded in the pipeline changelog.
5. The updated XML tree is written to the output folder with proper encoding and formatting. Any errors encountered during parsing or transformation are raised for pipeline-level handling.

### Libraries Used
- **pathlib.Path**: Used to manage file system paths in a platform-independent way.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **FieldTransformer**: Custom utility responsible for applying field-level transformations based on multiple Excel mapping tables.
