from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="DNA Explorer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "DNA Explorer API is running!"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting DNA Explorer API Server...")
    print("Web Interface: http://localhost:8000")
    print("API Documentation: http://localhost:8000/api/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
