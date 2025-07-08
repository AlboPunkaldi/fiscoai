from pathlib import Path
import json
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from collections import defaultdict

# --- File per i metadati delle fatture ---
INVOICES_FILE = Path("invoices.json")

# --- Costanti fiscali per il 2025 (puoi cambiarle quando cambiano le leggi) ---
COEFF_REDDITIVITA = Decimal("0.78")    # 78 %
INPS_ALIQUOTA     = Decimal("0.2607")  # 26,07 %
IMPOSTA_SOST      = Decimal("0.05")    # 5 % (startup < 5 anni)

# --------------------------------------------------------------------------- #
#                       FUNZIONI INTERNE (prefisso _ )                        #
# --------------------------------------------------------------------------- #

def _totale_incassi() -> Decimal:
    """
    Somma tutti gli 'amount' presenti in invoices.json.
    Se il file non esiste o è vuoto restituisce Decimal(0).
    """
    if not INVOICES_FILE.exists():
        return Decimal("0")
    data = json.loads(INVOICES_FILE.read_text())
    return sum(Decimal(str(inv["amount"])) for inv in data)

def _fatture_per_mese():
    """
    Ritorna un dizionario: {1: [fatture gennaio], 2: [...], ...}
    Usa l'indice mese estratto da 'invoice_date' (formato YYYY-MM-DD).
    """
    buckets = defaultdict(list)
    if INVOICES_FILE.exists():
        for inv in json.loads(INVOICES_FILE.read_text()):
            # '2025-07-06' → '07' → int(7)
            month = int(inv["invoice_date"][5:7])
            buckets[month].append(inv)
    return buckets

# --------------------------------------------------------------------------- #
#                  FUNZIONI PUBBLICHE (usate da FastAPI)                       #
# --------------------------------------------------------------------------- #

def calcola_tasse_anno() -> dict:
    """
    Calcola le imposte complessive dell'anno corrente.
    Ritorna un dict serializzabile in JSON.
    """
    ricavi = _totale_incassi()
    imponibile = (ricavi * COEFF_REDDITIVITA).quantize(Decimal("0.01"),
                                                       ROUND_HALF_UP)
    inps = (imponibile * INPS_ALIQUOTA).quantize(Decimal("0.01"),
                                                 ROUND_HALF_UP)
    imposta_sost = (imponibile * IMPOSTA_SOST).quantize(Decimal("0.01"),
                                                        ROUND_HALF_UP)
    totale = (inps + imposta_sost).quantize(Decimal("0.01"), ROUND_HALF_UP)

    return {
        "anno": date.today().year,
        "ricavi":        float(ricavi),
        "imponibile":    float(imponibile),
        "inps":          float(inps),
        "imposta_sostitutiva": float(imposta_sost),
        "tasse_totali":  float(totale)
    }

def riepilogo_mensile() -> list[dict]:
    """
    Lista di 12 dict (gen-dic) con ricavi e imposte di ogni mese.
    """
    per_mese = _fatture_per_mese()
    summary = []

    for m in range(1, 13):
        ricavi = sum(Decimal(str(inv["amount"])) for inv in per_mese.get(m, []))
        imponibile = (ricavi * COEFF_REDDITIVITA).quantize(Decimal("0.01"))
        inps = (imponibile * INPS_ALIQUOTA).quantize(Decimal("0.01"))
        imposta = (imponibile * IMPOSTA_SOST).quantize(Decimal("0.01"))
        totale = (inps + imposta).quantize(Decimal("0.01"))

        summary.append({
            "mese": m,
            "ricavi": float(ricavi),
            "imponibile": float(imponibile),
            "inps": float(inps),
            "imposta_sostitutiva": float(imposta),
            "tasse_totali": float(totale)
        })
    return summary