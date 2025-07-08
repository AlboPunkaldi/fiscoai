from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from models.invoice import InvoiceCreate, Invoice
from services.invoice_service import create_invoice

from datetime import date
from models.tax import TaxSummary, MonthlySummary
from services.tax_service import calcola_tasse_anno, riepilogo_mensile

from fastapi.middleware.cors import CORSMiddleware

from fastapi import Body
from models.ai import ChatRequest, ChatResponse
from services.ai_service import ask_chat

from fastapi import HTTPException
from openai import OpenAIError, RateLimitError

app = FastAPI(title="FiscoAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/invoices", response_model=Invoice)
def emit_invoice(inv: InvoiceCreate):
    """
    Crea una fattura e restituisce i suoi dati.
    """
    try:
        return create_invoice(inv)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/invoices/pdf/{number:path}")
def download_invoice(number: str):
    safe_number = number.replace("/", "-")
    path = f"pdf/Fattura_{safe_number}.pdf"
    return FileResponse(path, media_type="application/pdf")

@app.get("/tax/summary", response_model=TaxSummary)
def get_tax_summary():
    """
    Ritorna la previsione tasse dell'anno corrente (regime forfettario).
    """
    return calcola_tasse_anno()

@app.get("/tax/monthly", response_model=MonthlySummary)
def get_tax_monthly():
    """
    Riepiloga ricavi e imposte per ciascun mese dell'anno corrente.
    """
    return {
        "anno": date.today().year,
        "mesi": riepilogo_mensile()
    }

@app.post("/chat", response_model=ChatResponse)
def chat_ai(payload: ChatRequest = Body(...)):
    """
    Risponde a domande fiscali in linguaggio naturale,
    gestendo eventuali errori di quota o di API.
    """
    try:
        answer = ask_chat(payload.question)
    except RateLimitError:
        # Quota esaurita o problema di billing
        raise HTTPException(
            status_code=503,
            detail="Quota OpenAI esaurita o problemi di billing: riprova più tardi."
        )
    except OpenAIError as e:
        # Qualunque altro errore API
        raise HTTPException(
            status_code=502,
            detail=f"Errore OpenAI API: {e}"
        )
    return ChatResponse(answer=answer)