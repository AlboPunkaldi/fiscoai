from pydantic import BaseModel, Field

# riepilogo annuale (usato in /tax/summary)
class TaxSummary(BaseModel):
    anno: int = Field(..., example=2025)
    ricavi: float = Field(..., example=10000.0)
    imponibile: float = Field(..., example=7800.0)
    inps: float = Field(..., example=2034.46)
    imposta_sostitutiva: float = Field(..., example=390.0)
    tasse_totali: float = Field(..., example=2424.46)

# singola riga mese (usato in /tax/monthly)
class MonthlyRow(BaseModel):
    mese: int = Field(..., ge=1, le=12, example=7)
    ricavi: float
    imponibile: float
    inps: float
    imposta_sostitutiva: float
    tasse_totali: float

# risposta completa mensile
class MonthlySummary(BaseModel):
    anno: int = Field(..., example=2025)
    mesi: list[MonthlyRow]