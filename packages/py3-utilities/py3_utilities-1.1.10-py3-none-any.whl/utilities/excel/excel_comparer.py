import pandas as pd
import numpy as np
import logging

from typing import Optional, List, Dict, Any, Union

from ..utility_base import UtilityBase
from ..logger import Logger, LogWrapper


class ExcelComparer(UtilityBase):
    """
    A utility class for comparing two Excel files sheet by sheet and reporting differences.

    Supports column exclusion, tolerance for float comparison, and case-insensitive string comparison.
    Outputs can be printed, logged, or saved to CSV.
    """

    def __init__(
        self,
        file_path1: str,
        file_path2: str,
        ignore_columns: Optional[List[str]] = None,
        float_tolerance: float = 1e-6,
        case_insensitive: bool = False,
        verbose: bool = False,
        logger: Optional[Union[logging.Logger, Logger, LogWrapper]] = None,
        log_level: Optional[int] = None
    ):
        """
        Initializes the ExcelComparer with file paths and comparison options.

        :param file1: Path to the first Excel file.
        :param file2: Path to the second Excel file.
        :param ignore_columns: List of column names to ignore in comparison.
        :param float_tolerance: Tolerance when comparing float values.
        :param case_insensitive: Whether string comparison should ignore case.
        :param verbose: If True, logs differences during comparison.
        :param logger: Optional logger instance. If not provided, a default logger is used.
        :param log_level: Optional log level. If not provided INFO level will be used for logging
        """
        # Init base class
        super().__init__(verbose, logger, log_level)

        self.file_path1 = file_path1
        self.file_path2 = file_path2
        self.ignore_columns = set(ignore_columns or [])
        self.float_tolerance = float_tolerance
        self.case_insensitive = case_insensitive
        self.diff_report: Dict[str, List[Dict[str, Any]]] = {}
        self.sheet_level_diffs: List[str] = []

    def compare(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Compares the two Excel files and identifies differences.

        :return: A dictionary with sheet names as keys and lists of difference records as values.
        """
        xl1 = pd.read_excel(self.file_path1, sheet_name=None)
        xl2 = pd.read_excel(self.file_path2, sheet_name=None)

        sheets1 = set(xl1.keys())
        sheets2 = set(xl2.keys())
        all_sheets = sheets1.union(sheets2)

        for sheet in all_sheets:
            if sheet not in xl1:
                msg = f"Sheet '{sheet}' missing in file1."
                self.sheet_level_diffs.append(msg)
                self._log(msg)
                continue
            if sheet not in xl2:
                msg = f"Sheet '{sheet}' missing in file2."
                self.sheet_level_diffs.append(msg)
                self._log(msg)
                continue

            df1 = xl1[sheet].reset_index(drop=True)
            df2 = xl2[sheet].reset_index(drop=True)

            # Compare structure
            if df1.shape[0] != df2.shape[0]:
                msg = f"Sheet '{sheet}': Row count mismatch: file1={df1.shape[0]}, file2={df2.shape[0]}"
                self.sheet_level_diffs.append(msg)
                self._log(msg)

            if set(df1.columns) != set(df2.columns):
                msg = f"Sheet '{sheet}': Column mismatch:\n  file1: {list(df1.columns)}\n  file2: {list(df2.columns)}"
                self.sheet_level_diffs.append(msg)
                self._log(msg)

            # Use only columns in both, minus ignored ones
            common_cols = [col for col in df1.columns if col in df2.columns and col not in self.ignore_columns]
            df1 = df1[common_cols]
            df2 = df2[common_cols]

            max_len = max(len(df1), len(df2))
            df1 = df1.reindex(range(max_len))
            df2 = df2.reindex(range(max_len))

            sheet_diffs: List[Dict[str, Any]] = []

            for idx in range(max_len):
                row1 = df1.iloc[idx]
                row2 = df2.iloc[idx]

                for col in common_cols:
                    val1 = row1[col]
                    val2 = row2[col]

                    if self._values_differ(val1, val2):
                        sheet_diffs.append({
                            "sheet": sheet,
                            "row": idx,
                            "column": col,
                            "file1": val1,
                            "file2": val2
                        })

            if sheet_diffs:
                self.diff_report[sheet] = sheet_diffs

                self._log(f"\nDifferences found in sheet: '{sheet}'")
                for diff in sheet_diffs:
                    self._log(
                        f"Row {diff['row']}, Column '{diff['column']}': "
                        f"file1 = {diff['file1']}, file2 = {diff['file2']}"
                    )
            else:
                self._log(f"Sheet '{sheet}' is identical.")

        return self.diff_report

    def diff_to_csv(self, path: str) -> None:
        """
        Saves all cell-level differences to a CSV file.

        :param path: Output CSV file path.
        """
        if not self.diff_report:
            self._log("No differences to save.")
            return

        all_diffs = []
        for diffs in self.diff_report.values():
            all_diffs.extend(diffs)

        df = pd.DataFrame(all_diffs)
        df.to_csv(path, index=False)
        self._log(f"Diff report saved to: {path}")

    def diff_to_str(self) -> str:
        """
        Returns the full diff report including sheet-level structural differences as a string.

        :return: Differences as a string object.
        """
        diffs = []

        if not self.diff_report and not self.sheet_level_diffs:
            diffs.append("No differences found.")
        else:
            if self.sheet_level_diffs:
                diffs.append("Sheet-level differences:")
                for msg in self.sheet_level_diffs:
                    diffs.append(f"  - {msg}")

            for sheet, diffs in self.diff_report.items():
                diffs.append(f"\nSheet: {sheet}")
                for d in diffs:
                    diffs.append(f"  - Row {d['row']+2} | Col '{d['column']}' | file1: {d['file1']} | file2: {d['file2']}")

        return "\n".join(diffs)

    def _values_differ(self, val1: Any, val2: Any) -> bool:
        """
        Compares two values with support for float tolerance and case-insensitive strings.

        :param val1: First value.
        :param val2: Second value.
        :return: True if values are considered different.
        """
        if pd.isna(val1) and pd.isna(val2):
            return False

        if isinstance(val1, float) and isinstance(val2, float):
            return not np.isclose(val1, val2, atol=self.float_tolerance)

        if self.case_insensitive and isinstance(val1, str) and isinstance(val2, str):
            return val1.strip().lower() != val2.strip().lower()

        return val1 != val2
