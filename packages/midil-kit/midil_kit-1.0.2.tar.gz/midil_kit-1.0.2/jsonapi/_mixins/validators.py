import re
from typing import Any, Dict, Optional, Self, List, Union, TYPE_CHECKING
from enum import Enum

from pydantic import field_validator, model_validator

if TYPE_CHECKING:
    pass


def _validate_string(value: str, field: str, pattern: str, example: str) -> str:
    if not re.match(pattern, value):
        raise ValueError(f"{field} must match pattern: {example}")
    return value


class ResourceIdentifierValidatorMixin:
    @model_validator(mode="after")
    def validate_resource_identifier(self) -> "Self":
        if not getattr(self, "id", None) and not getattr(self, "lid", None):
            raise ValueError(
                "Either 'id' or 'lid' must be provided in a resource identifier"
            )
        return self

    @field_validator("id", "lid")
    def validate_id_fields(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return _validate_string(
            value, "ID field", r"^[a-zA-Z0-9_-]+$", "alphanumeric, hyphens, underscores"
        )

    @field_validator("type")
    def validate_resource_type(cls, resource_type: str) -> str:
        return _validate_string(
            resource_type,
            "Resource type",
            r"^[a-z][a-z0-9_-]*$",
            "lowercase, hyphens, underscores",
        )


class ResourceValidatorMixin:
    @model_validator(mode="after")
    def validate_resource(self) -> "Self":
        if not getattr(self, "type", None):
            raise ValueError("The 'type' field is required in a resource")
        if not getattr(self, "id", None) and not getattr(self, "lid", None):
            raise ValueError(
                "At least one of 'id' or 'lid' must be present in a resource"
            )
        if not getattr(self, "attributes", None) and not getattr(
            self, "relationships", None
        ):
            raise ValueError(
                "At least one of 'attributes' or 'relationships' must be present"
            )
        return self


class ErrorSourceValidatorMixin:
    @model_validator(mode="after")
    def validate_source(self) -> "Self":
        if not (
            getattr(self, "pointer", None)
            or getattr(self, "parameter", None)
            or getattr(self, "header", None)
        ):
            raise ValueError(
                "At least one of 'pointer', 'parameter', or 'header' must be set"
            )
        return self

    @field_validator("pointer")
    def validate_json_pointer(cls, pointer: Optional[str]) -> Optional[str]:
        if pointer is None:
            return None
        if not isinstance(pointer, str) or not pointer.startswith("/"):
            raise ValueError("JSON pointer must be a string starting with '/'")
        return pointer


class JSONAPIErrorValidatorMixin:
    @model_validator(mode="after")
    def validate_error(self) -> "Self":
        if not (getattr(self, "title", None) or getattr(self, "detail", None)):
            raise ValueError(
                "At least one of 'title' or 'detail' must be set in an error object"
            )
        return self


class DocumentValidatorMixin:
    @model_validator(mode="after")
    def validate_document(self) -> "Self":
        if (
            getattr(self, "data", None) is not None
            and getattr(self, "errors", None) is not None
        ):
            raise ValueError("A document MUST NOT contain both 'data' and 'errors'")
        if (
            getattr(self, "data", None) is None
            and getattr(self, "errors", None) is None
            and getattr(self, "meta", None) is None
        ):
            raise ValueError(
                "A document MUST contain at least one of 'data', 'errors', or 'meta'"
            )
        return self


class LinkValidatorMixin:
    @model_validator(mode="after")
    def validate_link(self) -> "Self":
        if not getattr(self, "href", None):
            raise ValueError("The 'href' field is required in a link object")
        return self

    @field_validator("href")
    def validate_link_href(cls, href: str) -> Optional[str]:
        if not (
            href.startswith("http://")
            or href.startswith("https://")
            or href.startswith("/")
        ):
            raise ValueError("Link href must be a valid URL or relative path")
        return href


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


def _validate_field_name(field_name: str) -> str:
    """Validate field name format."""
    if not re.match(
        r"^[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*$", field_name
    ):
        raise ValueError(f"Invalid field name: {field_name}")
    return field_name


def _validate_relationship_path(path: str) -> str:
    """Validate relationship path format."""
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*$", path):
        raise ValueError(f"Invalid relationship path: {path}")
    return path


class QueryParamsParserMixin:
    """Mixin for parsing JSON:API query parameters from raw input."""

    @model_validator(mode="before")
    @classmethod
    def parse_query_params(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw query parameters into structured format."""
        if not isinstance(values, dict):
            return values

        parsed: Dict[str, Any] = {}

        # Handle each parameter type
        for key, value in values.items():
            if key == "include":
                parsed["include"] = cls._parse_include(value)
            elif key == "sort":
                parsed["sort"] = cls._parse_sort(value)
            elif key.startswith("fields[") and key.endswith("]"):
                if "fields" not in parsed:
                    parsed["fields"] = {}
                resource_type = key[7:-1]
                parsed["fields"][resource_type] = cls._parse_fields(value)
            elif key.startswith("filter["):
                if "filters" not in parsed:
                    parsed["filters"] = []
                filter_condition = cls._parse_filter(key, value)
                if filter_condition:
                    parsed["filters"].append(filter_condition)
            elif key.startswith("page[") and key.endswith("]"):
                if "pagination" not in parsed:
                    parsed["pagination"] = {}
                page_param = key[5:-1]
                parsed["pagination"][page_param] = cls._parse_page_param(
                    page_param, value
                )
            else:
                # Store extra parameters
                if "extra_params" not in parsed:
                    parsed["extra_params"] = {}
                parsed["extra_params"][key] = value

        return parsed

    @classmethod
    def _parse_include(cls, value: Union[str, List[str]]) -> List[str]:
        """Parse include parameter."""
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value or []

    @classmethod
    def _parse_sort(cls, value: Union[str, List[str]]) -> List[Dict[str, str]]:
        """Parse sort parameter into field/direction pairs."""
        if isinstance(value, str):
            sort_fields = [v.strip() for v in value.split(",") if v.strip()]
        else:
            sort_fields = value or []

        parsed_sorts = []
        for field in sort_fields:
            if field.startswith("-"):
                parsed_sorts.append({"field": field[1:], "direction": "desc"})
            else:
                parsed_sorts.append({"field": field, "direction": "asc"})

        return parsed_sorts

    @classmethod
    def _parse_fields(cls, value: Union[str, List[str]]) -> List[str]:
        """Parse fields parameter."""
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value or []

    @classmethod
    def _parse_filter(cls, key: str, value: str) -> Optional[Dict[str, Any]]:
        """Parse filter parameter."""
        # Extract field name and operator from filter[field][operator] or filter[field]
        filter_match = re.match(r"filter\[([^\]]+)\](?:\[([^\]]+)\])?", key)
        if not filter_match:
            return None

        field_name = filter_match.group(1)
        operator_str = filter_match.group(2) or "eq"

        # Handle list values for IN and NOT_IN operators
        if operator_str in ["in", "not_in"]:
            filter_value: Union[List[str], str] = [
                v.strip() for v in value.split(",") if v.strip()
            ]
        else:
            filter_value = value

        return {"field": field_name, "operator": operator_str, "value": filter_value}

    @classmethod
    def _parse_page_param(cls, param: str, value: str) -> Union[int, str]:
        """Parse pagination parameter."""
        if param in ["number", "size", "limit", "offset"]:
            try:
                return int(value)
            except ValueError:
                raise ValueError(
                    f"Invalid pagination parameter {param}: must be integer"
                )
        return value


class QueryParamsValidatorMixin:
    """Mixin for validating JSON:API query parameters."""

    @field_validator("include")
    @classmethod
    def validate_include(cls, include: Optional[List[str]]) -> Optional[List[str]]:
        """Validate include relationships."""
        if include is None:
            return None

        validated = []
        for relationship in include:
            validated.append(_validate_relationship_path(relationship))
        return validated

    @field_validator("sort")
    @classmethod
    def validate_sort(
        cls, sort: Optional[List[Dict[str, str]]]
    ) -> Optional[List[Dict[str, str]]]:
        """Validate sort fields."""
        if sort is None:
            return None

        validated = []
        for sort_item in sort:
            field = sort_item.get("field", "")
            direction = sort_item.get("direction", "asc")

            _validate_field_name(field)
            if direction not in ["asc", "desc"]:
                raise ValueError(f"Invalid sort direction: {direction}")

            validated.append({"field": field, "direction": direction})
        return validated

    @field_validator("fields")
    @classmethod
    def validate_fields(
        cls, fields: Optional[Dict[str, List[str]]]
    ) -> Optional[Dict[str, List[str]]]:
        """Validate sparse fieldsets."""
        if fields is None:
            return None

        validated = {}
        for resource_type, field_list in fields.items():
            if not re.match(r"^[a-z][a-z0-9_-]*$", resource_type):
                raise ValueError(f"Invalid resource type: {resource_type}")

            validated_fields = []
            for field in field_list:
                validated_fields.append(_validate_field_name(field))
            validated[resource_type] = validated_fields

        return validated

    @field_validator("filters")
    @classmethod
    def validate_filters(
        cls, filters: Optional[List[Dict[str, Any]]]
    ) -> Optional[List[Dict[str, Any]]]:
        """Validate filter conditions."""
        if filters is None:
            return None

        validated = []
        for filter_item in filters:
            field = filter_item.get("field", "")
            operator = filter_item.get("operator", "eq")
            value = filter_item.get("value")

            _validate_field_name(field)
            if operator not in [op.value for op in FilterOperator]:
                raise ValueError(f"Invalid filter operator: {operator}")

            if operator in ["in", "not_in"] and not isinstance(value, list):
                raise ValueError(f"Filter operator {operator} requires list value")

            validated.append({"field": field, "operator": operator, "value": value})

        return validated

    @model_validator(mode="after")
    def validate_pagination_consistency(self) -> Self:
        """Validate pagination parameter consistency."""
        pagination = getattr(self, "pagination", None)
        if not pagination:
            return self

        has_page_based = "number" in pagination or "size" in pagination
        has_offset_based = "offset" in pagination or "limit" in pagination
        has_cursor_based = "cursor" in pagination

        pagination_types = sum([has_page_based, has_offset_based, has_cursor_based])
        if pagination_types > 1:
            raise ValueError(
                "Cannot mix different pagination strategies (page-based, offset-based, cursor-based)"
            )

        # Validate individual parameters
        for param, value in pagination.items():
            if param in ["number", "size", "limit"] and value < 1:
                raise ValueError(f"Pagination parameter {param} must be >= 1")
            elif param == "offset" and value < 0:
                raise ValueError("Pagination offset must be >= 0")

        return self
