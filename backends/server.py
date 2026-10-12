"""
Backend server: ONE FastAPI app, parameterised entirely by environment.

README_FIRST Part 4 - THE BACKENDS (backends/)
  - One FastAPI app, parameterised by env: name, port, /work delay in ms.
  - /health returns 200 in under 50ms and says nothing interesting.
  - /work sleeps the configured delay then returns 200 (load-test target).
  - /crash?seconds=N makes the app stop responding for N seconds without the
    process dying (implement it by making the health endpoint hang, and
    document exactly what it does).

Expected endpoints (names fixed; bodies are yours):
  GET /                 -> identity JSON (which backend am I?)
  GET /health           -> instant 200
  GET /work?ms=N        -> sleep N ms, then 200
  GET /crash?seconds=N  -> stop responding for N seconds, process stays alive

Env vars it reads (see .env.example):
  SERVER_NAME, SERVER_PORT, SERVER_WORK_DELAY_MS

TODO(M1): implement. Nothing is written here yet - C8 and ROADMAP M1 say you
write every line of this file yourself. Run it three times with three
different env sets; one file, three invocations, never three copies.
"""

import os
import asyncio 
from fastapi import FastAPI
from dotenv import load_dotenv

# Load ENV
load_dotenv()

app = FastAPI()

SERVER_NAME = os.getenv("SERVER_NAME","default")
SERVER_PORT = int(os.getenv("SERVER_PORT",8000))
SERVER_WORK_DELAY_MS = int(os.getenv("SERVER_WORK_DELAY_MS",0))

@app.get("/")
async def identity():
  return {
    "backend": SERVER_NAME,
    "port" : SERVER_PORT,
    "delay_ms" : SERVER_WORK_DELAY_MS
  }
  
@app.get("/health")
async def health():
  return {
    "status" : "OK"
  }
  
@app.get("/work")
async def work(ms : int):
  await asyncio.sleep(ms/1000.0)
  return {
    "done_in_ms":ms
  }