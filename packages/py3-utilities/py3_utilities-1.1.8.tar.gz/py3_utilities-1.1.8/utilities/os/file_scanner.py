import asyncio
import os
import re
import logging

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncGenerator, Callable, List, Optional, Tuple, Union
from enum import Enum, unique
from datetime import datetime
from collections import deque

from ..utility_base import UtilityBase
from ..logger import Logger, LogWrapper


@unique
class TraversalMethod(Enum):
    """Enum to define traversal methods."""

    BFS = "BFS"
    DFS = "DFS"


class FileScanner(UtilityBase):
    """Asynchronously scans files in a directory structure based on given criteria."""

    def __init__(
        self,
        root_dir: Union[str, Path],
        max_workers: int = 16,
        method: TraversalMethod = TraversalMethod.BFS,
        file_patterns: Optional[List[str]] = None,
        folder_patterns: Optional[List[str]] = None,
        first_folder_patterns: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
        min_file_size: Optional[int] = None,
        modified_after: Optional[datetime] = None,
        match_callback: Optional[Callable[[str], None]] = None,
        skip_hidden: bool = True,
        follow_symlinks: bool = False,
        verbose: bool = False,
        logger: Optional[Union[logging.Logger, Logger, LogWrapper]] = None,
        log_level: Optional[int] = None
    ):
        """
        Initialize the FileScanner.

        Args:
            root_dir (Union[str, Path]): Root directory to start scanning.
            max_workers (int, optional): Maximum number of concurrent workers. Defaults to 16.
            method (TraversalMethod, optional): Traversal method (BFS or DFS). Defaults to TraversalMethod.BFS.
            file_patterns (Optional[List[str]], optional): List of regex patterns to match file names.
            folder_patterns (Optional[List[str]], optional): List of regex patterns to match folder names.
            first_folder_patterns (Optional[List[str]], optional): List of regex patterns to match folder names directly under root (depth = 1 folders).
            max_depth (Optional[int], optional): Maximum depth to traverse.
            min_file_size (Optional[int], optional): Minimum file size in bytes to include.
            modified_after (Optional[datetime], optional): Include files modified after this datetime.
            match_callback (Optional[Callable[[str], None]], optional): Function to call when a file is found.
            skip_hidden (bool, optional): Skip hidden files and folders if True. Defaults to True.
            follow_symlinks (bool, optional): Follow symbolic links if True. Defaults to False.
            verbose (bool, optional): If True, logs files during the search. Defaults to False.
            logger (Optional[Union[logging.Logger, Logger, LogWrapper]], optional): Optional logger instance.
            log_level (Optional[int], optional): Optional log level. Defaults to INFO if not provided.
        """
        # Init base class
        super().__init__(verbose, logger, log_level)

        self.root_dir = Path(root_dir)
        self.max_workers = max_workers
        self.method = method
        self.file_patterns = [re.compile(p, re.IGNORECASE) for p in file_patterns] if file_patterns else []
        self.folder_patterns = [re.compile(p, re.IGNORECASE) for p in folder_patterns] if folder_patterns else []
        self.first_folder_patterns =  [re.compile(p, re.IGNORECASE) for p in first_folder_patterns] if first_folder_patterns else []
        self.max_depth = max_depth
        self.match_callback = match_callback
        self.min_file_size = min_file_size
        self.modified_after = modified_after
        self.skip_hidden = skip_hidden
        self.follow_symlinks = follow_symlinks

    async def scan_files(self) -> AsyncGenerator[Path, None]:
        """
        Start asynchronous scanning of files.

        Yields:
            Path: Path objects of files that match the criteria.
        """
        loop = asyncio.get_running_loop()

        self._log(f"Scanning `{self.root_dir}`, with {self.method} method.")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            if self.method == TraversalMethod.BFS:
                async for path in self._scan_bfs(loop, executor):
                    yield path
            elif self.method == TraversalMethod.DFS:
                async for path in self._scan_dfs(loop, executor):
                    yield path

    async def _scan_bfs(self, loop, executor) -> AsyncGenerator[Path, None]:
        """
        Perform asynchronous breadth-first scanning.

        Args:
            loop: Event loop.
            executor: Thread pool executor.

        Yields:
            Path: Path objects for files found.
        """
        queue = deque([(self.root_dir, 0)])

        while queue:
            tasks = []
            while queue and len(tasks) < self.max_workers:
                tasks.append(queue.popleft())

            futures = [loop.run_in_executor(executor, self._walk_fast, path, depth) for path, depth in tasks]

            for future in asyncio.as_completed(futures):
                subdirs, files, depth = await future
                if self.max_depth is None or depth < self.max_depth:
                    queue.extend([(subdir, depth + 1) for subdir in subdirs])

                for file in files:
                    yield Path(file)

    async def _scan_dfs(self, loop, executor) -> AsyncGenerator[Path, None]:
        """
        Perform asynchronous depth-first scanning.

        Args:
            loop: Event loop.
            executor: Thread pool executor.

        Yields:
            Path: Path objects for files found.
        """
        stack = [(self.root_dir, 0)]

        while stack:
            current_dir, current_depth = stack.pop()

            if self.max_depth is not None and current_depth > self.max_depth:
                continue

            subdirs, files, _ = await loop.run_in_executor(executor, self._walk_fast, current_dir, current_depth)

            for file in files:
                yield Path(file)

            stack.extend([(Path(sd), current_depth + 1) for sd in reversed(subdirs)])

    def _walk_fast(self, directory: Path, depth: int) -> Tuple[List[Path], List[Path], int]:
        """
        Quickly scan a directory, returning subdirectories and matching files.

        Args:
            directory (Path): Directory to scan.
            depth (int): Current depth.

        Returns:
            Tuple[List[Path], List[Path], int]: Subdirectories, matching files, and current depth.
        """
        subdirs, files = [], []
        try:
            with os.scandir(directory) as it:
                for entry in it:
                    if self.skip_hidden and entry.name.startswith('.'):
                        continue
                    if entry.is_symlink() and not self.follow_symlinks:
                        continue

                    entry_path = Path(entry.path)

                    if entry.is_dir(follow_symlinks=self.follow_symlinks):
                        if depth == 0:
                            if not self.first_folder_patterns or self._matches_patterns(entry.name, self.first_folder_patterns):
                                subdirs.append(entry_path)
                        else:
                            if not self.folder_patterns or self._matches_patterns(entry.name, self.folder_patterns):
                                subdirs.append(entry_path)
                    elif entry.is_file(follow_symlinks=self.follow_symlinks):
                        if not self.file_patterns or self._matches_patterns(entry.name, self.file_patterns):
                            stat = entry.stat(follow_symlinks=self.follow_symlinks)

                            if self._passes_stat_filters(stat):
                                self._log(f"File found: `{entry_path}`")
                                if self.match_callback:
                                    self.match_callback(entry_path) 

                                files.append(entry_path)

        except OSError as e:
            self._log_warning(f"Can't scan directory: {directory}: {e}")

        return subdirs, files, depth

    def _matches_patterns(self, name: str, patterns: List[re.Pattern]) -> bool:
        """
        Check if the given name matches any of the provided regex patterns.

        Args:
            name (str): Name to check.
            patterns (List[re.Pattern]): List of compiled regex patterns.

        Returns:
            bool: True if a match is found.
        """
        return any(p.search(name) for p in patterns)

    def _passes_stat_filters(self, stat) -> bool:
        """
        Check if a file's statistics pass the filtering criteria.

        Args:
            stat: File statistics object.

        Returns:
            bool: True if file meets criteria.
        """
        if self.min_file_size and stat.st_size < self.min_file_size:
            return False
        
        if self.modified_after and datetime.fromtimestamp(stat.st_mtime) < self.modified_after:
            return False
        
        return True
