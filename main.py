from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
import shutil
import os
from models import Invoice
from database import SessionLocal
from ocr_utils import extract_text_from_pdf, extract_text_from_image
from nlp_utils import categorize_expense
from extract_fields import extract_amount, extract_date, extract_vendor
from typing import List
from fastapi.staticfiles import StaticFiles

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post(
    "/upload/",
    summary="Upload Invoice",
    response_description="The extracted and categorized invoice data.",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Invoice uploaded and processed successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "filename": "invoice1.pdf",
                        "category": "Office Supplies",
                        "id": 1,
                        "amount": 1234.56,
                        "date": "2024-07-14",
                        "vendor": "Acme Corp"
                    }
                }
            }
        },
        400: {"description": "Unsupported file type."}
    },
)
async def upload_invoice(
    file: UploadFile = File(..., description="PDF or image file of the invoice to upload."),
    db: Session = Depends(get_db)
):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    ext = file.filename.lower().split('.')[-1]
    if ext == "pdf":
        text = extract_text_from_pdf(file_location)
    elif ext in ["jpg", "jpeg", "png", "bmp", "tiff"]:
        text = extract_text_from_image(file_location)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    # Categorize expense (placeholder)
    category = categorize_expense(text)

    # Extract amount, date, vendor from text
    amount = extract_amount(text)
    date = extract_date(text)
    vendor = extract_vendor(text)

    # Store in DB
    invoice = Invoice(
        filename=file.filename,
        extracted_text=text,
        category=category,
        amount=amount,
        date=date,
        vendor=vendor
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return {
        "filename": file.filename,
        "category": category,
        "id": invoice.id,
        "amount": amount,
        "date": date,
        "vendor": vendor
    }

@app.get(
    "/invoices/",
    summary="List Invoices",
    response_description="A list of all processed invoices.",
    responses={
        200: {
            "description": "List of invoices.",
            "content": {
                "application/json": {
                    "example": {
                        "invoices": [
                            {
                                "id": 1,
                                "filename": "invoice1.pdf",
                                "category": "Office Supplies",
                                "amount": 1234.56,
                                "date": "2024-07-14",
                                "vendor": "Acme Corp"
                            },
                            {
                                "id": 2,
                                "filename": "invoice2.png",
                                "category": "Travel",
                                "amount": 567.89,
                                "date": "2024-07-10",
                                "vendor": "Travel Co"
                            }
                        ]
                    }
                }
            }
        }
    },
)
def list_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    result = []
    for inv in invoices:
        result.append({
            "id": inv.id,
            "filename": inv.filename,
            "category": inv.category,
            "amount": inv.amount,
            "date": inv.date,
            "vendor": inv.vendor
        })
    return JSONResponse(content={"invoices": result}) 