from pathlib import Path
from datetime import datetime
import csv
import difflib
import re


class Changelog:
    """
    Tracks and logs modifications made to a single XML file across multiple processing tasks.

    Each change is logged in two formats:
    - A human-readable `.log` file (one per input file), for review and debugging.
    - A structured `.csv` file (one per input file), for downstream analysis or reporting.
    """

    def __init__(self, xml_file: str, log_dir: Path):
        """
        Initializes the Changelog instance for a specific XML file.

        Args:
            xml_file (str): Path to the XML file being tracked.
            log_dir (Path): Directory where log and CSV files will be written.
        """
        self.file_stem = Path(xml_file).stem  # Get file name without extension
        self.log_path = log_dir / f"{self.file_stem}.log"
        self.csv_path = log_dir / f"{self.file_stem}.csv"

        log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize CSV file with header, if not already present
        if not self.csv_path.exists():
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "task", "action", "field", "old_value", "new_value"])

    def _timestamp(self) -> str:
        """
        Returns the current timestamp in a standard format.
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _write_log_line(self, message: str):
        """
        Appends a line to the text-based log file.

        Args:
            message (str): Message to write to the log file.
        """
        timestamp = self._timestamp()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} - {message}\n")

    def _write_csv_row(self, task: str, action: str, field: str, old: str = "", new: str = ""):
        """
        Appends a row to the CSV log.

        Args:
            task (str): Name of the task or transformation.
            action (str): One of "add", "update", or "delete".
            field (str): Name of the field being modified.
            old (str): Previous value (if any).
            new (str): New value (if any).
        """
        timestamp = self._timestamp()
        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, task, action, field, old, new])

    def start_task(self, task_name: str):
        """
        Marks the beginning of a task block in the human-readable log.

        Args:
            task_name (str): Identifier for the current task (e.g., a transformation step).
        """
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"\n==> Task: {task_name}\n")

    def _normalize_line(self, line: str) -> str:
        """
        Normalizes a text line for comparison: removes bullets, trims whitespace, and lowercases.

        Args:
            line (str): Line of text to normalize.

        Returns:
            str: Normalized version of the input line.
        """
        line = re.sub(r'[•\u2022]', '', line)  # Remove bullet symbols
        line = re.sub(r'\s+', ' ', line)       # Collapse multiple spaces
        return line.strip().lower()

    def _get_diff_by_line(self, old: str, new: str) -> str:
        """
        Computes a line-by-line diff between two strings, ignoring bullet and spacing differences.

        Args:
            old (str): Original string.
            new (str): Modified string.

        Returns:
            str: Human-readable unified diff format.
        """
        old_lines = old.strip().splitlines()
        new_lines = new.strip().splitlines()
        old_norm = [self._normalize_line(l) for l in old_lines]
        new_norm = [self._normalize_line(l) for l in new_lines]

        diff = difflib.ndiff(old_norm, new_norm)

        result = []
        i_old = 0
        i_new = 0
        for line in diff:
            code = line[0]
            if code == ' ':
                result.append(f"  {old_lines[i_old]}")
                i_old += 1
                i_new += 1
            elif code == '-':
                result.append(f"- {old_lines[i_old]}")
                i_old += 1
            elif code == '+':
                result.append(f"+ {new_lines[i_new]}")
                i_new += 1
        return '\n'.join(result)

    def log_add(self, task: str, field: str, new_value: str):
        """
        Logs the addition of a new field.

        Args:
            task (str): Task name.
            field (str): Name of the added field.
            new_value (str): Value of the new field.
        """
        diff = f"+ {new_value}"
        self._write_log_line(f"[{task}] Field '{field}' ADDED:\n{diff}")
        self._write_csv_row(task, "add", field, "", new_value)

    def log_update(self, task: str, field: str, old_value: str, new_value: str):
        """
        Logs the update of an existing field, showing the textual diff.

        Args:
            task (str): Task name.
            field (str): Name of the updated field.
            old_value (str): Previous value.
            new_value (str): New value.
        """
        diff = self._get_diff_by_line(old_value, new_value)
        self._write_log_line(f"[{task}] Field '{field}' UPDATED:\n{diff}")
        self._write_csv_row(task, "update", field, old_value, new_value)

    def log_delete(self, task: str, field: str, old_value: str = ""):
        """
        Logs the deletion of a field.

        Args:
            task (str): Task name.
            field (str): Name of the deleted field.
            old_value (str, optional): Previous value of the field. Defaults to "".
        """
        msg = f"[{task}] Field '{field}' DELETED"
        if old_value:
            diff = f"- {old_value}"
            msg += f":\n{diff}"
        self._write_log_line(msg)
        self._write_csv_row(task, "delete", field, old_value, "")
