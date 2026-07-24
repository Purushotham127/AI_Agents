from __future__ import annotations

import json
from pathlib import Path
from typing import Any

WORKSPACE_DIR = Path("./workspace").resolve()
WORKSPACE_DIR.mkdir(exist_ok=True)

# Files that can never be deleted
PROTECTED_FILES = {"important.txt", "config.json"}


def get_safe_path(filename: str) -> Path:
    target = (WORKSPACE_DIR / filename).resolve()
    if not str(target).startswith(str(WORKSPACE_DIR)):
        raise ValueError(f"Security error: Path '{filename}' attempts to access outside the workspace.")
    return target


def register_file_tools(mcp_server: Any) -> None:
    @mcp_server.tool()
    def read_file(filename: str) -> str:
        """Read a file from the workspace."""
        try:
            path = get_safe_path(filename)
            if not path.exists():
                return json.dumps({"status": "error", "message": f"File '{filename}' does not exist."})
            content = path.read_text(encoding="utf-8")
            return json.dumps({"status": "success", "data": content})
        except Exception as exc:
            return json.dumps({"status": "error", "message": str(exc)})

    @mcp_server.tool()
    def write_file(filename: str, content: str) -> str:
        """Write content to a file in the workspace."""
        try:
            path = get_safe_path(filename)
            path.write_text(content, encoding="utf-8")
            return json.dumps({"status": "success", "message": f"Successfully wrote to '{filename}'"})
        except Exception as exc:
            return json.dumps({"status": "error", "message": str(exc)})

    @mcp_server.tool()
    def request_delete_confirmation(filename: str) -> str:
        """Start a safe, two-step deletion flow."""
        try:
            path = get_safe_path(filename)
            if filename in PROTECTED_FILES:
                return json.dumps({"status": "error", "message": f"File '{filename}' is protected and cannot be deleted."})
            if not path.exists():
                return json.dumps({"status": "error", "message": f"File '{filename}' does not exist."})

            import hashlib
            import time

            token = hashlib.md5(f"{filename}{time.time()}".encode()).hexdigest()[:8]
            pending_path = WORKSPACE_DIR / ".pending_deletions.json"
            pending = {}
            if pending_path.exists():
                pending = json.loads(pending_path.read_text())

            pending[token] = filename
            pending_path.write_text(json.dumps(pending))
            return json.dumps({
                "status": "confirmation_required",
                "message": f"You are about to permanently delete '{filename}'. To confirm, call confirm_delete_file with token='{token}'.",
                "confirmation_token": token,
                "filename": filename,
            })
        except Exception as exc:
            return json.dumps({"status": "error", "message": str(exc)})

    @mcp_server.tool()
    def confirm_delete_file(token: str) -> str:
        """Confirm and finalize a file deletion."""
        try:
            pending_path = WORKSPACE_DIR / ".pending_deletions.json"
            if not pending_path.exists():
                return json.dumps({"status": "error", "message": "No pending deletions found. Call request_delete_confirmation first."})

            pending = json.loads(pending_path.read_text())
            if token not in pending:
                return json.dumps({"status": "error", "message": f"Invalid or expired token '{token}'. Call request_delete_confirmation again."})

            filename = pending.pop(token)
            pending_path.write_text(json.dumps(pending))
            path = get_safe_path(filename)
            if not path.exists():
                return json.dumps({"status": "error", "message": f"File '{filename}' no longer exists."})

            path.unlink()
            return json.dumps({"status": "success", "message": f"File '{filename}' deleted successfully."})
        except Exception as exc:
            return json.dumps({"status": "error", "message": str(exc)})

    @mcp_server.tool()
    def list_files() -> str:
        """List all files in the workspace."""
        try:
            files = [f.name for f in WORKSPACE_DIR.glob("*") if f.is_file()]
            return json.dumps({"status": "success", "files": files})
        except Exception as exc:
            return json.dumps({"status": "error", "message": str(exc)})
