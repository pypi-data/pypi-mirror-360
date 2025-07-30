"""
GraphQL module for Essencia framework.

Provides GraphQL API support with Strawberry GraphQL.
"""
from .schema import schema
from .context import GraphQLContext, get_context
from .app import create_graphql_app

__all__ = [
    "schema",
    "GraphQLContext",
    "get_context",
    "create_graphql_app"
]