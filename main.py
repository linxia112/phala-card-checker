from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import card_processor

app = FastAPI(
    title="Card Checker API",
    description="An API to process card information. For educational purposes only.",
    version="1.0.0"
)

class CardInput(BaseModel):
    card_data: str = Field(...,
                           description="Card information in 'number|mm|yy|cvc' format.",
                           example="4000123456789010|12|28|123")

class ProcessResponse(BaseModel):
    card: str
    status: str
    message: str

@app.get("/", summary="Health Check")
def read_root():
    return {"status": "ok", "message": "API is running"}

@app.post("/process-card", response_model=ProcessResponse, summary="Process a single card")
def process_single_card(card_input: CardInput):
    if not card_input.card_data:
        raise HTTPException(status_code=400, detail="card_data field cannot be empty.")
    try:
        result = card_processor.process_card(card_input.card_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")
