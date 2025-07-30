# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Essencia is a comprehensive Python application framework built with Flet (Flutter for Python) that provides a foundation for building secure medical and business applications. It features a dual sync/async architecture, field-level encryption, advanced service patterns, and a complete middleware system, with special focus on the Brazilian market and healthcare domain.

## Development Setup

This project uses Python 3.12+ and manages dependencies through pyproject.toml with uv as the package manager.

### Installing Dependencies

```bash
uv pip install -e .
```

### Running the Application

Since this is a Flet application, you'll typically run it as a Python module:

```bash
python -m essencia
```

## Project Structure

- `src/essencia/` - Main package directory
  - `cache/` - Intelligent caching system with Redis support
  - `core/` - Core functionality including configuration and exceptions
  - `database/` - Database connectivity (async Motor and sync PyMongo)
  - `fields/` - Custom Pydantic fields including encrypted fields
  - `integrations/` - Framework integrations
    - `flet/` - Flet-specific security adapters and components
  - `medical/` - Medical domain calculations (BMI, BSA, etc.)
  - `middleware/` - Comprehensive middleware framework
  - `models/` - Data models for various domains
    - `laboratory.py` - Lab test models and analyzer
    - `auth.py` - User authentication models
    - `financial.py` - Financial goal and projection models
    - `diagnosis.py` - ICD codes and diagnosis records
    - `appointment.py` - Appointment scheduling models
    - `notification.py` - Notification system models
  - `security/` - Comprehensive security features
  - `services/` - Service layer with patterns and protocols
  - `ui/` - Flet-based UI components
  - `utils/` - Utility functions and validators
    - `lab_importer.py` - CSV import for lab results

## Key Components

### Models
- **MongoModel**: Base model for sync MongoDB operations
- **BaseModel**: Base model for async MongoDB operations
- **Domain Models**: Specialized models for medical, financial, and operational domains
- **Laboratory Models**: LabTestType, LabTest, LabTestBatch for lab data management
- **Authentication Models**: User, Session with role-based permissions
- **Financial Models**: FinancialGoal, CashFlowProjection for financial planning
- **Medical Models**: ICDCode, DiagnosisRecord, Appointment, Notification
- Support for MongoId, ObjectReferenceId, and StrEnum types
- Comprehensive mixins for auditing, caching, and validation

### Database
- **MongoDB**: Async database operations using Motor
- **Database**: Sync database operations using PyMongo
- **RedisClient**: Redis integration for caching and sessions
- **Connection pooling** and automatic reconnection handling

### Security
- **Encryption**: Field-level encryption using AES-256-GCM
- **Sanitization**: HTML/Markdown sanitizers for XSS prevention
- **Session Management**: Secure session handling with CSRF protection
- **Authorization**: Role-based access control (RBAC) with permissions
- **Rate Limiting**: Multiple strategies (sliding window, token bucket, fixed window)
- **Query Validation**: NoSQL injection prevention for MongoDB
- **Key Management**: Cryptographic key lifecycle and rotation
- **Security Headers**: CSP, HSTS, and other web security headers
- **Audit Logging**: Comprehensive security event tracking
- **Input Validation**: Comprehensive validators for Brazilian data formats

### Services
- **Protocol-Based Architecture**: Uses Python protocols for flexibility
- **Repository Pattern**: Data access abstraction
- **Unit of Work**: Transaction management
- **Service Registry**: Dependency injection and service discovery
- **Enhanced Mixins**: Caching, auditing, validation, pagination
- **Decorators**: Cross-cutting concerns (retry, circuit breaker, rate limit)

### Middleware
- **Security Middleware**: Authentication, authorization, CSRF, CORS
- **Monitoring**: Metrics collection, distributed tracing, structured logging
- **Optimization**: Response caching, compression, rate limiting
- **Resilience**: Circuit breakers, retry logic, timeout handling

### Cache
- **IntelligentCache**: Smart caching with TTL management
- **AsyncCache**: Async caching operations
- **Specialized Caches**: Medical data, financial data, session management
- **Cache Warming**: Proactive cache population
- **Invalidation Strategies**: TTL, LRU, dependency-based

### UI Components

