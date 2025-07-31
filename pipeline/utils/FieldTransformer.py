import os
import json
import re
import html
import pandas as pd
from lxml import etree
from typing import Optional, Dict, Any
from pipeline.utils.Changelog import Changelog


class FieldTransformer:
    """
    Applies field-level transformations to an XML ElementTree based on Excel + JSON configuration.
    Supports logging of all operations using an XmlChangelog instance.
    """

    def __init__(self, excel_path: str, file_id: str, task_name:str, changelog: Changelog):
        """
        Initialize the transformer.

        Args:
            excel_path (str): Name of the Excel file (only filename, not full path).
            file_id (str): ID of the XML file to match against the Excel rows.
            changelog (XmlChangelog): Instance for logging all modifications.
        """
        self.task_name=task_name
        self.excel_filename = os.path.basename(excel_path)
        self.excel_path = os.path.join("files", "conversion-tables", self.excel_filename)
        self.file_id = str(file_id)
        self.changelog = changelog
        self.config_path = self._resolve_config_path()
        self.config: Dict[str, Any] = {}
        self.df: Optional[pd.DataFrame] = None
        self.row: Optional[pd.Series] = None

        self._load_config()
        self._load_excel()
        self._match_row()

    def _resolve_config_path(self) -> str:
        excel_name = os.path.splitext(self.excel_filename)[0]
        return os.path.join("configs", f"{excel_name}.json")
    
    def _sanitize_for_xml(self, value):
        if pd.isna(value):
            return ""
        value = str(value)
        value = value.replace("_x000D_", " ")
        value = value.replace("\n", " ").replace("\t", " ")
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', value)
        value = html.escape(value)
        value = ' '.join(value.split())
        return value

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found at '{self.config_path}'")

        with open(self.config_path, encoding="utf-8") as f:
            try:
                self.config = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON config: {e}")

        if "file_id_column" not in self.config or "operations" not in self.config:
            raise ValueError("Config file must contain 'file_id_column' and 'operations'.")

    def _load_excel(self):
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Excel file not found: {self.excel_path}")
        self.df = pd.read_excel(self.excel_path)
        self._validate_excel_columns()

    def _validate_excel_columns(self):
        required_cols = {self.config["file_id_column"]}
        for op in self.config["operations"]:
            if "from" in op:
                required_cols.add(op["from"]["col"])
            if "to" in op:
                required_cols.add(op["to"]["col"])
        missing = required_cols - set(self.df.columns)
        if missing:
            raise ValueError(f"Missing columns in Excel file: {missing}")

    def _match_row(self):
        match = self.df[self.df[self.config["file_id_column"]].astype(str) == self.file_id]
        if match.empty:
            print(f"No matching row found for ID '{self.file_id}'. No transformations will be applied.")
            self.row = None
        else:
            self.row = match.iloc[0]

    def apply_transformations(self, tree: etree._ElementTree) -> etree._ElementTree:
        """
        Applies the configured transformations to the XML tree.

        Args:
            tree (etree._ElementTree): The XML tree to modify.

        Returns:
            etree._ElementTree: The transformed XML tree.
        """
        if self.row is None:
            return tree

        root = tree.getroot()
        for op in self.config["operations"]:
            self._apply_operation(op, root)

        return tree

    def _apply_operation(self, op: Dict[str, Any], root: etree._Element):
        op_type = op.get("type")

        if op_type == "update":
            self._apply_update(op, root)
        elif op_type == "add":
            self._apply_add(op, root)
        elif op_type == "delete":
            self._apply_delete(op, root)
        else:
            print(f"Unknown operation type: '{op_type}'")

    def _apply_update(self, op: Dict[str, Any], root: etree._Element):
        raw_val = self.row[op["to"]["col"]]
        to_val = self._sanitize_for_xml(raw_val)
        nodes = root.xpath(op["to"]["xpath"])
        if not nodes:
            print(f"Update skipped: no nodes found for XPath '{op['to']['xpath']}'")
            return
        for node in nodes:
            old_val = self._sanitize_for_xml(node.text or "")
            if old_val != to_val:
                node.text = to_val
                self.changelog.log_update(self.task_name, op["to"]["xpath"], old_val, to_val)

    def _apply_add(self, op: Dict[str, Any], root: etree._Element):
        raw_val = self.row[op["to"]["col"]]
        to_val = self._sanitize_for_xml(raw_val)
        parent_path = os.path.dirname(op["to"]["xpath"])
        tag = os.path.basename(op["to"]["xpath"])
        parent_nodes = root.xpath(parent_path)
        if not parent_nodes:
            print(f"Add skipped: parent node not found for XPath '{parent_path}'")
            return
        for parent in parent_nodes:
            new_elem = etree.Element(tag)
            new_elem.text = to_val
            parent.append(new_elem)
            self.changelog.log_add(self.task_name, op["to"]["xpath"], to_val)

    def _apply_delete(self, op: Dict[str, Any], root: etree._Element):
        nodes = root.xpath(op["from"]["xpath"])
        if not nodes:
            print(f"Delete skipped: no nodes found for XPath '{op['from']['xpath']}'")
            return
        for node in nodes:
            old_val = self._sanitize_for_xml(node.text or "")
            parent = node.getparent()
            if parent is not None:
                parent.remove(node)
                self.changelog.log_delete(self.task_name, op["from"]["xpath"], old_val)

