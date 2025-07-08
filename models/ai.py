from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    question: str = Field(
        ..., 
        example="Quanto pagherò di tasse se fatturo 50.000€ quest'anno?"
    )

class ChatResponse(BaseModel):
    answer: str = Field(
        ...,
        example="Se fatturi 50.000€ in regime forfettario, il calcolo è …"
    )