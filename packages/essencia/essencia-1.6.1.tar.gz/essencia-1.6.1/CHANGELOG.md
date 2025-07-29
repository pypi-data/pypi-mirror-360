# Changelog

## [1.6.1] - 2025-01-30

### Added
- **Laboratory System**: Complete lab test data management
  - `LabTestType`: Catalog of test types with reference ranges
  - `LabTest`: Individual test results with encrypted storage
  - `LabTestBatch`: Import tracking and auditing
  - `LabTestAnalyzer`: Trend analysis and reporting utilities
  - `LabCSVImporter`: CSV import with format normalization
  - `EncryptedLabResults`: New encrypted field type for lab data
- **Analysis Features**:
  - Patient test history with filtering
  - Trend analysis with statistical calculations
  - Abnormal result detection
  - Category-based test grouping
  - Comprehensive summary reports
- **Documentation**:
  - Laboratory system guide
  - Example usage scripts
  - API documentation updates

### Enhanced
- Updated README.md with laboratory system information
- Enhanced CLAUDE.md with technical details
- Added documentation index

## [1.6.0] - 2025-01-04

### Added
- **Web Module**: `essencia.web` - Complete FastAPI integration
  - **App Factory**: `create_app()` and `create_flet_app()` for rapid application setup
  - **API Configuration**: `FastAPIConfig` and `APISettings` for standardized configuration
  - **Dependencies**: Pre-built dependency injection functions
    - `get_db()`, `get_async_db()`: Database connections
    - `get_cache()`: Cache instance
    - `get_current_user()`: Current user from JWT
    - `require_auth()`, `require_role()`: Authentication/authorization
  - **Routers**:
    - `BaseRouter`: Foundation for API endpoints
    - `CRUDRouter`: Full CRUD operations with pagination
    - `AuthRouter`: Authentication endpoints (login, logout, refresh)
  - **WebSocket Support**:
    - `WebSocketManager`: WebSocket connection management
    - `ConnectionManager`: Multi-client connection handling
  - **Security Integration**:
    - JWT token creation and verification
    - OAuth2 with cookie support
    - Built-in CORS, rate limiting, and security headers

### Added - Medical Module
- **Medical Calculations**: `essencia.medical`
  - BMI (Body Mass Index) calculation
  - BSA (Body Surface Area) with multiple methods (DuBois, Mosteller, Boyd, Gehan-George)
  - Age calculation utilities
  - Medical-specific validators and formatters

### Enhanced
- **Updated CLAUDE.md**: Comprehensive documentation reflecting v1.6.0 architecture
  - Added middleware framework documentation
  - Protocol-based service patterns
  - Medical module usage examples
  - Best practices guide
  - Environment variables reference

### Technical Improvements
- Complete FastAPI integration for building REST APIs
- WebSocket support for real-time features
- Medical domain calculations for healthcare applications
- Enhanced documentation and examples

## [1.5.0] - 2025-01-04

### Added
- **Comprehensive Middleware Framework**: `essencia.middleware`
  - **Base Infrastructure**:
    - `Middleware` protocol and `BaseMiddleware` class
    - `MiddlewareChain` for composing middleware
    - `Request` and `Response` objects
    - `CompositeMiddleware` for combining middleware
  - **Monitoring Middleware**:
    - `MetricsMiddleware`: Request metrics and performance tracking
    - `TracingMiddleware`: Distributed tracing support
    - `LoggingMiddleware`: Structured request/response logging
    - `HealthCheckMiddleware`: Health and readiness endpoints
    - `PerformanceMiddleware`: Slow request detection
  - **Security Middleware**:
    - `AuthenticationMiddleware`: Request authentication
    - `AuthorizationMiddleware`: Role and permission checks
    - `CSRFMiddleware`: CSRF protection
    - `CORSMiddleware`: Cross-origin resource sharing
    - `SecurityHeadersMiddleware`: Security headers (CSP, HSTS, etc.)
  - **Optimization Middleware**:
    - `CacheMiddleware`: Response caching with TTL
    - `CompressionMiddleware`: Gzip compression
    - `RateLimitMiddleware`: Token bucket rate limiting
    - `CircuitBreakerMiddleware`: Circuit breaker pattern
    - `RetryMiddleware`: Automatic retry with backoff
  - **Error Handling**:
    - `ErrorHandlerMiddleware`: Comprehensive error handling
    - `ValidationMiddleware`: Input validation
    - `SanitizationMiddleware`: Input sanitization
    - `ExceptionMapperMiddleware`: Exception to HTTP mapping

### Enhanced Security Module
- **Security Patterns**: `essencia.security.patterns`
  - `SecurityMonitor`: Real-time threat detection
  - `PasswordPolicy`: Password complexity enforcement
  - `SecureTokenGenerator`: Secure token generation
  - `SecurityHeaders`: Security header configurations
  - `security_monitor_decorator`: Security event monitoring

### Features
- **Composable Architecture**: Chain middleware in any order
- **Async-First Design**: All middleware supports async operations
- **Performance Optimized**: Minimal overhead, smart caching
- **Security by Default**: Built-in protections against common attacks
- **Monitoring Ready**: Metrics, tracing, and logging built-in
- **Resilience Patterns**: Circuit breakers, retries, rate limiting

### Technical Details
- Located in `essencia.middleware` package
- Protocol-based design for extensibility
- Full async/await support
- Compatible with any Python web framework
- Comprehensive error handling and recovery

