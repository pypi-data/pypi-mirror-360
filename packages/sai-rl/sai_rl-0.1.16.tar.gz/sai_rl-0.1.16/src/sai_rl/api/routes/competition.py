from typing import Any, List, Mapping, Optional, TypedDict
from types import SimpleNamespace
import json

from sai_rl.api.routes.environment import EnvironmentType
from sai_rl.api.requestor import APIRequestor


class CompetitionType(TypedDict):
    id: str
    slug: str
    name: str
    opensource: bool
    environment: EnvironmentType
    environmentVariables: Mapping[str, Any]
    numberOfBenchmarks: Optional[int]
    seed: Optional[int]


class CompetitionAPI:
    def __init__(self, api: APIRequestor):
        self._api = api

    def get(self, competition_id: str) -> Optional[CompetitionType]:
        response = self._api.get(f"/v1/competitions/{competition_id}")

        if not response:
            return None

        raw_competition = response.json()
        if not raw_competition:
            return None

        comp_env = json.loads(
            json.dumps(raw_competition), object_hook=lambda d: SimpleNamespace(**d)
        )
        competition: CompetitionType = {
            "id": comp_env.id,
            "slug": comp_env.slug,
            "name": comp_env.name,
            "opensource": comp_env.opensource if hasattr(comp_env, "opensource") else False,
            "environment": {
                "id": comp_env.environment.id,
                "name": comp_env.environment.name,
                "gymId": comp_env.environment.gymId,
                "type": comp_env.environment.type,
                "actionType": comp_env.environment.actionType,
                "package": {
                    "id": comp_env.environment.package.id,
                    "name": comp_env.environment.package.name,
                    "version": comp_env.environment.package.version,
                },
            },
            "environmentVariables": vars(comp_env.environmentVariables)
            if hasattr(comp_env, "environmentVariables")
            and not isinstance(comp_env.environmentVariables, dict)
            else (
                comp_env.environmentVariables
                if hasattr(comp_env, "environmentVariables")
                else {}
            ),
            "numberOfBenchmarks": comp_env.numberOfBenchmarks
            if hasattr(comp_env, "numberOfBenchmarks")
            else None,
            "seed": comp_env.seed if hasattr(comp_env, "seed") else None,
            "evaluation_fn": comp_env.evaluationFn if hasattr(comp_env, "evaluationFn") else None
        }

        return competition

    def list(self) -> Optional[List[CompetitionType]]:
        response = self._api.get("/v1/competitions")

        if not response:
            return None

        raw_competitions = response.json()
        if not raw_competitions:
            return None

        competitions: List[CompetitionType] = []

        for raw_competition in raw_competitions:
            comp_env = json.loads(
                json.dumps(raw_competition), object_hook=lambda d: SimpleNamespace(**d)
            )
            competition: CompetitionType = {
                "id": comp_env.id,
                "slug": comp_env.slug,
                "name": comp_env.name,
                "opensource": comp_env.opensource if hasattr(comp_env, "opensource") else False,
                "environment": {
                    "id": comp_env.environment.id,
                    "name": comp_env.environment.name,
                    "gymId": comp_env.environment.gymnasiumEnv,
                    "type": comp_env.environment.type,
                    "actionType": comp_env.environment.actionType,
                    "package": {
                        "id": comp_env.environment.package.id,
                        "name": comp_env.environment.package.name,
                        "version": comp_env.environment.package.version,
                    },
                },
                "environmentVariables": comp_env.environmentVariables,
                "numberOfBenchmarks": comp_env.numberOfBenchmarks
                if hasattr(comp_env, "numberOfBenchmarks")
                else None,
                "seed": comp_env.seed if hasattr(comp_env, "seed") else None,
            }

            competitions.append(competition)

        return competitions
