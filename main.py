from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from graph import html_graph

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def index(user: str = None):
    file = html_graph(user=user)
    try:
        content = file.read_text(encoding="utf-8")
    finally:
        file.unlink()
    return HTMLResponse(content=content, status_code=200)
