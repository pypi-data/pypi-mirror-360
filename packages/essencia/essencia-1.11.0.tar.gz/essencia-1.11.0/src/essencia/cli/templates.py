"""
Code templates for CLI generation.
"""

MODEL_TEMPLATE = '''"""
{name} model definition.
"""
{imports}


class {name}(MongoModel):
    """{name} model."""
    
{fields}
    
    class Settings:
        collection_name = "{collection_name}"
        indexes = [
            # Add indexes here
        ]
'''

SERVICE_TEMPLATE = '''"""
{name} service implementation.
"""
from typing import List, Optional, Dict, Any
from essencia.services import Repository, ServiceResult, ServiceError
from ..models.{model_lower} import {model}


class {model}Repository(Repository[{model}]):
    """Repository for {model} data access."""
    
    model_class = {model}
    
    # Add custom query methods here
    async def find_by_name(self, name: str) -> Optional[{model}]:
        """Find {model_lower} by name."""
        return await self.find_one({{"name": name}})


class {name}:
    """Service for {model} operations."""
    
    def __init__(self, repository: {model}Repository):
        self.repository = repository
    
    async def create_{model_lower}(self, data: Dict[str, Any]) -> ServiceResult[{model}]:
        """Create a new {model_lower}."""
        try:
            # Validate data
            {model_lower} = {model}(**data)
            
            # Check for duplicates
            existing = await self.repository.find_by_name({model_lower}.name)
            if existing:
                return ServiceResult.failure("{model} with this name already exists")
            
            # Save
            saved = await self.repository.create({model_lower})
            return ServiceResult.success(saved)
            
        except Exception as e:
            return ServiceResult.failure(str(e))
    
    async def get_{model_lower}(self, {model_lower}_id: str) -> ServiceResult[{model}]:
        """Get a {model_lower} by ID."""
        {model_lower} = await self.repository.get({model_lower}_id)
        if not {model_lower}:
            return ServiceResult.failure("{model} not found")
        return ServiceResult.success({model_lower})
    
    async def update_{model_lower}(
        self, 
        {model_lower}_id: str, 
        data: Dict[str, Any]
    ) -> ServiceResult[{model}]:
        """Update a {model_lower}."""
        {model_lower} = await self.repository.get({model_lower}_id)
        if not {model_lower}:
            return ServiceResult.failure("{model} not found")
        
        # Update fields
        for key, value in data.items():
            if hasattr({model_lower}, key):
                setattr({model_lower}, key, value)
        
        # Save
        updated = await self.repository.update({model_lower})
        return ServiceResult.success(updated)
    
    async def delete_{model_lower}(self, {model_lower}_id: str) -> ServiceResult[bool]:
        """Delete a {model_lower}."""
        {model_lower} = await self.repository.get({model_lower}_id)
        if not {model_lower}:
            return ServiceResult.failure("{model} not found")
        
        await self.repository.delete({model_lower}_id)
        return ServiceResult.success(True)
    
    async def list_{model_lower}s(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> ServiceResult[List[{model}]]:
        """List {model_lower}s with pagination."""
        filters = filters or {{}}
        {model_lower}s = await self.repository.find_many(filters, skip=skip, limit=limit)
        return ServiceResult.success({model_lower}s)
'''

UI_COMPONENT_TEMPLATE = '''"""
{name} UI component.
"""
from typing import Optional, Callable, Dict, Any
import flet as ft
from essencia.ui.themes import ColorScheme


class {name}(ft.UserControl):
    """{name} component."""
    
    def __init__(
        self,
        on_submit: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        
    def build(self):
        """Build the component."""
        # Form fields
        self.name_field = ft.TextField(
            label="Name",
            width=300,
            autofocus=True
        )
        
        self.description_field = ft.TextField(
            label="Description",
            width=300,
            multiline=True,
            min_lines=3
        )
        
        # Buttons
        submit_button = ft.ElevatedButton(
            "Submit",
            icon=ft.icons.CHECK,
            on_click=self._handle_submit,
            bgcolor=ColorScheme.PRIMARY,
            color=ft.colors.WHITE
        )
        
        cancel_button = ft.OutlinedButton(
            "Cancel",
            icon=ft.icons.CLOSE,
            on_click=self._handle_cancel
        )
        
        # Layout
        return ft.Container(
            content=ft.Column([
                ft.Text("{name}", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20),
                self.name_field,
                self.description_field,
                ft.Row([
                    submit_button,
                    cancel_button
                ], spacing=10)
            ], spacing=10),
            padding=20,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=10
        )
    
    def _handle_submit(self, e):
        """Handle form submission."""
        if self.on_submit:
            data = {{
                "name": self.name_field.value,
                "description": self.description_field.value
            }}
            self.on_submit(data)
    
    def _handle_cancel(self, e):
        """Handle cancellation."""
        if self.on_cancel:
            self.on_cancel()
    
    def clear(self):
        """Clear form fields."""
        self.name_field.value = ""
        self.description_field.value = ""
        self.update()
    
    def set_data(self, data: Dict[str, Any]):
        """Set form data."""
        self.name_field.value = data.get("name", "")
        self.description_field.value = data.get("description", "")
        self.update()
'''

TEST_TEMPLATE = '''"""
Tests for {name} model.
"""
import pytest
from datetime import datetime
from {module_path} import {name}


class Test{name}:
    """Test {name} model."""
    
    @pytest.mark.unit
    def test_create_{name}_minimal(self):
        """Test creating {name} with minimal fields."""
        {name_lower} = {name}(
            # Add required fields here
        )
        
        assert {name_lower} is not None
        # Add more assertions
    
    @pytest.mark.unit
    def test_create_{name}_complete(self):
        """Test creating {name} with all fields."""
        {name_lower} = {name}(
            # Add all fields here
        )
        
        assert {name_lower} is not None
        # Add more assertions
    
    @pytest.mark.unit
    def test_{name}_validation(self):
        """Test {name} field validation."""
        # Test invalid data
        with pytest.raises(Exception):
            {name_lower} = {name}(
                # Add invalid data
            )
    
    @pytest.mark.integration
    @pytest.mark.database
    async def test_{name}_save(self, async_db):
        """Test saving {name} to database."""
        {name}.set_db(async_db)
        
        {name_lower} = {name}(
            # Add fields
        )
        
        saved = await {name_lower}.save()
        assert saved.id is not None
        
        # Verify in database
        found = await {name}.find_by_id(saved.id)
        assert found is not None
'''

API_TEMPLATE = '''"""
API endpoints for {resource}.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from essencia.models import {model}
from essencia.services import {service}
from ..dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/{resource_lower}",
    tags=["{resource}"]
)


@router.get("/", response_model=List[{model}])
async def list_{resource_lower}(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List {resource_lower} with pagination."""
    service = {service}(db)
    result = await service.list_{resource_lower}(skip=skip, limit=limit)
    
    if result.is_success:
        return result.data
    else:
        raise HTTPException(status_code=400, detail=result.error)


@router.get("/{{{resource_lower}_id}}", response_model={model})
async def get_{resource_lower}(
    {resource_lower}_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific {resource_lower}."""
    service = {service}(db)
    result = await service.get_{resource_lower}({resource_lower}_id)
    
    if result.is_success:
        return result.data
    else:
        raise HTTPException(status_code=404, detail=result.error)


@router.post("/", response_model={model}, status_code=201)
async def create_{resource_lower}(
    data: {model}Create,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new {resource_lower}."""
    service = {service}(db)
    result = await service.create_{resource_lower}(data.dict())
    
    if result.is_success:
        return result.data
    else:
        raise HTTPException(status_code=400, detail=result.error)


@router.put("/{{{resource_lower}_id}}", response_model={model})
async def update_{resource_lower}(
    {resource_lower}_id: str,
    data: {model}Update,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a {resource_lower}."""
    service = {service}(db)
    result = await service.update_{resource_lower}(
        {resource_lower}_id,
        data.dict(exclude_unset=True)
    )
    
    if result.is_success:
        return result.data
    else:
        raise HTTPException(status_code=400, detail=result.error)


@router.delete("/{{{resource_lower}_id}}", status_code=204)
async def delete_{resource_lower}(
    {resource_lower}_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a {resource_lower}."""
    service = {service}(db)
    result = await service.delete_{resource_lower}({resource_lower}_id)
    
    if not result.is_success:
        raise HTTPException(status_code=400, detail=result.error)
'''