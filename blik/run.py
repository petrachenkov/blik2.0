"""
Блик - Система управления заявками на IT обслуживание

Запуск приложения:
    python run.py

Или через uvicorn напрямую:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""

import uvicorn
from backend.config.settings import settings


if __name__ == "__main__":
    print(f"🚀 Запуск системы {settings.APP_NAME}...")
    print(f"📖 Документация API: http://localhost:{settings.WEB_PORT}/docs")
    print(f"🎨 Веб-интерфейс: http://localhost:{settings.WEB_PORT}/admin")
    print(f"🤖 Webhook для бота: http://localhost:{settings.WEB_PORT}/webhook/max")
    
    uvicorn.run(
        "backend.main:app",
        host=settings.WEB_HOST,
        port=settings.WEB_PORT,
        reload=settings.DEBUG
    )
