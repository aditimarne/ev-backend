from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
os.environ["GRADIO_SERVER_NAME"] = "0.0.0.0"

from battery_app.OLA_API import router as ola_router
from battery_app.REVOLT_API import router as revolt_router


app = FastAPI(title="EV Battery ML Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[" https://evbatteryhealth.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ola_router, prefix="/ola", tags=["OLA"])
app.include_router(revolt_router, prefix="/revolt", tags=["REVOLT"])

@app.get("/")
def root():
    return {"status": "EV ML Backend Running"}
