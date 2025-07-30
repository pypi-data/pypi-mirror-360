"""
Pagination components for data-driven interfaces.

Provides unified pagination system with multiple display modes,
responsive design, and integration with data providers.
"""

from .unified import (
    PaginationMode,
    PaginationConfig,
    PaginationDataProvider,
    UnifiedPagination,
    create_table_pagination,
    create_grid_pagination,
    create_list_pagination,
    create_mobile_pagination,
)

from .simple import (
    SimplePagination,
    CompactPagination,
    InfiniteScroll,
)

__all__ = [
    # Core pagination
    "PaginationMode",
    "PaginationConfig",
    "PaginationDataProvider",
    "UnifiedPagination",
    # Factory functions
    "create_table_pagination",
    "create_grid_pagination",
    "create_list_pagination",
    "create_mobile_pagination",
    # Simple pagination variants
    "SimplePagination",
    "CompactPagination",
    "InfiniteScroll",
]