# -*- coding: utf-8 -*-
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Annotated


# Warning: dupplicated code from backoffice for the Pydantic v1 compatibility
class Pagination(BaseModel):
    """Pagination management model"""

    page: int = Field(1, gt=0, description="Page number")
    limit: int = Field(10, gt=0, le=100, description="Page size")

    def offset(self) -> int:
        """Calculate offset from page and limit"""
        return (self.page - 1) * self.limit

    def last(self) -> int:
        """Return index of last element"""
        return self.offset() + self.limit


class SortDirection(str, Enum):
    """Possibles values for sorting direction"""

    ASC = "asc"
    DESC = "desc"


class Sort(BaseModel):
    """Sorting parameters model"""

    order_by: Annotated[Optional[str], Field(description="Sorting field")] = None

    def column(self) -> Optional[str]:
        """Get name of column to use for sorting"""
        return self.order_by.split(":", 1)[0] if self.order_by is not None else None

    def direction(self) -> str:
        """Get direction to sort"""

        values = [item.value for item in SortDirection]

        try:
            if (
                self.order_by is not None
                and (param := self.order_by.split(":", 1)[1]) in values
            ):
                return param
        except IndexError:
            pass

        return SortDirection.ASC


class PaginationMetadata(BaseModel):
    """Pagination data sent with paginated lists"""

    current_offset: int = 0
    records: int = 0
    total_records: int = 0


class BaseListReply(BaseModel):
    """Base model for reply to list requests"""

    pagination: PaginationMetadata = PaginationMetadata()
