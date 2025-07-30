# Mobile App Development Guide

This guide covers building mobile applications with Essencia using Flet.

## Overview

Essencia provides a complete mobile app framework built on Flet (Flutter for Python), offering:

- Native mobile UI components
- Offline-first architecture
- Biometric authentication
- Push notifications
- Camera integration
- Deep linking
- Cross-platform support (iOS, Android)

## Quick Start

### Basic Mobile App

```python
from essencia.mobile import create_mobile_app, MobileConfig
import flet as ft

# Configure app
config = MobileConfig(
    app_name="My Health App",
    theme_mode=ft.ThemeMode.LIGHT,
    primary_color=ft.colors.TEAL,
    offline_mode=True,
    biometric_auth=True
)

# Create app
app = create_mobile_app(config)

# Run app
ft.app(
    target=app.create_app,
    view=ft.AppView.FLET_APP,
    port=8550
)
```

## Mobile Components

### Navigation

```python
from essencia.mobile import MobileNavigator, MobileRoute, BottomNavigation

# Define routes
routes = [
    MobileRoute(
        path="/home",
        builder=lambda: HomeScreen(),
        auth_required=True,
        title="Home",
        icon=ft.icons.HOME
    ),
    MobileRoute(
        path="/patients",
        builder=lambda: PatientScreen(),
        auth_required=True,
        title="Patients",
        icon=ft.icons.PEOPLE
    )
]

# Bottom navigation
bottom_nav = BottomNavigation(
    items=[
        ft.NavigationDestination(
            icon=ft.icons.HOME_OUTLINED,
            selected_icon=ft.icons.HOME,
            label="Home"
        ),
        ft.NavigationDestination(
            icon=ft.icons.PEOPLE_OUTLINE,
            selected_icon=ft.icons.PEOPLE,
            label="Patients"
        )
    ],
    on_change=handle_nav_change
)
```

### UI Components

```python
from essencia.mobile import (
    MobileHeader, MobileCard, MobileList,
    MobileForm, MobileButton, MobileDialog
)

# Header with actions
header = MobileHeader(
    title="Patients",
    subtitle="15 active",
    actions=[
        ft.IconButton(icon=ft.icons.SEARCH),
        ft.IconButton(icon=ft.icons.ADD)
    ]
)

# Card with interaction
card = MobileCard(
    title="Maria Silva",
    subtitle="Last visit: 2 days ago",
    leading=ft.Icon(ft.icons.PERSON),
    trailing=ft.Icon(ft.icons.CHEVRON_RIGHT),
    on_click=lambda e: navigate_to_patient("123")
)

# List with builder
patient_list = MobileList(
    data=patients,
    item_builder=build_patient_card,
    on_item_click=handle_patient_select,
    empty_message="No patients found"
)

# Form with validation
form = MobileForm(
    fields=[
        ft.TextField(label="Name", required=True),
        ft.TextField(label="Email", keyboard_type=ft.KeyboardType.EMAIL),
        ft.DatePicker(label="Birth Date")
    ],
    on_submit=handle_form_submit,
    submit_text="Save Patient"
)
```

## Screens

### Login Screen

```python
from essencia.mobile import LoginScreen

class CustomLoginScreen(LoginScreen):
    def build(self):
        # Customize login screen
        controls = super().build()
        
        # Add custom branding
        controls.insert(0, ft.Image(
            src="logo.png",
            width=200,
            height=100
        ))
        
        return controls
    
    def _handle_login(self, data):
        # Custom authentication
        if self.authenticate(data["email"], data["password"]):
            self.on_login_success(user_data)
        else:
            self._show_error("Invalid credentials")
```

### Patient Screen

```python
from essencia.mobile import BaseScreen, MobileSearchBar

class PatientDetailScreen(BaseScreen):
    def __init__(self, patient_id: str, **kwargs):
        self.patient_id = patient_id
        super().__init__(**kwargs)
    
    def build(self):
        patient = self.load_patient(self.patient_id)
        
        return [
            MobileHeader(
                title=patient.name,
                back_button=True,
                on_back=lambda: self.navigator.go_back()
            ),
            
            # Patient info card
            MobileCard(
                content=ft.Column([
                    ft.Text(f"Age: {patient.age}"),
                    ft.Text(f"CPF: {patient.cpf}"),
                    ft.Text(f"Phone: {patient.phone}")
                ])
            ),
            
            # Action buttons
            ft.Row([
                MobileButton(
                    text="New Appointment",
                    icon=ft.icons.CALENDAR_TODAY,
                    on_click=self.schedule_appointment
                ),
                MobileButton(
                    text="Medical History",
                    icon=ft.icons.HISTORY,
                    on_click=self.show_history
                )
            ])
        ]
```

