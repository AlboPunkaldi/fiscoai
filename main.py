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

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from models.user import UserCreate
from services.auth_service import (
    create_user, authenticate, create_access_token, get_current_user
)

app = FastAPI(title="FiscoAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/invoices", response_model=Invoice)
def emit_invoice(inv: InvoiceCreate, user=Depends(get_current_user)):
    """
    Crea una fattura e restituisce i suoi dati.
    """
    try:
        return create_invoice(inv)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/invoices/pdf/{number:path}")
def download_invoice(number: str, user=Depends(get_current_user)):
    safe_number = number.replace("/", "-")
    path = f"pdf/Fattura_{safe_number}.pdf"
    return FileResponse(path, media_type="application/pdf")

@app.get("/tax/summary", response_model=TaxSummary)
def get_tax_summary(user=Depends(get_current_user)):
    """
    Ritorna la previsione tasse dell'anno corrente (regime forfettario).
    """
    return calcola_tasse_anno()

@app.get("/tax/monthly", response_model=MonthlySummary)
def get_tax_monthly(user=Depends(get_current_user)):
    """
    Riepiloga ricavi e imposte per ciascun mese dell'anno corrente.
    """
    return {
        "anno": date.today().year,
        "mesi": riepilogo_mensile()
    }

@app.post("/chat", response_model=ChatResponse)
def chat_ai(payload: ChatRequest = Body(...), user=Depends(get_current_user)):
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

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate):
    """
    Registra un utente.
    Body JSON: { "email": "..", "password": ".." }
    """
    create_user(payload)
    return {"msg": "Utente creato correttamente"}

@app.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    """
    Accetta form-urlencoded: username=<email>&password=<pwd>
    Restituisce: { "access_token": "...", "token_type": "bearer" }
    """
    user = authenticate(form.username, form.password)
    if not user:
        raise HTTPException(status_code=400, detail="Email o password errate")
    token = create_access_token(user.email)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/me")
def me(user = Depends(get_current_user)):
    return {"email": user.email, "role": user.role}