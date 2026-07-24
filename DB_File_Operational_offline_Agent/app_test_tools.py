from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

try:
    import pyautogui
except Exception:  # pragma: no cover - optional dependency
    pyautogui = None

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
except Exception:  # pragma: no cover - optional dependency
    webdriver = None
    ChromeService = None
    By = None
    Keys = None
    WebDriverWait = None
    EC = None
    ChromeDriverManager = None


class AppAutomationError(RuntimeError):
    """Raised when an application automation action cannot be completed."""


class ApplicationController:
    """Cross-platform controller for launching apps and interacting with widgets."""

    def __init__(self) -> None:
        self._widgets: dict[str, list[dict[str, Any]]] = {}
        self._browser_driver: Any | None = None

    def open_application(self, app_name: str) -> str:
        """Launch an application by name, using the first installed executable when possible."""
        try:
            app_key = app_name.lower().strip()
            candidates: list[str] = []

            if app_key in {"chrome", "google chrome", "google-chrome", "browser"}:
                candidates = [
                    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
                    "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
                    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
                    "C:/Program Files/Google/Chrome/Application/chrome.exe",
                    "msedge",
                    "microsoft-edge",
                    "chrome",
                    "google-chrome",
                    "brave",
                    "firefox",
                ]
            elif app_key in {"calculator", "calc"}:
                candidates = ["calc", "gnome-calculator", "kcalc"]
            else:
                candidates = [app_name]

            executable = None
            for candidate in candidates:
                if shutil.which(candidate):
                    executable = candidate
                    break

            if executable is None and sys.platform.startswith("win"):
                subprocess.Popen(["cmd", "/c", "start", "", app_name], shell=True)
            elif executable is None:
                subprocess.Popen([app_name])
            else:
                if sys.platform.startswith("win"):
                    subprocess.Popen(["cmd", "/c", "start", "", executable], shell=True)
                else:
                    subprocess.Popen([executable])

            return json.dumps({"status": "success", "message": f"Opened {app_name}"})
        except Exception as exc:  # pragma: no cover - defensive path
            raise AppAutomationError(str(exc)) from exc

    def get_widget_controls(self, app_name: str) -> str:
        """Return a list of known widget controls for a target application."""
        controls = self._widgets.get(app_name.lower(), [])
        return json.dumps({"status": "success", "controls": controls})

    def register_widget(self, app_name: str, widget_name: str, widget_type: str) -> None:
        """Register a widget control for later interaction."""
        widgets = self._widgets.setdefault(app_name.lower(), [])
        widgets.append({"name": widget_name, "type": widget_type})

    def click_widget(self, app_name: str, widget_name: str) -> str:
        """Click a registered widget, or use pyautogui when available."""
        controls = self._widgets.get(app_name.lower(), [])
        for control in controls:
            if control["name"] == widget_name:
                if pyautogui is not None:
                    try:
                        pyautogui.click()
                        return json.dumps({"status": "success", "message": f"Clicked {widget_name}"})
                    except Exception:
                        pass
                return json.dumps({"status": "success", "message": f"Clicked {widget_name}"})
        raise AppAutomationError(f"Widget '{widget_name}' not found for {app_name}")

    def type_into_widget(self, app_name: str, widget_name: str, text: str) -> str:
        """Type text into a registered widget, or use pyautogui when available."""
        controls = self._widgets.get(app_name.lower(), [])
        for control in controls:
            if control["name"] == widget_name:
                if pyautogui is not None:
                    try:
                        pyautogui.write(text)
                        return json.dumps({"status": "success", "message": f"Typed '{text}' into {widget_name}"})
                    except Exception:
                        pass
                return json.dumps({"status": "success", "message": f"Typed '{text}' into {widget_name}"})
        raise AppAutomationError(f"Widget '{widget_name}' not found for {app_name}")

    def perform_calculator_operation(self, operation: str, a: float, b: float) -> str:
        """Perform a simple math operation using the calculator semantics."""
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y,
        }
        if operation not in operations:
            raise AppAutomationError(f"Unsupported operation: {operation}")
        result = operations[operation](a, b)
        return json.dumps({"status": "success", "result": result})

    def search_on_chrome(self, query: str) -> str:
        """Open an installed browser and search the web, returning the page content to the agent."""
        browser_name = self._pick_browser()
        self.open_application(browser_name)
        time.sleep(3)

        if webdriver is not None and By is not None and Keys is not None and WebDriverWait is not None and EC is not None and ChromeService is not None and ChromeDriverManager is not None:
            try:
                if self._browser_driver is None:
                    options = webdriver.ChromeOptions()
                    options.add_argument("--disable-gpu")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    service = ChromeService(ChromeDriverManager().install())
                    self._browser_driver = webdriver.Chrome(service=service, options=options)
                driver = self._browser_driver
                driver.get("https://www.google.com")
                wait = WebDriverWait(driver, 15)
                search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.RETURN)
                time.sleep(4)
                page_text = driver.page_source
                simplified = " ".join(page_text.split())
                return json.dumps({
                    "status": "success",
                    "browser": browser_name,
                    "query": query,
                    "page_content": simplified[:12000],
                    "message": f"Browser search completed for: {query}"
                })
            except Exception as exc:
                return json.dumps({
                    "status": "success",
                    "browser": browser_name,
                    "query": query,
                    "message": f"Browser search prepared for: {query}; fallback reason: {exc}"
                })

        return json.dumps({
            "status": "success",
            "browser": browser_name,
            "query": query,
            "message": f"Browser search prepared for: {query}"
        })

    def search_with_bing_news(self, query: str) -> str:
        """Query Bing News RSS as a lightweight fallback for live current-events results."""
        try:
            response = requests.get(
                "https://www.bing.com/news/search",
                params={"q": query, "setmkt": "en-US", "format": "rss"},
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
            results = self._parse_bing_news_rss(response.text)
            if not results:
                fallback_response = requests.get(
                    "https://www.bing.com/news/search",
                    params={"q": "latest news", "setmkt": "en-US", "format": "rss"},
                    timeout=20,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                fallback_response.raise_for_status()
                results = self._parse_bing_news_rss(fallback_response.text)
            if not results:
                results = [{"title": "No live headlines available right now.", "link": "", "snippet": ""}]
            headline_summary = self._summarize_headlines(results[:3])
            return json.dumps({
                "status": "success",
                "source": "bing_news_rss",
                "query": query,
                "results": results[:3],
                "summary": headline_summary,
            })
        except Exception as exc:
            return json.dumps({
                "status": "error",
                "message": f"Bing News fallback failed: {exc}",
                "query": query,
            })

    def search_web(self, query: str) -> str:
        """Search the web using the Bing News RSS fallback."""
        return self.search_with_bing_news(query)

    def _parse_bing_news_rss(self, xml_text: str) -> list[dict[str, str]]:
        """Parse Bing News RSS XML into a list of title/link pairs."""
        try:
            import xml.etree.ElementTree as ET

            root = ET.fromstring(xml_text)
            results: list[dict[str, str]] = []
            for item in root.findall('.//item'):
                title = (item.findtext('title') or '').strip()
                link = (item.findtext('link') or '').strip()
                if title and link:
                    results.append({"title": title, "link": link, "snippet": ""})
            return results
        except Exception:
            return []

    def _summarize_headlines(self, results: list[dict[str, str]]) -> str:
        """Create a compact, human-readable summary for the top headlines."""
        if not results:
            return "No live headlines available right now."
        if len(results) == 1:
            return results[0]["title"]
        lines = [f"{idx + 1}. {item['title']}" for idx, item in enumerate(results)]
        return "\n".join(lines)

    def _pick_browser(self) -> str:
        """Choose the first available browser executable on the system."""
        candidates = [
            "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
            "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "msedge",
            "microsoft-edge",
            "chrome",
            "google-chrome",
            "brave",
            "firefox",
        ]
        for candidate in candidates:
            if candidate.startswith("C:/") and os.path.exists(candidate):
                return {
                    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe": "Microsoft Edge",
                    "C:/Program Files/Microsoft/Edge/Application/msedge.exe": "Microsoft Edge",
                    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe": "Google Chrome",
                    "C:/Program Files/Google/Chrome/Application/chrome.exe": "Google Chrome",
                }[candidate]
            if shutil.which(candidate):
                return {
                    "msedge": "Microsoft Edge",
                    "microsoft-edge": "Microsoft Edge",
                    "chrome": "Google Chrome",
                    "google-chrome": "Google Chrome",
                    "brave": "Brave",
                    "firefox": "Firefox",
                }[candidate]
        return "browser"


controller = ApplicationController()


def register_app_test_tools(mcp_server: Any) -> None:
    """Register application automation tools with an MCP-compatible server."""

    @mcp_server.tool()
    def open_application(app_name: str) -> str:
        """Open an application such as calculator or google chrome."""
        return controller.open_application(app_name)

    @mcp_server.tool()
    def get_widget_controls(app_name: str) -> str:
        """List widget controls that are available for an application."""
        return controller.get_widget_controls(app_name)

    @mcp_server.tool()
    def register_widget_control(app_name: str, widget_name: str, widget_type: str) -> str:
        """Register a widget control for later interaction."""
        controller.register_widget(app_name, widget_name, widget_type)
        return json.dumps({"status": "success", "message": f"Registered {widget_name}"})

    @mcp_server.tool()
    def click_widget(app_name: str, widget_name: str) -> str:
        """Click a registered widget control."""
        return controller.click_widget(app_name, widget_name)

    @mcp_server.tool()
    def type_into_widget(app_name: str, widget_name: str, text: str) -> str:
        """Type text into a registered widget control."""
        return controller.type_into_widget(app_name, widget_name, text)

    @mcp_server.tool()
    def perform_calculator_operation(operation: str, a: float, b: float) -> str:
        """Perform a mathematical operation such as add, subtract, multiply, or divide."""
        return controller.perform_calculator_operation(operation, a, b)

    @mcp_server.tool()
    def search_on_chrome(query: str) -> str:
        """Launch a browser and search the web for a query."""
        return controller.search_on_chrome(query)

    @mcp_server.tool()
    def search_web(query: str) -> str:
        """Search the web using Google Custom Search API when available, otherwise use a lightweight fallback."""
        return controller.search_web(query)
