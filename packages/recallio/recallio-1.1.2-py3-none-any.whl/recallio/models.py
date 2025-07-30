"""Data models for Recallio API requests and responses."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class MemoryWriteRequest:
    """Request body for `/api/Memory/write`."""

    userId: str
    projectId: str
    content: str
    consentFlag: bool
    tags: Optional[List[str]] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryRecallRequest:
    """Request body for `/api/Memory/recall`."""

    projectId: str
    userId: str
    query: str
    scope: str
    tags: Optional[List[str]] = None
    limit: Optional[int] = None
    similarityThreshold: Optional[float] = None
    summarized: Optional[bool] = None
    reRank: Optional[bool] = None
    type: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryDeleteRequest:
    """Request body for `/api/Memory/delete`."""

    scope: str
    userId: Optional[str] = None
    projectId: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryDto:
    """Response body for memory objects."""

    id: Optional[str] = None
    userId: Optional[str] = None
    projectId: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    createdAt: Optional[str] = None
    expiresAt: Optional[str] = None


@dataclass
class MemoryWithScoreDto(MemoryDto):
    """Memory object returned from search with similarity information."""

    similarityScore: Optional[float] = None
    similarityLevel: Optional[str] = None


@dataclass
class ErrorReturnClass:
    """Error response returned by the API."""

    error: str


@dataclass
class RecallSummaryRequest:
    """Request body for `/api/Memory/recall-summary`."""

    projectId: str
    userId: str
    scope: str
    tags: Optional[List[str]] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SummarizedMemoriesDto:
    """Summarized memory response."""

    content: Optional[str] = None
    numberOfMemories: Optional[int] = None


@dataclass
class GraphAddRequest:
    """Request body for `/api/GraphMemory/add`."""

    data: Optional[str] = None
    user_id: Optional[str] = None
    project_id: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GraphSearchRequest:
    """Request body for `/api/GraphMemory/search`."""

    query: Optional[str] = None
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    limit: Optional[int] = None
    threshold: Optional[float] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GraphSearchResult:
    """Result item returned from graph search."""

    source: Optional[str] = None
    relationship: Optional[str] = None
    destination: Optional[str] = None
    score: Optional[float] = None
    source_type: Optional[str] = None
    destination_type: Optional[str] = None


@dataclass
class MemoryExportRequest:
    """Query parameters for `/api/Memory/export`."""

    type: str
    format: str
    userId: Optional[str] = None
    projectId: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None

    def to_params(self) -> dict:
        params = {
            "Type": self.type,
            "Format": self.format,
        }
        if self.userId is not None:
            params["UserId"] = self.userId
        if self.projectId is not None:
            params["ProjectId"] = self.projectId
        if self.startDate is not None:
            params["StartDate"] = self.startDate
        if self.endDate is not None:
            params["EndDate"] = self.endDate
        return params
