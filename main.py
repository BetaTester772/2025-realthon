from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FastAPI Application", version="1.0.0")

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/dumy-histo")
async def get_dummy_histogram():
    dummy_histogram = {
            "0-10"  : 0.05,
            "10-20" : 0.10,
            "20-30" : 0.15,
            "30-40" : 0.20,
            "40-50" : 0.10,
            "50-60" : 0.10,
            "60-70" : 0.10,
            "70-80" : 0.05,
            "80-90" : 0.10,
            "90-100": 0.05
    }
    return dummy_histogram
