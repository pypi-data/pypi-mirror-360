from typing import Optional, TypedDict, List
from types import SimpleNamespace
import json

from sai_rl.api.routes.package import PackageType

from sai_rl.api.requestor import APIRequestor

from sai_rl.types import EnvironmentStandardType, EnvironmentActionType


class EnvironmentType(TypedDict):
    id: str
    name: str
    gymId: str
    type: EnvironmentStandardType
    actionType: EnvironmentActionType
    package: PackageType


class EnvironmentAPI:
    def __init__(self, api: APIRequestor):
        self._api = api

    def get(self, environment_id: str) -> Optional[EnvironmentType]:
        response = self._api.get(f"/v1/environments/{environment_id}")

        if not response:
            return None

        raw_environment = response.json()
        if not raw_environment:
            return None

        env_obj = json.loads(json.dumps(raw_environment), object_hook=lambda d: SimpleNamespace(**d))
        environment: EnvironmentType = {
            "id": env_obj.id,
            "name": env_obj.name,
            "gymId": env_obj.gymId,
            "type": env_obj.type,
            "actionType": env_obj.actionType,
            "package": {
                "id": env_obj.package.id,
                "name": env_obj.package.name,
                "version": env_obj.package.version
            }
        }

        return environment

    def list(self) -> Optional[List[EnvironmentType]]:
        response = self._api.get("/v1/environments")

        if not response:
            return None

        raw_environments = response.json()
        if not raw_environments:
            return None

        environments: List[EnvironmentType] = []

        for raw_environment in raw_environments:
            env_obj = json.loads(json.dumps(raw_environment), object_hook=lambda d: SimpleNamespace(**d))
            environment: EnvironmentType = {
                "id": env_obj.id,
                "name": env_obj.name,
                "gymId": env_obj.gymnasiumEnv,
                "type": env_obj.type,
                "actionType": env_obj.actionType,
                "package": {
                    "id": env_obj.package.id,
                    "name": env_obj.package.name,
                    "version": env_obj.package.version
                }
            }

            environments.append(environment)

        return environments
