"""HTTP client for the Recallio API."""
from __future__ import annotations

import requests

from .models import (
    MemoryWriteRequest,
    MemoryRecallRequest,
    MemoryDeleteRequest,
    RecallSummaryRequest,
    MemoryExportRequest,
    MemoryDto,
    MemoryWithScoreDto,
    SummarizedMemoriesDto,
    GraphAddRequest,
    GraphSearchRequest,
    GraphSearchResult,
)
from .errors import RecallioAPIError


class RecallioClient:
    """Client for interacting with the Recallio API."""

    def __init__(self, api_key: str, base_url: str = "https://app.recallio.ai") -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _request(
        self,
        method: str,
        path: str,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, json=json, params=params)
        if response.status_code >= 200 and response.status_code < 300:
            if response.content:
                try:
                    return response.json()
                except ValueError:
                    return response.text
            return {}
        try:
            data = response.json()
            message = data.get("error", response.text)
        except ValueError:
            message = response.text
        raise RecallioAPIError(message, status_code=response.status_code)

    def write_memory(self, request: MemoryWriteRequest) -> MemoryDto:
        data = self._request("POST", "/api/Memory/write", json=request.to_dict())
        return MemoryDto(**data)

    def recall_memory(self, request: MemoryRecallRequest) -> list[MemoryWithScoreDto]:
        data = self._request("POST", "/api/Memory/recall", json=request.to_dict())
        if isinstance(data, list):
            return [MemoryWithScoreDto(**item) for item in data]
        return [MemoryWithScoreDto(**data)]

    def recall_summary(self, request: RecallSummaryRequest) -> SummarizedMemoriesDto:
        data = self._request("POST", "/api/Memory/recall-summary", json=request.to_dict())
        if isinstance(data, dict):
            return SummarizedMemoriesDto(**data)
        return SummarizedMemoriesDto()

    def delete_memory(self, request: MemoryDeleteRequest) -> None:
        self._request("POST", "/api/Memory/delete", json=request.to_dict())
        return None

    def export_memory(self, request: MemoryExportRequest) -> str:
        data = self._request("GET", "/api/Memory/export", params=request.to_params())
        if isinstance(data, str):
            return data
        return ""

    def add_graph_memory(self, request: GraphAddRequest) -> MemoryDto:
        data = self._request("POST", "/api/GraphMemory/add", json=request.to_dict())
        return MemoryDto(**data)

    def search_graph_memory(self, request: GraphSearchRequest) -> list[GraphSearchResult]:
        data = self._request("POST", "/api/GraphMemory/search", json=request.to_dict())
        if isinstance(data, list):
            return [GraphSearchResult(**item) for item in data]
        return [GraphSearchResult(**data)]

    def get_graph_relationships(
        self,
        user_id: str | None = None,
        project_id: str | None = None,
        limit: int | None = None,
    ) -> list[GraphSearchResult]:
        params = {}
        if user_id is not None:
            params["userId"] = user_id
        if project_id is not None:
            params["projectId"] = project_id
        if limit is not None:
            params["limit"] = limit
        data = self._request("GET", "/api/GraphMemory/relationships", params=params)
        if isinstance(data, list):
            return [GraphSearchResult(**item) for item in data]
        return [GraphSearchResult(**data)]

    def delete_all_graph_memory(
        self,
        user_id: str | None = None,
        project_id: str | None = None,
    ) -> None:
        params = {}
        if user_id is not None:
            params["userId"] = user_id
        if project_id is not None:
            params["projectId"] = project_id
        self._request("DELETE", "/api/GraphMemory/delete-all", params=params)
        return None
