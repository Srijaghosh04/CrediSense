import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from models.schemas import (
    CompanyApplicationCreate, CompanyApplication,
    DocumentUploadRequest, DocumentUploadResponse, IngestedDocument,
    PrimaryInsightCreate, PrimaryInsight,
    ResearchResult, CAMReport, CAMExportRequest,
    APIResponse, ApplicationStatus, DocumentType,
    ExtractedFinancials, StructuredDataAnomaly, RiskAlert,
    FiveCsScore, FiveCsNarrative, CreditDecision
)
from store import db
from services.ingestor import IngestorService
from authentication.auth import verify_token

ingestor_service = IngestorService()
router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/applications", response_model=CompanyApplication)
def create_application(app_data: CompanyApplicationCreate, user: dict = Depends(verify_token)):
    app_id = f"APP-{uuid.uuid4().hex[:6]}"
    application = CompanyApplication(
        id=app_id,
        **app_data.model_dump()
    )
    
    if db.client:
        data = application.model_dump(mode="json")
        res = db.client.table("applications").insert(data).execute()
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to save application")
    return application

@router.get("/applications", response_model=list[CompanyApplication])
def list_applications(user: dict = Depends(verify_token)):
    if db.client:
        res = db.client.table("applications").select("*").execute()
        return [CompanyApplication(**row) for row in res.data]
    return []

