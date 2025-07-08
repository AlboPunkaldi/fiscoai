from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import date
from sqlmodel import select
from services.db import get_session
from models.invoice import Invoice as InvoiceORM
from models.invoice import InvoiceCreate

def _generate_pdf(inv: InvoiceCreate) -> str:
    pdf_dir = Path("pdf")
    pdf_dir.mkdir(exist_ok=True)

    # 🔑  sostituiamo / con - SOLO per il filesystem
    safe_number = inv.number.replace("/", "-")
    file_path = pdf_dir / f"Fattura_{safe_number}.pdf"

    c = canvas.Canvas(str(file_path), pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 80,
                 f"Fattura n. {inv.number} del {inv.invoice_date.isoformat()}")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 110, f"Cliente: {inv.customer_name}")
    c.drawString(50, height - 140, f"Descrizione: {inv.description}")
    c.drawString(50, height - 170, f"Imponibile: € {inv.amount:,.2f}")
    iva_amount = inv.amount * inv.vat_rate / 100
    c.drawString(50, height - 200, f"IVA {inv.vat_rate}%: € {iva_amount:,.2f}")
    c.drawString(50, height - 230, f"Totale: € {inv.amount + iva_amount:,.2f}")

    c.showPage()
    c.save()
    return str(file_path)

def create_invoice(inv: InvoiceCreate) -> dict:
    """
    1) Genera il PDF
    2) Inserisce il record in Postgres
    3) Restituisce un dict con i campi salvati + pdf_path
    """
    # ——— 1) Genera il PDF ———
    pdf_dir = Path("pdf")
    pdf_dir.mkdir(exist_ok=True)
    safe_number = inv.number.replace("/", "-")
    file_path = pdf_dir / f"Fattura_{safe_number}.pdf"
    c = canvas.Canvas(str(file_path), pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 80,
                 f"Fattura n. {inv.number} del {inv.invoice_date.isoformat()}")
    # … (resto del disegno come prima) …
    c.showPage()
    c.save()

    # ——— 2) Salva in Postgres ———
    invoice_record = InvoiceORM(
        number=inv.number,
        invoice_date=inv.invoice_date,
        customer_name=inv.customer_name,
        description=inv.description,
        amount=inv.amount,
        vat_rate=inv.vat_rate
    )
    # next(get_session()) restituisce un generator yield, quindi with lo chiude correttamente
    with next(get_session()) as session:
        session.add(invoice_record)
        session.commit()
        session.refresh(invoice_record)

    # ——— 3) Restituisci i dati + percorso PDF ———
    data = invoice_record.dict()
    data["pdf_path"] = str(file_path)
    return data

def _totale_incassi() -> float:
    """
    Somma tutti i campi 'amount' nella tabella invoice.
    """
    stmt = select(InvoiceORM.amount)
    with next(get_session()) as session:
        results = session.exec(stmt).all()  # lista di float
    return sum(results)

def _fatture_per_mese():
    """
    Raggruppa le righe per mese: ritorna {mese: [record,…], …}
    """
    stmt = select(InvoiceORM)
    with next(get_session()) as session:
        all_invoices = session.exec(stmt).all()  # lista di oggetti InvoiceORM
    buckets: dict[int, list[InvoiceORM]] = defaultdict(list)
    for inv in all_invoices:
        month = inv.invoice_date.month
        buckets[month].append(inv)
    return buckets