
from typing import List, Tuple, Optional
from pydantic import BaseModel, Field
import os
import json
from typing import List, Dict, Any
from pathlib import Path
from rich import print
from linkiq.model.profile import Profile
from linkiq.model.lead import Lead
from datetime import datetime
from linkiq.model.db_client import DBClient
    
class Campaign(BaseModel):
    name: str = Field(..., description="Unique name for the campaign")
    
    include_keywords: Optional[List[str]] = Field(default_factory=list, description="Keywords required in a profile")
    exclude_keywords: Optional[List[str]] = Field(default_factory=list, description="Keywords that disqualify a profile")
    
    ideal_persona: Optional[str] = Field("", description="Prompt to evaluate a lead's quality")
    lead_score_threshold: Optional[int] = Field(0, ge=0, le=100, description="Minimum score required to consider a lead qualified")
    
    model_provider: Optional[str] = Field("", description="Model provider openai, anthropic, or grok.")
    model: Optional[str] = Field("", description="Model name to use")

    connect_message: Optional[str] = Field("", description="Message sent with the connection request")
    first_message: Optional[str] = Field("", description="First message after connection is accepted")
    subject_line: Optional[str] = Field("", description="First message subject line")
    follow_up: Optional[str] = Field("", description="Follow-up message if no reply after first message")

    def lead_score(self, profile: Profile) -> Tuple[int, str]:
        """
        Returns a score between 0 and 100 representing how well the profile fits this campaign.
        And a reason for the score
        """
        text_fields = f"{profile.name or ''} {profile.title or ''} {profile.company or ''}".lower()
        reason = ""
        # 0. If no filters or scoring criteria are set, treat all leads as minimally qualified
        if (
            not self.exclude_keywords and
            not self.include_keywords and
            not self.ideal_persona
        ):
            return 100, "No lead scoring criteria is set. Default score is 100."

        # 1. Check exclusion
        for keyword in self.exclude_keywords:
            if keyword.lower() in text_fields:
                return 0, f"Exclude keyword {keyword} found in name, title, or company"

        # 2. Compute keyword match score
        match_count = 0
        total_keywords = len(self.include_keywords)
        for keyword in self.include_keywords:
            if keyword.lower() in text_fields:
                reason += f"Include keyword {keyword} found in name, title, or company\n" 
                match_count += 1

        keyword_score = 100
        if total_keywords > 0:
            keyword_score = int((match_count / total_keywords) * 100)
            reason += f" Found {match_count} keywords in include_keywords\n"
        else:
            reason += " No include_keywords set. Default score is 100. \n"

        # 3. AI scoring (optional - not implemented yet)
        # You could add OpenAI or Claude-based scoring using self.ideal_persona here

        return keyword_score, reason


class CampaignHandler:
    def __init__(self, campaign_dir: str = None):
        # Resolve campaign directory path with fallbacks
        resolved_path = (
            campaign_dir
            or os.environ.get("CAMPAIGN_DIR")
            or "~/.linkiq/campaigns"
        )
        self.campaign_path = Path(os.path.expanduser(resolved_path)).resolve()

        # Ensure directory exists
        self.campaign_path.mkdir(parents=True, exist_ok=True)

        self.campaigns: List[Campaign] = []
        self._load_campaigns()

    def _load_campaigns(self):
        for file in self.campaign_path.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"[yellow]Skipping invalid JSON file:[/yellow] {file} ({e})")
                continue

            self._parse_campaign_data(data, file.name)

    def _parse_campaign_data(self, data: Any, filename: str):
        if isinstance(data, dict):
            self._try_add_campaign(data, filename)
        elif isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict):
                    self._try_add_campaign(entry, filename)
                else:
                    print(f"[dim]Skipping non-dict item in {filename}[/dim]")
        else:
            print(f"[dim]Skipping unsupported data format in {filename}[/dim]")

    def _try_add_campaign(self, data: Dict[str, Any], filename: str):
        if not data.get("name"):
            print(f"[yellow]Skipping campaign without name in {filename}[/yellow]")
            return

        if not (data.get("connect_message") or data.get("first_message")):
            print(f"[yellow]Skipping campaign without connect or first message in {filename}[/yellow]")
            return

        try:
            campaign = Campaign(
                name=data.get("name"),
                include_keywords=data.get("include_keywords", []),
                exclude_keywords=data.get("exclude_keywords", []),
                ideal_persona=data.get("ideal_persona"),
                ai_lead_score_threshold=data.get("ai_lead_score_threshold", 0),
                model_provider=data.get("model_provider"),
                model=data.get("model"),
                connect_message=data.get("connect_message"),
                first_message=data.get("first_message"),
                follow_up=data.get("follow_up")
            )
            self.campaigns.append(campaign)
            print(f"[green]Loaded campaign:[/green] {campaign.name}")
        except Exception as e:
            print(f"[red]Failed to load campaign '{data.get('name', 'unknown')}' in {filename}: {e}[/red]")

    def lead_score(self, profile: Profile) -> Tuple[str, int, str]:
        """
        Returns the highest score from all campaigns for the given profile.
        """
        max_lead_score = 0 
        max_lead_score_reason = ""
        campaign_name = ""
        for cmpgn in self.campaigns:
            lead_score, lead_score_reason = cmpgn.lead_score(profile)
            if lead_score > cmpgn.lead_score_threshold:
                if max_lead_score < lead_score:
                    max_lead_score = lead_score
                    campaign_name = cmpgn.name
                    max_lead_score_reason = lead_score_reason
        return campaign_name, max_lead_score, max_lead_score_reason

    def get_all(self) -> List[Campaign]:
        return self.campaigns

    def get_by_name(self, name: str) -> Campaign | None:
        for c in self.campaigns:
            if c.name == name:
                return c
        return None

    def lead_gen(self, db_client: DBClient, profile: Profile):
        campaign_name, lead_score, lead_score_reason = self.lead_score(profile)
        
        if lead_score <= 0 or not campaign_name:
            print(f"[yellow]Lead {profile.url} does not qualify for any campaign[/yellow]")
            return
        print(f"[green]Lead {profile.url} scored {lead_score} in campaign {campaign_name}[/green]")
        print(f"[green]Reason: {lead_score_reason}[/green]")
        lead = Lead(campaign_name=campaign_name,
                    profile=profile.url,
                    stage="CREATED",
                    created_at=datetime.now(),
                    score=lead_score,
                    reason=lead_score_reason)
        lead.add(db_client)
    
    def get_names(self) -> List[str]:
        return [c.name for c in self.campaigns]
    
    @staticmethod
    def create(data: Dict[str, Any]):
        """Create a campaign JSON file from dictionary input."""
        name = data.get("name")
        if not name:
            print("[yellow]Cannot create campaign: 'name' field is missing[/yellow]")
            return

        campaign_dir = Path(os.environ.get("CAMPAIGN_DIR", "~/.linkiq/campaigns")).expanduser().resolve()
        campaign_dir.mkdir(parents=True, exist_ok=True)

        filepath = campaign_dir / f"{name}.json"
        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            print(f"[green]Campaign '{name}' created at {filepath}[/green]")
        except Exception as e:
            print(f"[red]Failed to write campaign file: {e}[/red]")

        
