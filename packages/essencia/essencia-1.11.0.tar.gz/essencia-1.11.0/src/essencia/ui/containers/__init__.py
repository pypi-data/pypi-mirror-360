"""
Container components for building complex layouts.

Provides dashboard, card, and other container components for
organizing content in Flet applications.
"""

from .dashboard_base import (
    BaseDashboard,
    SyncDashboard,
    AsyncDashboard,
    DashboardConfig,
    StatCard,
    QuickAction,
    create_stats_dashboard,
    create_admin_dashboard,
)

__all__ = [
    "BaseDashboard",
    "SyncDashboard", 
    "AsyncDashboard",
    "DashboardConfig",
    "StatCard",
    "QuickAction",
    "create_stats_dashboard",
    "create_admin_dashboard",
]