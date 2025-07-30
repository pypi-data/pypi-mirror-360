from typing import List

from ...models.isr.work import WorkModel

DEFAULT_FILTER_WORKS = {
    "dates":{
        "from_date":None,
        "to_date":None
    },
    "deviation_statuses":[],
    "executor_org_ids":[],
    "only_in_progress":False,
    "only_milestones":False,
    "only_with_category":False,
    "only_with_checkpoints":False,
    "only_without_category":False,
    "only_works":False
}

class WorksResource:
    def __init__(self, client):
        self._client = client

    def list(self, csg_id, filters: list = DEFAULT_FILTER_WORKS) -> List[WorkModel]:
        data = self._client.post(f"/api/isr-new-service/common/{csg_id}/all", json=filters)
        return [WorkModel.model_validate(item) for item in data.get("works")]
