from ya_market_api.guide.region.dataclass.region import Region

from typing import Optional

from pydantic.main import BaseModel
from pydantic.fields import Field


class Request(BaseModel):
	region_id: int
	page: Optional[int] = None
	page_size: Optional[int] = Field(default=None, serialization_alias="pageSize")


class ResponsePager(BaseModel):
	current_page: Optional[int] = Field(None, validation_alias="currentPage")
	from_: Optional[int] = Field(None, validation_alias="from")
	page_size: Optional[int] = Field(None, validation_alias="pageSize")
	page_count: Optional[int] = Field(None, validation_alias="pageCount")
	to: Optional[int] = None
	total: Optional[int] = None


class Response(BaseModel):
	pager: Optional[ResponsePager] = None
	region: Optional[Region] = Field(default=None, validation_alias="regions")
