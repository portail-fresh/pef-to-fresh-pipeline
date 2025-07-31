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
    Supports logging of all operations using a Changelog instance.
    """

    def __init__(self, excel_path: str, file_id: str, task_name: str, changelog: Changelog):
        """
        Initializes the FieldTransformer with input paths, configuration and logging.

        Args:
            excel_path (str): Name of the Excel file (filename only).
            file_id (str): ID of the XML file to match against Excel rows.
            task_name (str): Name of the current processing task.
            changelog (Changelog): Changelog instance for tracking modifications.
        """
        self.task_name = task_name
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

    def _sanitize_for_xml(self, value) -> str:
        """
        Cleans up a raw string for safe XML insertion.

        Args:
            value: A raw cell value (can be NaN, number, or string).

        Returns:
            str: XML-safe string.
        """
        if pd.isna(value):
            return ""
        value = str(value)
        value = value.replace("_x000D_", " ")
        value = value.replace("\n", " ").replace("\t", " ")
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', value)
        value = html.escape(value)
        value = ' '.join(value.split())
        return value

    def _normalize_xpath(self, xpath: str) -> str:
        """
        Ensures that the XPath string starts with '//' unless it's absolute or relative.

        Args:
            xpath (str): Raw XPath from config.

        Returns:
            str: Normalized XPath.
        """
        if xpath.startswith(("/", ".", "//")):
            return xpath
        return f"//{xpath}"

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
        Applies configured transformations to the provided XML tree.

        Args:
            tree (etree._ElementTree): Input XML tree.

        Returns:
            etree._ElementTree: Modified XML tree.
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
        xpath = self._normalize_xpath(op["to"]["xpath"])
        nodes = root.xpath(xpath)
        if not nodes:
            print(f"Update skipped: no nodes found for XPath '{xpath}'")
            return
        for node in nodes:
            old_val = self._sanitize_for_xml(node.text or "")
            if old_val != to_val:
                node.text = to_val
                self.changelog.log_update(self.task_name, xpath, old_val, to_val)

    def _apply_add(self, op: Dict[str, Any], root: etree._Element):
        raw_val = self.row[op["to"]["col"]]
        to_val = self._sanitize_for_xml(raw_val)
        xpath = self._normalize_xpath(op["to"]["xpath"].strip())
        is_fresh = op["to"].get("is_fresh", True)

        # Clean trailing slash
        xpath = xpath.rstrip("/")
        
        # Split into parent path and tag
        path_parts = xpath.rsplit("/", 1)
        if len(path_parts) == 2:
            parent_path, tag = path_parts
        else:
            # Means xpath is just like 'ExclusionCriteria'
            parent_path = "."
            tag = path_parts[0]

        if not tag:
            raise ValueError(f"Invalid XPath: cannot extract tag name from '{xpath}'")

        parent_nodes = root.xpath(parent_path)
        if not parent_nodes:
            print(f"Parent node not found for XPath '{parent_path}'. Inserting under root instead.")
            parent_nodes = [root]

        for parent in parent_nodes:
            if is_fresh:
                new_elem = etree.Element(f"{{urn:fresh-enrichment:v1}}{tag}")
            else:
                new_elem = etree.Element(tag)
            new_elem.text = to_val
            parent.append(new_elem)
            self.changelog.log_add(self.task_name, xpath, to_val)




    def _apply_delete(self, op: Dict[str, Any], root: etree._Element):
        xpath = self._normalize_xpath(op["from"]["xpath"])
        nodes = root.xpath(xpath)
        if not nodes:
            print(f"Delete skipped: no nodes found for XPath '{xpath}'")
            return
        for node in nodes:
            old_val = self._sanitize_for_xml(node.text or "")
            parent = node.getparent()
            if parent is not None:
                parent.remove(node)
                self.changelog.log_delete(self.task_name, xpath, old_val)
