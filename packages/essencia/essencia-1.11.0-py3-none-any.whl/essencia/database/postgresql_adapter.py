"""PostgreSQL adapter implementing the abstract database interface."""
from typing import Any, Dict, List, Optional, Type
import logging
import json
from datetime import datetime
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Integer, DateTime, JSON, select, update, delete, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.exc import IntegrityError, OperationalError
import uuid

from .abstract import AbstractDatabase, SyncAbstractDatabase, DatabaseConfig, QueryBuilder


logger = logging.getLogger(__name__)


class PostgreSQLQueryBuilder(QueryBuilder):
    """PostgreSQL-specific query builder using SQLAlchemy."""
    
    def __init__(self, table: Table):
        self.table = table
        self.query = select(table)
        self._where_clauses = []
        self._order_by_clauses = []
        self._limit_value = None
        self._offset_value = None
    
    def where(self, **kwargs) -> 'PostgreSQLQueryBuilder':
        """Add WHERE conditions."""
        for key, value in kwargs.items():
            if hasattr(self.table.c, key):
                self._where_clauses.append(getattr(self.table.c, key) == value)
        return self
    
    def order_by(self, field: str, desc: bool = False) -> 'PostgreSQLQueryBuilder':
        """Add ORDER BY clause."""
        if hasattr(self.table.c, field):
            column = getattr(self.table.c, field)
            if desc:
                column = column.desc()
            self._order_by_clauses.append(column)
        return self
    
    def limit(self, n: int) -> 'PostgreSQLQueryBuilder':
        """Add LIMIT clause."""
        self._limit_value = n
        return self
    
    def offset(self, n: int) -> 'PostgreSQLQueryBuilder':
        """Add OFFSET clause."""
        self._offset_value = n
        return self
    
    def build(self) -> Any:
        """Build the final query object."""
        query = self.query
        
        # Apply WHERE clauses
        for clause in self._where_clauses:
            query = query.where(clause)
        
        # Apply ORDER BY
        if self._order_by_clauses:
            query = query.order_by(*self._order_by_clauses)
        
        # Apply LIMIT and OFFSET
        if self._limit_value:
            query = query.limit(self._limit_value)
        if self._offset_value:
            query = query.offset(self._offset_value)
        
        return query


