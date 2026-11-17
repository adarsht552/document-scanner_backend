from fastapi import FastAPI
from sqlalchemy import text
from app.database.connection import engine
from app.routes.auth import router as auth_router
from app.routes.profiles import router as profiles_router

app = FastAPI(
    title="Document Understanding API",
    description="An API for document understanding and information extraction.",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(profiles_router)

@app.get("/")
def home():
    return {"message": "Welcome to the Document Understanding API!"}



@app.get("/test-db")
def test_database():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return {
        "status": "connected",
        "database": "Supabase PostgreSQL",
        "result": result.scalar()
    }
    except Exception as e:
        return {"message": "Database connection failed.", "error": str(e)}
