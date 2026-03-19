from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import execute_query

app = FastAPI(title="Inova Monitoring")

# Setup templates and static files
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Render the dashboard index page.
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Inova Apps Interface"},
    )

@app.get("/api/data")
async def get_data(query: str = "SELECT current_database(), current_user, version();"):
    """
    API endpoint to execute a query and return JSON results.
    Default query returns basic DB info.
    """
    try:
        results = execute_query(query)
        return {"success": True, "data": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
