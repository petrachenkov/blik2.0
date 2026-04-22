from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


async def admin_panel(request: Request) -> HTMLResponse:
    """Render admin panel"""
    return templates.TemplateResponse("admin.html", {"request": request})
