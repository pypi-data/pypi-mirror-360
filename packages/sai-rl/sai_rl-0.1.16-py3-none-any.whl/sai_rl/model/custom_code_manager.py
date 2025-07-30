import time
from typing import Optional, Callable

import os
import re
import inspect
import requests

import numpy as np
import gymnasium as gym

from rich.syntax import Syntax

from sai_rl.utils import config
from sai_rl.sai_console import SAIConsole, SAIStatus
from sai_rl.error import CustomCodeError, NetworkError


class CustomCodeManager:
    _console: Optional[SAIConsole]
    _env: Optional[gym.Env]

    def __init__(
        self,
        code: Optional[str | type | Callable] = None,
        function_type: str = "custom",
        code_type: str = "function",
        download_dir: str = config.temp_path,
        env: Optional[gym.Env] = None,
        verbose: bool = False,
        console: Optional[SAIConsole] = None,
        status: Optional[SAIStatus] = None,
    ):
        self._function_type = function_type
        self._code_type = code_type
        self._console = console
        self._env = env

        self.verbose = verbose

        self._code = None
        self._code_source = None

        self._download_dir = download_dir
        self._path = None

        if status:
            status.update(f"Loading {function_type} {code_type}...")

        self.load(code, status)

    def _print(self):
        if not self._code_source:
            return

        if not self._console:
            return

        panel_group = self._console.group(
            Syntax(self._code_source, "python", theme="github-dark"),
        )

        panel = self._console.panel(
            panel_group, title=f"{self._function_type.capitalize()} {self._code_type.capitalize()}", padding=(1, 2)
        )

        self._console.print()
        self._console.print(panel)

    def _load_from_code(self, code: str, status: Optional[SAIStatus] = None):
        if status:
            status.update(f"Loading {self._function_type} {self._code_type} from code...")

        clean_code = self.remove_imports(code)

        object_name = None
        object_type = None
        for line in clean_code.splitlines():
            line = line.strip()
            if line.startswith("def "):
                object_name = line.split("def ")[1].split("(")[0].strip()
                object_type = "function"
                break
            elif line.startswith("class "):
                object_name = line.split("class ")[1].split("(")[0].split(":")[0].strip()
                object_type = "class"
                break

        if not object_name or not object_type:
            raise CustomCodeError("No function or class definition found in the provided code")

        namespace = dict({"np": np, "env": self._env})
        exec(clean_code, namespace)

        loaded_object = namespace[object_name]
        if object_type == "class":
            self._code = loaded_object()
        else:
            self._code = loaded_object

        self._code_source = clean_code


    def _load_from_file(self, path: str, status: Optional[SAIStatus] = None):
        if status:
            status.update(f"Loading {self._function_type} {self._code_type} from file...")

        self._path = path
        if not os.path.exists(path):
            raise CustomCodeError(f"File not found: {path}")

        with open(path, "r") as f:
            code = f.read()
            self._load_from_code(code)

    def _load_from_url(self, url: str, status: Optional[SAIStatus] = None):
        if status:
            status.update(f"Downloading {self._function_type} {self._code_type} from URL...")
            status.stop()

        if not self._download_dir:
            raise CustomCodeError("Download path not set")

        os.makedirs(self._download_dir, exist_ok=True)
        path = f"{self._download_dir}/{time.time()}.py"

        if os.path.exists(path):
            os.remove(path)

        try:
            if self._console:
                with self._console.progress(f"Downloading {self._function_type} {self._code_type}") as progress:
                    with requests.get(url, stream=True) as response:
                        response.raise_for_status()
                        total_size = int(response.headers.get("content-length", 0))
                        task = progress.add_task("Downloading...", total=total_size)

                        chunk_size = 8192  # 8 KB
                        downloaded_size = 0

                        with open(path, "wb") as f:
                            for chunk in response.iter_content(chunk_size=chunk_size):
                                if chunk:
                                    f.write(chunk)
                                    downloaded_size += len(chunk)
                                    progress.update(task, advance=len(chunk))
            else:
                with requests.get(url) as response:
                    response.raise_for_status()
                    with open(path, "wb") as f:
                        f.write(response.content)

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Failed to download {self._function_type} {self._code_type}: {e}")

        if status:
            status.start()

        self._load_from_file(path, status)

    @staticmethod
    def remove_imports(code_string: str) -> str:
        """Remove import statements from code for security."""
        pattern = re.compile(
            r"^\s*#?\s*(from\s+\w+\s+import\s+.*|import\s+\w+.*|from\s+\w+\s+import\s+\(.*\)|import\s+\(.*\))",
            re.MULTILINE,
        )
        return re.sub(pattern, "", code_string)

    def has_method(self, method_name: str) -> bool:
        return hasattr(self._code, method_name) and callable(getattr(self._code, method_name))
 
    def load(
        self,
        custom_code: Optional[str | Callable] = None,
        status: Optional[SAIStatus] = None,
    ):
        if status:
            status.update(f"Loading {self._function_type} {self._code_type}...")

        if not custom_code:
            if self._console:
                self._console.warning(f"No {self._function_type} function provided, skipping load.")
            return

        if isinstance(custom_code, str):
            if custom_code.startswith(("http://", "https://")):
                self._load_from_url(custom_code, status)
            elif custom_code.endswith((".py")) and os.path.exists(custom_code):
                self._load_from_file(custom_code, status)
            elif custom_code.startswith("def") or custom_code.startswith("class"):
                self._load_from_code(custom_code, status)
            else:
                raise CustomCodeError(
                    f"Unsupported {self._function_type} {self._code_type} path: {custom_code}"
                )
        elif callable(custom_code):
            custom_code_source = inspect.getsource(custom_code)
            self._load_from_code(custom_code_source)
        else:
            raise CustomCodeError(
                f"Unsupported {self._function_type} {self._code_type} type: {type(custom_code)}"
            )

        if self.verbose:
            self._print()

        if self._console:
            self._console.success(f"Successfully loaded {self._function_type} {self._code_type}.")

    def save_code(self, path: str):
        if not self._code_source:
            raise CustomCodeError(f"No {self._function_type} {self._code_type} loaded")

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path), exist_ok=True)

        if os.path.exists(path):
            raise CustomCodeError(f"File already exists: {path}")

        if not path.endswith(".py"):
            raise CustomCodeError("File must end with .py")

        with open(path, "w") as f:
            f.write(self._code_source)
        self._path = path

    def clean(self):
        if self._path and os.path.exists(self._path):
            os.remove(self._path)
            self._path = None
        self._code = None
        self._code_source = None
