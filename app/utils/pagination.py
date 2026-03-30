from __future__ import annotations

import math
from typing import Optional,Tuple,Generic,TypeVar,Annotated,List
from pydantic import BaseModel, Field
from pydantic import computed_field as compute_field
from fastapi import Depends,Query


T = TypeVar("T")

class PaginateResponse(BaseModel,Generic[T]):
    items:list[T]
    total:int
    page:int
    page_size:int
    
    @compute_field
    @property
    def pages(self)->int:
        return math.ceil(self.total / self.page_size) if self.page_size else 0
    
    @compute_field
    @property
    def has_next(self)->bool:
        return self.page < self.pages

    @compute_field
    @property
    def has_prev(self)->bool:
        return self.page > 1

class PaginationParams:
    def __init__(
        self,
        page:int = Query(1,ge=1),
        page_size:int = Query(10,ge=1,le=100)
    ):
        self.page = page
        self.page_size = page_size

    def to_dict(self)->dict:
        return {"page":self.page,"page_size":self.page_size}

paginationDep = Annotated[PaginationParams,Depends(PaginationParams)]


def make_paginated_response(
    items: List[T], total: int, p: PaginationParams
) -> PaginatedResponse[T]:
    return PaginatedResponse(
        items=items, 
        total=total, 
        page=p.page, 
        page_size=p.page_size
        )