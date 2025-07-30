from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from linkiq.model.db_client import DBClient
from linkiq.model.lead import Lead
from fastapi import Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()
db_client = DBClient()

# Allow frontend dev server to access backend if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to your frontend URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/view/static", StaticFiles(directory=static_path, html=True), name="static")

index_html = os.path.join(static_path, "index.html")

# @app.get("/")
# def serve_index():
#     return FileResponse(index_html)
#
# # Fallback route for client-side routing (e.g., /dashboard, /profile)
# @app.get("/{full_path:path}")
# def spa_fallback(full_path: str, request: Request):
#     return FileResponse(index_html)

# Response models for frontend compatibility
class LeadOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    company: str
    qualification_status: str
    engagement_status: str
    created_at: str
    last_contact: str

class LeadMetrics(BaseModel):
    identified: int
    qualified: int
    engaged: int

class PaginatedLeads(BaseModel):
    leads: List
    total: int
    page: int
    size: int
    pages: int


def format_lead(lead: Lead) -> LeadOut:
    # Adapt your internal model to the format your frontend expects
    return LeadOut(
        id=lead.id or 0,
        name=lead.profile.split("/")[-1],  # Fallback example
        email=f"{lead.profile.split('/')[-1]}@example.com",
        phone="N/A",
        company=lead.campaign_name,
        qualification_status="qualified" if "Qualified" in lead.stage else "unqualified",
        engagement_status="engaged" if "Engaged" in lead.stage else "not_engaged",
        created_at=lead.created_at.isoformat(),
        last_contact=lead.updated_at.isoformat(),
    )


@app.get("/api/leads", response_model=PaginatedLeads)
def get_leads(
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0, le=100),
        campaign_name: Optional[str] = Query(None),
        stage: Optional[str] = Query(None),
        created_at_from: Optional[str] = Query(None),
        created_at_to: Optional[str] = Query(None),
        sort_field: Optional[str] = Query(None),
        sort_direction: Optional[str] = Query("asc")
):

    all_leads = Lead.get_filtered(
        db_client=db_client,
        campaign_name=campaign_name,
        stage=stage,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        sort_field=sort_field,
        sort_direction=sort_direction,
    )

    total = len(all_leads)
    start = (page - 1) * size
    end = start + size
    page_leads = all_leads[start:end]
    # print(page_leads)

    return PaginatedLeads(
        leads=page_leads,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )

@app.get("/api/leads/metrics", response_model=LeadMetrics)
def get_metrics(
        campaign_name: Optional[str] = Query(None),
        created_at_from: Optional[str] = Query(None),
        created_at_to: Optional[str] = Query(None)
):
    leads = Lead.get_filtered(
        db_client=db_client,
        campaign_name=campaign_name,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
    )

    identified = len(leads)
    qualified = sum(1 for l in leads if "Qualified" in l.stage)
    engaged = sum(1 for l in leads if "Engaged" in l.stage or "Won" in l.stage)

    return LeadMetrics(
        identified=identified,
        qualified=qualified,
        engaged=engaged
    )

@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    # Don't serve index.html for API or static routes
    if request.url.path.startswith("/api") or request.url.path.startswith("/view/static"):
        return JSONResponse(status_code=404, content={"error": "Not Found"})

    # For all other routes, serve index.html
    return FileResponse(index_html)