from typing import Optional, Set, Dict, Any
from fastapi import Request, HTTPException
from jsonapi import JSONAPIQueryParams, JSONAPIDocument
from jsonapi._mixins.validators import FilterOperator
from jsonapi.extensions.utils import JSONAPIQueryValidator


class JSONAPIQueryDependency:
    """FastAPI dependency for JSON:API query parameters."""

    def __init__(self, validator: Optional[JSONAPIQueryValidator] = None):
        self.validator = validator

    def __call__(self, request: Request) -> JSONAPIQueryParams:
        """FastAPI dependency callable."""
        query_params = dict(request.query_params)
        params = JSONAPIQueryParams.model_validate(query_params)

        if self.validator:
            errors = self.validator.validate(params)
            if errors:
                raise HTTPException(
                    status_code=400,
                    detail=JSONAPIDocument[Any](errors=errors).model_dump(),
                )

        return params


def create_jsonapi_dependency(
    allowed_fields: Optional[Set[str]] = None,
    allowed_relationships: Optional[Set[str]] = None,
    allowed_sort_fields: Optional[Set[str]] = None,
    allowed_filter_fields: Optional[Set[str]] = None,
    allowed_filter_operators: Optional[Dict[str, Set[FilterOperator]]] = None,
    max_page_size: Optional[int] = None,
    max_includes: Optional[int] = None,
) -> JSONAPIQueryDependency:
    """Create a configured JSON:API query dependency for FastAPI."""
    validator = JSONAPIQueryValidator(
        allowed_fields=allowed_fields,
        allowed_relationships=allowed_relationships,
        allowed_sort_fields=allowed_sort_fields,
        allowed_filter_fields=allowed_filter_fields,
        allowed_filter_operators=allowed_filter_operators,
        max_page_size=max_page_size,
        max_includes=max_includes,
    )
    return JSONAPIQueryDependency(validator)
