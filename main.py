from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from routers.patient import router as patient_router
from routers.bed_alot import router as bed_router
from routers.tpa import router as tpa_router
from dotenv import load_dotenv
import os
from starlette.responses import JSONResponse

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY not set in .env file")

ALLOWED_ORIGIN = "https://reception.up.railway.app"

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

app = FastAPI(
    title="KK Hospital Backend API",
    description="Backend API for KK Hospital",
    version="1.0.0"
)

# 1. CORS Middleware - Register FIRST!
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["x-api-key", "content-type", "authorization"],
)

# 2. Add CORS headers to ALL responses, even errors
@app.middleware("http")
async def ensure_cors_on_response(request: Request, call_next):
    response = await call_next(request)
    origin = request.headers.get("origin")
    if origin == ALLOWED_ORIGIN:
        response.headers["access-control-allow-origin"] = origin
        response.headers["access-control-allow-credentials"] = "true"
        response.headers["access-control-allow-methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        response.headers["access-control-allow-headers"] = "x-api-key,content-type,authorization"
    return response

# 3. Dependency to check API key (skip for preflight)
def get_api_key(request: Request, api_key: str = Depends(api_key_header)):
    if request.method == "OPTIONS":
        return None  # Allow preflight requests without auth!
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Invalid API Key"
        )
    return api_key

# 4. Root endpoint (no authentication required)
@app.get("/")
def root():
    return JSONResponse(
        content={"message": "Welcome to the KK Hospital Backend API. For documentation, please refer to /docs."}
    )

# 5. Include routers with API Key dependency
app.include_router(patient_router, dependencies=[Depends(get_api_key)])
app.include_router(bed_router, dependencies=[Depends(get_api_key)])
app.include_router(tpa_router, dependencies=[Depends(get_api_key)])

# 6. Uvicorn startup for Railway
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
