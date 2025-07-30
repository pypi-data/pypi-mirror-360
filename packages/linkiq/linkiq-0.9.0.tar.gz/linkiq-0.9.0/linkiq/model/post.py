from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from linkiq.model.db_client import DBClient

class Post(BaseModel):
    model_config = {"populate_by_name": True}
    url: str = Field(..., alias="URL")
    last_scanned_at: Optional[datetime] = Field(None, alias="LAST_SCANNED_AT")
    scanned_count: int = Field(0, alias="SCANNED_COUNT")
    age: int = Field(0, alias="AGE")

    def add(self, db_client: DBClient):
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO {db_client.POSTS_TABLE} (URL, LAST_SCANNED_AT, SCANNED_COUNT, AGE)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(URL) DO UPDATE SET
                    LAST_SCANNED_AT=excluded.LAST_SCANNED_AT,
                    SCANNED_COUNT=excluded.SCANNED_COUNT,
                    AGE=excluded.AGE;
            ''', (self.url, self.last_scanned_at, self.scanned_count, self.age))
            conn.commit()

    @classmethod
    def get(cls, db_client: DBClient, url: str) -> Optional['Post']:
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT URL, LAST_SCANNED_AT, SCANNED_COUNT, AGE
                FROM {db_client.POSTS_TABLE}
                WHERE URL = ?
            ''', (url,))
            row = cursor.fetchone()
            if row:
                return cls(url=row[0], last_scanned_at=row[1], scanned_count=row[2], age=row[3])
            return None

    @classmethod
    def bulk_insert_if_new(cls, db_client: DBClient, posts: List[Dict[str, str]]):
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            inserted = 0
            for post in posts:
                url = post["url"]
                age = post["age"]

                cursor.execute(f'''
                    INSERT OR IGNORE INTO {db_client.POSTS_TABLE} (URL, LAST_SCANNED_AT, SCANNED_COUNT, AGE)
                    VALUES (?, ?, ?, ?)
                ''', (url, None, 0, age))
                
                if cursor.rowcount > 0:
                    inserted += 1

            conn.commit()
        print(f"[green]Inserted {inserted} new posts.[/green]")
    
    @classmethod
    def get_unscanned_by_max_age(cls, db_client: DBClient, max_age: str) -> List['Post']:
        """
        Get all posts where SCANNED_COUNT = 0 and AGE < max_age.
        Note: AGE is stored as a string like "3d", "2w", "1mo", etc.
        This query filters lexically, so ensure max_age format is consistent.
        """
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT URL, LAST_SCANNED_AT, SCANNED_COUNT, AGE
                FROM {db_client.POSTS_TABLE}
                WHERE SCANNED_COUNT = 0 AND AGE < ?
            ''', (max_age,))
            rows = cursor.fetchall()

            return [
                cls(url=row[0], last_scanned_at=row[1], scanned_count=row[2], age=row[3])
                for row in rows
            ]

    @classmethod
    def get_all(cls, db_client: DBClient) -> List['Post']:
        """
        Get all posts.
        """
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT URL, LAST_SCANNED_AT, SCANNED_COUNT, AGE
                FROM {db_client.POSTS_TABLE}
            ''')
            rows = cursor.fetchall()

            return [
                cls(url=row[0], last_scanned_at=row[1], scanned_count=row[2], age=row[3])
                for row in rows
            ]