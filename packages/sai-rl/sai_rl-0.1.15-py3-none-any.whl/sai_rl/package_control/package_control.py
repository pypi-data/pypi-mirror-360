from typing import Optional

import subprocess
import sys
import json
import importlib
import shutil
import re
from importlib.metadata import Distribution, version, PackageNotFoundError
from imageio_ffmpeg import get_ffmpeg_exe

from sai_rl.api.client import APIClient
from sai_rl.error import PackageError
from sai_rl.sai_console import SAIConsole, SAIStatus


def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


class PackageControl:
    def __init__(
        self,
        api: APIClient,
        console: SAIConsole,
        is_disabled: bool = False,
    ):
        self._api = api
        self._console = console
        self._disabled = is_disabled

        self._version_checked = False
        self._dependencies_checked = False

    @property
    def setup_complete(self) -> bool:
        return self._version_checked and self._dependencies_checked

    @staticmethod
    def is_cmd_available(cmd: str) -> bool:
        return shutil.which(cmd) is not None

    def _is_installed(self, package_name: str) -> bool:
        try:
            version(package_name)
            return True
        except PackageNotFoundError:
            return False

    def _is_editable_install(self, package_name: str) -> bool:
        try:
            direct_url = Distribution.from_name(package_name).read_text(
                "direct_url.json"
            )
            if direct_url is None:
                return False

            pkg_is_editable = (
                json.loads(direct_url).get("dir_info", {}).get("editable", False)
            )
            return pkg_is_editable
        except Exception:
            return False

    def _check_ffmpeg(self):
        try:
            ffmpeg_exe = get_ffmpeg_exe()
            subprocess.run([ffmpeg_exe, "-version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise PackageError(
                "FFmpeg is not installed or not found in the system PATH. Please install FFmpeg to ensure all features work correctly."
            )

    def _get_package_version(self, package_name: str) -> Optional[str]:
        try:
            return version(package_name)
        except Exception:
            return None

    def setup(self, status: Optional[SAIStatus] = None):
        skip_check_version = self._is_editable_install("sai_rl")

        if not skip_check_version:
            self.check_version(status=status)
            self.check_dependencies(status=status)

        self._version_checked = True
        self._dependencies_checked = True

    def check_dependencies(self, status: Optional[SAIStatus] = None):
        if status:
            status.update("Checking dependencies...")

        self._check_ffmpeg()

    def check_version(
        self, package_name: str = "sai_rl", status: Optional[SAIStatus] = None
    ) -> bool:
        if self._disabled:
            return True

        if status:
            status.update(f"Checking {package_name} version...")

        if self._is_editable_install(package_name):
            self._console.warning(
                f"{package_name} is an editable install. Version checking is disabled. \n"
            )
            return True

        latest_package_info = self._api.package.get(package_name)
        if not latest_package_info:
            raise PackageError(f"Package {package_name} latest version not found.")

        current_version = self._get_package_version(package_name)

        if current_version != latest_package_info["version"]:
            self._console.warning(
                f"{package_name} is out of date. Latest version is {latest_package_info['version']}. \n"
            )
            return False

        self._console.debug(f"{package_name} is up to date. \n")
        return True

    def update(
        self, package_name: str = "sai_rl", status: Optional[SAIStatus] = None
    ) -> None:
        if status:
            status.update(f"Updating {package_name} package...")

        is_installed = self._is_installed(package_name)
        message = "Updating" if is_installed else "Installing"

        if self._is_editable_install(package_name):
            self._console.warning(
                f"{package_name} is an editable install. Update is disabled."
            )
            return

        try:
            normalized_package_name = normalize(package_name)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    normalized_package_name,
                    "--upgrade",
                ]
            )
            if result.returncode != 0:
                result = subprocess.run(
                    ["uv", "pip", "install", normalized_package_name, "--upgrade"]
                )

            if result.returncode != 0:
                raise PackageError(
                    f"Unable to {message.lower()} {package_name} package. Please manually install it using 'pip install {normalized_package_name} --upgrade'."
                )

            self._console.success(
                f"Successfully {message.lower()} {package_name} package. \n"
            )
        except subprocess.CalledProcessError as e:
            self._console.error(f"Command failed with exit code {e.returncode}")
            raise PackageError(
                f"Unable to {message.lower()} {package_name} package. Please try again."
            )

    def uninstall(
        self, package_name: str = "sai_rl", status: Optional[SAIStatus] = None
    ) -> None:
        if status:
            status.update(f"Uninstalling {package_name} package...")

        try:
            normalized_package_name = normalize(package_name)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "uninstall",
                    normalized_package_name,
                    "--yes",
                ]
            )
            if result.returncode != 0:
                result = subprocess.run(
                    ["uv", "pip", "uninstall", normalized_package_name, "--yes"]
                )
            if result.returncode != 0:
                raise PackageError(
                    f"Unable to uninstall {package_name} package. Please manually uninstall it using 'pip uninstall {normalized_package_name} --yes'."
                )

            self._console.success(
                f"Successfully uninstalled {package_name} package. \n"
            )
        except subprocess.CalledProcessError:
            raise PackageError(
                f"Unable to uninstall {package_name} package. Please try again."
            )

    def load(
        self, package_name: str = "sai_rl", status: Optional[SAIStatus] = None
    ) -> None:
        if status:
            status.update(f"Importing {package_name} package...")

        if not self.check_version(package_name, status=status):
            self.update(package_name, status=status)

        try:
            importlib.import_module(package_name)
            self._console.success(f"Successfully imported {package_name} package.")
        except ImportError:
            raise PackageError(
                f"Unable to import {package_name} package. Please install it using 'sai install {package_name}'."
            )
