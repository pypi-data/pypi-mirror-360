from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from linkiq.model.db_client import DBClient
from rich import print

class Schedule(BaseModel):
    model_config = {"populate_by_name": True}
    task: str = Field(..., alias="TASK")
    last_run: Optional[datetime] = Field(None, alias="LAST_RUN")
    next_run: Optional[datetime] = Field(None, alias="NEXT_RUN")

    def add(self, db_client: DBClient):
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO {db_client.SCHEDULE_TABLE} (TASK, LAST_RUN, NEXT_RUN)
                VALUES (?, ?, ?)
                ON CONFLICT(TASK) DO UPDATE SET
                    LAST_RUN=excluded.LAST_RUN,
                    NEXT_RUN=excluded.NEXT_RUN;
            ''', (self.task, self.last_run, self.next_run))
            conn.commit()

    @classmethod
    def get(cls, db_client: DBClient, task: str) -> Optional['Schedule']:
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT TASK, LAST_RUN, NEXT_RUN
                FROM {db_client.SCHEDULE_TABLE}
                WHERE TASK = ?
            ''', (task,))
            row = cursor.fetchone()
            if row:
                return cls(task=row[0], last_run=row[1], next_run=row[2])
            return None
        
    @classmethod
    def get_due_tasks(cls, db_client: DBClient) -> List['Schedule']:
        """Fetch tasks from the DB where NEXT_RUN <= now."""
        now = datetime.now() # Use UTC to avoid timezone issues
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT TASK, LAST_RUN, NEXT_RUN
                FROM {db_client.SCHEDULE_TABLE}
                WHERE NEXT_RUN <= ?
            ''', (now,))
            rows = cursor.fetchall()
        return [cls(task=row[0], last_run=row[1], next_run=row[2]) for row in rows]
    
    @classmethod
    def is_table_empty(cls, db_client: DBClient) -> bool:
        """Check if the scheduler table is empty."""
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT 1 FROM {db_client.SCHEDULE_TABLE} LIMIT 1;")
            return cursor.fetchone() is None
    
    @classmethod
    def get_next_scheduled_time(cls, db_client: DBClient) -> Optional[datetime]:
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT MIN(NEXT_RUN)
                FROM {db_client.SCHEDULE_TABLE}
            ''')
            row = cursor.fetchone()
            if row and row[0] is not None:
                # parse including microseconds
                return datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
            return None


