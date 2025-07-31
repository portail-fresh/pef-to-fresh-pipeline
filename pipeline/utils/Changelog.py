from pathlib import Path
from datetime import datetime
import csv
import difflib
import re


class Changelog:
    """
    Tracks modifications to a single XML file across multiple tasks.

    Logs are written both as:
    - A human-readable .log file (one per file)
    - A structured CSV file (one per file) for downstream analysis
    """

    def __init__(self, xml_file: str, log_dir: Path):
        self.file_stem = Path(xml_file).stem  # Remove extension
        self.log_path = log_dir / f"{self.file_stem}.log"
        self.csv_path = log_dir / f"{self.file_stem}.csv"

        log_dir.mkdir(parents=True, exist_ok=True)
        if not self.csv_path.exists():
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "task", "action", "field", "old_value", "new_value"])

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _write_log_line(self, message: str):
        timestamp = self._timestamp()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} - {message}\n")

    def _write_csv_row(self, task: str, action: str, field: str, old: str = "", new: str = ""):
        timestamp = self._timestamp()
        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, task, action, field, old, new])

    def start_task(self, task_name: str):
        """
        Marks the beginning of a new task section in the text log.
        """
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"\n==> Task: {task_name}\n")

    """
    def log_add(self, task: str, field: str, new_value: str):
        self._write_log_line(f"[{task}] Field '{field}' ADDED with value: {new_value}")
        self._write_csv_row(task, "add", field, "", new_value)

    def log_update(self, task: str, field: str, old_value: str, new_value: str):
        self._write_log_line(f"[{task}] Field '{field}' UPDATED from: {old_value} \nto:\n {new_value}")
        self._write_csv_row(task, "update", field, old_value, new_value)

    def log_delete(self, task: str, field: str, old_value: str = ""):
        msg = f"[{task}] Field '{field}' DELETED"
        if old_value:
            msg += f" (was: {old_value})"
        self._write_log_line(msg)
        self._write_csv_row(task, "delete", field, old_value, "")

    def log_custom(self, task: str, message: str):
        self._write_log_line(f"[{task}] {message}")
        self._write_csv_row(task, "custom", "", "", message)
    """
    
    def _normalize_line(self, line: str) -> str:
        line = re.sub(r'[•\u2022]', '', line)  # Rimuove bullet
        line = re.sub(r'\s+', ' ', line)       # Normalizza spazi
        return line.strip().lower()

    def _get_diff_by_line(self, old: str, new: str) -> str:
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
        diff = f"+ {new_value}"
        self._write_log_line(f"[{task}] Field '{field}' ADDED:\n{diff}")
        self._write_csv_row(task, "add", field, "", new_value)

    def log_update(self, task: str, field: str, old_value: str, new_value: str):
        diff = self._get_diff_by_line(old_value, new_value)
        self._write_log_line(f"[{task}] Field '{field}' UPDATED:\n{diff}")
        self._write_csv_row(task, "update", field, old_value, new_value)
        
    def log_delete(self, task: str, field: str, old_value: str = ""):
        msg = f"[{task}] Field '{field}' DELETED"
        if old_value:
            diff = f"- {old_value}"
            msg += f":\n{diff}"
        self._write_log_line(msg)
        self._write_csv_row(task, "delete", field, old_value, "")

