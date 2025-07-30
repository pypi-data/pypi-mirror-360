from typing import Any, Dict, List, Optional, TypeVar, Union
from enum import Enum
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

from jsonapi._mixins.serializers import (
    DocumentSerializerMixin,
    ErrorSerializerMixin,
    ResourceSerializerMixin,
)
from jsonapi._mixins.validators import (
    DocumentValidatorMixin,
    ErrorSourceValidatorMixin,
    JSONAPIErrorValidatorMixin,
    LinkValidatorMixin,
    ResourceIdentifierValidatorMixin,
    ResourceValidatorMixin,
    QueryParamsValidatorMixin,
    QueryParamsParserMixin,
)
from jsonapi._mixins.serializers import QueryParamsSerializerMixin

# Type aliases
ResourceType = TypeVar("ResourceType", bound="Resource")
RelationshipType = TypeVar("RelationshipType", bound="Relationship")
ResourceData = Union["Resource[Any]", List["Resource[Any]"], None]
ErrorList = List["JSONAPIError"]
LinkValue = Union[str, "LinkObject"]
RelationshipData = Union["ResourceIdentifier", List["ResourceIdentifier"], None]


# Constants
JSONAPI_CONTENT_TYPE: str = "application/vnd.api+json"
JSONAPI_ACCEPT: str = "application/vnd.api+json"


# Generic meta object
MetaObject = Optional[Dict[str, Any]]


# JSON:API Info and Error models
class JSONAPIInfo(BaseModel):
    version: str = Field(default="1.1", description="JSON:API specification version")
    ext: Optional[List[str]] = Field(
        default=None, alias="ext", description="Extension members"
    )
    profile: Optional[List[str]] = Field(
        default=None, alias="profile", description="Profile members"
    )
    meta: MetaObject = Field(
        default=None,
        alias="meta",
        description="Metadata about the JSON:API specification",
    )


class ErrorSource(BaseModel, ErrorSourceValidatorMixin):
    pointer: Optional[str] = Field(
        default=None, alias="pointer", description="The pointer to the error"
    )
    parameter: Optional[str] = Field(
        default=None, alias="parameter", description="The parameter of the error"
    )
    header: Optional[str] = Field(
        default=None, alias="header", description="The header of the error"
    )


class JSONAPIError(BaseModel, ErrorSerializerMixin, JSONAPIErrorValidatorMixin):
    id: Optional[str] = Field(
        default=None, alias="id", description="The unique identifier of the error"
    )
    links: Optional[Dict[str, Union[str, "LinkObject"]]] = Field(
        default=None, alias="links", description="Links related to the error"
    )
    status: Optional[str] = Field(
        default=None, alias="status", description="The HTTP status code of the error"
    )
    code: Optional[str] = Field(
        default=None, alias="code", description="The error code"
    )
    title: Optional[str] = Field(
        default=None, alias="title", description="The title of the error"
    )
    detail: Optional[str] = Field(
        default=None, alias="detail", description="The detail of the error"
    )
    source: Optional[ErrorSource] = Field(
        default=None, alias="source", description="The source of the error"
    )
    meta: MetaObject = Field(
        default=None, alias="meta", description="Metadata about the error"
    )


# Link models
class LinkObject(BaseModel, LinkValidatorMixin):
    href: str
    rel: Optional[str] = Field(
        default=None, alias="rel", description="The relationship of the link"
    )
    describedby: Optional[str] = Field(
        default=None, alias="describedby", description="The describedby of the link"
    )
    title: Optional[str] = Field(
        default=None, alias="title", description="The title of the link"
    )
    type: Optional[str] = Field(
        default=None, alias="type", description="The type of the link"
    )
    hreflang: Optional[Union[str, List[str]]] = Field(
        default=None, alias="hreflang", description="The hreflang of the link"
    )
    meta: MetaObject = Field(
        default=None, alias="meta", description="Metadata about the link"
    )


class Links(BaseModel):
    self: LinkValue = Field(..., alias="self", description="The self link")
    related: Optional[LinkValue] = Field(
        default=None, alias="related", description="The related link"
    )
    first: Optional[LinkValue] = Field(
        default=None, alias="first", description="The first link"
    )
    last: Optional[LinkValue] = Field(
        default=None, alias="last", description="The last link"
    )
    prev: Optional[LinkValue] = Field(
        default=None, alias="prev", description="The previous link"
    )
    next: Optional[LinkValue] = Field(
        default=None, alias="next", description="The next link"
    )

    model_config = ConfigDict(
        extra="forbid", validate_assignment=True, use_enum_values=True
    )


