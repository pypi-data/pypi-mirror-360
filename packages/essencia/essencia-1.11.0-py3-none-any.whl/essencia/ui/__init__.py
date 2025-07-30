"""UI module for Essencia application."""

from .app import EssenciaApp
from .pages import HomePage, LoginPage, DashboardPage
from .components import Header, Footer, UserCard

# Import new layout components
from .layout import (
    AppBar,
    Panel as NewPanel,  # New enhanced Panel
    Grid as NewGrid,    # New enhanced Grid
    Dashboard,
    StyledMarkdown,
)

# Import new button components
from .buttons import (
    # Elevated buttons
    ThemedElevatedButton as NewThemedElevatedButton,
    PrimaryButton,
    SecondaryButton,
    ErrorButton,
    SuccessButton,
    WarningButton,
    InfoButton,
    # Outlined buttons
    ThemedOutlinedButton as NewThemedOutlinedButton,
    OutlinedPrimaryButton,
    OutlinedSecondaryButton,
    # Text buttons
    ThemedTextButton as NewThemedTextButton,
    LinkButton,
    # Icon buttons
    ThemedIconButton,
    ThemedFloatingActionButton as NewThemedFloatingActionButton,
    # Special buttons
    LoadingButton,
    ToggleButton,
    SplitButton,
    ButtonGroup as NewButtonGroup,
    ActionButton,
)

# Import new input components
from .inputs import (
    # Text inputs
    ThemedTextField as NewThemedTextField,
    PasswordField,
    SearchField,
    MultilineTextField,
    # Date/Time inputs
    ThemedDatePicker as NewThemedDatePicker,
    open_date_picker,
    DateRangePicker,
    ThemedTimePicker,
    # Selection inputs
    ThemedDropdown as NewThemedDropdown,
    ThemedAutocomplete,
    ThemedCheckbox as NewThemedCheckbox,
    ThemedSwitch as NewThemedSwitch,
    ThemedRadioGroup as NewThemedRadioGroup,
    RadioOption,
    # Numeric inputs
    ThemedSlider as NewThemedSlider,
    RangeSlider,
    # File inputs
    ThemedFilePicker,
    ImagePicker,
    # Color input
    ThemedColorPicker,
)

# Import theme components
from .themes import (
    # Theme-aware components
    ThemedComponent,
    ThemedContainer as NewThemedContainer,
    ThemedCard as NewThemedCard,
    ThemedText,
    ThemedDivider,
    apply_theme_to_control as new_apply_theme_to_control,
    get_theme_from_page,
    # Theme provider
    ThemeProvider,
    DefaultTheme,
    create_theme,
    apply_theme_to_page,
)

# Import new feedback components
from .feedback import (
    # Loading components
    LoadingIndicator,
    LoadingOverlay,
    LoadingWrapper,
    LoadingButton,
    SkeletonLoader,
    LazyLoadContainer,
    ProgressTracker,
    LoadingStyle,
    LoadingSize,
    # Notification components
    Toast,
    Snackbar,
    Alert,
    show_toast,
    show_snackbar,
    show_alert,
    NotificationType,
    NotificationPosition,
)

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
    
    # Loading indicators (from controls for backward compatibility)
    LoadingIndicator as ControlsLoadingIndicator,
    LoadingOverlay as ControlsLoadingOverlay,
    SkeletonLoader as ControlsSkeletonLoader,
    ProgressTracker as ControlsProgressTracker,
    
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
    
    # New layout components
    "AppBar",
    "Dashboard",
    "StyledMarkdown",
    "NewPanel",  # Enhanced Panel
    "NewGrid",   # Enhanced Grid
    
    # New button components - Elevated
    "NewThemedElevatedButton",
    "PrimaryButton",
    "SecondaryButton",
    "ErrorButton",
    "SuccessButton",
    "WarningButton",
    "InfoButton",
    
    # New button components - Outlined
    "NewThemedOutlinedButton",
    "OutlinedPrimaryButton",
    "OutlinedSecondaryButton",
    
    # New button components - Text
    "NewThemedTextButton",
    "LinkButton",
    
    # New button components - Icon
    "ThemedIconButton",
    "NewThemedFloatingActionButton",
    
    # New button components - Special
    "LoadingButton",
    "ToggleButton", 
    "SplitButton",
    "NewButtonGroup",
    "ActionButton",
    
    # New input components - Text
    "NewThemedTextField",
    "PasswordField",
    "SearchField",
    "MultilineTextField",
    
    # New input components - Date/Time
    "NewThemedDatePicker",
    "open_date_picker",
    "DateRangePicker",
    "ThemedTimePicker",
    
    # New input components - Selection
    "NewThemedDropdown",
    "ThemedAutocomplete",
    "NewThemedCheckbox",
    "NewThemedSwitch",
    "NewThemedRadioGroup",
    "RadioOption",
    
    # New input components - Numeric
    "NewThemedSlider",
    "RangeSlider",
    
    # New input components - File
    "ThemedFilePicker",
    "ImagePicker",
    
    # New input components - Color
    "ThemedColorPicker",
    
    # Theme components
    "ThemedComponent",
    "NewThemedContainer",
    "NewThemedCard", 
    "ThemedText",
    "ThemedDivider",
    "new_apply_theme_to_control",
    "get_theme_from_page",
    
    # Theme provider
    "ThemeProvider",
    "DefaultTheme",
    "create_theme",
    "apply_theme_to_page",
    
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
    
    # Loading indicators (new feedback module)
    "LoadingIndicator",
    "LoadingOverlay",
    "LoadingWrapper",
    "LoadingButton",
    "SkeletonLoader",
    "LazyLoadContainer",
    "ProgressTracker",
    "LoadingStyle",
    "LoadingSize",
    
    # Notification components
    "Toast",
    "Snackbar",
    "Alert",
    "show_toast",
    "show_snackbar",
    "show_alert",
    "NotificationType",
    "NotificationPosition",
    
    # Loading indicators (from controls - deprecated)
    "ControlsLoadingIndicator",
    "ControlsLoadingOverlay",
    "ControlsSkeletonLoader",
    "ControlsProgressTracker",
    
    # Button components
    "ThemedElevatedButton",
    "ThemedTextButton",
    "ThemedOutlinedButton",
    "ThemedFloatingActionButton",
    "ButtonGroup",
]