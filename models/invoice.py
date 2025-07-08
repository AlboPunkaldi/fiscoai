from pydantic import BaseModel, Field
from datetime import date
from typing import Literal
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, Field as PydanticField
from datetime import date
from typing import Optional

class InvoiceBase(SQLModel):
    number: str
    invoice_date: date
    customer_name: str
    description: str
    amount: float
    vat_rate: int

class Invoice(InvoiceBase, table=True):
    """
    Questa classe rappresenta la tabella 'invoice' in Postgres.
    - table=True crea la tabella automaticamente.
    - id: chiave primaria autoincrementale.
    """
    id: Optional[int] = Field(default=None, primary_key=True)

class InvoiceCreate(BaseModel):
    number: str = PydanticField(..., example="1/2025")
    invoice_date: date = PydanticField(..., example="2025-07-06")
    customer_name: str = PydanticField(..., example="Mario Rossi")
    description: str = PydanticField(..., example="Consulenza software")
    amount: float = PydanticField(..., gt=0, example=1000.0)
    vat_rate: int = PydanticField(22, example=22)
    
class Invoice(InvoiceCreate):
    pdf_path: str