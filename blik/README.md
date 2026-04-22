# Блик - Система управления заявками на IT обслуживание

Система управления заявками (тикет-система)类似于 Zammad, с интеграцией мессенджера MAX и Active Directory.

## 🚀 Возможности

### Для пользователей (мессенджер MAX):
- ✅ Однократная авторизация через Active Directory
- ✅ Создание заявок на IT обслуживание
- ✅ Просмотр статуса своих заявок
- ✅ Уведомления об изменениях
- ✅ Простой и понятный интерфейс

### Для администраторов (веб-интерфейс):
- ✅ Управление всеми заявками
- ✅ Назначение исполнителей
- ✅ Изменение приоритета и статуса
- ✅ Фильтрация и поиск
- ✅ Статистика по заявкам
- ✅ Авторизация через AD

## 📁 Структура проекта

```
blik/
├── backend/           # Backend на FastAPI
│   ├── config/       # Конфигурация
│   ├── models/       # SQLAlchemy модели
│   ├── routes/       # API endpoints
│   ├── services/     # Бизнес-логика
│   ├── database.py   # База данных
│   └── main.py       # Точка входа
├── bot/              # Бот для MAX мессенджера
│   └── max_bot_handler.py
├── web/              # Веб-интерфейс
│   └── routes.py
├── templates/        # HTML шаблоны
│   └── admin.html
├── static/           # Статические файлы
├── requirements.txt  # Зависимости Python
├── .env.example      # Пример конфигурации
└── run.py           # Запуск приложения
```

## 🔧 Установка

1. **Клонируйте репозиторий:**
```bash
cd /workspace/blik
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Настройте окружение:**
```bash
cp .env.example .env
# Отредактируйте .env с вашими настройками
```

4. **Настройте Active Directory:**
- `AD_SERVER` - адрес вашего LDAP сервера
- `AD_BASE_DN` - базовый DN для поиска
- `AD_BIND_DN` - учетная запись сервиса
- `AD_BIND_PASSWORD` - пароль сервисной учетки

5. **Настройте MAX Bot:**
- Получите токен бота в MAX
- Укажите `MAX_BOT_TOKEN` в .env
- Настройте webhook URL

## 🏃 Запуск

```bash
python run.py
```

Или напрямую через uvicorn:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

После запуска:
- 📖 API документация: http://localhost:8000/docs
- 🎨 Веб-интерфейс: http://localhost:8000/admin
- 🤷 Webhook для бота: http://localhost:8000/webhook/max

## 📱 Использование бота

1. Пользователь начинает диалог с ботом в MAX
2. Бот предлагает авторизоваться через AD
3. После авторизации аккаунт сохраняется
4. Пользователь может создавать заявки командами:
   - "Новая заявка" - создание тикета
   - "Мои заявки" - просмотр своих тикетов
   - "Помощь" - справка

## 🖥️ Использование веб-интерфейса

1. Откройте http://localhost:8000/admin
2. Войдите используя учетные данные AD
3. Управляйте заявками:
   - Меняйте статус
   - Назначайте исполнителей
   - Изменяйте приоритет
   - Фильтруйте и ищите

## 🔐 Безопасность

⚠️ **Важно для production:**
- Смените `SECRET_KEY` на уникальный
- Настройте CORS правильно
- Используйте HTTPS
- Ограничьте доступ к AD сервисной учетке
- Реализуйте rate limiting

## 🛠 Технологии

- **Backend:** FastAPI, SQLAlchemy (async), Pydantic
- **База данных:** SQLite (dev) / PostgreSQL (prod)
- **Бот:** aiohttp, aiofiles
- **Веб:** TailwindCSS, Vanilla JS
- **AD:** ldap3
- **Auth:** JWT, Active Directory LDAP

## 📝 API Endpoints

### Authentication
- `POST /api/auth/ad-login` - Вход через AD

### Tickets (User)
- `POST /api/tickets/create` - Создать заявку
- `GET /api/tickets/my-tickets` - Мои заявки
- `GET /api/tickets/{id}` - Получить заявку

### Admin
- `GET /api/admin/tickets/` - Все заявки
- `PUT /api/admin/tickets/{id}` - Обновить заявку
- `GET /api/admin/tickets/admins` - Список админов

## 📄 Лицензия

MIT
