"""
Integration tests for MongoDB operations.
"""
import pytest
from datetime import datetime

from essencia.models import MongoModel, BaseModel
from essencia.database import Database, AsyncDatabase
from tests.fixtures.factories import create_test_user, create_test_patient


class TestUser(MongoModel):
    """Test user model."""
    username: str
    email: str
    is_active: bool = True
    created_at: datetime = None
    
    class Settings:
        collection_name = "test_users"


class TestAsyncUser(BaseModel):
    """Test async user model."""
    username: str
    email: str
    is_active: bool = True
    created_at: datetime = None
    
    class Settings:
        collection_name = "test_async_users"


class TestMongoDBSync:
    """Test synchronous MongoDB operations."""
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_model_save_and_find(self, sync_db):
        """Test saving and finding a model."""
        # Set the database for MongoModel
        MongoModel.set_db(sync_db)
        
        # Create and save user
        user = TestUser(
            username="testuser",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        saved_user = user.save()
        
        assert saved_user.id is not None
        assert saved_user.username == "testuser"
        
        # Find user
        found_user = TestUser.find_one({"username": "testuser"})
        assert found_user is not None
        assert found_user.id == saved_user.id
        assert found_user.email == "test@example.com"
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_model_update(self, sync_db):
        """Test updating a model."""
        MongoModel.set_db(sync_db)
        
        # Create user
        user = TestUser(
            username="updateuser",
            email="update@example.com"
        ).save()
        
        # Update user
        user.email = "newemail@example.com"
        user.is_active = False
        updated_user = user.save()
        
        # Verify update
        found_user = TestUser.find_by_id(user.id)
        assert found_user.email == "newemail@example.com"
        assert found_user.is_active is False
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_model_delete(self, sync_db):
        """Test deleting a model."""
        MongoModel.set_db(sync_db)
        
        # Create user
        user = TestUser(
            username="deleteuser",
            email="delete@example.com"
        ).save()
        
        user_id = user.id
        
        # Delete user
        user.delete()
        
        # Verify deletion
        found_user = TestUser.find_by_id(user_id)
        assert found_user is None
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_find_many(self, sync_db):
        """Test finding multiple models."""
        MongoModel.set_db(sync_db)
        
        # Create multiple users
        for i in range(5):
            TestUser(
                username=f"user{i}",
                email=f"user{i}@example.com",
                is_active=i % 2 == 0
            ).save()
        
        # Find all users
        all_users = TestUser.find_many({})
        assert len(all_users) >= 5
        
        # Find active users
        active_users = TestUser.find_many({"is_active": True})
        assert len(active_users) >= 3
        
        # Find with limit
        limited_users = TestUser.find_many({}, limit=2)
        assert len(limited_users) == 2
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_count_documents(self, sync_db):
        """Test counting documents."""
        MongoModel.set_db(sync_db)
        
        # Create users
        for i in range(3):
            TestUser(
                username=f"countuser{i}",
                email=f"count{i}@example.com"
            ).save()
        
        # Count all
        total_count = TestUser.count_documents({})
        assert total_count >= 3
        
        # Count with filter
        count = TestUser.count_documents({"username": {"$regex": "^countuser"}})
        assert count == 3


@pytest.mark.asyncio
class TestMongoDBAsync:
    """Test asynchronous MongoDB operations."""
    
    @pytest.mark.integration
    @pytest.mark.database
    async def test_async_save_and_find(self, async_db):
        """Test async saving and finding a model."""
        # Set the database for BaseModel
        BaseModel.set_db(async_db)
        
        # Create and save user
        user = TestAsyncUser(
            username="asyncuser",
            email="async@example.com",
            created_at=datetime.utcnow()
        )
        saved_user = await user.save()
        
        assert saved_user.id is not None
        assert saved_user.username == "asyncuser"
        
        # Find user
        found_user = await TestAsyncUser.find_one({"username": "asyncuser"})
        assert found_user is not None
        assert found_user.id == saved_user.id
        assert found_user.email == "async@example.com"
    
    @pytest.mark.integration
    @pytest.mark.database
    async def test_async_update(self, async_db):
        """Test async updating a model."""
        BaseModel.set_db(async_db)
        
        # Create user
        user = await TestAsyncUser(
            username="asyncupdate",
            email="asyncupdate@example.com"
        ).save()
        
        # Update user
        user.email = "newasyncemail@example.com"
        user.is_active = False
        updated_user = await user.save()
        
        # Verify update
        found_user = await TestAsyncUser.find_by_id(user.id)
        assert found_user.email == "newasyncemail@example.com"
        assert found_user.is_active is False
    
    @pytest.mark.integration
    @pytest.mark.database
    async def test_async_delete(self, async_db):
        """Test async deleting a model."""
        BaseModel.set_db(async_db)
        
        # Create user
        user = await TestAsyncUser(
            username="asyncdelete",
            email="asyncdelete@example.com"
        ).save()
        
        user_id = user.id
        
        # Delete user
        await user.delete()
        
        # Verify deletion
        found_user = await TestAsyncUser.find_by_id(user_id)
        assert found_user is None
    
    @pytest.mark.integration
    @pytest.mark.database
    async def test_async_find_many(self, async_db):
        """Test async finding multiple models."""
        BaseModel.set_db(async_db)
        
        # Create multiple users
        for i in range(5):
            await TestAsyncUser(
                username=f"asyncuser{i}",
                email=f"asyncuser{i}@example.com",
                is_active=i % 2 == 0
            ).save()
        
        # Find all users
        all_users = await TestAsyncUser.find_many({})
        assert len(all_users) >= 5
        
        # Find active users
        active_users = await TestAsyncUser.find_many({"is_active": True})
        assert len(active_users) >= 3
        
        # Find with limit
        limited_users = await TestAsyncUser.find_many({}, limit=2)
        assert len(limited_users) == 2
    
    @pytest.mark.integration
    @pytest.mark.database
    async def test_async_aggregation(self, async_db):
        """Test async aggregation pipeline."""
        BaseModel.set_db(async_db)
        
        # Create users with different domains
        domains = ["gmail.com", "yahoo.com", "gmail.com", "outlook.com", "gmail.com"]
        for i, domain in enumerate(domains):
            await TestAsyncUser(
                username=f"agguser{i}",
                email=f"agguser{i}@{domain}"
            ).save()
        
        # Aggregate by email domain
        pipeline = [
            {"$match": {"username": {"$regex": "^agguser"}}},
            {"$group": {
                "_id": {"$substr": ["$email", {"$indexOfBytes": ["$email", "@"]}, -1]},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        results = await TestAsyncUser.aggregate(pipeline)
        assert len(results) > 0
        
        # Gmail should have the most users
        assert results[0]["_id"] == "@gmail.com"
        assert results[0]["count"] == 3