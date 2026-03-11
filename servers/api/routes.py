import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models.schemas import (
    CompanyApplicationCreate, CompanyApplication,
    DocumentUploadRequest, DocumentUploadResponse, IngestedDocument,
    PrimaryInsightCreate, PrimaryInsight,
    ResearchResult, CAMReport, CAMExportRequest,
    APIResponse, ApplicationStatus, DocumentType,
    ExtractedFinancials, StructuredDataAnomaly, RiskAlert,
    FiveCsScore, FiveCsNarrative, CreditDecision
)
from store import applications_db, documents_db, insights_db, research_db, cam_reports_db
from services.ingestor import IngestorService

ingestor_service = IngestorService()

router = APIRouter()


# Health Check

@router.get("/health")
def health_check():
    return {"status": "ok"}

# Route 1: Create a new loan application

@router.post("/applications", response_model=CompanyApplication)
def create_application(app_data: CompanyApplicationCreate):
    app_id = f"APP-{uuid.uuid4().hex[:6]}"
    application = CompanyApplication(
        id=app_id,
        **app_data.model_dump()
    )
    applications_db[app_id] = application
    return application


# Route 2: List all applications

@router.get("/applications", response_model=list[CompanyApplication])
def list_applications():
    return list(applications_db.values())

# Route 3: Get a single application by ID

@router.get("/applications/{application_id}", response_model=CompanyApplication)
def get_application(application_id: str):
    if application_id not in applications_db:
        raise HTTPException(status_code=404, detail="Application not found")
    return applications_db[application_id]



# Route 4: Upload and parse a document (PDF/CSV)

@router.post("/ingest/document", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    application_id: str = Form(...),
    file_type: DocumentType = Form(...)
):
    if application_id not in applications_db:
        raise HTTPException(status_code=404, detail="Application not found")

    applications_db[application_id].status = ApplicationStatus.INGESTING

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

    if application_id not in documents_db:
        documents_db[application_id] = []
    documents_db[application_id].append(document)

    return DocumentUploadResponse(
        success=True,
        document=document,
        message=f"Document '{file.filename}' processed successfully."
    )



# Route 5: Upload structured data (CSV/Excel)


@router.post("/ingest/structured", response_model=DocumentUploadResponse)
async def upload_structured_data(
    file: UploadFile = File(...),
    application_id: str = Form(...),
    file_type: DocumentType = Form(...)
):
    if application_id not in applications_db:
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

    if application_id not in documents_db:
        documents_db[application_id] = []
    documents_db[application_id].append(document)

    return DocumentUploadResponse(
        success=True,
        document=document,
        message=f"Structured file '{file.filename}' processed successfully."
    )



# Route 6: Get all documents for an application


@router.get("/ingest/documents/{application_id}", response_model=list[IngestedDocument])
def get_documents(application_id: str):
    if application_id not in applications_db:
        raise HTTPException(status_code=404, detail="Application not found")
    return documents_db.get(application_id, [])



# Route 7: Trigger web research for a company


@router.get("/research/company/{application_id}", response_model=ResearchResult)
def research_company(application_id: str):
    if application_id not in applications_db:
        raise HTTPException(status_code=404, detail="Application not found")

    app = applications_db[application_id]
    app.status = ApplicationStatus.RESEARCHING

    # TODO: Replace with actual ResearcherService web crawling
    result = ResearchResult(
        application_id=application_id,
        company_name=app.company_name,
        alerts=[],
        sector_outlook="[Pending] Research not yet implemented",
        promoter_background="[Pending] Research not yet implemented"
    )

    research_db[application_id] = result
    return result



# Route 8: Submit primary insights (Credit Officer notes)


@router.post("/engine/primary-insights", response_model=PrimaryInsight)
def add_primary_insight(insight_data: PrimaryInsightCreate):
    if insight_data.application_id not in applications_db:
        raise HTTPException(status_code=404, detail="Application not found")

    insight_id = f"INS-{uuid.uuid4().hex[:6]}"

    insight = PrimaryInsight(
        id=insight_id,
        **insight_data.model_dump()
    )

    if insight_data.application_id not in insights_db:
        insights_db[insight_data.application_id] = []
    insights_db[insight_data.application_id].append(insight)

    return insight



# Route 9: Get all insights for an application


@router.get("/engine/insights/{application_id}", response_model=list[PrimaryInsight])
def get_insights(application_id: str):
    if application_id not in applications_db:
        raise HTTPException(status_code=404, detail="Application not found")
    return insights_db.get(application_id, [])



# Route 10: Generate the CAM Report


@router.post("/engine/generate-cam", response_model=CAMReport)
def generate_cam(application_id: str):
    if application_id not in applications_db:
        raise HTTPException(status_code=404, detail="Application not found")

    app = applications_db[application_id]
    app.status = ApplicationStatus.UNDER_REVIEW

    cam_id = f"CAM-{uuid.uuid4().hex[:6]}"

    # TODO: Replace with actual EngineService CAM generation
    # This will use LangChain + OpenAI to generate the Five Cs, scoring, and decision
    cam = CAMReport(
        id=cam_id,
        application=app,
        financials=None,
        anomalies=[],
        risk_alerts=research_db.get(application_id, ResearchResult(
            application_id=application_id,
            company_name=app.company_name
        )).alerts,
        primary_insights=insights_db.get(application_id, []),
        sector_outlook=research_db.get(application_id, ResearchResult(
            application_id=application_id,
            company_name=app.company_name
        )).sector_outlook,
        promoter_background=research_db.get(application_id, ResearchResult(
            application_id=application_id,
            company_name=app.company_name
        )).promoter_background,
        five_cs_scores=None,
        five_cs_narrative=None,
        decision=None
    )

    cam_reports_db[application_id] = cam
    return cam

# Route 11: Export CAM as Word/PDF

@router.post("/engine/export-cam")
def export_cam(export_request: CAMExportRequest):
    if export_request.application_id not in cam_reports_db:
        raise HTTPException(status_code=404, detail="CAM not generated yet. Call /engine/generate-cam first.")

    # TODO: Replace with actual python-docx / reportlab export logic
    return APIResponse(
        success=True,
        message=f"CAM export in {export_request.format.value} format is not yet implemented.",
        data={"application_id": export_request.application_id, "format": export_request.format.value}
    )