# Resource models
class ResourceIdentifier(BaseModel, ResourceIdentifierValidatorMixin):
    type: str
    id: Optional[str] = Field(
        default=None, alias="id", description="The unique identifier of the resource"
    )
    lid: Optional[str] = Field(
        default=None, alias="lid", description="The local identifier of the resource"
    )
    meta: Optional[MetaObject] = Field(
        default=None, alias="meta", description="Metadata about the resource"
    )


class Relationship(BaseModel):
    data: RelationshipData = Field(
        ..., alias="data", description="The relationship data of the resource"
    )
    links: Optional[Links] = Field(
        default=None, alias="links", description="Links related to the relationship"
    )
    meta: MetaObject = Field(
        default=None, alias="meta", description="Metadata about the relationship"
    )


class Resource[AttributesType: BaseModel](
    ResourceIdentifier, ResourceSerializerMixin, ResourceValidatorMixin
):
    attributes: Optional[AttributesType] = Field(
        default=None, alias="attributes", description="The attributes of the resource"
    )
    relationships: Optional[Dict[str, Relationship]] = Field(
        default=None,
        alias="relationships",
        description="The relationships of the resource",
    )
    links: Optional[Links] = Field(
        default=None, alias="links", description="Links related to the resource"
    )
    meta: MetaObject = Field(
        default=None, alias="meta", description="Metadata about the resource"
    )

    model_config = ConfigDict(
        extra="forbid", validate_assignment=True, use_enum_values=True
    )


# Document models
class JSONAPIDocument[T: BaseModel](
    BaseModel, DocumentSerializerMixin, DocumentValidatorMixin
):
    data: Optional[Union[Resource[T], List[Resource[T]]]] = Field(
        default=None, alias="data", description="The primary data of the document"
    )
    errors: Optional[ErrorList] = Field(
        default=None, alias="errors", description="An array of error objects"
    )
    meta: MetaObject = Field(
        default=None,
        alias="meta",
        description="Metadata about the resource that the document describes",
    )
    jsonapi: Optional[JSONAPIInfo] = Field(
        default_factory=lambda: JSONAPIInfo(),
        alias="jsonapi",
        description="Information about the JSON:API specification",
    )
    links: Optional[Links] = Field(
        default=None, alias="links", description="Links related to the primary data"
    )
    included: Optional[List[Resource[BaseModel]]] = Field(
        default=None,
        alias="included",
        description="An array of resource objects that are related to the primary data and/or each other",
    )


class JSONAPIHeader(BaseModel):
    version: str = Field(
        default="1.1",
        alias="jsonapi-version",
        description="The version of the JSON:API specification",
    )
    accept: str = Field(
        default=JSONAPI_ACCEPT,
        alias="accept",
        description="The media type of the body of the resource",
    )
    content_type: str = Field(
        default=JSONAPI_CONTENT_TYPE,
        alias="content-type",
        description="The media type of the body of the resource",
    )


class JSONAPIRequestBody[T: BaseModel](BaseModel):
    data: Union[Resource[T], List[Resource[T]]]
    meta: Optional[MetaObject] = Field(
        default=None,
        alias="meta",
        description="Metadata about the resource that the document describes",
    )
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class SortDirection(str, Enum):
    """Enumeration for sort directions."""

    ASC = "asc"
    DESC = "desc"


class FilterOperator(str, Enum):
    """Enumeration for filter operators."""

    EQ = "eq"  # equals
    NE = "ne"  # not equals
    LT = "lt"  # less than
    LE = "le"  # less than or equal
    GT = "gt"  # greater than
    GE = "ge"  # greater than or equal
    LIKE = "like"  # contains
    IN = "in"  # in list
    NOT_IN = "not_in"  # not in list


@dataclass
class SortField:
    """Represents a single sort field with direction."""

    field: str
    direction: SortDirection = SortDirection.ASC

    @classmethod
    def from_string(cls, sort_string: str) -> "SortField":
        """Create SortField from string representation."""
        if sort_string.startswith("-"):
            return cls(field=sort_string[1:], direction=SortDirection.DESC)
        return cls(field=sort_string, direction=SortDirection.ASC)

    def to_string(self) -> str:
        """Convert to string representation."""
        prefix = "-" if self.direction == SortDirection.DESC else ""
        return f"{prefix}{self.field}"