## Offline Storage

### Setup Offline Storage

```python
from essencia.mobile import OfflineStorage, SyncManager

# Initialize storage
storage = OfflineStorage()

# Save patient offline
patient = Patient(name="João Silva", cpf="123.456.789-00")
doc_id = await storage.save("patients", patient)

# Query offline data
patients = await storage.query(
    "patients",
    filter={"active": True},
    limit=20
)

# Setup sync manager
sync_manager = SyncManager(
    storage=storage,
    api_client=api_client,
    sync_interval=300  # 5 minutes
)

# Start automatic sync
await sync_manager.start_sync()

# Manual sync
result = await sync_manager.sync_now()
print(f"Synced: {result['synced']}, Failed: {result['failed']}")
```

### Conflict Resolution

```python
class ConflictResolver:
    def resolve(self, local_doc, remote_doc):
        # Implement your conflict resolution strategy
        # Example: Last write wins
        if local_doc["updated_at"] > remote_doc["updated_at"]:
            return local_doc
        return remote_doc

sync_manager.conflict_resolver = ConflictResolver()
```

## Mobile Utilities

### Biometric Authentication

```python
from essencia.mobile.utils import BiometricAuth

# Check availability
if await BiometricAuth.is_available():
    # Authenticate
    authenticated = await BiometricAuth.authenticate(
        reason="Authenticate to view patient data"
    )
    
    if authenticated:
        show_sensitive_data()
    else:
        show_error("Authentication failed")
```

### Camera Integration

```python
from essencia.mobile.utils import MobileCamera

# Take photo
if await MobileCamera.request_permission():
    photo_path = await MobileCamera.take_photo()
    
    # Upload photo
    patient.photo = photo_path
    await save_patient(patient)

# Scan QR code
qr_content = await MobileCamera.scan_qr_code()
if qr_content:
    handle_qr_data(qr_content)
```

### Push Notifications

```python
from essencia.mobile.utils import MobileNotifications

# Request permission
if await MobileNotifications.request_permission():
    # Schedule appointment reminder
    await MobileNotifications.schedule_notification(
        title="Appointment Reminder",
        body="You have an appointment with Dr. Silva at 2:00 PM",
        scheduled_time=appointment_time - timedelta(hours=1)
    )
    
    # Show immediate notification
    await MobileNotifications.show_notification(
        title="New Message",
        body="Dr. Silva sent you a message",
        action_url="essencia://messages/123"
    )
```

### Deep Linking

```python
from essencia.mobile.utils import MobileDeepLinks

# Generate deep link
link = MobileDeepLinks.generate_deep_link(
    screen="patient",
    params={"id": "123", "tab": "history"}
)
# Result: essencia://app/patient?id=123&tab=history

# Handle deep link
def handle_deep_link(url: str):
    screen, params = MobileDeepLinks.parse_deep_link(url)
    
    if screen == "patient":
        navigator.navigate(f"/patients/{params['id']}")
    elif screen == "appointment":
        navigator.navigate(f"/appointments/{params['id']}")
```

## Platform-Specific Features

### iOS Features

```python
from essencia.mobile.utils import DeviceInfo

if DeviceInfo.get_platform() == "ios":
    # Use iOS-specific features
    page.theme = ft.Theme(
        page_transitions={
            "ios": ft.PageTransitionTheme.CUPERTINO
        }
    )
    
    # Face ID authentication
    if await BiometricAuth.get_biometric_type() == "face_id":
        show_face_id_prompt()
```

### Android Features

```python
if DeviceInfo.get_platform() == "android":
    # Material You dynamic colors
    page.theme = ft.Theme(
        use_material3=True,
        color_scheme_seed=ft.colors.TEAL
    )
    
    # Android-specific permissions
    permissions = [
        "android.permission.CAMERA",
        "android.permission.READ_EXTERNAL_STORAGE"
    ]
```

## Performance Optimization

### Lazy Loading

