import asyncio
import logging
import concurrent.futures
import re
import pandas as pd
import docx
import pdfplumber

from typing import List, Union, Optional, Dict, AsyncGenerator, Set
from pathlib import Path

from ..utility_base import UtilityBase
from ..logger import Logger, LogWrapper

class ContentScanner(UtilityBase):
    """
    Class for searching in the content of files.
    """

    def __init__(
        self,
        string_patterns: Optional[List[str]] = None,
        regex_patterns: Optional[List[str]] = None,
        case_sensitive: bool = False,
        max_results: Optional[int] = None,
        verbose: bool = False,
        logger: Optional[Union[logging.Logger, Logger, LogWrapper]] = None,
        log_level: Optional[int] = None
    ) -> None:
        """
        Initialize the content scanner with search patterns and scanning settings.

        Args:
            string_patterns: List of simple string patterns to match.
            regex_patterns: List of regular expression patterns to match.
            case_sensitive: Whether the match should be case-sensitive.
            max_results: Optional maximum number of results to return per file.
            verbose: If True, logs matches during the content search.
            logger: Optional logger instance. If not provided, a default logger is used.
            log_level: Optional log level. If not provided, INFO level will be used for logging.
        """
        # Init base class
        super().__init__(verbose, logger, log_level)

        if not string_patterns and not regex_patterns:
            raise ValueError("At least one of 'string_patterns' or 'regex_patterns' must be provided.")

        self.string_patterns = string_patterns or []
        self.regex_patterns = [re.compile(r, 0 if case_sensitive else re.IGNORECASE) for r in (regex_patterns or [])]
        self.case_sensitive = case_sensitive
        self.max_results = max_results
        self.text_extensions = self._init_text_extensions()
        self.loop = asyncio.get_event_loop()
        self.executor = concurrent.futures.ThreadPoolExecutor()

    def _init_text_extensions(self) -> Set[str]:
        """
        Initialize the set of recognized plain text file extensions.

        Returns:
            A set of file extensions treated as plain text.
        """
        return {
            # Code
            '.py', '.js', '.ts', '.java', '.c', '.cpp', '.cs', '.go', '.rb', '.php', '.rs', '.sh', '.bash', '.zsh',
            '.sql', '.pl',
            # Config & Data
            '.ini', '.conf', '.cfg', '.toml', '.yaml', '.yml', '.json', '.env', '.properties', '.xml',
            # Markup & Docs
            '.html', '.htm', '.css', '.md', '.txt', '.rst', '.log', '.csv', '.tsv',
            # Miscellaneous
            '.gitignore', '.gitattributes', 'Dockerfile', 'Makefile', 'README', 'LICENSE', 'CHANGELOG'
        }

    async def scan_files(self, file_paths: List[Union[str, Path]]) -> AsyncGenerator:
        """
        Asynchronously scan multiple files for matching content.

        Args:
            file_paths: List of file paths to scan.

        Yields:
            dict: Dictionaries with file, line, and line number of matches.
        """
        for file in file_paths:
            file_result = await self.loop.run_in_executor(self.executor, self._scan_file, Path(file))

            for match in file_result:
                self._log(f"Match found in `{file}`")

                yield match

    def _scan_file(self, file_path: Path) -> List[Dict[str, Union[str, int]]]:
        """
        Determine the file type and scan it appropriately.

        Args:
            file_path: Path object representing the file.

        Returns:
            List of dictionaries with match results.
        """
        try:
            ext = file_path.suffix.lower()
            if ext in ['.csv', '.tsv']:
                return self._scan_csv(file_path)
            elif ext in ['.xls', '.xlsx']:
                return self._scan_excel(file_path)
            elif ext == '.docx':
                return self._scan_docx(file_path)
            elif ext == '.pdf':
                return self._scan_pdf(file_path)
            elif ext in self.text_extensions or file_path.is_file():
                return self._scan_plain_text(file_path)
        except Exception as e:
            self._log_exception(f"Error scanning `{file_path.name}`: {e}")
        
        return []

    def _match_line(self, line: str) -> bool:
        """
        Check if a line matches any of the defined patterns.

        Args:
            line: A line of text.

        Returns:
            True if the line matches, else False.
        """
        content = line if self.case_sensitive else line.lower()
        string_check = any((p if self.case_sensitive else p.lower()) in content for p in self.string_patterns)
        regex_check = any(r.search(line) for r in self.regex_patterns)

        return string_check or regex_check

    def _scan_plain_text(self, file_path: Path) -> List[Dict[str, Union[str, int]]]:
        """
        Scan plain text files line-by-line.

        Args:
            file_path: Path to the file.

        Returns:
            List of dictionaries containing matches.
        """
        matches = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for lineno, line in enumerate(f, start=1):
                    if self._match_line(line):
                        matches.append({'file': str(file_path), 'line': line.strip(), 'line_number': lineno})
                        if self.max_results and len(matches) >= self.max_results:
                            break
        except Exception:
            pass

        return matches

    def _scan_csv(self, file_path: Path) -> List[Dict[str, Union[str, int]]]:
        """
        Scan CSV/TSV files for matching cell values.

        Args:
            file_path: Path to the CSV/TSV file.

        Returns:
            List of match dictionaries.
        """
        matches = []
        try:
            df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
            for index, row in df.iterrows():
                for col in row:
                    if isinstance(col, str) and self._match_line(col):
                        matches.append({'file': str(file_path), 'line': col.strip(), 'line_number': index + 1})
                        if self.max_results and len(matches) >= self.max_results:
                            return matches
        except Exception:
            pass

        return matches

    def _scan_excel(self, file_path: Path) -> List[Dict[str, Union[str, int]]]:
        """
        Scan Excel files for matching cell content.

        Args:
            file_path: Path to the Excel file.

        Returns:
            List of match dictionaries.
        """
        matches = []
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            for index, row in df.iterrows():
                for col in row:
                    if isinstance(col, str) and self._match_line(col):
                        matches.append({'file': str(file_path), 'line': col.strip(), 'line_number': index + 1})
                        if self.max_results and len(matches) >= self.max_results:
                            return matches
        except Exception:
            pass

        return matches

    def _scan_docx(self, file_path: Path) -> List[Dict[str, Union[str, int]]]:
        """
        Scan .docx files for matching paragraph text.

        Args:
            file_path: Path to the DOCX file.

        Returns:
            List of match dictionaries.
        """
        matches = []
        try:
            doc = docx.Document(file_path)
            for i, para in enumerate(doc.paragraphs):
                text = para.text
                if self._match_line(text):
                    matches.append({'file': str(file_path), 'line': text.strip(), 'line_number': i + 1})
                    if self.max_results and len(matches) >= self.max_results:
                        break
        except Exception:
            pass

        return matches

    def _scan_pdf(self, file_path: Path) -> List[Dict[str, Union[str, str]]]:
        """
        Scan PDF files page-by-page and line-by-line.

        Args:
            file_path: Path to the PDF file.

        Returns:
            List of match dictionaries.
        """
        matches = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ''
                    for lineno, line in enumerate(text.split('\n'), start=1):
                        if self._match_line(line):
                            matches.append({'file': str(file_path), 'line': line.strip(), 'line_number': f"Page {i+1}, Line {lineno}"})
                            if self.max_results and len(matches) >= self.max_results:
                                return matches
        except Exception:
            pass

        return matches