class PostgreSQLAdapter(AbstractDatabase):
    """Async PostgreSQL adapter using SQLAlchemy."""
    
    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self.engine: Optional[AsyncEngine] = None
        self.async_session_maker = None
        self.metadata = MetaData()
        self.tables: Dict[str, Table] = {}
    
    async def connect(self) -> None:
        """Establish PostgreSQL connection."""
        try:
            # Convert URL to async PostgreSQL URL
            url = self.config.url
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif not url.startswith("postgresql+asyncpg://"):
                url = f"postgresql+asyncpg://{url}"
            
            self.engine = create_async_engine(
                url,
                echo=self.config.options.get('echo', False),
                pool_pre_ping=True,
                pool_size=self.config.options.get('pool_size', 10),
                max_overflow=self.config.options.get('max_overflow', 20)
            )
            
            self.async_session_maker = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            
            logger.info(f"Connected to PostgreSQL: {self.config.database_name}")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Disconnected from PostgreSQL")
    
    async def is_connected(self) -> bool:
        """Check if PostgreSQL is connected."""
        if not self.engine:
            return False
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except:
            return False
    
    async def execute(self, query: Any, **kwargs) -> Any:
        """Execute a raw SQL query."""
        async with self.async_session_maker() as session:
            result = await session.execute(query, kwargs)
            await session.commit()
            return result
    
    def _get_or_create_table(self, collection: str) -> Table:
        """Get or create a table definition for a collection."""
        if collection not in self.tables:
            # Create a generic table structure
            table = Table(
                collection,
                self.metadata,
                Column('id', String, primary_key=True, default=lambda: str(uuid.uuid4())),
                Column('data', JSONB, nullable=False),
                Column('created_at', DateTime, default=datetime.utcnow),
                Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
                extend_existing=True
            )
            self.tables[collection] = table
        return self.tables[collection]
    
    async def _ensure_table_exists(self, collection: str):
        """Ensure table exists in database."""
        table = self._get_or_create_table(collection)
        async with self.engine.begin() as conn:
            await conn.run_sync(table.create, checkfirst=True)
    
    def _doc_to_row(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert document to PostgreSQL row format."""
        row_data = doc.copy()
        id_value = row_data.pop('id', row_data.pop('_id', str(uuid.uuid4())))
        
        return {
            'id': str(id_value),
            'data': row_data
        }
    
    def _row_to_doc(self, row: Any) -> Dict[str, Any]:
        """Convert PostgreSQL row to document format."""
        if hasattr(row, '_mapping'):
            # Row from query result
            doc = dict(row._mapping.get('data', {}))
            doc['id'] = row._mapping['id']
        else:
            # Dictionary row
            doc = dict(row.get('data', {}))
            doc['id'] = row['id']
        return doc
    
    async def find_one(self, collection: str, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document."""
        await self._ensure_table_exists(collection)
        table = self._get_or_create_table(collection)
        
        async with self.async_session_maker() as session:
            # Handle ID filter specially
            if 'id' in filter:
                query = select(table).where(table.c.id == str(filter['id']))
            else:
                # Use JSONB containment for other filters
                query = select(table).where(table.c.data.contains(filter))
            
            result = await session.execute(query.limit(1))
            row = result.first()
            
            if row:
                return self._row_to_doc(row)
            return None
    
    async def find_many(self, collection: str, filter: Dict[str, Any], 
                       limit: Optional[int] = None, skip: Optional[int] = None,
                       sort: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        """Find multiple documents."""
        await self._ensure_table_exists(collection)
        table = self._get_or_create_table(collection)
        
        async with self.async_session_maker() as session:
            # Build base query
            if 'id' in filter:
                query = select(table).where(table.c.id == str(filter['id']))
            elif filter:
                query = select(table).where(table.c.data.contains(filter))
            else:
                query = select(table)
            
            # Apply sorting
            if sort:
                for field, direction in sort:
                    if field == 'id':
                        col = table.c.id
                    else:
                        # Sort by JSONB field
                        col = table.c.data[field]
                    
                    if direction < 0:
                        col = col.desc()
                    query = query.order_by(col)
            
            # Apply pagination
            if skip:
                query = query.offset(skip)
            if limit:
                query = query.limit(limit)
            
            result = await session.execute(query)
            rows = result.fetchall()
            
            return [self._row_to_doc(row) for row in rows]
    
    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a single document and return its ID."""
        await self._ensure_table_exists(collection)
        table = self._get_or_create_table(collection)
        
        row_data = self._doc_to_row(document)
        
        async with self.async_session_maker() as session:
            stmt = table.insert().values(**row_data)
            await session.execute(stmt)
            await session.commit()
            return row_data['id']
    
    async def insert_many(self, collection: str, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents and return their IDs."""
        await self._ensure_table_exists(collection)
        table = self._get_or_create_table(collection)
        
        rows = [self._doc_to_row(doc) for doc in documents]
        ids = [row['id'] for row in rows]
        
        async with self.async_session_maker() as session:
            stmt = table.insert().values(rows)
            await session.execute(stmt)
            await session.commit()
            return ids
    
    async def update_one(self, collection: str, filter: Dict[str, Any], 
                        update: Dict[str, Any]) -> int:
        """Update a single document and return affected count."""
        await self._ensure_table_exists(collection)
        table = self._get_or_create_table(collection)
        
        async with self.async_session_maker() as session:
            # Build WHERE clause
            if 'id' in filter:
                where_clause = table.c.id == str(filter['id'])
            else:
                where_clause = table.c.data.contains(filter)
            
            # Get current document
            select_stmt = select(table).where(where_clause).limit(1)
            result = await session.execute(select_stmt)
            row = result.first()
            
            if not row:
                return 0
            
            # Merge update with existing data
            current_data = dict(row._mapping['data'])
            
            # Handle MongoDB-style update operators
            if '$set' in update:
                current_data.update(update['$set'])
            else:
                current_data.update(update)
            
            # Update the row
            update_stmt = (
                table.update()
                .where(table.c.id == row._mapping['id'])
                .values(data=current_data, updated_at=datetime.utcnow())
            )
            
            await session.execute(update_stmt)
            await session.commit()
            return 1
    
    async def update_many(self, collection: str, filter: Dict[str, Any], 
                         update: Dict[str, Any]) -> int:
        """Update multiple documents and return affected count."""
        await self._ensure_table_exists(collection)
        table = self._get_or_create_table(collection)
        
        async with self.async_session_maker() as session:
            # Build WHERE clause
            if 'id' in filter:
                where_clause = table.c.id == str(filter['id'])
            elif filter:
                where_clause = table.c.data.contains(filter)
            else:
                where_clause = True
            
            # Get all matching documents
            select_stmt = select(table).where(where_clause)
            result = await session.execute(select_stmt)
            rows = result.fetchall()
            
            if not rows:
                return 0
            
            # Update each row
            count = 0
            for row in rows:
                current_data = dict(row._mapping['data'])
                
                # Handle MongoDB-style update operators
                if '$set' in update:
                    current_data.update(update['$set'])
                else:
                    current_data.update(update)
                
                update_stmt = (
                    table.update()
                    .where(table.c.id == row._mapping['id'])
                    .values(data=current_data, updated_at=datetime.utcnow())
                )
                
                await session.execute(update_stmt)
                count += 1
            
            await session.commit()
            return count
    
    async def delete_one(self, collection: str, filter: Dict[str, Any]) -> int:
        """Delete a single document and return affected count."""
        await self._ensure_table_exists(collection)
        table = self._get_or_create_table(collection)
        
        async with self.async_session_maker() as session:
            # Build WHERE clause
            if 'id' in filter:
                where_clause = table.c.id == str(filter['id'])
            else:
                # Find matching document first
                select_stmt = select(table.c.id).where(table.c.data.contains(filter)).limit(1)
                result = await session.execute(select_stmt)
                row = result.first()
                if not row:
                    return 0
                where_clause = table.c.id == row[0]
            
            # Delete the row
            delete_stmt = delete(table).where(where_clause)
            result = await session.execute(delete_stmt)
            await session.commit()
            return result.rowcount
    
    async def delete_many(self, collection: str, filter: Dict[str, Any]) -> int:
        """Delete multiple documents and return affected count."""
        await self._ensure_table_exists(collection)
        table = self._get_or_create_table(collection)
        
        async with self.async_session_maker() as session:
            # Build WHERE clause
            if 'id' in filter:
                where_clause = table.c.id == str(filter['id'])
            elif filter:
                where_clause = table.c.data.contains(filter)
            else:
                where_clause = True
            
            # Delete rows
            delete_stmt = delete(table).where(where_clause)
            result = await session.execute(delete_stmt)
            await session.commit()
            return result.rowcount
    
    async def count(self, collection: str, filter: Dict[str, Any]) -> int:
        """Count documents matching filter."""
        await self._ensure_table_exists(collection)
        table = self._get_or_create_table(collection)
        
        async with self.async_session_maker() as session:
            # Build WHERE clause
            if 'id' in filter:
                where_clause = table.c.id == str(filter['id'])
            elif filter:
                where_clause = table.c.data.contains(filter)
            else:
                where_clause = True
            
            # Count rows
            count_stmt = select(func.count()).select_from(table).where(where_clause)
            result = await session.execute(count_stmt)
            return result.scalar()
    
    async def create_index(self, collection: str, keys: List[tuple], unique: bool = False) -> None:
        """Create an index on the collection."""
        # PostgreSQL automatically indexes primary keys
        # For JSONB fields, we'd need GIN indexes which require more complex handling
        logger.info(f"Index creation on JSONB fields not implemented yet for collection: {collection}")
    
    def get_query_builder(self) -> QueryBuilder:
        """Get a PostgreSQL query builder."""
        # This would need the table name, so we'll return a generic one
        return PostgreSQLQueryBuilder(Table('dummy', self.metadata))
    
    @asynccontextmanager
    async def transaction(self):
        """Context manager for database transactions."""
        async with self.async_session_maker() as session:
            async with session.begin():
                yield session