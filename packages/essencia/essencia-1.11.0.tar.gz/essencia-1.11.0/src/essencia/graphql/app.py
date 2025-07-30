"""
GraphQL application setup for Essencia.
"""
from typing import Optional

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL

from .schema import schema
from .context import get_context


def create_graphql_app(
    app: FastAPI,
    path: str = "/graphql",
    settings: Optional[Any] = None
) -> FastAPI:
    """
    Add GraphQL endpoint to FastAPI app.
    
    Args:
        app: FastAPI application
        path: GraphQL endpoint path
        settings: Application settings
        
    Returns:
        FastAPI app with GraphQL endpoint
    """
    if not settings:
        settings = app.state.settings
    
    # Create GraphQL router
    graphql_router = GraphQLRouter(
        schema,
        path=path,
        context_getter=lambda request: get_context(request, settings),
        subscription_protocols=[
            GRAPHQL_TRANSPORT_WS_PROTOCOL,
            GRAPHQL_WS_PROTOCOL,
        ],
        graphiql=True,  # Enable GraphiQL interface
    )
    
    # Include router
    app.include_router(graphql_router, prefix="")
    
    # Add to OpenAPI
    app.openapi_tags.append({
        "name": "graphql",
        "description": "GraphQL endpoint for advanced queries"
    })
    
    return app


# Example usage in main app
def create_app_with_graphql():
    """Create app with both REST and GraphQL APIs."""
    from essencia.api import create_app
    
    # Create REST API app
    app = create_app()
    
    # Add GraphQL
    app = create_graphql_app(app)
    
    return app


from typing import Any