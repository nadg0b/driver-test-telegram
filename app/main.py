from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any

import json, random


with open('data/data.json', 'r', encoding="utf-8") as f:
    questions_data = json.load(f)


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/questions", response_model=List[Dict[str, Any]])
async def get_questions():
    ticket_num = random.randint(1, 86)
    return [q for q in questions_data if q["ticket_num"] == ticket_num]


@app.get("/", response_class=HTMLResponse)
async def get_start():
    with open("templates/start.html", mode="r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.get("/quiz", response_class=HTMLResponse)
async def get_quiz():
    with open("templates/index.html", mode="r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)
