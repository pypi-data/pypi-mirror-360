"""UI module for Essencia application."""

from .app import EssenciaApp
from .pages import HomePage, LoginPage, DashboardPage
from .components import Header, Footer, UserCard

# Import all controls
from .controls import (
    # Base classes and configuration
    ControlConfig,
    ThemedControl,
    DataProvider,
    SecurityProvider,
    ThemeProvider,
    EssenciaControlsConfig,
    configure_controls,
    get_controls_config,
    
    # Input components
    ThemedTextField,
    ThemedDatePicker,
    ThemedDropdown,
    ThemedCheckbox,
    ThemedRadioGroup,
    ThemedSlider,
    ThemedSwitch,
    open_themed_date_picker,
    
    # Form components
    FieldType,
    ValidationRule,
    FieldValidation,
    FormField,
    FormConfig,
    FormBuilder,
    SecureForm,
    CommonValidators,
    ValidationResult,
    
    # Pagination components
    PaginationMode,
    PaginationConfig,
    PaginationDataProvider,
    UnifiedPagination,
    create_table_pagination,
    create_grid_pagination,
    create_list_pagination,
    
    # Lazy loading components
    LazyLoadWidget,
    LazyDataWidget,
    LazyStatsWidget,
    LazyListWidget,
    LazyGridWidget,
    AsyncDataProvider,
    
    # Dashboard components
    DashboardConfig,
    StatCard,
    QuickAction,
    BaseDashboard,
    SyncDashboard,
    AsyncDashboard,
    create_stats_dashboard,
    create_admin_dashboard,
    
    # Theme-aware components
    ThemedComponent,
    ThemedContainer,
    ThemedCard,
    ThemedAppBar,
    ThemedNavigationRail,
    ThemedDataTable,
    apply_theme_to_control,
    
    # Layout components
    Panel,
    Section,
    Grid,
    FlexLayout,
    TabLayout,
    SplitView,
    ResponsiveLayout,
    
    # Timeline components
    TimelineConfig,
    TimelineItem,
    TimelineOrientation,
    BaseTimeline,
    VerticalTimeline,
    HorizontalTimeline,
    
    # Loading indicators
    LoadingIndicator,
    LoadingOverlay,
    SkeletonLoader,
    ProgressTracker,
    
    # Button components
    ThemedElevatedButton,
    ThemedTextButton,
    ThemedOutlinedButton,
    ThemedFloatingActionButton,
    ButtonGroup,
)

__all__ = [
    # App and pages
    "EssenciaApp",
    "HomePage",
    "LoginPage", 
    "DashboardPage",
    "Header",
    "Footer",
    "UserCard",
    
    # Base classes and configuration
    "ControlConfig",
    "ThemedControl",
    "DataProvider",
    "SecurityProvider",
    "ThemeProvider",
    "EssenciaControlsConfig",
    "configure_controls",
    "get_controls_config",
    
    # Input components
    "ThemedTextField",
    "ThemedDatePicker",
    "ThemedDropdown",
    "ThemedCheckbox",
    "ThemedRadioGroup",
    "ThemedSlider",
    "ThemedSwitch",
    "open_themed_date_picker",
    
    # Form components
    "FieldType",
    "ValidationRule",
    "FieldValidation",
    "FormField",
    "FormConfig",
    "FormBuilder",
    "SecureForm",
    "CommonValidators",
    "ValidationResult",
    
    # Pagination components
    "PaginationMode",
    "PaginationConfig",
    "PaginationDataProvider",
    "UnifiedPagination",
    "create_table_pagination",
    "create_grid_pagination",
    "create_list_pagination",
    
    # Lazy loading components
    "LazyLoadWidget",
    "LazyDataWidget",
    "LazyStatsWidget",
    "LazyListWidget",
    "LazyGridWidget",
    "AsyncDataProvider",
    
    # Dashboard components
    "DashboardConfig",
    "StatCard",
    "QuickAction",
    "BaseDashboard",
    "SyncDashboard",
    "AsyncDashboard",
    "create_stats_dashboard",
    "create_admin_dashboard",
    
    # Theme-aware components
    "ThemedComponent",
    "ThemedContainer",
    "ThemedCard",
    "ThemedAppBar",
    "ThemedNavigationRail",
    "ThemedDataTable",
    "apply_theme_to_control",
    
    # Layout components
    "Panel",
    "Section",
    "Grid",
    "FlexLayout",
    "TabLayout",
    "SplitView",
    "ResponsiveLayout",
    
    # Timeline components
    "TimelineConfig",
    "TimelineItem",
    "TimelineOrientation",
    "BaseTimeline",
    "VerticalTimeline",
    "HorizontalTimeline",
    
    # Loading indicators
    "LoadingIndicator",
    "LoadingOverlay",
    "SkeletonLoader",
    "ProgressTracker",
    
    # Button components
    "ThemedElevatedButton",
    "ThemedTextButton",
    "ThemedOutlinedButton",
    "ThemedFloatingActionButton",
    "ButtonGroup",
]