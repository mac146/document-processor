import asyncio
import json
import os
import time

import fitz  # PyMuPDF
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, int]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    page_count = len(doc)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    if not text.strip():
        raise ValueError("Could not extract text - PDF appears to be scanned")

    return text, page_count


def call_groq(text: str) -> tuple[dict, int]:
    prompt = f"""
You are a document classifier. Analyze the document below and return ONLY a JSON object with no explanation, no markdown, no backticks.

Return exactly this structure:
{{
    "document_type": "invoice or contract or resume or report or other",
    "confidence": 0.91,
    "extracted_fields": {{
        "document_date": "YYYY-MM-DD or null",
        "total_amount": 1234.56 or null,
        "counterparty": "Company or person name or null"
    }}
}}

Document:
{text[:4000]}
"""

    start = time.time()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    processing_time_ms = int((time.time() - start) * 1000)

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)
    return result, processing_time_ms


async def process_document(job_id: str, file_bytes: bytes):
    from database import update_job_failed, update_job_success

    try:
        # Run blocking PDF parsing and Groq network I/O off the event loop.
        text, page_count = await asyncio.to_thread(extract_text_from_pdf, file_bytes)
        result, processing_time_ms = await asyncio.to_thread(call_groq, text)

        await update_job_success(
            job_id=job_id,
            document_type=result.get("document_type"),
            confidence=result.get("confidence"),
            extracted_fields=result.get("extracted_fields", {}),
            page_count=page_count,
            processing_time_ms=processing_time_ms,
        )
    except Exception as e:
        await update_job_failed(job_id=job_id, error=str(e))
