from sqlmodel import SQLModel, create_engine, Session

# DATABASE_URL: indica a SQLModel dove si trova Postgres
DATABASE_URL = "postgresql://localhost/fiscoai_db"

# create_engine costruisce un pool di connessioni
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    """
    Fornisce una sessione DB. 
    Usa 'with get_session() as session:' per leggere o modificare dati.
    """
    with Session(engine) as session:
        yield session