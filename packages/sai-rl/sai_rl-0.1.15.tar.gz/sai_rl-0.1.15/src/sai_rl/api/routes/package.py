from typing import Optional, TypedDict, List

from sai_rl.api.requestor import APIRequestor


class PackageType(TypedDict):
    id: str
    name: str
    version: str


class PackageAPI:
    def __init__(self, api: APIRequestor):
        self._api = api

    def get(self, package_name: str) -> Optional[PackageType]:
        response = self._api.get(f"/v1/packages/{package_name}")

        if not response:
            return None

        raw_package = response.json()
        if not raw_package:
            return None

        package: PackageType = {
            "id": raw_package.get("id"),
            "name": raw_package.get("name"),
            "version": raw_package.get("version"),
        }

        return package

    def list(self) -> Optional[List[PackageType]]:
        response = self._api.get("/v1/packages")

        if not response:
            return None

        raw_packages = response.json()

        if not raw_packages:
            return None

        packages: List[PackageType] = []

        for raw_package in raw_packages:
            package: PackageType = {
                "id": raw_package.get("id"),
                "name": raw_package.get("name"),
                "version": raw_package.get("version"),
            }

            packages.append(package)

        return packages
