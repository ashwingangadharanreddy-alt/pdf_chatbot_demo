from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routes.upload import router as upload_router
from routes.chat import router as chat_router

# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------
app = FastAPI(
    title="Document RAG API",
    description="Backend API for a Retrieval-Augmented Generation (RAG) chatbot.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Register Routers
# --------------------------------------------------
app.include_router(upload_router, tags=["Upload"])
app.include_router(chat_router, tags=["Chat"])

# --------------------------------------------------
# Startup Event
# --------------------------------------------------
@app.on_event("startup")
async def startup():
    print("✅ Document RAG API Started")

# --------------------------------------------------
# Shutdown Event
# --------------------------------------------------
@app.on_event("shutdown")
async def shutdown():
    print("🛑 Document RAG API Stopped")

# --------------------------------------------------
# Home Route
# --------------------------------------------------
@app.get("/", tags=["Home"])
def home():
    return {
        "status": "running",
        "message": "Document RAG API is running successfully."
    }

# --------------------------------------------------
# Health Check
# --------------------------------------------------
@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy",
        "server": "online"
    }

# --------------------------------------------------
# Custom 404 Handler
# --------------------------------------------------
@app.exception_handler(404)
async def not_found(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found.",
            "path": str(request.url)
        }
    )