from typing import Optional, TypedDict, List
from types import SimpleNamespace
import json

from sai_rl.api.requestor import APIRequestor
from sai_rl.types import EnvironmentActionType, EnvironmentStandardType


class SubmissionEnvironmentType(TypedDict):
    id: str
    name: str
    gymId: str
    type: EnvironmentStandardType
    actionType: EnvironmentActionType


class SubmissionCompetitionType(TypedDict):
    id: str
    slug: str
    name: str
    environment: SubmissionEnvironmentType


class SubmissionType(TypedDict):
    id: str
    name: str
    type: str
    status: str
    score: Optional[str]
    competition: SubmissionCompetitionType
    updatedAt: str
    createdAt: str


class SubmissionAPI:
    def __init__(self, api: APIRequestor):
        self._api = api

    def list(self) -> Optional[List[SubmissionType]]:
        response = self._api.get("/v1/submissions")

        if not response:
            return None

        raw_submissions = response.json()
        if not raw_submissions:
            return None

        submissions: List[SubmissionType] = []

        for raw_submission in raw_submissions:
            sub_obs = json.loads(
                json.dumps(raw_submission), object_hook=lambda d: SimpleNamespace(**d)
            )
            submission: SubmissionType = {
                "id": sub_obs.id,
                "name": sub_obs.name,
                "type": sub_obs.type,
                "status": sub_obs.status,
                "score": sub_obs.score if hasattr(sub_obs, "score") else None,
                "competition": {
                    "id": sub_obs.competition.id,
                    "slug": sub_obs.competition.slug,
                    "name": sub_obs.competition.name,
                    "environment": {
                        "id": sub_obs.competition.environment.id,
                        "name": sub_obs.competition.environment.name,
                        "gymId": sub_obs.competition.environment.gymId,
                        "type": sub_obs.competition.environment.type,
                        "actionType": sub_obs.competition.environment.actionType,
                    },
                },
                "updatedAt": sub_obs.updatedAt,
                "createdAt": sub_obs.createdAt,
            }

            submissions.append(submission)

        return submissions

    def create(self, data: dict, files: dict) -> Optional[SubmissionType]:
        response = self._api.post("/v1/submissions", data=data, files=files)

        if not response:
            return None

        raw_submission = response.json()

        sub_obs = json.loads(
            json.dumps(raw_submission), object_hook=lambda d: SimpleNamespace(**d)
        )
        submission: SubmissionType = {
            "id": sub_obs.id,
            "name": sub_obs.name,
            "type": sub_obs.type,
            "status": sub_obs.status,
            "score": sub_obs.score if hasattr(sub_obs, "score") else None,
            "competition": {
                "id": sub_obs.competition.id,
                "slug": sub_obs.competition.slug,
                "name": sub_obs.competition.name,
                "environment": {
                    "id": sub_obs.competition.environment.id,
                    "name": sub_obs.competition.environment.name,
                    "gymId": sub_obs.competition.environment.gymId,
                    "type": sub_obs.competition.environment.type,
                    "actionType": sub_obs.competition.environment.actionType,
                },
            },
            "updatedAt": sub_obs.updatedAt,
            "createdAt": sub_obs.createdAt,
        }

        return submission
