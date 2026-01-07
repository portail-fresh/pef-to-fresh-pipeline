# Class: `PipelineContext`

The `PipelineContext` class serves as a centralized context object for a pipeline run, providing shared resources, folder paths, logging, and per-file changelogs for XML transformations. It is designed to simplify access to configuration, outputs, and logging for all stages of the pipeline.

---

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `folder_config` | `dict` | Loaded folder configuration from `folders.yaml`. Contains paths such as input files, conversion tables, and runs folder. |
| `api_config` | `dict` | Loaded API configuration from `api.yaml`. Includes credentials for external APIs (e.g., ICD). |
| `original_folder` | `str` | Path to the folder containing the original input XML files. |
| `runs_folder` | `str` | Base path for storing pipeline run outputs and logs. |
| `conversion_tables_folder` | `str` | Path to Excel conversion tables used for XML transformations. |
| `vocabs_folder` | `str` | Path to vocabulary files used in the pipeline. |
| `icd_client_id` | `str` | OAuth2 client ID for ICD API. |
| `icd_client_secret` | `str` | OAuth2 client secret for ICD API. |
| `icd_token_endpoint` | `str` | OAuth2 token endpoint for ICD API. |
| `icd_token` | `str or None` | Cached OAuth2 token for ICD API requests. |
| `run_dir` | `Path` | Unique folder for the current pipeline run. Automatically created with timestamp. |
| `outputs_dir` | `Path` | Subfolder under `run_dir` where processed XML files are saved. |
| `changelogs_dir` | `Path` | Subfolder under `run_dir` where per-file changelogs are stored. |
| `logger` | `logging.Logger` | Logger instance configured for the pipeline. |
| `changelogs` | `dict[str, Changelog]` | Dictionary holding `Changelog` instances for each XML file processed. |

---

## Methods

### `get_run_dir() -> Path`
Returns the main directory of the current pipeline run.

---

### `get_outputs_dir() -> Path`
Returns the path to the outputs folder for this run.

---

### `get_changelogs_dir() -> Path`
Returns the path to the changelogs folder for this run.

---

### `get_original_folder() -> str`
Returns the path to the folder containing original input XML files.

---

### `get_vocabs_folder() -> str`
Returns the path to the folder containing vocabulary files.

---

### `init_changelog_for_file(xml_file: str)`
Initializes a `Changelog` object for the given XML file if it does not already exist.  
This allows tracking all modifications applied to the file during the pipeline run.

**Parameters:**
- `xml_file` – Name of the XML file to initialize the changelog for.

---

### `get_changelog(xml_file: str) -> Changelog | None`
Returns the `Changelog` object for a given XML file.  
Returns `None` if the changelog has not been initialized.

**Parameters:**
- `xml_file` – Name of the XML file.

---

### `get_logger() -> logging.Logger`
Returns the logger instance for the pipeline. Can be used for consistent logging across tasks.

---

### `get_conversion_tables_folder() -> str`
Returns the folder path containing the Excel conversion tables used in transformations.

---

## Usage Example

```python
context = PipelineContext()

# Access folders
inputs = context.get_original_folder()
outputs = context.get_outputs_dir()

# Initialize changelog for a file
context.init_changelog_for_file("study_001.xml")
changelog = context.get_changelog("study_001.xml")

# Access logger
logger = context.get_logger()
logger.info("Pipeline started for study_001.xml")
