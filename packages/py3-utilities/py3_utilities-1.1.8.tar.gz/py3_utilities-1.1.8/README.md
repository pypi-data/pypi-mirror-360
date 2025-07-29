# Table of contents
- [1. Installation](#1-installation)
- [2. Config File handling](#2-config-file-handling)
  - [2.1 Config Parser](#21-config-parser)
  - [2.2 Config Writer](#22-config-writer)
  - [2.3 Automatic Logger Configuration](#23-automatic-logger-configuration)
  - [2.4 Behind the Scenes (Automatic Initialization)](#24-behind-the-scenes-automatic-initialization)
- [3. Other utilities](#3-other-utilities)
  - [3.1 Logger utilities](#31-logger-utilities)
  - [3.2 Jira Utilities](#32-jira-utilities)
  - [3.3 Gitlab Utilities](#33-gitlab-utilities)
  - [3.4 AI Utilities](#34-ai-utilities)
  - [3.5 OS Utilities](#35-os-utilities)
  - [3.6 Excel utilities](#36-excel-utilities)
  - [3.7 Config utilities](#37-config-utilities)

## 📁 Project Structure

```
[root]/utilities/                        # Shared utility modules
│   ├── __init__.py                      # Exposes the loaded configuration and the internal classes, functions
│   ├── ai/           
│   │   ├── __init__.py                  # Exposes the internal classes/interfaces
│   │   ├── azure_docint_client.py       # A utility wrapper around Azure Document Intelligence API that parses documents
│   │   ├── azure_openai_client.py       # A full-featured wrapper around Azure OpenAI that manages conversation sessions
│   ├── config/           
│   │   ├── __init__.py                  # Loads the content of all `yaml`, `yml`, `toml`, `ini`, `xml` or `json` files
│   │   ├── config_parser.py             # Multi-format config loader implementation(.env + yaml/toml/json/ini/xml)
│   │   └── config_writer.py             # Multi-format config writer implementation(yaml/toml/json/ini/xml)
│   ├── gitlab/                
│   │   ├── __init__.py                  # Exposes the internal classes/interfaces
│   │   ├── gitlab_client.py             # A client for interacting with a GitLab instance.
│   ├── jira/                
│   │   ├── __init__.py                  # Exposes the internal classes/interfaces
│   │   ├── jira_client.py               # A client for interacting with Jira's REST API V2
│   ├── excel/                
│   │   ├── __init__.py                  # Exposes the internal classes/interfaces
│   │   ├── excel_comparer.py            # A utility class for comparing two Excel files sheet by sheet
│   ├── os/                
│   │   ├── __init__.py                  # Exposes the internal classes/interfaces
│   │   ├── content_scanner.py           # Scans the content of different file types
│   │   ├── directory_event.py           # Dataclass to store directory events
│   │   ├── directory_watcher_crossplatform.py 
│   │   ├── directory_watcher_windows.py # Watches for file system changes in a directory (Windows and crossplatform version)
│   │   ├── file_scanner.py              # Recursively scans directories for files matching criteria
│   └── logger/
│       ├── __init__.py                  # Automatically creates the loggers and decorators defined in the config file
│       ├── logger.py                    # Logger class
│       ├── log_decorator.py             # async/sync logger decorator implementation
│       └── log_wrapper.py               # A wrapper for the loggers and decorators, providing an easy-to-use interface
```

# 1. Installation

The **`py3-utilities`** package requires **Python 3.11 or newer**.

> ⚠️ The base package does **not** include any functionality by default. All modules are included as optional dependencies.

### Installing with `pip`

To install with the desired functionality, use one or more of the available **extras**:

```bash
# Logging utilities
pip install py3-utilities[logger]

# Configuration file support
pip install py3-utilities[config]

# Gitlab client
pip install py3-utilities[gitlab]

# Excel client
pip install py3-utilities[excel]

# OS-level utilities
pip install py3-utilities[os-windows]
pip install py3-utilities[os-crossplatform]

# AI integrations (OpenAI, Azure)
pip install py3-utilities[ai]

# Jira-related functionality
pip install py3-utilities[jira]

# Install everything
pip install py3-utilities[all]
```

---

### Installing with Poetry

You can also include `py3-utilities` in your **`pyproject.toml`** file:

```toml
[tool.poetry.dependencies]
python = ">=3.11,<4.0"
py3-utilities = { version = "^1.0.1", extras = ["logger", "config"] }
```

Just list the extras you need under the `extras` key.

To add it via CLI:

```bash
poetry add py3-utilities -E logger -E config
```

# 2. Config File handling

## 2.1 Config Parser

The configuration parser system is powered by a `Config` singleton class that loads environment variables from a `.env` file and merges all matching configuration files (`*.yaml`, `*.yml`, `*.toml`, `*.json`, `*.ini`, `*.xml`) found in the root project directory, or inside a config folder (`cfg`, `conf`, `config`, `configuration`). These files are combined into a single config tree and converted into nested `SimpleNamespace` objects for easy dot-access in Python.

### Supported File Types

- `.env`: Environment variables
- `.yaml`, `.yml`: YAML config files
- `.toml`: TOML config files
- `.json`: JSON config files
- `.ini`: INI config files
- `.xml`: XML config files (attributes and text content are parsed into dicts)

### XML Parsing Notes

- **Attributes** are parsed as normal keys (no `@` prefix).
- **Text content** inside tags is placed under a `"value"` key (unless the element only has text).
- Nested elements and repeated tags are handled as nested dicts or lists.

### Example Config Files

- **TOML configuration:**
```toml
[application]
download_folder = "tmp"
output_folder   = "output"
```

- **`.env` file:**
```env
API_TOKEN = "abcd..."
```

- **YAML file:**
```yaml
logging:
  root_folder: "logs"
```

- **XML file:**
```xml
<database host="localhost" port="5432">mydb</database>
```

### Loading Configuration

To parse and access configuration values:

```python
from utilities import parse_config

# Regular loading from root directory, or from config folders inside the root dir
config = parse_config()

# Config files can also be loaded from custom directories
config = parse_config(config_paths=["dir1", "path/to/dir2"])

# TOML part
config.application.download_folder
config.application.output_folder

# YAML part
config.logging.root_folder

# XML part
config.database.host       # "localhost"
config.database.port       # "5432"
config.database.value      # "mydb"

# .env file
config.os.env.api_token

# Other environment variables
config.os.env.path
```

---

## 2.2 Config Writer

The utilities module also provides a `write_config` function to serialize and export configuration data into different formats (`json`, `yaml`, `toml`, `ini`, or `xml`). This is useful for saving updated configuration states, debugging, or exporting subsets of the config for other applications.

### Writing Configuration

You can write a parsed or custom config structure to a file as follows:

```python
from utilities import write_config

# Example: Save current config to YAML, excluding 'os' key
write_config(config, "output_config.yaml", format="yaml", exclude_keys=["os"])
```

### Supported Formats
- `json`
- `yaml` / `yml`
- `toml`
- `ini`
- `xml`

### Excluding Keys

Use the `exclude_keys` parameter to omit top-level keys (e.g., `os`) when writing the config:
```python
write_config(config, "config.json", format="json", exclude_keys=["os"])
```

## 2.3 Automatic Logger Configuration

A properly formatted part of the configuration file automatically controls the behavior of your logging system. Each logger can be customized individually for console, file, and JSON outputs, including rotation settings and timestamp formats.

**The logger configuration is read automatically by the `Config` singleton loader when the `utilities` module is imported**. If the configuration includes a `[logging.loggers.<name>.<optiona_sub_name>]` section, a logger will be automatically created and exposed via the `log` namespace.

For example, a logger defined as:
```toml
[logging.loggers.app.logger]
```
Will be accessible via:
```python
log.app.logger.info("...")
```

These loggers can also be used as **function decorators**:
```python
@log.app.logger
def my_function():
    ...
```
This will automatically log function entry, exit, and optionally exceptions (depending on decorator settings).

---

### Root Settings (`[logging]`)

| Field              | Type    | Description                                     | Default |
|--------------------|---------|-------------------------------------------------|---------|
| `root_folder`      | string  | Directory where log files are stored            | `logs`  |
| `cleanup_old_logs` | bool    | Enable automatic deletion of old logs           | `true`  |
| `cleanup_days`     | int     | Number of days to keep log files                | `7`     |

---

### Logger Section (`[logging.loggers.<logger_name>.<optional_sub_name>]`)

Each logger is defined under this section.

#### Common Fields

| Field             | Type    | Description                                  | Default  |
|-------------------|---------|----------------------------------------------|----------|
| `enabled`         | bool    | Whether the logger is active                 | `false`  |
| `clear_handlers`  | bool    | Remove existing handlers                     | `false`  |

---

#### Console Output

| Field                     | Type    | Description                             | Default       |
|---------------------------|---------|-----------------------------------------|---------------|
| `console_output`          | bool    | Enable/disable console logging          | `false`       |
| `console_log_level`       | string  | Log level (`DEBUG`, `INFO`, etc.)       | `"INFO"`      |
| `console_timestamp_format`| string  | Format for timestamps (strftime format) | optional      |

---

#### File Output

| Field                        | Type    | Description                              | Default       |
|------------------------------|---------|------------------------------------------|---------------|
| `file_output`                | bool    | Enable/disable plain text file logging   | `false`       |
| `file_log_level`             | string  | Log level                                | `"INFO"`      |
| `file_rotation_time`         | bool    | Enable time-based rotation               | `false`       |
| `file_rotation_when`         | string  | Time unit for rotation (e.g. `midnight`) | `"midnight"`  |
| `file_rotation_interval`     | int     | Number of units between rotations        | `1`           |
| `file_rotation_backup_count` | int   | Number of backups to retain              | `7`           |
| `file_timestamp_format`      | string  | Format for timestamps                    | optional      |

---

#### JSON Output

| Field                       | Type    | Description                              | Default       |
|-----------------------------|---------|------------------------------------------|---------------|
| `json_output`               | bool    | Enable/disable JSON file logging         | `false`       |
| `json_log_level`            | string  | Log level                                | `"INFO"`      |
| `json_rotation_time`        | bool    | Enable time-based rotation               | `false`       |
| `json_rotation_when`        | string  | Time unit for rotation                   | `"midnight"`  |
| `json_rotation_interval`    | int     | Number of units between rotations        | `1`           |
| `json_rotation_backup_count`| int     | Number of backups to retain              | `7`           |
| `json_timestamp_format`     | string  | Format for timestamps                    | optional      |

#### Decorator

| Field                          | Type    | Description                              | Default       |
|--------------------------------|---------|------------------------------------------|---------------|
| `decorator_raise_exception`    | bool    | Enable/disable JSON file logging         | `false`       |
| `decorator_log_level`          | string  | Log level                                | `"DEBUG"`     |
| `decorator_max_log_length`     | int     | Enable time-based rotation               | `500`         |
| `decorator_log_arguments`      | bool    | Time unit for rotation                   | `true`        |
| `decorator_tag`                | string  | Number of units between rotations        | `"decorator"` |
| `decorator_warn_duration`      | int     | Number of backups to retain              | optional      |
| `decorator_log_stack`          | bool    | Whether to log call stack                | `false`       |
| `decorator_log_return_value`   | bool    | Whether to log function return values    | `false`       |
| `decorator_log_execution_time` | bool    | Whether to log function execution times  | `false`       |
| `decorator_sensitive_params`   | list    | Format for timestamps                    | optional      |

---

### Example Configuration

```toml
# --- Logger creation ---

[logging]
root_folder = "logs"
cleanup_old_logs = true
cleanup_days = 7

# Create a logger for Jira related operations
[logging.loggers.jira.logger]
enabled = true
clear_handlers = false

# Console
console_output = true
console_log_level = "INFO"
console_timestamp_format = "%Y-%m-%d %H:%M:%S"

# File
file_output = true
file_log_level = "INFO"
file_rotation_time = true
file_rotation_when = "midnight"
file_rotation_interval = 1
file_rotation_backup_count = 7
file_timestamp_format = "%Y-%m-%dT%H:%M:%S"

# JSON
json_output = true
json_log_level = "INFO"
json_rotation_time = true
json_rotation_when = "midnight"
json_rotation_interval = 1
json_rotation_backup_count = 7
json_timestamp_format = "%Y-%m-%dT%H:%M:%S"

# Decorator options
decorator_raise_exception = true
decorator_log_level = "DEBUG"
decorator_max_log_length = 100
decorator_log_arguments = false
decorator_tag = "decorator"
decorator_warn_duration = 5
decorator_log_stack = false
decorator_log_return_value = false
decorator_log_execution_time = true
decorator_sensitive_params = ["api_token"]

# Create another for other stuff
[logging.loggers.other]
enabled = true
file_output = true
json_output = false
console_output = false

# --- Application ---

[application]
# Write your other configurations here ...
```

These will be accessible via:
```python
from utilities import log

# ...

log.jira.logger.info("...")
log.other.info("...")
```

---

### Notes

- If `file_output`, `json_output` and `console_output` are false, the logger will fall back to a `NullHandler`.
- Rotation is only time-based; size-based rotation is not currently supported from config.
- Timestamp format strings follow [Python's `strftime` syntax](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes).
- Loggers are exposed via `log.<logger_name>`, e.g. `log.jira.logger` if the config key is `[logging.loggers.jira.logger]`.
- These loggers can be used as decorators to automatically log function calls.

## 2.4 Behind the Scenes (Automatic Initialization)

The `utilities.logger` package is designed to minimize boilerplate and automate logger setup using configuration-driven initialization.

When you import `log` from `utilities` it parses the available config files:

---

### Config Parser (`config/__init__.py`)

- `parse_config()` initializes the `Config` singleton.
- It loads environment variables (`.env` file too), and all `.yaml`, `.toml`, `ini`, `.xml` and `.json` files from the project library.
- All configs are merged into a nested `SimpleNamespace`, accessible via dot notation:

```python
from utilities import parse_config

config = parse_config()
...
```

---

### Logger Module (`logger/__init__.py`)

Upon import:
- It reads `config.logging.loggers.*` entries.
- For each enabled logger:
  - A `Logger` instance is created.
  - A matching `LogDecorator` is configured.
  - These are bundled into a `LogWrapper`, exposing both logging and decorating in one object.
  - The `log.<name>` namespace is dynamically built to match the config structure.

Example config:
```toml
[logging.loggers.analytics]
enabled = true
```
Enables:
```python
from utilities import log

log.analytics.info("...logged!")

@log.analytics
def do_something():
    ...
```

# 3. Other utilities

**The interfaces used by the initialization part are also exposed and can be used manually**.

## 3.1 Logger utilities

The `logger` utility module provides structured, flexible, and context-aware logging. It supports console, plain-text, and JSON output, async logging via queue listeners, per-day log foldering, log rotation (size/time-based), as well as decorators for automatic function logging (sync or async).

The main components are:

- `Logger`: Core configuration and setup utility for logging
- `LogDecorator`: Decorator for function-level logging (arguments, return values, exceptions)
- `LogWrapper`: A convenience wrapper combining the logger and decorator

---

### `Logger` class

A full-featured logger wrapper around Python’s `logging` module. It supports:

- Output to console, plain-text, and/or JSON log files
- Rotation (size or time-based)
- Context variable injection (for JSON)
- Asynchronous logging via queue
- Cleanup/compression of old logs

#### Usage

```python
from utilities import Logger

logger = Logger(
    name="my_app",                       # REQUIRED: Name of the logger
    base_log_dir="logs",                # OPTIONAL: Base directory for log files (default: 'logs')
    clear_handlers=True,                # OPTIONAL: Remove previous handlers if any
    file_output=True,                   # OPTIONAL: Enable plain text file logging
    json_output=True,                   # OPTIONAL: Enable JSON-formatted file logging
    console_output=True,                # OPTIONAL: Enable console logging
    file_rotation_time_based=True,      # OPTIONAL: Rotate file logs daily
    json_rotation_size_based=True,      # OPTIONAL: Rotate JSON logs by file size
    async_queue_size=10000              # OPTIONAL: Queue size for async logging
)

log = logger.get_logger()
log.info("App started")
```

---

### `Logger.cleanup_old_logs(...)` (static method)

Deletes daily log folders older than the specified number of days.

#### Usage

```python
Logger.cleanup_old_logs(
    base_log_dir="logs",       # REQUIRED
    name="my_app",             # REQUIRED: Logger name or "*" to match all
    days=5,                    # OPTIONAL: Delete logs older than this many days (default: 7)
    verbose=True               # OPTIONAL: Print deletions (default: False)
)
```

---

### `Logger.compress_old_logs(...)` (static method)

Archives daily log folders older than the specified number of days.

#### Usage

```python
archive_path = Logger.compress_old_logs(
    base_log_dir="logs",           # REQUIRED
    name="my_app",                 # REQUIRED: Logger name or "*" to match all
    days=10,                       # OPTIONAL: Archive logs older than this (default: 7)
    archive_name="old_logs",      # OPTIONAL: File name without extension
    verbose=True                   # OPTIONAL: Print archive creation details
)
```

---

### `LogDecorator` class

A decorator to wrap any function (sync or async) and automatically log:

- Execution time
- Arguments (with optional masking)
- Return value
- Stack trace on error
- Performance warnings

#### Usage

```python
from utilities import LogDecorator

decorator = LogDecorator(
    logger=logger.get_logger(),         # REQUIRED: logger instance
    raise_exception=False,             # OPTIONAL: Don't re-raise after logging
    log_arguments=True,                # OPTIONAL: Log function arguments
    sensitive_params=["password"],     # OPTIONAL: Redact sensitive argument names
    log_return=True,                   # OPTIONAL: Log return value
    log_execution_time=True,           # OPTIONAL: Log duration
    warn_duration=1.5                  # OPTIONAL: Warn if duration > X sec
)

@decorator
def process_user(username, password):
    ...
```

---

### `LogWrapper` class

A helper that bundles both the `Logger` and `LogDecorator`. It acts as a unified interface to:

- Decorate functions
- Call logging methods (`info`, `error`, etc.)
- Access context methods (`context_scope`, `set_context`, etc.)

#### Usage

```python
from utilities import LogWrapper

log = LogWrapper(decorator, logger)

@log
def example():
    log.info("Inside decorated function")
    ...
```

## 3.2 Jira Utilities

The Jira utility module provides an asynchronous interface for interacting with Jira's REST API (v2). It abstracts common Jira operations like issue lookup, comment reading, changelog filtering, and sprint/board querying, making it easier to incorporate Jira functionality into your Python workflows.

### Classes and Functions

---

### `JiraClient`

This class handles all asynchronous interactions with the Jira server using `aiohttp`. It supports configurable logging, retries, and selective data fetching (e.g., comments, worklogs, changelogs).

#### Usage:
```python
from utilities import JiraClient

client = JiraClient(
    api_key="your-api-token",              # Mandatory: API token for Jira REST authentication
    jira_url="https://your-domain.atlassian.net",  # Mandatory: Base Jira instance URL
    retry_cnt=3,                           # Optional: Number of retry attempts (default: 1)
    verbose=True,                          # Optional: Enables detailed logs (default: False)
    log_urls=True,                         # Optional: Logs every requested URL (default: False)
    logger=None,                           # Optional: Custom logger instance
    log_level=None                         # Optional: Logging level, default is INFO
)
```

---

#### `await client.start_session()`
Initializes the aiohttp session. This **must** be called before making any API requests.

---

#### `await client.close_session()`
Closes the aiohttp session to clean up resources.

---

#### `await client.read_issue(...)`
Fetches a Jira issue with optional comments, worklogs, and filtered changelog.
```python
issue = await client.read_issue(
    issue_id="PROJ-123",                 # Mandatory: Jira issue ID
    read_changelog=True,                  # Optional: Includes changelog (default: False)
    read_comments=True,                   # Optional: Includes comments (default: False)
    read_worklog=True,                    # Optional: Includes worklog (default: False)
    changelog_filter=["status", "assignee"]  # Optional: List of changelog fields to include
)
```

---

#### `await client.read_linked_issue_keys(issue_key: str)`
Returns a lists of issue keys created under a Jira task by links.
```python
keys = await client.read_linked_issue_keys(
    issue_key="ISSUE-123"  # Mandatory: The issue key
)
```

---

#### `await client.read_linked_epic_keys(epic_key: str)`
Returns a lists of issue keys created under a Jira epic by links.
```python
keys = await client.read_linked_epic_keys(
    epic_key="EPIC-123"  # Mandatory: The epic key
)
```

---

#### `await client.read_custom_jql_keys(custom_jql: str)`
Returns a list of issue keys matching a JQL query.
```python
keys = await client.read_custom_jql_keys(
    custom_jql="project = PROJ AND status = 'To Do'"  # Mandatory: Your JQL query
)
```

---

#### `await client.read_board_id(board_name: str)`
Looks up the board ID from its name.
```python
board_id = await client.read_board_id(
    board_name="Development Board"  # Mandatory: Exact name of the Jira board
)
```

---

#### `await client.read_sprint_list(...)`
Returns active/closed sprints from a board, with optional filters.
```python
sprints = await client.read_sprint_list(
    board_id=12,                       # Mandatory: Jira board ID
    origin_board=True,                # Optional: Only return sprints from the original board (default: False)
    name_filter="Q1"                  # Optional: Filter sprints by name substring (default: None)
)
```

---

#### `await client.send_request(...)`

Examples on using this function:

Create an issue:
```python
async def create_issue(self, summary, project_key, description):
    data = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Task"}
        }
    }

    return await self.jira_client.send_request("POST", "/rest/api/2/issue", json=data)
```

Add a comment:
```python
async def add_comment(self, issue_key, body):
    data = {"body": body}
    path = f"/rest/api/2/issue/{issue_key}/comment"
    return await self.jira_client.send_request("POST", path, json=data)
```

Delete a comment:
```python
async def delete_comment(self, issue_key, comment_id):
    path = f"/rest/api/2/issue/{issue_key}/comment/{comment_id}"
    await self.jira_client.send_request("DELETE", path)
```

Update an issue:
```python
async def update_issue(self, issue_key, update_fields):
    data = {"fields": update_fields}
    path = f"/rest/api/2/issue/{issue_key}"
    
    return await self.jira_client.send_request("PUT", path, json=data)
```

---

This module uses robust error handling, retry logic, and supports all core Jira querying needs in a simple asynchronous workflow.

## 3.3 Gitlab Utilities

A client for interacting with a GitLab instance.  
Capable of listing branches, tags, fetching commit info and changes, cloning repositories, and switching branches.

### GitlabClient
**Description:**
The GitlabClient class is a utility for interacting with a GitLab instance, primarily aimed at:

- Listing branches and tags
- Querying commit and merge request (MR) metadata
- Cloning repositories and checking out branches
- Retrieving commit changes

It's built as a wrapper around the python-gitlab and GitPython libraries, providing a unified interface for high-level GitLab and local repository operations.

**Usage Example:**
```python
from utilities import GitlabClient

client = GitlabClient(
    url=GITLAB_URL,
    private_token=PRIVATE_TOKEN,
    verbose=True,
    logger=logger,
    timeout=10,
    retries=3,
    large_repo_threshold=500
)

project_path = "your-group/your-project"  # Or numeric project ID

# 2. Get a project
project = client.get_project(project_path)
print("Project:", project)

# 3. List branches
branches = client.list_branches(project_path, max_branches=10) # List N branches in alphabetical order
branches = client.list_recent_branches(project_path, num_branches=10) # List N branches with the most recent commits
print("Branches:", branches)

# 4. Get parent merge request for a branch
parent_mr = client.get_branch_mr(project_path, branch_name="feature-branch")
print("Parent MR:", parent_mr)

# 5. List tags
tags = client.list_tags(project_path)
print("Tags:", tags)

# 6. List changed files between tags
files = client.list_changed_files_between_tags(project_path, "v1.0.0", "v2.0.0")
print(files)

# 7. List commits on a branch
commits = client.list_commits(project_path, branch="main", max_commits=10)
print("Commits on main:", commits)

# 8. List unique commits on a branch (not in base)
unique_commits = client.list_unique_commits_on_branch(
    project_path, base_branch="main", compare_branch="feature-branch"
)
print("Unique commits:", unique_commits)

# 9. Get files changed in a commit
if commits:
    changed_files = client.get_commit_changed_files(project_path, commit_id=commits[0].commit_id)
    print(f"Files changed in commit {commits[0].commit_short_id}:", changed_files)

# 10. Clone a repository (to local directory)
local_path = "./local_repo"
repo = client.clone_repository(project_path, local_path, branch="main")
print("Local repo:", repo)

# 11. Checkout a branch in the local repo
client.checkout_branch(local_path, branch="feature-branch")
print("Checked out feature-branch in local repo.")

#12. Download pipeline artifacts
client.download_pipeline_artifacts(
    project_path="your/group/project",
    pipeline_id=123456,
    jobs_of_interest=[
        "job1",
        "job2",
        # etc.
    ],
    output_folder="C:/some_folder/output"
)
```

## 3.4 AI Utilities

This section describes the utility wrappers for working with Azure's AI services. Each class encapsulates logic for specific services and includes optional logging, retries, and caching mechanisms. 

### AzureDocumentIntelligenceClient
A utility wrapper around Azure Document Intelligence API that parses documents (like PDFs) using Azure's prebuilt models and caches results locally.

#### Class: `AzureDocumentIntelligenceClient`

##### Description:
Provides a simplified interface for calling Azure Document Intelligence's `prebuilt-layout` model. Supports result caching and custom logging.

##### Initialization:
```python
from utilities import AzureDocumentIntelligenceClient

client = AzureDocumentIntelligenceClient(
    endpoint="<AZURE_DOCINT_ENDPOINT>",         # Required
    api_key="<AZURE_DOCINT_API_KEY>",           # Required
    verbose=True,                                 # Optional (default: False)
    logger=my_logger,                             # Optional (default: None)
    log_level=logging.DEBUG                       # Optional (default: INFO)
)
```

##### Method: `parse_document(file_path: str, output_format: ContentFormat = ContentFormat.MARKDOWN) -> str`
Parses a document using Azure Document Intelligence and returns the result. Caches result in a `.pkl` file.

###### Example:
```python
from azure.ai.documentintelligence.models import ContentFormat

content = client.parse_document(
    file_path="./document.pdf",                     # Required
    output_format=ContentFormat.MARKDOWN             # Optional (default: MARKDOWN)
)
```

---

### AzureOpenAIClient
A full-featured wrapper around Azure OpenAI that manages conversation sessions, retries, logging, and saving history to disk.

#### Class: `AzureOpenAIClient`

##### Description:
Encapsulates all the configuration and operational logic for using Azure OpenAI's Chat Completions endpoint. Maintains multiple conversation sessions and supports advanced configuration like temperature, top_p, and penalties.

##### Initialization:
```python
client = AzureOpenAIClient(
    azure_endpoint="<AZURE_OPENAI_ENDPOINT>",           # Required
    api_key="<AZURE_OPENAI_API_KEY>",                   # Required
    api_version="2024-03-01-preview",                    # Required
    llm_model="gpt-4",                                   # Required
    default_system_message="You are a helpful assistant.", # Optional
    max_tokens=2000,                                      # Optional
    temperature=0.7,                                      # Optional
    top_p=0.9,                                            # Optional
    frequency_penalty=0.0,                                # Optional
    presence_penalty=0.0,                                 # Optional
    include_message_history=True,                         # Optional
    save_sessions_to_disk=True,                           # Optional
    verbose=True,                                         # Optional
    log_messages=True,                                    # Optional
    logger=my_logger,                                     # Optional
    log_level=logging.INFO                                # Optional
)
```

##### Method: `request_completion(message_content: str, session_id: Optional[str] = None)`
Sends a message to the model and returns the assistant's reply.

###### Example:
```python
response = client.request_completion(
    message_content="Explain quantum computing in simple terms",  # Required
    session_id="session1"                                         # Optional (default: "default")
)
```

##### Method: `trim_conversation_history(session_id: Optional[str], max_length: int = 50)`
Trims the history of the specified session to the last N messages.

##### Method: `change_system_message(system_message: str, session_id: Optional[str])`
Updates the system message used in a given session.

##### Method: `get_conversation_history_as_text(session_id: Optional[str]) -> str`
Returns the entire session history as a plain text string.

##### Method: `reset_conversation(session_id: Optional[str])`
Resets the session to only the system message.

##### Method: `save_conversation(file_path: str, session_id: Optional[str])`
Saves session history to disk as JSON.

##### Method: `load_conversation(file_path: str, session_id: Optional[str])`
Loads session history from a JSON file.

##### Method: `get_message_count(session_id: Optional[str]) -> int`
Returns the number of messages exchanged in the session.

##### Async Method: `request_completion_async(...)`
Asynchronous version of `request_completion()`.

## 3.5 OS Utilities

This section describes additional utility modules aimed at filesystem and content-level operations. These tools can be used independently to scan, monitor, or write file content efficiently across various formats.

### `ContentScanner` Class

**Purpose**: Scans the content of different file types (text, CSV, Excel, DOCX, PDF, etc.) for specified string or regex patterns.

**Class**: `ContentScanner`

**Constructor Usage**:
```python
from utilities import ContentScanner

scanner = ContentScanner(
    string_patterns=['error', 'fail'],     # Optional: list of plain string patterns
    regex_patterns=[r'\berror\b'],       # Optional: list of regex patterns
    case_sensitive=False,                  # Optional: defaults to False
    max_results=10,                        # Optional: maximum matches per file
    verbose=True                           # Optional: enable logging
)
```

**Method**: `scan_files(file_paths: List[Union[str, Path]]) -> AsyncGenerator`

**Description**: Asynchronously scans a list of files and yields matches as dictionaries containing the file path, matching line, and line number.

---

### `DirectoryWatcher` Class (Windows Only)

**Purpose**: Watches for file system changes in a directory using the Windows Win32 API.

**Class**: `DirectoryWatcher`

**Constructor Usage**:
```python
from utilities import DirectoryWatcher

watcher = DirectoryWatcher(
    path='C:/projects',                    # Required: path to watch
    recursive=True,                        # Optional: monitor subdirectories
    debounce_interval=1.0,                 # Optional: debounce time in seconds
    file_patterns=['*.txt', '*.log'],      # Optional: glob patterns
    event_callback=my_callback             # Optional: function to call on each event
)
```

**Method**: `watch() -> AsyncGenerator`

**Description**: Asynchronously yields `DirectoryChangeEvent` objects for file changes.

**Note**: Only works on Windows.

---

### `FileScanner` Class

**Purpose**: Recursively scans directories for files matching criteria like name, size, modification date, and folder pattern.

**Class**: `FileScanner`

**Constructor Usage**:
```python
from utilities import FileScanner, TraversalMethod
from datetime import datetime

scanner = FileScanner(
    root_dir='C:/data',                    # Required: root directory
    max_workers=10,                        # Optional: number of worker threads
    method=TraversalMethod.DFS,            # Optional: BFS or DFS traversal
    file_patterns=[r'.*\.log$'],          # Optional: regex for files
    folder_patterns=[r'logs'],             # Optional: regex for folder names
    first_folder_patterns=[r'2025'],       # Optional: regex for top-level folders
    max_depth=5,                           # Optional: depth limit
    min_file_size=1024,                    # Optional: min size in bytes
    modified_after=datetime(2024, 1, 1),   # Optional: filter by modification time
    skip_hidden=True,                      # Optional: ignore hidden files/folders
    follow_symlinks=False                  # Optional: whether to follow symlinks
)
```

**Method**: `scan_files() -> AsyncGenerator`

**Description**: Asynchronously yields matching file paths as `Path` objects.

## 3.6 Excel Utilities

The Excel utility modules provide streamlined ways to compare and modify Excel files, either to validate content across files or make controlled edits. These are particularly useful for automating test validation, data migration verification, and editing result files.

### ExcelComparer
**Description:**
The `ExcelComparer` class provides an automated way to compare two Excel files sheet-by-sheet. It supports column exclusions, float value tolerance, and case-insensitive comparisons. Useful for validating exported data from different environments or after transformations.

**Usage Example:**
```python
from utilities import ExcelComparer

comparer = ExcelComparer(
    file_path1='old_version.xlsx',                 # (required) Path to the first Excel file
    file_path2='new_version.xlsx',                 # (required) Path to the second Excel file
    ignore_columns=['last_updated', 'id'],         # (optional) List of columns to ignore in comparison
    float_tolerance=1e-4,                          # (optional) Float comparison tolerance (default: 1e-6)
    case_insensitive=True,                         # (optional) Whether to ignore case when comparing strings
    verbose=True                                   # (optional) Enable verbose output
)

report = comparer.compare()
comparer.diff_to_csv("comparison_output.csv")
print(comparer.diff_to_str())
```

## 3.7 Config utilities

The `Config` utilities module provides mechanisms to load, merge, access, and write configuration files across multiple standard formats such as `.env`, `.yaml`, `.json`, `.toml`, `.ini`, and `.xml`. It contains two main components:

### `Config` class (from `config_parser.py`)

This class implements a singleton pattern to manage and expose application configurations. It automatically loads environment variables and merges all config file contents found in the current directory.

#### Features:
- Loads `.env` variables.
- Supports config files: YAML, JSON, TOML, INI, and XML.
- Converts configs to a nested `SimpleNamespace` structure.
- Merges multiple config files into one consistent structure.
- Provides an `env` field to access environment variables.
- Supports hot-reloading of config.

#### Usage:
```python
from utilities import Config

cfg = Config().get()
print(cfg.app.name)        # Access config value
print(cfg.os.env.DEBUG)    # Access environment variable

Config().reload()          # Reload configuration if files are updated
```

---

### `write_config` function (from `config_writer.py`)

This utility function exports a configuration dictionary or `SimpleNamespace` to a file in a specified format. Useful for persisting or exporting configuration values after runtime modifications.

#### Parameters:
- `config` (dict | SimpleNamespace): Configuration data to write.
- `filename` (str): Path to the output file.
- `format` (ConfigFormat): The target file format (JSON, YAML, TOML, INI, XML).
- `exclude_keys` (List[str], optional): Top-level keys to exclude from the output.

#### Usage:
```python
from utilities import write_config, ConfigFormat
from types import SimpleNamespace

config = SimpleNamespace(app=SimpleNamespace(name="MyApp", debug=True))

write_config(
    config=config,                    # Mandatory
    filename="config_out.yaml",      # Mandatory
    format=ConfigFormat.YAML,         # Mandatory
    exclude_keys=["secret"]          # Optional
)
```

This ensures a clean and modular way to handle config loading and writing for any project using these utilities.