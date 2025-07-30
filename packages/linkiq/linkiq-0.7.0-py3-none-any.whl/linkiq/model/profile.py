from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from linkiq.model.db_client import DBClient
from rich import print

class Profile(BaseModel):
    model_config = {"populate_by_name": True}
    url: str = Field(..., alias="URL")
    name: Optional[str] = Field(None, alias="NAME")
    connection_degree: Optional[str] = Field(None, alias="CONNECTION_DEGREE")
    company: Optional[str] = Field(None, alias="COMPANY")
    title: Optional[str] = Field(None, alias="TITLE")
    location: Optional[str] = Field(None, alias="LOCATION")
    about: Optional[str] = Field(None, alias="ABOUT")
    experience: Optional[str] = Field(None, alias="EXPERIENCE")
    interest_signal: int = Field(default=0, alias="INTEREST_SIGNAL")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, alias="CREATED_AT")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, alias="UPDATED_AT")

    def add(self, db_client):
        """Insert or update profile row."""
        # Update the updated_at timestamp for any modification
        self.updated_at = datetime.now()
                
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO {db_client.PROFILES_TABLE} (URL, NAME, CONNECTION_DEGREE, COMPANY, TITLE, LOCATION, ABOUT, EXPERIENCE, INTEREST_SIGNAL, CREATED_AT, UPDATED_AT)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(URL) DO UPDATE SET
                    NAME=excluded.NAME,
                    CONNECTION_DEGREE=excluded.CONNECTION_DEGREE,
                    COMPANY=excluded.COMPANY,
                    TITLE=excluded.TITLE,
                    LOCATION=excluded.LOCATION,
                    ABOUT=excluded.ABOUT,
                    EXPERIENCE=excluded.EXPERIENCE,
                    INTEREST_SIGNAL=excluded.INTEREST_SIGNAL,
                    UPDATED_AT=excluded.UPDATED_AT;
            ''', (self.url, self.name, self.connection_degree, self.company, self.title, self.location, self.about, self.experience, self.interest_signal, self.created_at, self.updated_at))
            conn.commit()

    @staticmethod
    def get(db_client: DBClient, url: str) -> Optional["Profile"]:
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT URL, NAME, CONNECTION_DEGREE, COMPANY, TITLE, LOCATION, ABOUT, EXPERIENCE, INTEREST_SIGNAL, CREATED_AT, UPDATED_AT
                FROM {db_client.PROFILES_TABLE}
                WHERE URL = ?;
            ''', (url,))
            row = cursor.fetchone()
            if row:
                # Create dictionary with proper field names (aliases)
                data = {
                    "URL": row[0],
                    "NAME": row[1],
                     "CONNECTION_DEGREE": row[2],
                    "COMPANY": row[3],
                    "TITLE": row[4],
                    "LOCATION": row[5],
                    "ABOUT": row[6],
                    "EXPERIENCE": row[7],
                    "INTEREST_SIGNAL": row[8],
                    "CREATED_AT": row[9],
                    "UPDATED_AT": row[10]
                }
                return Profile(**data)
            return None

    def delete(self, db_client: DBClient) -> bool:
        """Delete profile from database."""
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                DELETE FROM {db_client.PROFILES_TABLE}
                WHERE URL = ?;
            ''', (self.url,))
            conn.commit()
            return cursor.rowcount > 0