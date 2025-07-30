from typing import Any, Dict, List, Optional

from pydantic import model_serializer


class ResourceSerializerMixin:
    @model_serializer(mode="plain")
    def to_jsonapi(self, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        base = {
            "type": getattr(self, "type", None),
            "id": getattr(self, "id", None),
            "lid": getattr(self, "lid", None),
        }
        meta = getattr(self, "meta", None)
        if meta:
            base["meta"] = meta
        links = getattr(self, "links", None)
        if links:
            base["links"] = dict(links.model_dump(exclude_none=True))
        attributes = getattr(self, "attributes", None)
        if attributes:
            if fields:
                base["attributes"] = dict(
                    attributes.model_dump(include=set(fields), exclude_none=True)
                )
            else:
                base["attributes"] = dict(attributes.model_dump(exclude_none=True))
        relationships = getattr(self, "relationships", None)
        if relationships:
            base["relationships"] = {
                k: dict(v.model_dump(exclude_none=True))
                for k, v in relationships.items()
            }
        return {k: v for k, v in base.items() if v is not None}


class ErrorSerializerMixin:
    @model_serializer(mode="plain")
    def to_jsonapi(self) -> Dict[str, Any]:
        return dict(getattr(self, "model_dump")(exclude_none=True))


class DocumentSerializerMixin:
    @model_serializer(mode="plain")
    def to_jsonapi(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        data = getattr(self, "data", None)
        if data:
            if isinstance(data, list):
                result["data"] = [d.to_jsonapi() for d in data]
            else:
                result["data"] = data.to_jsonapi()
        errors = getattr(self, "errors", None)
        if errors:
            result["errors"] = [e.to_jsonapi() for e in errors]
        meta = getattr(self, "meta", None)
        if meta:
            result["meta"] = meta
        jsonapi = getattr(self, "jsonapi", None)
        if jsonapi:
            result["jsonapi"] = jsonapi.model_dump(exclude_none=True)
        links = getattr(self, "links", None)
        if links:
            result["links"] = links.model_dump(exclude_none=True)
        included = getattr(self, "included", None)
        if included:
            result["included"] = [i.to_jsonapi() for i in included]
        return result


class QueryParamsSerializerMixin:
    """Mixin for serializing JSON:API query parameters to query string."""

    def to_query_string(self) -> str:
        """Convert query parameters to query string format."""
        params = []

        # Sparse fields
        fields = getattr(self, "fields", None)
        if fields:
            for resource_type, field_list in fields.items():
                params.append(f"fields[{resource_type}]={','.join(field_list)}")

        # Include
        include = getattr(self, "include", None)
        if include:
            params.append(f"include={','.join(include)}")

        # Sort
        sort = getattr(self, "sort", None)
        if sort:
            sort_strings = []
            for sort_item in sort:
                field = sort_item["field"]
                direction = sort_item["direction"]
                prefix = "-" if direction == "desc" else ""
                sort_strings.append(f"{prefix}{field}")
            params.append(f"sort={','.join(sort_strings)}")

        # Filters
        filters = getattr(self, "filters", None)
        if filters:
            for filter_item in filters:
                field = filter_item["field"]
                operator = filter_item["operator"]
                value = filter_item["value"]

                if operator == "eq":
                    params.append(f"filter[{field}]={value}")
                else:
                    if isinstance(value, list):
                        value_str = ",".join(value)
                    else:
                        value_str = str(value)
                    params.append(f"filter[{field}][{operator}]={value_str}")

        # Pagination
        pagination = getattr(self, "pagination", None)
        if pagination:
            for param, value in pagination.items():
                params.append(f"page[{param}]={value}")

        # Extra parameters
        extra_params = getattr(self, "extra_params", None)
        if extra_params:
            for key, value in extra_params.items():
                params.append(f"{key}={value}")

        return "&".join(params)
