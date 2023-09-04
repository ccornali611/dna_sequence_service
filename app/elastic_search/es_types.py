from typing import List, Optional, TypedDict


class CreatorObj(TypedDict):
    id: str
    handle: str
    name: str

class IndexDoc(TypedDict):
    id: str
    name: str
    bases: str
    createdAt: str
    creator: CreatorObj

class IndexDocWithHighlight(IndexDoc):
    highlight: Optional[TypedDict('Highlight', { 'bases': List[str]})]

class SearchHit(TypedDict):
    _id: str
    _score: Optional[int]
    _source: IndexDoc

class SearchRequestResult(TypedDict):
    total: int
    page: int
    hits: List[IndexDocWithHighlight]

class TotalDict(TypedDict):
    total: int
    relation: str
