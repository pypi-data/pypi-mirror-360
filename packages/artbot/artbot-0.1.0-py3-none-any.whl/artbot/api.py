from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

@app.post("/ascii", response_class=HTMLResponse)
async def post_ascii_html():
    file_path = "result/ascii_art.html"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="ascii_art.html non trouvé")

    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content, status_code=200)

