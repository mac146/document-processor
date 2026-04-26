import aiosqlite
import uuid
import os

DB_PATH = "jobs.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'processing',
                document_type TEXT,
                confidence REAL,
                extracted_date TEXT,
                extracted_amount REAL,
                extracted_counterparty TEXT,
                page_count INTEGER,
                processing_time_ms INTEGER,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def create_job() -> str:
    job_id = uuid.uuid4().hex[:8]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO jobs (job_id, status) VALUES (?, ?)",
            (job_id, "processing")
        )
        await db.commit()
    return job_id

async def update_job_success(job_id: str, document_type: str, confidence: float,
                              extracted_fields: dict, page_count: int, processing_time_ms: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE jobs SET
                status = 'complete',
                document_type = ?,
                confidence = ?,
                extracted_date = ?,
                extracted_amount = ?,
                extracted_counterparty = ?,
                page_count = ?,
                processing_time_ms = ?,
                error = null
            WHERE job_id = ?
        """, (
            document_type,
            confidence,
            extracted_fields.get("document_date"),
            extracted_fields.get("total_amount"),
            extracted_fields.get("counterparty"),
            page_count,
            processing_time_ms,
            job_id
        ))
        await db.commit()

async def update_job_failed(job_id: str, error: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE jobs SET
                status = 'failed',
                error = ?
            WHERE job_id = ?
        """, (error, job_id))
        await db.commit()

async def get_job(job_id: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM jobs WHERE job_id = ?", (job_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return dict(row)