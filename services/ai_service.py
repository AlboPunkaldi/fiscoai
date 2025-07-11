import os
import openai
from dotenv import load_dotenv

from services.tax_service import calcola_tasse_anno, riepilogo_mensile

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def _build_financial_context() -> str:
    anno_data = calcola_tasse_anno()
    monthly = riepilogo_mensile()
    ctx = (
        f"Anno {anno_data['anno']}: "
        f"Ricavi={anno_data['ricavi']}€, "
        f"Imponibile={anno_data['imponibile']}€, "
        f"INPS={anno_data['inps']}€, "
        f"Imposta={anno_data['imposta_sostitutiva']}€, "
        f"TasseTotali={anno_data['tasse_totali']}€.\n"
    )
    ctx += "Riepilogo mensile (mese:ricavi): "
    mesi = [f"{r['mese']}:{r['ricavi']}" for r in monthly if r["ricavi"] > 0]
    ctx += ", ".join(mesi) + "."
    return ctx

def ask_chat(question: str) -> str:
    fin_ctx = _build_financial_context()
    messages = [
        {
            "role": "system",
            "content": (
                "Sei un commercialista virtuale esperto di regime forfettario italiano. "
                "Rispondi in modo chiaro e preciso ai quesiti."
            )
        },
        {
            "role": "system",
            "content": f"Dati utente:\n{fin_ctx}"
        },
        {
            "role": "user",
            "content": question
        }
    ]
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()