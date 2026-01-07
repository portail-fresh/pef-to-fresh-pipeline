# Class: `Changelog`

The `Changelog` class tracks and logs all modifications made to a single XML file during a pipeline run.  
It records changes in both **human-readable log files** and **structured CSV files**, enabling detailed auditing and downstream analysis.

---

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `file_stem` | `str` | Base name of the XML file (without extension). |
| `log_path` | `Path` | Path to the human-readable `.log` file. |
| `csv_path` | `Path` | Path to the structured `.csv` file. |

---

## Methods

### `__init__(xml_file: str, log_dir: Path)`
Initializes a new `Changelog` instance for a given XML file. Creates the log and CSV files if they do not already exist.

**Parameters:**
- `xml_file` – Path or name of the XML file to track.
- `log_dir` – Directory where `.log` and `.csv` files will be saved.

---

### `start_task(task_name: str)`
Marks the beginning of a task in the human-readable log.  
Useful for visually grouping changes from a single transformation step.

**Parameters:**
- `task_name` – Name of the current task.

---

### `log_add(task: str, field: str, new_value: str)`
Logs the addition of a new value/field in the XML.

**Parameters:**
- `task` – Name of the transformation task.
- `field` – Name of the field being added.
- `new_value` – Value of the newly added field.

---

### `log_update(task: str, field: str, old_value: str, new_value: str)`
Logs an update to an existing field, including a line-by-line diff for readability.

**Parameters:**
- `task` – Name of the transformation task.
- `field` – Name of the field being updated.
- `old_value` – Original value before the change.
- `new_value` – Updated value after the change.

---

### `log_delete(task: str, field: str, old_value: str = "")`
Logs the deletion of a field from the XML.

**Parameters:**
- `task` – Name of the transformation task.
- `field` – Name of the field being deleted.
- `old_value` – Optional previous value of the deleted field.

---

### Internal/Helper Methods

These methods are primarily used internally by the class:

- `_timestamp() -> str`  
  Returns the current timestamp in `"YYYY-MM-DD HH:MM:SS"` format.

- `_write_log_line(message: str)`  
  Appends a single line to the human-readable `.log` file.

- `_write_csv_row(task: str, action: str, field: str, old: str = "", new: str = "")`  
  Appends a row to the CSV log with structured information.

- `_normalize_line(line: str) -> str`  
  Normalizes text for comparison by removing bullets, collapsing whitespace, and lowercasing.

- `_get_diff_by_line(old: str, new: str) -> str`  
  Generates a human-readable, line-by-line diff between two strings, ignoring bullet characters and spacing differences.

---

## Usage Example

```python
from pathlib import Path

# Initialize a changelog for a file
log_dir = Path("pipeline/runs/changelogs")
changelog = Changelog("study_001.xml", log_dir)

# Start a task
changelog.start_task("update_sampling_mode")

# Log an addition
changelog.log_add("update_sampling_mode", "SamplingModeEN", "Randomized")

# Log an update with diff
changelog.log_update("update_sampling_mode", "SamplingModeFR", "Aléatoire", "Randomisé")

# Log a deletion
changelog.log_delete("remove_empty_values", "DeterminantsDeSanteEN", "Diet")
