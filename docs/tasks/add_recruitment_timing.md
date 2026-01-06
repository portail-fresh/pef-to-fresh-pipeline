## add_recruitment_timing

### About
This task updates the recruitment timing information in an XML file based on the value of `<TypeEnqueteFR>/<value>`. It standardizes cross-sectional and longitudinal study types by either replacing them with `<RecruitmentTimingFR>`/`<RecruitmentTimingEN>` elements or deleting the original type elements when appropriate.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process.
- **input_folder** (`str`): Folder containing the XML file.
- **output_folder** (`str`): Folder where the updated XML file will be written.
- **context** (`optional`): Pipeline context providing access to changelog utilities and other runtime data.

### Output Arguments
- Returns the path to the updated XML file after modifications.

### How It Works
1. The XML file is parsed and all `<TypeEnqueteFR>` elements are located anywhere in the hierarchy.
2. For each `<TypeEnqueteFR>/<value>`, three scenarios are handled:
   - `"Etudes transversales non répétées (hors enquêtes cas-témoins)"`: replaces with `<RecruitmentTimingFR>` = `"Etude transversale non répétée"` and `<RecruitmentTimingEN>` = `"One-time cross-sectional study"`.
   - `"Etudes transversales répétées (hors enquêtes cas-témoins)"`: replaces with `<RecruitmentTimingFR>` = `"Etude transversale répétée"` and `<RecruitmentTimingEN>` = `"Repeated cross-sectional study"`.
   - `"Etudes longitudinales (hors cohortes)"`: deletes `<TypeEnqueteFR>` and `<TypeEnqueteEN>` without adding new elements.
3. The function removes the original `<TypeEnqueteFR>` and corresponding `<TypeEnqueteEN>` elements, then adds the new recruitment timing elements if needed.
4. All changes are optionally logged in the pipeline changelog for traceability.
5. The updated XML tree is written back to the output folder with proper formatting.

### Libraries Used
- **lxml.etree**: Used for parsing, modifying, and writing XML documents.
