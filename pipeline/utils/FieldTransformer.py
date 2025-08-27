import os
import json
import re
import html
import unicodedata
import pandas as pd
from lxml import etree
from typing import Optional, Dict, Any, List
from pipeline.utils.Changelog import Changelog


class FieldTransformer:
    """
    FieldTransformer applies XML transformations to a single file using
    a combination of Excel lookup tables and a corresponding JSON configuration file.

    It supports two operational modes:

    - 'by_id' (default): applies transformations based on a unique file identifier (e.g., file name),
      matching the corresponding row in the Excel file.
    - 'general': applies transformations row-by-row across the entire Excel file,
      matching values globally within the XML without needing a specific file ID.

    All changes are logged using the provided Changelog instance.

    Attributes:
        task_name (str): Name of the task for changelog tracking.
        excel_filename (str): Filename of the Excel mapping table.
        excel_path (str): Full path to the Excel file (inside 'files/conversion-tables').
        file_id (str): Unique identifier for the current XML file.
        changelog (Changelog): Changelog instance to record all modifications.
        config_path (str): Path to the associated JSON configuration file.
        config (Dict): Parsed JSON configuration.
        df (pd.DataFrame): Loaded Excel data as a DataFrame.
        row (pd.Series): Matched row for the current file (used in 'by_id' mode).
        mode (str): Operation mode, either 'by_id' or 'general'.
    """

    def __init__(self, excel_path: str, file_id: str, task_name: str, changelog: Changelog):
        """
        Initialize the FieldTransformer with file paths and configuration.

        Args:
            excel_path (str): Path to the Excel file containing the mapping table.
            file_id (str): Identifier used to locate the relevant row in 'by_id' mode.
            task_name (str): Name of the task for changelog grouping.
            changelog (Changelog): Changelog instance used for logging operations.
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
        self.mode: str = "by_id"
        self._replace_set_logged = set()

        self._load_config()
        self._load_excel()

        if self.mode == "by_id":
            self._match_row()

    def _resolve_config_path(self) -> str:
        """
        Determines the path to the JSON config file associated with the Excel file.

        Returns:
            str: Path to the JSON configuration file.
        """
        excel_name = os.path.splitext(self.excel_filename)[0]
        return os.path.join("configs", f"{excel_name}.json")

    def _sanitize_for_xml(self, value) -> str:
        """
        Cleans a value to make it safe and valid for XML output.

        Args:
            value: Any value from Excel or XML.

        Returns:
            str: Sanitized and XML-safe string.
        """
        if pd.isna(value):
            return ""
        value = str(value)
        value = value.replace("_x000D_", " ").replace("\n", " ").replace("\t", " ")
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', value)
        value = html.escape(value)
        return ' '.join(value.split())

    def _normalize_xpath(self, xpath: str) -> str:
        """
        Converts shorthand XPath to a fully-qualified one, ensuring it starts with '/' or '//'.

        Args:
            xpath (str): Original XPath string.

        Returns:
            str: Normalized XPath string.
        """
        return xpath if xpath.startswith(("/", ".", "//")) else f"//{xpath}"

    def _load_config(self):
        """
        Loads the transformation configuration from the JSON file.

        Raises:
            FileNotFoundError: If config file does not exist.
            ValueError: If JSON is invalid or required fields are missing.
        """
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
        """
        Loads the Excel mapping table and validates required columns.

        Raises:
            FileNotFoundError: If Excel file does not exist.
            ValueError: If required columns are missing.
        """
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Excel file not found: {self.excel_path}")
        self.df = pd.read_excel(self.excel_path)
        self._validate_excel_columns()

    def _validate_excel_columns(self):
        """
        Validates that all required columns referenced in operations are present in the Excel file.

        Raises:
            ValueError: If any expected column is missing.
        """
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
        self.row = match if not match.empty else pd.DataFrame()

    def apply_transformations(self, tree: etree._ElementTree) -> etree._ElementTree:
        if self.mode == "by_id" and self.row.empty:
            return tree

        root = tree.getroot()
        for op in self.config["operations"]:
            if not op.get("enabled", True):
                continue
            if self.mode == "by_id":
                for _, row in self.row.iterrows():  # iteri su tutte le righe corrispondenti
                    self._apply_operation(op, root, row)
            else:
                for _, row in self.df.iterrows():
                    self._apply_operation(op, root, row)
        return tree

    def _apply_operation(self, op: Dict[str, Any], root: etree._Element, row: pd.Series):
        """
        Dispatches the operation to the correct handler based on 'type'.

        Args:
            op (Dict[str, Any]): Operation configuration.
            root (etree._Element): Root element of the XML tree.
            row (pd.Series): Current row (from Excel).
        """
        op_type = op.get("type")
        if op_type == "update":
            self._apply_update(op, root, row)
        elif op_type == "add":
            self._apply_add(op, root, row)
        elif op_type == "delete":
            self._apply_delete(op, root)
        elif op_type == "replace_set":
            self._apply_replace_set(op, root, row)
            
    def _is_significant(self, value: str) -> bool:
        """
        Checks if a string contains meaningful (non-whitespace) content.

        Args:
            value (str): Value to check.

        Returns:
            bool: True if value is significant.
        """
        return bool(value.strip() and re.search(r'\w', value))
    
    


    def _apply_replace_set(self, op: Dict[str, Any], root: etree._Element, row: pd.Series):
        """
        Performs a 'replace_set' operation on the XML tree, replacing all existing
        child <value> elements at the target XPath with new values derived from
        mappings in the Excel table. Designed to work in 'general' mode.

        The process is as follows:
        1. Extract all current values from the 'from' XPath in the XML.
        2. Map each extracted value to its corresponding 'to' value in the Excel table.
        3. Replace all child <value> elements at the 'to' XPath with the mapped values.
        4. Log each new value in the changelog, only once per operation.

        Args:
            op (Dict[str, Any]): The operation configuration dictionary, containing
                                'from' and 'to' keys with 'xpath' and 'col'.
            root (etree._Element): The root element of the XML tree to modify.
            row (pd.Series): The current row from the Excel DataFrame. Not used
                            for logging deduplication in this method.
        """
        # Normalize XPath and column references
        from_xpath = self._normalize_xpath(op["from"]["xpath"])
        to_xpath = self._normalize_xpath(op["to"]["xpath"])
        from_col = op["from"]["col"]
        to_col = op["to"]["col"]

        collected_vals = []
        
        def _canon_for_match(s: str) -> str:
            # 1) stringa
            s = "" if s is None else str(s)
            # 2) decodifica entità HTML/XML (es. &#x27; -> ')
            s = html.unescape(s)
            # 3) normalizzazione Unicode (NFKC gestisce accenti composti/decomposti)
            s = unicodedata.normalize("NFKC", s)
            # 4) uniforma apostrofi/virgolette “curve” a l'apostrofo semplice
            s = re.sub(r"[’‘ʼ`´ˈʹ\u2019\u2018\u2032\u02BC]", "'", s)
            # 5) sostituisci NBSP e compatta spazi
            s = s.replace("\xa0", " ").strip()
            s = re.sub(r"\s+", " ", s)
            s = s.replace("&#x27;","'")
            return s

        # Step 1: Collect all current values from the 'from' XPath
        from_nodes = root.xpath(from_xpath)
        for node in from_nodes:
            for val_node in self._extract_value_nodes(node):
                raw_val = self._sanitize_for_xml(val_node.text or "")
                if not raw_val:
                    continue


                # Step 2: Map XML value to Excel 'to' column
                #matches = self.df[self.df[from_col].astype(str) == raw_val]
                raw_val_norm = _canon_for_match(raw_val)
                df_from_norm = self.df[from_col].astype(str).map(_canon_for_match)
                #print("xml", raw_val_norm, "excel", df_from_norm )
                matches = self.df[df_from_norm == raw_val_norm]
                if not matches.empty:
                    mapped_val = self._sanitize_for_xml(matches[to_col].iloc[0])
                    if self._is_significant(mapped_val):
                        collected_vals.append(mapped_val)

        # Step 3: Replace all child <value> elements at 'to' XPath
        to_nodes = root.xpath(to_xpath)
        for node in to_nodes:
            # Remove existing children
            for val_node in list(node):
                node.remove(val_node)
            # Append mapped values as new <value> elements
            for new_val in collected_vals:
                new_elem = etree.Element("value")
                new_elem.text = new_val
                node.append(new_elem)

        # Step 4: Log each new value once per operation
        if collected_vals and not getattr(self, "_replace_set_logged", False):
            for val in collected_vals:
                self.changelog.log_update(
                    self.task_name,
                    to_xpath,
                    "[reset]",
                    val
                )
            # Mark operation as logged to avoid duplicate logs in subsequent iterations
            self._replace_set_logged = True



    def _apply_update(self, op: Dict[str, Any], root: etree._Element, row: pd.Series):
        """
        Updates existing values in the XML that match the 'from' value, replacing them with 'to'.

        Args:
            op (Dict[str, Any]): Update operation definition.
            root (etree._Element): Root XML element.
            row (pd.Series): Row from the Excel table.
        """
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
        """
        Adds a new element to the XML tree with the specified value.

        Args:
            op (Dict[str, Any]): Add operation definition.
            root (etree._Element): Root XML element.
            row (pd.Series): Row from the Excel table.
        """
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
        """
        Deletes elements matching the specified XPath.

        Args:
            op (Dict[str, Any]): Delete operation definition.
            root (etree._Element): Root XML element.
        """
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
        """
        Extracts <value> subelements if present, otherwise returns the node itself.

        Args:
            node (etree._Element): XML element to inspect.

        Returns:
            List[etree._Element]: List of elements containing textual values.
        """
        return node.findall("value") or [node]