**Layout Components** (v1.10.0):
- **AppBar**: Customizable app bar with navigation and actions
- **Panel**: Styled containers with borders and elevation
- **Grid**: Responsive grid system with easy control management
- **Dashboard**: Multi-section layout (header, sidebar, body, footer)
- **StyledMarkdown**: Markdown renderer with theme-aware presets

**Button Components** (v1.10.0):
- **Elevated Buttons**: Primary, Secondary, Error, Success, Warning, Info
- **Outlined Buttons**: Border-styled variants for secondary actions
- **Text Buttons**: Minimal style for inline actions
- **Icon Buttons**: Icon-only buttons with theme integration
- **Special Buttons**: LoadingButton, ToggleButton, SplitButton, ButtonGroup

**Input Components**:
- **Themed Controls**: TextField, DatePicker, Dropdown with consistent styling
- **Form Builder**: Dynamic form generation with validation
- **Secure Forms**: Forms with built-in sanitization and validation

**Display Components**:
- **Dashboard Components**: Charts, metrics, KPIs
- **Data Tables**: Sortable, filterable with pagination
- **Timeline Components**: Vertical and horizontal timelines
- **Loading Indicators**: Consistent loading states
- **Lazy Loading**: Performance-optimized data widgets

### Validators
- **Brazilian Formats**: CPF, CNPJ, Phone, CEP
- **General**: Email, Date, Money, Password
- **Medical**: Patient data, prescriptions
- All validators provide helpful error messages in Portuguese

### Integrations
- **Flet Integration**: Complete security integration for Flet applications
  - FletRateLimiter: Rate limiting with page context
  - FletAuditLogger: Automatic audit logging
  - FletSessionManager: Session management
  - FletAuthorizationMiddleware: Permission checking
  - Secure Components: SecureButton, SecureTextField, AuditedForm
  - Decorators: @flet_rate_limit, @flet_audit, @flet_authorized

### Fields
- **Encrypted Fields**: CPF, RG, Medical Data, Financial Data, Lab Results
- **Default Fields**: Date/datetime with timezone support
- **Medical Fields**: Specialized encryption for healthcare data
- **Laboratory Fields**: Encrypted storage for test results
- **Computed Fields**: Automatic calculation and caching

## Architecture Patterns

1. **Protocol-Based Design**: Flexible contracts using Python protocols
2. **Repository Pattern**: Clean data access abstraction
3. **Unit of Work**: Atomic operations and transaction management
4. **Service Layer**: Business logic separation
5. **Middleware Chain**: Composable request/response processing
6. **Factory Pattern**: Service creation and dependency injection
7. **Decorator Pattern**: Method enhancement without modification
8. **Observer Pattern**: Event-driven architecture support

## Key Dependencies

- **Flet**: Cross-platform UI framework (Flutter for Python)
- **Motor**: Async MongoDB driver for Python
- **PyMongo**: Sync MongoDB driver
- **Pydantic**: Data validation using Python type annotations
- **Redis/aioredis**: In-memory data structure store
- **Cryptography**: Field-level encryption support
- **Unidecode**: Text normalization for search
- **httpx**: Async HTTP client
- **prometheus-client**: Metrics collection
- **structlog**: Structured logging

## Usage Examples

### Using Encrypted Fields
```python
from essencia.models import MongoModel
from essencia.fields import EncryptedCPF, EncryptedMedicalData

class Patient(MongoModel):
    name: str
    cpf: EncryptedCPF
    medical_history: EncryptedMedicalData
```

### Using Service Patterns
```python
from essencia.services import ServiceRegistry, Repository
from essencia.models import MongoModel

# Register services
registry = ServiceRegistry()
registry.register("patient_repo", PatientRepository())

# Use with Unit of Work
async with UnitOfWork() as uow:
    patient = await uow.patients.get(patient_id)
    patient.update_medical_record(new_data)
    await uow.commit()
```

### Using Middleware
```python
from essencia.middleware import MiddlewareStack, RateLimitMiddleware

middleware = MiddlewareStack()
middleware.add(RateLimitMiddleware(requests_per_minute=60))
middleware.add(AuthenticationMiddleware())
middleware.add(LoggingMiddleware())
```