```python
class LazyListScreen(BaseScreen):
    def build(self):
        return [
            MobileHeader(title="Patients"),
            ft.ListView(
                controls=[],
                on_scroll_end=self.load_more,
                padding=ft.padding.only(bottom=80)
            )
        ]
    
    async def load_more(self, e):
        # Load next batch
        next_batch = await self.load_patients(
            skip=self.loaded_count,
            limit=20
        )
        
        # Add to list
        for patient in next_batch:
            e.control.controls.append(
                self.build_patient_card(patient)
            )
        
        self.loaded_count += len(next_batch)
        e.page.update()
```

### Image Caching

```python
from essencia.mobile import OfflineStorage

class ImageCache:
    def __init__(self, storage: OfflineStorage):
        self.storage = storage
    
    async def get_image(self, url: str) -> str:
        # Check cache
        cached = await self.storage.cache_get(f"img_{url}")
        if cached:
            return cached
        
        # Download and cache
        image_data = await download_image(url)
        local_path = await save_image_locally(image_data)
        
        # Cache for 7 days
        await self.storage.cache_set(
            f"img_{url}",
            local_path,
            ttl=7 * 24 * 3600
        )
        
        return local_path
```

## Testing Mobile Apps

### Unit Tests

```python
import pytest
from essencia.mobile import MobileApp, MobileConfig

@pytest.fixture
def mobile_app():
    config = MobileConfig(
        app_name="Test App",
        offline_mode=True
    )
    return MobileApp(config)

def test_navigation(mobile_app):
    # Test navigation
    mobile_app.navigator.navigate("/home")
    assert mobile_app.navigator.current_route == "/home"
    
    # Test back navigation
    mobile_app.navigator.navigate("/patients")
    mobile_app.navigator.go_back()
    assert mobile_app.navigator.current_route == "/home"
```

### Integration Tests

```python
async def test_offline_sync():
    storage = OfflineStorage()
    
    # Save offline
    patient = Patient(name="Test Patient")
    doc_id = await storage.save("patients", patient)
    
    # Verify in queue
    queue = await storage.get_sync_queue()
    assert len(queue) == 1
    assert queue[0]["operation"] == "create"
    
    # Sync
    sync_manager = SyncManager(storage, mock_api_client)
    result = await sync_manager.sync_now()
    
    assert result["synced"] == 1
    assert result["failed"] == 0
```

## Deployment

### Building for iOS

```bash
# Install Flet build tools
pip install flet[build]

# Build iOS app
flet build ios --name "Essencia Health" \
    --bundle-id "com.essencia.health" \
    --team-id "YOUR_TEAM_ID"
```

### Building for Android

```bash
# Build Android app
flet build android --name "Essencia Health" \
    --package "com.essencia.health" \
    --keystore "path/to/keystore.jks"
```

### Configuration

Create `flet.toml` for build configuration:

```toml
[project]
name = "Essencia Health"
description = "Medical management system"
version = "1.0.0"

[android]
package = "com.essencia.health"
min_sdk_version = 21
target_sdk_version = 33

[ios]
bundle_id = "com.essencia.health"
deployment_target = "12.0"

[permissions]
android = [
    "android.permission.CAMERA",
    "android.permission.INTERNET",
    "android.permission.USE_BIOMETRIC"
]
ios = [
    "NSCameraUsageDescription",
    "NSFaceIDUsageDescription"
]
```

## Best Practices

1. **Offline First**: Always design for offline usage
2. **Responsive Design**: Test on multiple screen sizes
3. **Performance**: Use lazy loading for large lists
4. **Security**: Enable biometric auth for sensitive data
5. **User Experience**: Follow platform design guidelines
6. **Error Handling**: Gracefully handle network failures
7. **Testing**: Test on real devices when possible

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Ensure all dependencies are installed
   - Check platform-specific requirements
   - Verify signing certificates

2. **Performance Issues**
   - Use virtual scrolling for long lists
   - Implement image caching
   - Minimize state updates

3. **Sync Conflicts**
   - Implement proper conflict resolution
   - Use optimistic UI updates
   - Handle network timeouts

## Further Resources

- [Flet Documentation](https://flet.dev)
- [Flutter Platform Channels](https://flutter.dev/docs/development/platform-integration/platform-channels)
- [Mobile Security Best Practices](https://owasp.org/www-project-mobile-top-10/)