from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from linkiq.model.db_client import DBClient
from rich import print

class Queue(BaseModel):
    model_config = {"populate_by_name": True}
    profile: str = Field(..., alias="PROFILE")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, alias="CREATED_AT")

    def add(self, db_client: DBClient):
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT OR IGNORE INTO {db_client.QUEUES_TABLE} (PROFILE, CREATED_AT)
                VALUES (?, ?);
            ''', (self.profile, self.created_at))
            conn.commit()
    
    def delete(self, db_client: DBClient) -> bool:
        """
        Delete the queue entry for this profile.
        Returns True if a row was deleted, False otherwise.
        """
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                DELETE FROM {db_client.QUEUES_TABLE}
                WHERE PROFILE = ?
            ''', (self.profile,))
            conn.commit()
            return cursor.rowcount > 0

    @classmethod
    def get(cls, db_client: DBClient, profile: str) -> Optional['Queue']:
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT PROFILE, CREATED_AT
                FROM {db_client.QUEUES_TABLE}
                WHERE PROFILE = ?
            ''', (profile,))
            row = cursor.fetchone()
            if row:
                return cls(profile=row[0], created_at=row[1])
            return None
    
    @classmethod
    def get_all(cls, db_client: DBClient) -> list['Queue']:
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT PROFILE, CREATED_AT
                FROM {db_client.QUEUES_TABLE}
            ''')
            return [cls(profile=row[0], created_at=row[1]) for row in cursor.fetchall()]
    
    @classmethod
    def get_oldest(cls, db_client: DBClient, limit: int = 10) -> list['Queue']:
        """
        Get the oldest `limit` profiles from the queue, sorted by CREATED_AT ascending (FIFO).
        """
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT PROFILE, CREATED_AT
                FROM {db_client.QUEUES_TABLE}
                ORDER BY CREATED_AT ASC
                LIMIT ?
            ''', (limit,))
            return [cls(profile=row[0], created_at=row[1]) for row in cursor.fetchall()]
    
    @classmethod
    def bulk_insert(cls, db_client: DBClient, profiles: list[str]):
        """
        Insert multiple profiles into the queue, ignoring duplicates.
        """
        if not profiles:
            return
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(f'''
                INSERT OR IGNORE INTO {db_client.QUEUES_TABLE} (PROFILE, CREATED_AT)
                VALUES (?, ?)
            ''', [(profile, datetime.now()) for profile in profiles])
            conn.commit()

