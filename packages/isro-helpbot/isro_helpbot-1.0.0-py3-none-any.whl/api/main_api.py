# api/main_api.py

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import sys

# Fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from isro_helpbot.core.chat_engine import process_user_query, update_knowledge_graph

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data", "clean_text")

# Serve frontend
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "ui", "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "ui", "templates"))

chat_history = []

class QueryRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(req: QueryRequest):
    reply = process_user_query(req.message, chat_history)
    chat_history.append((req.message, reply))
    return {"response": reply}

@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    update_knowledge_graph(files, DATA_DIR)
    return JSONResponse(content={"message": "Knowledge Graph updated"})

@app.post("/clear")
def clear():
    chat_history.clear()
    return {"message": "Chat cleared"}
