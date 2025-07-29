"""
Essencia UI Controls Module

This module provides a comprehensive set of reusable UI components for Flet applications.
It includes form builders, themed inputs, pagination, lazy loading, and dashboard components.

All components are theme-aware and can be configured with custom providers for:
- Theme management
- Data access
- Security features
- Internationalization
"""

from .base import (
    # Base classes and protocols
    ControlConfig,
    ThemedControl,
    DataProvider,
    SecurityProvider,
    ThemeProvider,
    EssenciaControlsConfig,
    configure_controls,
    get_controls_config,
)

from .inputs import (
    # Themed input components
    ThemedTextField,
    ThemedDatePicker,
    ThemedDropdown,
    ThemedCheckbox,
    ThemedRadioGroup,
    ThemedSlider,
    ThemedSwitch,
    open_themed_date_picker,
)

from .forms import (
    # Form building system
    FieldType,
    ValidationRule,
    FieldValidation,
    FormField,
    FormConfig,
    FormBuilder,
    SecureForm,
    # Validators
    CommonValidators,
    ValidationResult,
)

from .pagination import (
    # Pagination components
    PaginationMode,
    PaginationConfig,
    PaginationDataProvider,
    UnifiedPagination,
    create_table_pagination,
    create_grid_pagination,
    create_list_pagination,
)

from .lazy import (
    # Lazy loading components
    LazyLoadWidget,
    LazyDataWidget,
    LazyStatsWidget,
    LazyListWidget,
    LazyGridWidget,
    AsyncDataProvider,
)

from .dashboard import (
    # Dashboard components
    DashboardConfig,
    StatCard,
    QuickAction,
    BaseDashboard,
    SyncDashboard,
    AsyncDashboard,
    create_stats_dashboard,
    create_admin_dashboard,
)

from .theme import (
    # Theme-aware components
    ThemedComponent,
    ThemedContainer,
    ThemedCard,
    ThemedAppBar,
    ThemedNavigationRail,
    ThemedDataTable,
    apply_theme_to_control,
)

from .layout import (
    # Layout components
    Panel,
    Section,
    Grid,
    FlexLayout,
    TabLayout,
    SplitView,
    ResponsiveLayout,
)

from .timeline import (
    # Timeline components
    TimelineConfig,
    TimelineItem,
    TimelineOrientation,
    BaseTimeline,
    VerticalTimeline,
    HorizontalTimeline,
)

from .loading import (
    # Loading indicators
    LoadingIndicator,
    LoadingOverlay,
    SkeletonLoader,
    ProgressTracker,
)

from .buttons import (
    # Button components
    ThemedElevatedButton,
    ThemedTextButton,
    ThemedOutlinedButton,
    ThemedIconButton,
    ThemedFloatingActionButton,
    ButtonGroup,
)

__all__ = [
    # Base
    "ControlConfig",
    "ThemedControl",
    "DataProvider",
    "SecurityProvider",
    "ThemeProvider",
    "EssenciaControlsConfig",
    "configure_controls",
    "get_controls_config",
    
    # Inputs
    "ThemedTextField",
    "ThemedDatePicker",
    "ThemedDropdown",
    "ThemedCheckbox",
    "ThemedRadioGroup",
    "ThemedSlider",
    "ThemedSwitch",
    "open_themed_date_picker",
    
    # Forms
    "FieldType",
    "ValidationRule",
    "FieldValidation",
    "FormField",
    "FormConfig",
    "FormBuilder",
    "SecureForm",
    "CommonValidators",
    "ValidationResult",
    
    # Pagination
    "PaginationMode",
    "PaginationConfig",
    "PaginationDataProvider",
    "UnifiedPagination",
    "create_table_pagination",
    "create_grid_pagination",
    "create_list_pagination",
    
    # Lazy Loading
    "LazyLoadWidget",
    "LazyDataWidget",
    "LazyStatsWidget",
    "LazyListWidget",
    "LazyGridWidget",
    "AsyncDataProvider",
    
    # Dashboard
    "DashboardConfig",
    "StatCard",
    "QuickAction",
    "BaseDashboard",
    "SyncDashboard",
    "AsyncDashboard",
    "create_stats_dashboard",
    "create_admin_dashboard",
    
    # Theme Components
    "ThemedComponent",
    "ThemedContainer",
    "ThemedCard",
    "ThemedAppBar",
    "ThemedNavigationRail",
    "ThemedDataTable",
    "apply_theme_to_control",
    
    # Layout
    "Panel",
    "Section",
    "Grid",
    "FlexLayout",
    "TabLayout",
    "SplitView",
    "ResponsiveLayout",
    
    # Timeline
    "TimelineConfig",
    "TimelineItem",
    "TimelineOrientation",
    "BaseTimeline",
    "VerticalTimeline",
    "HorizontalTimeline",
    
    # Loading
    "LoadingIndicator",
    "LoadingOverlay",
    "SkeletonLoader",
    "ProgressTracker",
    
    # Buttons
    "ThemedElevatedButton",
    "ThemedTextButton",
    "ThemedOutlinedButton",
    "ThemedIconButton",
    "ThemedFloatingActionButton",
    "ButtonGroup",
]