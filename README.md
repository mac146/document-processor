# Document Processor API

This project is a FastAPI-based document processing service built as an internship interview assignment. It accepts a PDF, processes it in the background, classifies the document using the Groq API, extracts a few fields, and stores the result in SQLite.

## Features

- Upload PDF documents
- Process files asynchronously
- Classify document type with confidence score
- Extract `document_date`, `total_amount`, and `counterparty`
- Store job status and results in SQLite
- Fetch results later using a `job_id`

## Tech Stack

- Python
- FastAPI
- SQLite
- PyMuPDF
- Groq API

## Project Structure

```text
document-processor/
|-- main.py
|-- processor.py
|-- database.py
|-- models.py
|-- requirements.txt
|-- .env.example
```

## How It Works

1. Upload a PDF to `POST /process-document`
2. The API creates a job and returns a `job_id`
3. The file is processed in a background task
4. Extracted text is sent to Groq for classification and field extraction
5. The result is stored in SQLite
6. Check the result using `GET /result/{job_id}`

## Setup

```bash
git clone <your-repo-url>
cd document-processor
python -m venv venv
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Run the server:

```bash
uvicorn main:app --reload
```

Open Swagger docs at `http://127.0.0.1:8000/docs`.

Live deployment:

```text
https://document-processor-production-cc18.up.railway.app
```

## API Endpoints

- `GET /health` - health check
- `POST /process-document` - upload a PDF and start processing
- `GET /result/{job_id}` - get job status and extracted result

Final curl commands:

Upload:

```bash
curl -X POST https://document-processor-production-cc18.up.railway.app/process-document -F "file=@/path/to/invoice.pdf"
```

Get result:

```bash
curl https://document-processor-production-cc18.up.railway.app/result/{job_id}
```

Example response:

```json
{
  "job_id": "a1b2c3d4",
  "status": "complete",
  "document_type": "invoice",
  "confidence": 0.94,
  "extracted_fields": {
    "document_date": "2025-01-10",
    "total_amount": 1250.5,
    "counterparty": "ABC Pvt Ltd"
  },
  "page_count": 3,
  "processing_time_ms": 1420,
  "error": null
}
```

## Limitations

- Only PDF files are supported
- Scanned PDFs without extractable text are not supported
- No OCR fallback yet
- No authentication or test suite yet
