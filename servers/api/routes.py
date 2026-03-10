import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
import json
from services.ingestor import IngestorService
from services.researcher import ResearcherService
from services.engine import EngineService
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter()

# Dependency injection for services (simplified for hackathon)
def get_ingestor_service(): return IngestorService()
def get_researcher_service(): return ResearcherService()
def get_engine_service(): return EngineService()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/ingest/document")
async def ingest_document(
    file: UploadFile = File(...),
    ingestor: IngestorService = Depends(get_ingestor_service)
):
    """
    Ingests a PDF document, parses it, and uses LLM to extract financial covenants and risks.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Save the uploaded file temporarily
    file_path = os.path.join(tempfile.gettempdir(), file.filename)
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    try:
        result = ingestor.parse_pdf(file_path)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/research/company/{company_id}")
async def research_company(
    company_id: str,
    researcher: ResearcherService = Depends(get_researcher_service)
):
    """
    Triggers a DuckDuckGo search for the company and uses LLM to cluster findings into Risk Alerts.
    """
    try:
        result = researcher.search_company(company_id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CAMRequest(BaseModel):
    application_id: str
    company_data: Dict[str, Any]
    research_data: Dict[str, Any]
    primary_insights: str

@router.post("/engine/generate-cam")
async def generate_cam(
    request: CAMRequest,
    engine: EngineService = Depends(get_engine_service)
):
    """
    Aggregates data and generates the 5 Cs of Credit CAM using an LLM.
    """
    try:
        result = engine.generate_cam(
            company_data=request.company_data,
            research_data=request.research_data,
            primary_insights=request.primary_insights
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
