"""
Mobile offline storage and synchronization.
"""
from typing import Optional, Dict, Any, List, Type, TypeVar
from datetime import datetime, timedelta
import json
import asyncio
from pathlib import Path
import aiofiles
from dataclasses import dataclass, asdict

from essencia.core import EssenciaError
from essencia.models import BaseModel

T = TypeVar('T', bound=BaseModel)


@dataclass
class SyncStatus:
    """Synchronization status."""
    last_sync: Optional[datetime] = None
    pending_changes: int = 0
    sync_errors: List[Dict[str, Any]] = None
    is_syncing: bool = False
    
    def __post_init__(self):
        if self.sync_errors is None:
            self.sync_errors = []


class OfflineStorage:
    """Offline storage manager for mobile apps."""
    
    def __init__(self, base_path: Path = Path.home() / ".essencia" / "mobile"):
        """Initialize offline storage."""
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Storage paths
        self.data_path = self.base_path / "data"
        self.queue_path = self.base_path / "queue"
        self.cache_path = self.base_path / "cache"
        
        # Create directories
        self.data_path.mkdir(exist_ok=True)
        self.queue_path.mkdir(exist_ok=True)
        self.cache_path.mkdir(exist_ok=True)
        
        # Sync status
        self.sync_status = SyncStatus()
    
    async def save(self, collection: str, document: BaseModel) -> str:
        """Save document to offline storage."""
        try:
            # Get document ID
            doc_id = str(document.id) if hasattr(document, 'id') else str(id(document))
            
            # Create collection directory
            collection_path = self.data_path / collection
            collection_path.mkdir(exist_ok=True)
            
            # Save document
            doc_path = collection_path / f"{doc_id}.json"
            async with aiofiles.open(doc_path, 'w') as f:
                await f.write(document.model_dump_json())
            
            # Add to sync queue
            await self._add_to_queue('create', collection, doc_id, document.model_dump())
            
            return doc_id
            
        except Exception as e:
            raise EssenciaError(f"Failed to save document: {str(e)}")
    
    async def update(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Update document in offline storage."""
        try:
            # Load existing document
            doc = await self.get(collection, doc_id)
            if not doc:
                raise EssenciaError(f"Document {doc_id} not found")
            
            # Update fields
            doc.update(data)
            
            # Save updated document
            collection_path = self.data_path / collection
            doc_path = collection_path / f"{doc_id}.json"
            async with aiofiles.open(doc_path, 'w') as f:
                await f.write(json.dumps(doc))
            
            # Add to sync queue
            await self._add_to_queue('update', collection, doc_id, data)
            
            return True
            
        except Exception as e:
            raise EssenciaError(f"Failed to update document: {str(e)}")
    
    async def delete(self, collection: str, doc_id: str) -> bool:
        """Delete document from offline storage."""
        try:
            # Delete document file
            collection_path = self.data_path / collection
            doc_path = collection_path / f"{doc_id}.json"
            if doc_path.exists():
                doc_path.unlink()
            
            # Add to sync queue
            await self._add_to_queue('delete', collection, doc_id, {})
            
            return True
            
        except Exception as e:
            raise EssenciaError(f"Failed to delete document: {str(e)}")
    
    async def get(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document from offline storage."""
        try:
            collection_path = self.data_path / collection
            doc_path = collection_path / f"{doc_id}.json"
            
            if not doc_path.exists():
                return None
            
            async with aiofiles.open(doc_path, 'r') as f:
                content = await f.read()
                return json.loads(content)
                
        except Exception as e:
            raise EssenciaError(f"Failed to get document: {str(e)}")
    
    async def query(
        self,
        collection: str,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Query documents from offline storage."""
        try:
            collection_path = self.data_path / collection
            if not collection_path.exists():
                return []
            
            documents = []
            
            # Load all documents
            for doc_path in collection_path.glob("*.json"):
                async with aiofiles.open(doc_path, 'r') as f:
                    content = await f.read()
                    doc = json.loads(content)
                    
                    # Apply filter
                    if filter:
                        match = all(
                            doc.get(key) == value
                            for key, value in filter.items()
                        )
                        if not match:
                            continue
                    
                    documents.append(doc)
            
            # Apply pagination
            return documents[skip:skip + limit]
            
        except Exception as e:
            raise EssenciaError(f"Failed to query documents: {str(e)}")
    
    async def _add_to_queue(
        self,
        operation: str,
        collection: str,
        doc_id: str,
        data: Dict[str, Any]
    ):
        """Add operation to sync queue."""
        queue_item = {
            "id": str(datetime.now().timestamp()),
            "operation": operation,
            "collection": collection,
            "doc_id": doc_id,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "attempts": 0
        }
        
        # Save to queue
        queue_file = self.queue_path / f"{queue_item['id']}.json"
        async with aiofiles.open(queue_file, 'w') as f:
            await f.write(json.dumps(queue_item))
        
        # Update sync status
        self.sync_status.pending_changes += 1
    
    async def get_sync_queue(self) -> List[Dict[str, Any]]:
        """Get pending sync operations."""
        queue_items = []
        
        for queue_file in sorted(self.queue_path.glob("*.json")):
            async with aiofiles.open(queue_file, 'r') as f:
                content = await f.read()
                queue_items.append(json.loads(content))
        
        return queue_items
    
    async def remove_from_queue(self, queue_id: str):
        """Remove item from sync queue."""
        queue_file = self.queue_path / f"{queue_id}.json"
        if queue_file.exists():
            queue_file.unlink()
            self.sync_status.pending_changes = max(0, self.sync_status.pending_changes - 1)
    
    async def cache_set(self, key: str, value: Any, ttl: int = 3600):
        """Set cache value."""
        cache_item = {
            "value": value,
            "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat()
        }
        
        cache_file = self.cache_path / f"{key}.json"
        async with aiofiles.open(cache_file, 'w') as f:
            await f.write(json.dumps(cache_item))
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get cache value."""
        cache_file = self.cache_path / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            async with aiofiles.open(cache_file, 'r') as f:
                content = await f.read()
                cache_item = json.loads(content)
            
            # Check expiration
            expires_at = datetime.fromisoformat(cache_item["expires_at"])
            if datetime.now() > expires_at:
                cache_file.unlink()
                return None
            
            return cache_item["value"]
            
        except Exception:
            return None
    
    async def clear_cache(self):
        """Clear all cache."""
        for cache_file in self.cache_path.glob("*.json"):
            cache_file.unlink()
    
    async def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information."""
        def get_dir_size(path: Path) -> int:
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        
        return {
            "data_size_bytes": get_dir_size(self.data_path),
            "queue_size_bytes": get_dir_size(self.queue_path),
            "cache_size_bytes": get_dir_size(self.cache_path),
            "total_size_bytes": get_dir_size(self.base_path),
            "sync_status": asdict(self.sync_status)
        }


class SyncManager:
    """Synchronization manager for offline data."""
    
    def __init__(
        self,
        storage: OfflineStorage,
        api_client: Optional[Any] = None,
        sync_interval: int = 300  # 5 minutes
    ):
        self.storage = storage
        self.api_client = api_client
        self.sync_interval = sync_interval
        self._sync_task: Optional[asyncio.Task] = None
    
    async def start_sync(self):
        """Start automatic synchronization."""
        if self._sync_task:
            return
        
        self._sync_task = asyncio.create_task(self._sync_loop())
    
    async def stop_sync(self):
        """Stop automatic synchronization."""
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
            self._sync_task = None
    
    async def sync_now(self) -> Dict[str, Any]:
        """Perform synchronization now."""
        if not self.api_client:
            return {"success": False, "error": "No API client configured"}
        
        if self.storage.sync_status.is_syncing:
            return {"success": False, "error": "Sync already in progress"}
        
        self.storage.sync_status.is_syncing = True
        results = {"success": True, "synced": 0, "failed": 0, "errors": []}
        
        try:
            # Get sync queue
            queue_items = await self.storage.get_sync_queue()
            
            for item in queue_items:
                try:
                    # Process based on operation
                    if item["operation"] == "create":
                        await self._sync_create(item)
                    elif item["operation"] == "update":
                        await self._sync_update(item)
                    elif item["operation"] == "delete":
                        await self._sync_delete(item)
                    
                    # Remove from queue on success
                    await self.storage.remove_from_queue(item["id"])
                    results["synced"] += 1
                    
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append({
                        "item": item,
                        "error": str(e)
                    })
                    
                    # Increment attempts
                    item["attempts"] += 1
                    if item["attempts"] >= 3:
                        # Move to dead letter queue
                        self.storage.sync_status.sync_errors.append({
                            "item": item,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        })
                        await self.storage.remove_from_queue(item["id"])
            
            # Update sync status
            self.storage.sync_status.last_sync = datetime.now()
            
        finally:
            self.storage.sync_status.is_syncing = False
        
        return results
    
    async def _sync_loop(self):
        """Synchronization loop."""
        while True:
            try:
                await asyncio.sleep(self.sync_interval)
                await self.sync_now()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Sync error: {e}")
    
    async def _sync_create(self, item: Dict[str, Any]):
        """Sync create operation."""
        # Implementation depends on API client
        pass
    
    async def _sync_update(self, item: Dict[str, Any]):
        """Sync update operation."""
        # Implementation depends on API client
        pass
    
    async def _sync_delete(self, item: Dict[str, Any]):
        """Sync delete operation."""
        # Implementation depends on API client
        pass