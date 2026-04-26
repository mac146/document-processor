from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from contextlib import asynccontextmanager
from database import init_db, create_job, get_job
from processor import process_document
from models import JobCreatedResponse, JobResultResponse, ExtractedFields

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/process-document", response_model=JobCreatedResponse)
async def process_document_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    # validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # read file bytes
    file_bytes = await file.read()

    # create job in DB
    job_id = await create_job()

    # fire background task
    background_tasks.add_task(process_document, job_id, file_bytes)

    return JobCreatedResponse(job_id=job_id, status="processing")


@app.get("/result/{job_id}", response_model=JobResultResponse)
async def get_result(job_id: str):
    job = await get_job(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResultResponse(
        job_id=job["job_id"],
        status=job["status"],
        document_type=job.get("document_type"),
        confidence=job.get("confidence"),
        extracted_fields=ExtractedFields(
            document_date=job.get("extracted_date"),
            total_amount=job.get("extracted_amount"),
            counterparty=job.get("extracted_counterparty")
        ),
        page_count=job.get("page_count"),
        processing_time_ms=job.get("processing_time_ms"),
        error=job.get("error")
    )