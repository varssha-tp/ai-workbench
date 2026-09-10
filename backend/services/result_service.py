import uuid

import pandas as pd


class ResultStore:
    def __init__(self):
        self._results: dict[str, pd.DataFrame] = {}

    def save(self, df: pd.DataFrame) -> str:
        result_id = str(uuid.uuid4())
        self._results[result_id] = df
        return result_id

    def get(self, result_id: str) -> pd.DataFrame | None:
        return self._results.get(result_id)


result_store = ResultStore()
