import csv
import json
import os
from typing import Any, Dict, List, Optional


def _ensure_parent_directory(path: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def write_text_file(path: str, content: str) -> Dict[str, Any]:
    """Write plain text content to a file."""
    try:
        _ensure_parent_directory(path)
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
        return {"success": True, "message": f"Text file written to {path}", "path": path}
    except Exception as exc:
        return {"success": False, "message": f"Unable to write text file: {exc}", "path": path}


def write_json_file(path: str, data: Any, indent: int = 2) -> Dict[str, Any]:
    """Write JSON content to a file."""
    try:
        _ensure_parent_directory(path)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=indent, ensure_ascii=False)
        return {"success": True, "message": f"JSON file written to {path}", "path": path}
    except Exception as exc:
        return {"success": False, "message": f"Unable to write JSON file: {exc}", "path": path}


def write_csv_file(
    path: str,
    rows: Any,
    fieldnames: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Write rows to a CSV file."""
    try:
        _ensure_parent_directory(path)
        if rows is None:
            return {"success": False, "message": "No rows provided for CSV output.", "path": path}

        if isinstance(rows, dict):
            rows = [rows]
        elif not isinstance(rows, list):
            return {
                "success": False,
                "message": "Rows must be a list of dictionaries or lists.",
                "path": path,
            }

        if not rows:
            return {"success": False, "message": "No rows provided for CSV output.", "path": path}

        with open(path, "w", encoding="utf-8", newline="") as file:
            if isinstance(rows[0], dict):
                if fieldnames is None:
                    fieldnames = list(rows[0].keys())
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            else:
                writer = csv.writer(file)
                if fieldnames:
                    writer.writerow(fieldnames)
                writer.writerows(rows)

        return {"success": True, "message": f"CSV file written to {path}", "path": path}
    except Exception as exc:
        return {"success": False, "message": f"Unable to write CSV file: {exc}", "path": path}


def write_yaml_file(path: str, data: Any, indent: int = 2) -> Dict[str, Any]:
    """Write YAML content to a file if PyYAML is installed."""
    try:
        import yaml
    except ImportError:
        return {
            "success": False,
            "message": "PyYAML is not installed. Install it to use YAML output.",
            "path": path,
        }

    try:
        _ensure_parent_directory(path)
        with open(path, "w", encoding="utf-8") as file:
            yaml.safe_dump(data, file, sort_keys=False, indent=indent)
        return {"success": True, "message": f"YAML file written to {path}", "path": path}
    except Exception as exc:
        return {"success": False, "message": f"Unable to write YAML file: {exc}", "path": path}


def write_data_file(path: str, data: Any, file_format: Optional[str] = None) -> Dict[str, Any]:
    """Write data to the requested file format based on path or explicit format."""
    if file_format is None:
        _, extension = os.path.splitext(path)
        file_format = extension.lower().lstrip('.')

    if file_format in {"txt", "text"}:
        return write_text_file(path, str(data))
    if file_format == "json":
        return write_json_file(path, data)
    if file_format == "csv":
        if isinstance(data, dict):
            rows = [data]
        else:
            rows = data
        return write_csv_file(path, rows)
    if file_format in {"yaml", "yml"}:
        return write_yaml_file(path, data)

    return {
        "success": False,
        "message": f"Unsupported file format: {file_format}",
        "path": path,
    }
