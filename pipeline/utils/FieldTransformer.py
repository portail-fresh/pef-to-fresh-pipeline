import os
import json
import re
import html
import pandas as pd
from lxml import etree
from typing import Optional, Dict, Any, List
from pipeline.utils.Changelog import Changelog


class FieldTransformer:
    """
    Applies field-level transformations to an XML ElementTree based on Excel + JSON configuration.
    Supports both 'by_id' and 'general' modes, and logs operations with a Changelog.
    """

    def __init__(self, excel_path: str, file_id: str, task_name: str, changelog: Changelog):
        self.task_name = task_name
        self.excel_filename = os.path.basename(excel_path)
        self.excel_path = os.path.join("files", "conversion-tables", self.excel_filename)
        self.file_id = str(file_id)
        self.changelog = changelog
        self.config_path = self._resolve_config_path()
        self.config: Dict[str, Any] = {}
        self.df: Optional[pd.DataFrame] = None
        self.row: Optional[pd.Series] = None
        self.mode: str = "by_id"

        self._load_config()
        self._load_excel()

        if self.mode == "by_id":
            self._match_row()

    def _resolve_config_path(self) -> str:
        excel_name = os.path.splitext(self.excel_filename)[0]
        return os.path.join("configs", f"{excel_name}.json")

    def _sanitize_for_xml(self, value) -> str:
        if pd.isna(value):
            return ""
        value = str(value)
        value = value.replace("_x000D_", " ").replace("\n", " ").replace("\t", " ")
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', value)
        value = html.escape(value)
        return ' '.join(value.split())

    def _normalize_xpath(self, xpath: str) -> str:
        return xpath if xpath.startswith(("/", ".", "//")) else f"//{xpath}"

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found at '{self.config_path}'")

        with open(self.config_path, encoding="utf-8") as f:
            try:
                self.config = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON config: {e}")

        if "operations" not in self.config:
            raise ValueError("Config file must contain 'operations'.")

        self.mode = self.config.get("mode", "by_id")

        if self.mode not in {"by_id", "general"}:
            raise ValueError(f"Unsupported mode: '{self.mode}'")

        if self.mode == "by_id" and "file_id_column" not in self.config:
            raise ValueError("Missing 'file_id_column' in config for mode 'by_id'.")

    def _load_excel(self):
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Excel file not found: {self.excel_path}")
        self.df = pd.read_excel(self.excel_path)
        self._validate_excel_columns()

    def _validate_excel_columns(self):
        required_cols = set()
        for op in self.config["operations"]:
            if "from" in op and "col" in op["from"]:
                required_cols.add(op["from"]["col"])
            if "to" in op and "col" in op["to"]:
                required_cols.add(op["to"]["col"])
        if self.mode == "by_id":
            required_cols.add(self.config["file_id_column"])
        missing = required_cols - set(self.df.columns)
        if missing:
            raise ValueError(f"Missing columns in Excel file: {missing}")

    def _match_row(self):
        match = self.df[self.df[self.config["file_id_column"]].astype(str) == self.file_id]
        self.row = match.iloc[0] if not match.empty else None

    def apply_transformations(self, tree: etree._ElementTree) -> etree._ElementTree:
        if self.mode == "by_id" and self.row is None:
            return tree

        root = tree.getroot()
        for op in self.config["operations"]:
            if not op.get("enabled", True):
                continue
            if self.mode == "by_id":
                self._apply_operation(op, root, self.row)
            else:
                for _, row in self.df.iterrows():
                    self._apply_operation(op, root, row)
        return tree

    def _apply_operation(self, op: Dict[str, Any], root: etree._Element, row: pd.Series):
        op_type = op.get("type")
        if op_type == "update":
            self._apply_update(op, root, row)
        elif op_type == "add":
            self._apply_add(op, root, row)
        elif op_type == "delete":
            self._apply_delete(op, root)

    def _is_significant(self, value: str) -> bool:
        return bool(value.strip() and re.search(r'\w', value))

    def _apply_update(self, op: Dict[str, Any], root: etree._Element, row: pd.Series):
        from_val_raw = row.get(op["from"]["col"])
        to_val_raw = row.get(op["to"]["col"])
        if pd.isna(from_val_raw) or pd.isna(to_val_raw):
            return

        from_val = self._sanitize_for_xml(from_val_raw)
        to_val = self._sanitize_for_xml(to_val_raw)
        xpath = self._normalize_xpath(op["to"]["xpath"])
        nodes = root.xpath(xpath)

        for node in nodes:
            for val_node in self._extract_value_nodes(node):
                old_val = self._sanitize_for_xml(val_node.text or "")
                if old_val == from_val and old_val != to_val:
                    val_node.text = to_val
                    self.changelog.log_update(self.task_name, xpath, old_val, to_val)

    def _apply_add(self, op: Dict[str, Any], root: etree._Element, row: pd.Series):
        raw_val = row.get(op["to"]["col"])
        to_val = self._sanitize_for_xml(raw_val)
        if not self._is_significant(to_val):
            return

        xpath = self._normalize_xpath(op["to"]["xpath"].strip()).rstrip("/")
        path_parts = xpath.rsplit("/", 1)
        parent_path, tag = path_parts if len(path_parts) == 2 else (".", path_parts[0])
        if not tag:
            raise ValueError(f"Invalid XPath: cannot extract tag name from '{xpath}'")

        is_fresh = op["to"].get("is_fresh", True)
        parent_nodes = root.xpath(parent_path) or [root]
        for parent in parent_nodes:
            new_elem = etree.Element(f"{{urn:fresh-enrichment:v1}}{tag}") if is_fresh else etree.Element(tag)
            new_elem.text = to_val
            parent.append(new_elem)
            self.changelog.log_add(self.task_name, xpath, to_val)

    def _apply_delete(self, op: Dict[str, Any], root: etree._Element):
        xpath = self._normalize_xpath(op["from"]["xpath"])
        nodes = root.xpath(xpath)
        for node in nodes:
            for val_node in self._extract_value_nodes(node):
                old_val = self._sanitize_for_xml(val_node.text or "")
                parent = val_node.getparent()
                if parent is not None:
                    parent.remove(val_node)
                    self.changelog.log_delete(self.task_name, xpath, old_val)

    def _extract_value_nodes(self, node: etree._Element) -> List[etree._Element]:
        return node.findall("value") or [node]