## [1.4.0] - 2025-01-04

### Added
- **Comprehensive Services Framework**: `essencia.services`
  - **Base Service Pattern**: Protocol-based service architecture with async/sync support
  - **Service Configuration**: Flexible configuration system with retry, caching, and timeout settings
  - **Service Result Pattern**: Standardized result wrapper for consistent error handling
  - **Advanced Mixins**:
    - `CacheMixin`: Smart caching with key generation and invalidation patterns
    - `AuditMixin`: Complete audit trail integration
    - `ValidationMixin`: Field validation including CPF, email, phone
    - `PaginationMixin`: Standardized pagination helpers
    - `SearchMixin`: MongoDB search query builders
    - `ExportMixin`: Data export to CSV, JSON, and dict formats
  - **Decorators**:
    - `@service_method`: Method logging and timing
    - `@cached`: Intelligent caching with TTL
    - `@audited`: Automatic audit trail creation
    - `@authorized`: Role and permission checks
    - `@validated`: Input validation with schemas
    - `@transactional`: Transaction management with retries
  - **Architectural Patterns**:
    - `RepositoryPattern`: Generic CRUD repository
    - `UnitOfWork`: Transaction management across repositories
    - `ServiceRegistry`: Service discovery and lifecycle management
    - `ServiceFactory`: Dependency injection support

### Features
- **Protocol-Based Design**: All components use Python protocols for maximum flexibility
- **Dual Async/Sync Support**: Services can operate in both modes seamlessly
- **Built-in Error Handling**: Retry logic, circuit breakers, and graceful degradation
- **Health Checks**: Standard health check interface for all services
- **Dependency Injection**: ServiceFactory supports automatic dependency resolution
- **Transaction Support**: Full transaction support with rollback capabilities
- **Monitoring Ready**: Built-in logging, metrics, and timing

### Technical Details
- Located in `essencia.services` package
- Maintains backward compatibility with existing services
- Full type hints and async support throughout
- Designed for microservices and monolithic architectures

## [1.3.0] - 2025-01-04

### Added
- **Comprehensive UI Controls Module**: `essencia.ui.controls`
  - **Input Components**: ThemedTextField, ThemedDatePicker, ThemedDropdown, ThemedCheckbox, ThemedRadioGroup, ThemedSlider, ThemedSwitch
  - **Form Framework**: FormBuilder with declarative API, field validation, security features (CSRF, sanitization)
  - **Data Display**: UnifiedPagination with table/grid/list modes, LazyLoadWidget for async data
  - **Dashboard System**: BaseDashboard, AsyncDashboard with stats cards, quick actions, auto-refresh
  - **Layout Components**: Panel, Section, Grid, FlexLayout, TabLayout, SplitView, ResponsiveLayout
  - **Timeline Components**: VerticalTimeline, HorizontalTimeline with customizable items
  - **Loading Indicators**: LoadingIndicator, LoadingOverlay, SkeletonLoader, ProgressTracker
  - **Button Components**: Full set of themed buttons with consistent styling

### Features
- **Theme System**: All components are theme-aware with configurable providers
- **Data Provider Pattern**: Abstract data loading for pagination and lazy components
- **Security Integration**: Forms support CSRF protection and input sanitization
- **Responsive Design**: Components adapt to different screen sizes
- **Async Support**: Built-in support for async data loading and operations
- **Internationalization Ready**: Configurable locale and format settings

### Technical Details
- Located in `essencia.ui.controls` package
- Follows Protocol-based design for extensibility
- Fully typed with comprehensive type hints
- Compatible with Flet 0.28.3+

## [1.2.0] - 2025-01-04

### Added
- **AsyncModelMixin**: Full async support for all MongoDB operations
  - Async methods: `afind()`, `afind_one()`, `afind_by_key()`, `asave()`, `aupdate()`, `adelete()`
  - Bulk operations: `abulk_create()`, `abulk_update()`
  - Pagination: `afind_paginated()`
  - Aggregation: `aaggregate()`
  - Transactions: `AsyncTransactionContext`
- **AsyncMongoDB**: Async database driver using Motor
  - Full async MongoDB operations
  - Connection pooling and optimization
  - Transaction support
- **async_cache_result**: Decorator for caching async function results
- All MongoModel subclasses now inherit AsyncModelMixin automatically

### Changed
- MongoModel now inherits from both BaseModel and AsyncModelMixin
- Added motor to core dependencies (previously only in optional)

### Technical Details
- Located in `essencia.models.async_models` and `essencia.database.async_mongodb`
- Compatible with existing sync operations (no breaking changes)
- Follows the same API pattern as sync methods with 'a' prefix

## [1.1.1] - 2025-01-04

### Fixed
- Fixed aioredis compatibility issue with Python 3.12+ by disabling aioredis imports for PyInstaller compatibility
- Fixed missing `date` import in medical.py module
- Fixed incorrect AsyncCache import in main __init__.py (changed to AsyncCacheManager)
- All modules now import successfully without the `TypeError: duplicate base class TimeoutError` error

### Changed
- Disabled aioredis in rate_limiter.py and async_cache.py with appropriate warning messages
- These changes maintain backward compatibility while allowing the package to work with modern Python versions

## [1.1.0] - Previous release
- Initial release of the essencia framework