@dataclass
class FilterCondition:
    """Represents a single filter condition."""

    field: str
    operator: FilterOperator
    value: Union[str, List[str]]

    def __post_init__(self):
        """Validate filter condition after initialization."""
        if self.operator in [FilterOperator.IN, FilterOperator.NOT_IN]:
            if not isinstance(self.value, list):
                self.value = [self.value] if self.value else []


@dataclass
class PaginationParams:
    """Represents pagination parameters."""

    number: Optional[int] = None
    size: Optional[int] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
    cursor: Optional[str] = None

    def __post_init__(self):
        """Validate pagination parameters."""
        if self.number is not None and self.number < 1:
            raise ValueError("Page number must be >= 1")
        if self.size is not None and self.size < 1:
            raise ValueError("Page size must be >= 1")
        if self.offset is not None and self.offset < 0:
            raise ValueError("Offset must be >= 0")
        if self.limit is not None and self.limit < 1:
            raise ValueError("Limit must be >= 1")

    @property
    def is_cursor_based(self) -> bool:
        """Check if pagination is cursor-based."""
        return self.cursor is not None

    @property
    def is_offset_based(self) -> bool:
        """Check if pagination is offset-based."""
        return self.offset is not None or self.limit is not None

    @property
    def is_page_based(self) -> bool:
        """Check if pagination is page-based."""
        return self.number is not None or self.size is not None


class JSONAPIQueryParams(
    BaseModel,
    QueryParamsParserMixin,
    QueryParamsValidatorMixin,
    QueryParamsSerializerMixin,
):
    """JSON:API query parameters model with parsing, validation, and serialization."""

    include: Optional[List[str]] = Field(
        default=None, description="List of related resources to include"
    )
    sort: Optional[List[Dict[str, str]]] = Field(
        default=None, description="List of sort fields with directions"
    )
    filters: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="List of filter conditions"
    )
    fields: Optional[Dict[str, List[str]]] = Field(
        default=None, description="Sparse fieldsets by resource type"
    )
    pagination: Optional[Dict[str, Union[int, str]]] = Field(
        default=None, description="Pagination parameters"
    )
    extra_params: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional query parameters"
    )

    # Convenience methods for working with parsed data
    def get_sort_fields(self) -> List[SortField]:
        """Get sort fields as SortField objects."""
        if not self.sort:
            return []

        sort_fields = []
        for sort_item in self.sort:
            direction = (
                SortDirection.DESC
                if sort_item["direction"] == "desc"
                else SortDirection.ASC
            )
            sort_fields.append(SortField(field=sort_item["field"], direction=direction))
        return sort_fields

    def get_filter_conditions(self) -> List[FilterCondition]:
        """Get filters as FilterCondition objects."""
        if not self.filters:
            return []

        conditions = []
        for filter_item in self.filters:
            operator = FilterOperator(filter_item["operator"])
            conditions.append(
                FilterCondition(
                    field=filter_item["field"],
                    operator=operator,
                    value=filter_item["value"],
                )
            )
        return conditions

    def get_pagination_params(self) -> Optional[PaginationParams]:
        """Get pagination as PaginationParams object."""
        if not self.pagination:
            return None

        # Type-safe extraction of pagination parameters
        number = self.pagination.get("number")
        size = self.pagination.get("size")
        offset = self.pagination.get("offset")
        limit = self.pagination.get("limit")
        cursor = self.pagination.get("cursor")

        # Convert numeric values to int if they are strings
        if isinstance(number, str):
            number = int(number)
        if isinstance(size, str):
            size = int(size)
        if isinstance(offset, str):
            offset = int(offset)
        if isinstance(limit, str):
            limit = int(limit)
        if isinstance(cursor, int):
            cursor = str(cursor)

        return PaginationParams(
            number=number,
            size=size,
            offset=offset,
            limit=limit,
            cursor=cursor,
        )

    def get_sparse_fields(self, resource_type: str) -> Optional[List[str]]:
        """Get sparse fields for a specific resource type."""
        if not self.fields:
            return None
        return self.fields.get(resource_type)

    def get_included_resources(self) -> List[str]:
        """Get list of resources to include."""
        return self.include or []
