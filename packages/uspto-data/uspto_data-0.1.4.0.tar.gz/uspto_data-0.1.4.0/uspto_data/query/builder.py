from typing import Dict, List, Optional, Any

class QueryBuilder:
    def __init__(self):
        self.query: Dict[str, Optional[Any]] = {
            "q": None,
            "filters": [],
            "rangeFilters": [],
            "sort": [],
            "fields": None,
            "pagination": {"offset": 0, "limit": 25},
            "facets": None,
        }

    def set_query(self, q: str):
        """Set the 'q' parameter for freeform or DSL-specific queries."""
        self.query["q"] = q
        return self

    def add_filter(self, name: str, values: List[str]):
        """Add a filter to narrow down results."""
        self.query["filters"].append({"name": name, "value": values})
        return self

    def add_range_filter(self, field: str, value_from: str, value_to: str):
        """Add a range filter for narrowing down results."""
        self.query["rangeFilters"].append({
            "field": field,
            "valueFrom": value_from,
            "valueTo": value_to
        })
        return self

    def set_sort(self, field: str, order: str = "desc"):
        """Set sorting for the results."""
        self.query["sort"].append({"field": field, "order": order})
        return self

    def set_fields(self, fields: List[str]):
        """Specify fields to include in the response."""
        self.query["fields"] = fields
        return self

    def set_pagination(self, offset: int = 0, limit: int = 25):
        """Set pagination parameters."""
        self.query["pagination"] = {"offset": offset, "limit": limit}
        return self

    def set_facets(self, facets: List[str]):
        """Set facets for aggregations."""
        self.query["facets"] = facets
        return self

    def build(self) -> Dict[str, Any]:
        """Build and return the final query payload, excluding empty fields."""
        return {key: value for key, value in self.query.items() if value}
