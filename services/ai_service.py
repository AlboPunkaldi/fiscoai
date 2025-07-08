import os
import openai
from dotenv import load_dotenv

# 1) Carica variabili da .env
load_dotenv()

# 2) Imposta la chiave nel client
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_chat(question: str) -> str:
    """
    Invia la domanda a OpenAI con la nuova API e ritorna la risposta.
    """
    # Usa il nuovo percorso openai.chat.completions.create
    response = openai.chat.completions.create(
        model="gpt-4o",   # o "gpt-4o-mini" se non hai accesso a gpt-4o
        messages=[
            {
                "role": "system",
                "content": (
                    "Sei un commercialista esperto di regime forfettario italiano. "
                    "Rispondi con chiarezza e precisione ai quesiti fiscali."
                )
            },
            {"role": "user", "content": question}
        ],
        temperature=0.2,
        max_tokens=300
    )
    # Nel nuovo client il contenuto sta in response["choices"][0]["message"]["content"]
    return response.choices[0].message.content.strip()