@router.get("/applications/{application_id}", response_model=CompanyApplication)
def get_application(application_id: str, user: dict = Depends(verify_token)):
    if db.client:
        res = db.client.table("applications").select("*").eq("id", application_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Application not found")
        return CompanyApplication(**res.data[0])
    raise HTTPException(status_code=500, detail="Database not configured")

@router.post("/ingest/document", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    application_id: str = Form(...),
    file_type: DocumentType = Form(...),
    user: dict = Depends(verify_token)
):
    if db.client:
        app_res = db.client.table("applications").select("*").eq("id", application_id).execute()
        if not app_res.data:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # update status
        db.client.table("applications").update({"status": ApplicationStatus.INGESTING}).eq("id", application_id).execute()

    file_content = await file.read()
    doc_id = f"DOC-{uuid.uuid4().hex[:6]}"

    try:
        document = ingestor_service.parse_pdf(
            file_content=file_content,
            file_name=file.filename or "unknown",
            application_id=application_id,
            doc_id=doc_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

    if db.client:
        doc_data = document.model_dump(mode="json")
        db.client.table("ingested_documents").insert(doc_data).execute()

    return DocumentUploadResponse(
        success=True,
        document=document,
        message=f"Document '{file.filename}' processed successfully."
    )

@router.post("/ingest/structured", response_model=DocumentUploadResponse)
async def upload_structured_data(
    file: UploadFile = File(...),
    application_id: str = Form(...),
    file_type: DocumentType = Form(...),
    user: dict = Depends(verify_token)
):
    if db.client:
        app_res = db.client.table("applications").select("*").eq("id", application_id).execute()
        if not app_res.data:
            raise HTTPException(status_code=404, detail="Application not found")

    file_content = await file.read()
    doc_id = f"DOC-{uuid.uuid4().hex[:6]}"

    try:
        document = ingestor_service.process_structured(
            file_content=file_content,
            file_name=file.filename or "unknown",
            file_type=file_type,
            application_id=application_id,
            doc_id=doc_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process structured data: {str(e)}")

    if db.client:
        doc_data = document.model_dump(mode="json")
        db.client.table("ingested_documents").insert(doc_data).execute()

    return DocumentUploadResponse(
        success=True,
        document=document,
        message=f"Structured file '{file.filename}' processed successfully."
    )

@router.get("/ingest/documents/{application_id}", response_model=list[IngestedDocument])
def get_documents(application_id: str, user: dict = Depends(verify_token)):
    if db.client:
        res = db.client.table("ingested_documents").select("*").eq("application_id", application_id).execute()
        return [IngestedDocument(**row) for row in res.data]
    return []

@router.get("/research/company/{application_id}", response_model=ResearchResult)
def research_company(application_id: str, user: dict = Depends(verify_token)):
    if db.client:
        app_res = db.client.table("applications").select("*").eq("id", application_id).execute()
        if not app_res.data:
            raise HTTPException(status_code=404, detail="Application not found")
        company_name = app_res.data[0]['company_name']
        db.client.table("applications").update({"status": ApplicationStatus.RESEARCHING}).eq("id", application_id).execute()
    else:
        company_name = "Mock Company"

    result = ResearchResult(
        application_id=application_id,
        company_name=company_name,
        alerts=[],
        sector_outlook="[Pending] Research not yet implemented",
        promoter_background="[Pending] Research not yet implemented"
    )

    if db.client:
        db_data = {
            "application_id": result.application_id,
            "sector_outlook": result.sector_outlook,
            "promoter_background": result.promoter_background,
            "researched_at": result.researched_at.isoformat()
        }
        db.client.table("research_results").insert(db_data).execute()

    return result

@router.post("/engine/primary-insights", response_model=PrimaryInsight)
def add_primary_insight(insight_data: PrimaryInsightCreate, user: dict = Depends(verify_token)):
    insight_id = f"INS-{uuid.uuid4().hex[:6]}"
    insight = PrimaryInsight(
        id=insight_id,
        **insight_data.model_dump()
    )

    if db.client:
        app_res = db.client.table("applications").select("id").eq("id", insight_data.application_id).execute()
        if not app_res.data:
            raise HTTPException(status_code=404, detail="Application not found")
            
        data = insight.model_dump(mode="json")
        db.client.table("primary_insights").insert(data).execute()

    return insight

@router.get("/engine/insights/{application_id}", response_model=list[PrimaryInsight])
def get_insights(application_id: str, user: dict = Depends(verify_token)):
    if db.client:
        res = db.client.table("primary_insights").select("*").eq("application_id", application_id).execute()
        return [PrimaryInsight(**row) for row in res.data]
    return []

@router.post("/engine/generate-cam", response_model=CAMReport)
def generate_cam(application_id: str, user: dict = Depends(verify_token)):
    if not db.client:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    app_res = db.client.table("applications").select("*").eq("id", application_id).execute()
    if not app_res.data:
        raise HTTPException(status_code=404, detail="Application not found")
        
    app = CompanyApplication(**app_res.data[0])
    
    db.client.table("applications").update({"status": ApplicationStatus.UNDER_REVIEW}).eq("id", application_id).execute()

    cam_id = f"CAM-{uuid.uuid4().hex[:6]}"
    
    res_insights = db.client.table("primary_insights").select("*").eq("application_id", application_id).execute()
    insights = [PrimaryInsight(**row) for row in res_insights.data]
    
    res_research = db.client.table("research_results").select("*").eq("application_id", application_id).execute()
    research = res_research.data[0] if res_research.data else {}
    
    res_alerts = db.client.table("risk_alerts").select("*").eq("application_id", application_id).execute()
    alerts = [RiskAlert(**row) for row in res_alerts.data]
    
    cam = CAMReport(
        id=cam_id,
        application=app,
        financials=None,
        anomalies=[],
        risk_alerts=alerts,
        primary_insights=insights,
        sector_outlook=research.get("sector_outlook", ""),
        promoter_background=research.get("promoter_background", ""),
        five_cs_scores=None,
        five_cs_narrative=None,
        decision=None
    )

    cam_data = {
        "id": cam.id,
        "application_id": cam.application.id,
        "sector_outlook": cam.sector_outlook,
        "promoter_background": cam.promoter_background,
        "five_cs_scores": None,
        "five_cs_narrative": None,
        "decision": None,
        "generated_at": cam.generated_at.isoformat()
    }
    
    existing_cam = db.client.table("cam_reports").select("id").eq("application_id", application_id).execute()
    if existing_cam.data:
        db.client.table("cam_reports").update(cam_data).eq("application_id", application_id).execute()
    else:
        db.client.table("cam_reports").insert(cam_data).execute()

    return cam

@router.post("/engine/export-cam")
def export_cam(export_request: CAMExportRequest, user: dict = Depends(verify_token)):
    if db.client:
        cam_res = db.client.table("cam_reports").select("id").eq("application_id", export_request.application_id).execute()
        if not cam_res.data:
            raise HTTPException(status_code=404, detail="CAM not generated yet. Call /engine/generate-cam first.")

    return APIResponse(
        success=True,
        message=f"CAM export in {export_request.format.value} format is not yet implemented.",
        data={"application_id": export_request.application_id, "format": export_request.format.value}
    )