### Using Medical Calculations
```python
from essencia.medical import calculate_bmi, calculate_bsa

bmi = calculate_bmi(weight_kg=70, height_cm=175)
bsa = calculate_bsa(weight_kg=70, height_cm=175, method="dubois")
```

### Using Laboratory System
```python
from essencia.models import LabTest, LabTestAnalyzer, LabTestType
from essencia.utils import LabCSVImporter

# Import lab results from CSV
importer = LabCSVImporter(patient_key="patient_123", doctor_key="dr_smith")
success_count, errors = importer.import_csv("lab_results.csv", laboratory="Lab Central")

# Analyze test trends
trend = LabTestAnalyzer.get_test_trend("patient_123", "Hemoglobina", limit=10)
print(f"Mean: {trend['mean']}, Trend: {trend['trend']}")

# Get abnormal results
abnormal = LabTestAnalyzer.get_abnormal_results("patient_123")

# Generate summary report
summary = LabTestAnalyzer.generate_summary_report("patient_123", days=365)
```

### Using Flet Integration
```python
from essencia.integrations.flet import (
    apply_security_to_page,
    SecureButton,
    flet_rate_limit,
    flet_audit,
    AuditedForm
)

def main(page: ft.Page):
    # Apply comprehensive security
    apply_security_to_page(page)
    
    # Use secure components
    @flet_audit("USER_ACTION")
    @flet_rate_limit(limit=5, window=60)
    def handle_click(e):
        print("Secure click!")
    
    secure_btn = SecureButton(
        text="Click Me",
        on_click=handle_click,
        required_permission="user_action"
    )
    
    # Create audited form
    form = AuditedForm(
        form_name="patient_form",
        controls=[
            SecureTextField(label="Name", sanitize=True),
            SecureTextField(label="CPF", pattern=r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
        ]
    )
    
    page.add(secure_btn, form)
```

## Environment Variables

- `ESSENCIA_ENCRYPTION_KEY`: Base64-encoded encryption key for field encryption
- `MONGODB_URL`: MongoDB connection string
- `REDIS_URL`: Redis connection string
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)
- `SESSION_SECRET`: Secret key for session encryption
- `RATE_LIMIT_ENABLED`: Enable/disable rate limiting

## Recent Major Updates

- **v1.10.0**: Added comprehensive UI component library (layout, buttons, theme-aware controls)
- **v1.9.0**: Added Flet integration module with security adapters and components
- **v1.8.0**: Added comprehensive security modules (query validation, key management, security headers)
- **v1.7.0**: Migrated models from clinic application (User, Financial, Diagnosis, Appointment)
- **v1.6.0**: Added Laboratory System with encrypted test results, CSV import, and trend analysis
- **v1.5.0**: Added comprehensive middleware framework with monitoring and resilience patterns
- **v1.4.0**: Introduced protocol-based service architecture with repository and UoW patterns
- **v1.3.0**: Added Flet UI components for rapid application development
- **v1.2.0**: Full async support with Motor integration
- Recent fixes for event loop handling and import errors

## Project Insights

- This is the core essencia package, designed as a foundation for medical and business applications
- Provides both sync and async patterns for flexible migration paths
- Security-first design suitable for healthcare applications and LGPD compliance
- Brazilian market focus with built-in validators and formatters
- Production-ready with monitoring, error handling, and resilience patterns
- Extensible architecture using protocols and dependency injection

## Best Practices

1. **Use async patterns** for high-performance applications
2. **Enable field encryption** for sensitive data (CPF, medical records)
3. **Implement proper error handling** using the provided exception hierarchy
4. **Use the service layer** for business logic, not in models
5. **Apply middleware** for cross-cutting concerns
6. **Leverage caching** for frequently accessed data
7. **Follow the protocol interfaces** for custom implementations

## Memories

- Keep the local CLAUDE.MD using only English
- The package now includes components transferred from the flet-app project
- Focus on making components generic and reusable across different applications
- Framework emphasizes security, performance, and Brazilian regulatory compliance
- Version 1.9.0 introduces Flet integration module for seamless security integration
- Security modules have been centralized from clinic application to essencia
- All imports from clinic.security should now use essencia.security