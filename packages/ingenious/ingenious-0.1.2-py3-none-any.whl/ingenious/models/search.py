from pydantic import BaseModel


class SearchQuery(BaseModel):
    query: str
    top: int


class SearchResult(BaseModel):
    results: list[dict]
