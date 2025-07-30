from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from linkiq.model.db_client import DBClient


class Lead(BaseModel):
    model_config = {"populate_by_name": True}
    id: Optional[int] = Field(None, alias="ID")
    campaign_name: str = Field(..., alias="CAMPAIGN_NAME")
    profile: str = Field(..., alias="PROFILE") 
    stage: str = Field(..., alias="STAGE")
    """
    stage can be CREATED, CONNECT_REQUEST_SENT, CONNECTED, FIRST_MESSAGE_SENT, DONE
    """
    created_at: Optional[datetime] = Field(default_factory=datetime.now, alias="CREATED_AT")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, alias="UPDATED_AT")
    score: Optional[int] = Field(None, alias="SCORE")
    reason: Optional[str] = Field(None, alias="REASON")

    def add(self, db_client: DBClient):
        """Insert or update lead row based on CAMPAIGN_NAME + PROFILE combination."""
        self.updated_at = datetime.now()
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO {db_client.LEADS_TABLE} (CAMPAIGN_NAME, PROFILE, STAGE, CREATED_AT, UPDATED_AT)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(CAMPAIGN_NAME, PROFILE) DO UPDATE SET
                    STAGE=excluded.STAGE,
                    UPDATED_AT=excluded.UPDATED_AT;
            ''', (self.campaign_name, self.profile, self.stage, self.created_at, self.updated_at))
            conn.commit()

    @classmethod
    def get(cls, db_client: DBClient, campaign_name: str, profile: str) -> Optional['Lead']:
        """Retrieve a lead by name and profile combination."""
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT ID, CAMPAIGN_NAME, PROFILE, STAGE, CREATED_AT, UPDATED_AT
                FROM {db_client.LEADS_TABLE}
                WHERE CAMPAIGN_NAME LIKE ? AND PROFILE LIKE ?
            ''', (campaign_name, profile))
            
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row[0],
                    campaign_name=row[1],
                    profile=row[2],
                    stage=row[3],
                    created_at=row[4],
                    updated_at=row[5]
                )
            return None

    @classmethod
    def get_filtered(
            cls,
            db_client: DBClient,
            campaign_name: Optional[str] = None,
            stage: Optional[str] = None,
            created_at_from: Optional[str] = None,
            created_at_to: Optional[str] = None,
            sort_field: Optional[str] = None,
            sort_direction: Optional[str] = "asc"
    ) -> list['Lead']:
        query = f'''
            SELECT ID, CAMPAIGN_NAME, PROFILE, STAGE, CREATED_AT, UPDATED_AT
            FROM {db_client.LEADS_TABLE}
            WHERE 1=1
        '''
        params = []

        if campaign_name:
            query += " AND CAMPAIGN_NAME LIKE ?"
            params.append(f"%{campaign_name}%")

        if stage:
            query += " AND STAGE = ?"
            params.append(stage)

        if created_at_from:
            query += " AND CREATED_AT >= ?"
            params.append(created_at_from)

        if created_at_to:
            query += " AND CREATED_AT <= ?"
            params.append(created_at_to)

        # Apply sorting (safe allowlist check)
        allowed_fields = {
            "ID", "CAMPAIGN_NAME", "PROFILE", "STAGE", "CREATED_AT", "UPDATED_AT"
        }
        if sort_field in allowed_fields:
            direction = "DESC" if sort_direction and sort_direction.lower() == "desc" else "ASC"
            query += f" ORDER BY {sort_field.upper()} {direction}"

        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        return [cls(
            id=row[0],
            campaign_name=row[1],
            profile=row[2],
            stage=row[3],
            created_at=row[4],
            updated_at=row[5]
        ) for row in rows]

    @classmethod
    def get_by_campaign_name(cls, db_client: DBClient, campaign_name: str) -> list['Lead']:
        """Retrieve all leads with a specific campaign_name (across different profiles)."""
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT ID, CAMPAIGN_NAME, PROFILE, STAGE, CREATED_AT, UPDATED_AT
                FROM {db_client.LEADS_TABLE}
                WHERE CAMPAIGN_NAME LIKE ?
            ''', (campaign_name,))
            
            rows = cursor.fetchall()
            return [cls(
                id=row[0],
                campaign_name=row[1],
                profile=row[2],
                stage=row[3],
                created_at=row[4],
                updated_at=row[5]
            ) for row in rows]

    @classmethod
    def get_by_profile(cls, db_client: DBClient, profile: str) -> list['Lead']:
        """Retrieve all leads for a specific profile."""
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT ID, CAMPAIGN_NAME, PROFILE, STAGE, CREATED_AT, UPDATED_AT
                FROM {db_client.LEADS_TABLE}
                WHERE PROFILE LIKE ?
            ''', (profile,))
            
            rows = cursor.fetchall()
            return [cls(
                id=row[0],
                campaign_name=row[1],
                profile=row[2],
                stage=row[3],
                created_at=row[4],
                updated_at=row[5]
            ) for row in rows]
    
    @classmethod
    def get_leads_for_outreach(cls, db_client: DBClient, stages: list[str], limit: Optional[int] = None) -> list['Lead']:
        """
        Retrieve leads with specified stages and optional limit.
        
        Args:
            db_client (DBClient): Database client for access.
            stages (list[str]): Required list of stages to filter on.
            limit (int, optional): Maximum number of leads to return.
        """
        if not stages:
            raise []

        with db_client._get_connection() as conn:
            cursor = conn.cursor()

            # Create placeholders for SQL IN clause
            placeholders = ','.join('?' for _ in stages)
            query = f'''
                SELECT ID, CAMPAIGN_NAME, PROFILE, STAGE, CREATED_AT, UPDATED_AT
                FROM {db_client.LEADS_TABLE}
                WHERE STAGE IN ({placeholders})
            '''
            params = list(stages)

            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [
                cls(
                    id=row[0],
                    campaign_name=row[1],
                    profile=row[2],
                    stage=row[3],
                    created_at=row[4],
                    updated_at=row[5]
                )
                for row in rows
            ]

    
    def delete(self, db_client: DBClient) -> bool:
        """Delete a lead by campaign_name and profile combination."""
        with db_client._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                DELETE FROM {db_client.LEADS_TABLE}
                WHERE CAMPAIGN_NAME = ? AND PROFILE = ?
            ''', (self.campaign_name, self.profile))
            
            rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected > 0
          