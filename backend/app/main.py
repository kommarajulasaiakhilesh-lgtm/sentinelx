from fastapi import FastAPI

app = FastAPI(
    title="SentinelX",
    description="AI Agent Security Control Plane",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "SentinelX is running",
        "version": "0.1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }