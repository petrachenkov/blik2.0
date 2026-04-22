# Блик - Система управления IT заявками

Современная система управления заявками на IT обслуживание, аналог Zammad. Состоит из бота в мессенджере MAX для пользователей и веб-интерфейса для администраторов.

## Возможности

### Для пользователей (бот в мессенджере MAX):
- Авторизация через Active Directory (однократная настройка)
- Создание заявок на IT обслуживание
- Просмотр статуса своих заявок
- Получение уведомлений об изменениях

### Для администраторов (веб-интерфейс):
- Просмотр всех заявок
- Назначение приоритетов (Низкий, Средний, Высокий, Критический)
- Назначение ответственного администратора
- Изменение статуса заявки (Новая, В работе, Ожидание, Решена, Закрыта)
- Добавление комментариев
- Фильтрация и поиск заявок

## Архитектура

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Мессенджер    │────▶│   Backend        │◀────│  Веб-интерфейс  │
│   MAX (бот)     │     │   (FastAPI)      │     │  (Vue.js + Vite)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │   PostgreSQL     │
                        │   (База данных)  │
                        └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │   Active         │
                        │   Directory      │
                        └──────────────────┘
```

## Требования

- Python 3.9+
- PostgreSQL 12+
- Node.js 18+ (для веб-интерфейса)
- Доступ к серверу Active Directory

## Настройка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd blik
```

### 2. Настройка базы данных

Создайте базу данных PostgreSQL:

```bash
sudo -u postgres psql
CREATE DATABASE blik;
CREATE USER blik_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE blik TO blik_user;
\q
```

### 3. Настройка переменных окружения

Скопируйте файл `.env.example` в `.env` и заполните значения:

```bash
cp backend/.env.example backend/.env
```

#### Обязательные параметры в `.env`:

```ini
# База данных
DATABASE_URL=postgresql://blik_user:your_secure_password@localhost:5432/blik

# Active Directory
AD_SERVER=dc.example.com
AD_PORT=389
AD_BASE_DN=DC=example,DC=com
AD_BIND_DN=CN=Service Account,CN=Users,DC=example,DC=com
AD_BIND_PASSWORD=service_account_password
AD_USER_ATTRIBUTE=sAMAccountName

# Мессенджер MAX
MAX_API_KEY=your_max_api_key
MAX_API_SECRET=your_max_api_secret
MAX_WEBHOOK_URL=https://your-domain.com/api/v1/max/webhook

# Безопасность
SECRET_KEY=your_super_secret_key_for_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Веб-интерфейс
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=["http://localhost:3000","https://your-domain.com"]

# Логирование
LOG_LEVEL=INFO
```

### 4. Настройка веб-интерфейса

Перейдите в директорию фронтенда и установите зависимости:

```bash
cd frontend
npm install
```

Скопируйте `.env.example` в `.env` и настройте:

```ini
VITE_API_URL=http://localhost:8000
VITE_MAX_LOGIN_ENABLED=true
```

## Установка зависимостей

### Бэкенд

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Фронтенд

```bash
cd frontend
npm install
```

## Запуск

### Вариант 1: Раздельный запуск (рекомендуется для разработки)

#### Терминал 1 - Бэкенд:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Терминал 2 - Фронтенд:

```bash
cd frontend
npm run dev
```

#### Терминал 3 - Worker для обработки задач (опционально):

```bash
cd backend
source venv/bin/activate
python -m app.workers.max_worker
```

### Вариант 2: Docker (для продакшена)

```bash
docker-compose up -d
```

Сервисы будут доступны по адресам:
- Бэкенд: http://localhost:8000
- Фронтенд: http://localhost:3000
- База данных: localhost:5432

## Первоначальная настройка

### 1. Создание первого администратора

После запуска бэкенда создайте первого суперпользователя:

```bash
cd backend
source venv/bin/activate
python -m app.scripts.create_admin
```

Введите данные:
- Логин (из Active Directory)
- Пароль (локальный пароль для веб-интерфейса)
- Email
- Роль (admin/superadmin)

### 2. Настройка бота в мессенджере MAX

1. Зарегистрируйте бота в панели управления MAX
2. Получите API ключи
3. Настройте webhook URL в панели MAX: `https://your-domain.com/api/v1/max/webhook`
4. Убедитесь, что в `.env` указаны правильные `MAX_API_KEY` и `MAX_API_SECRET`

### 3. Проверка подключения к Active Directory

Убедитесь, что сервисный аккаунт имеет права на чтение пользователей из AD.

## Использование

### Для пользователей (в мессенджере MAX):

1. Найдите бота "Блик" в мессенджере
2. Нажмите `/start`
3. Введите команду `/login`
4. Введите логин и пароль от Active Directory
5. После успешной авторизации аккаунт сохраняется
6. Используйте команды:
   - `/new` - создать новую заявку
   - `/my` - просмотреть свои заявки
   - `/status <ID>` - статус конкретной заявки
   - `/help` - справка

### Для администраторов (веб-интерфейс):

1. Откройте http://localhost:3000
2. Войдите под учетной записью администратора
3. На главной странице отображаются все заявки
4. Используйте фильтры для поиска
5. Кликните на заявку для деталей:
   - Измените приоритет
   - Назначьте исполнителя
   - Обновите статус
   - Добавьте комментарий

## Структура проекта

```
blik/
├── backend/                 # Бэкенд на FastAPI
│   ├── app/
│   │   ├── api/            # API эндпоинты
│   │   ├── core/           # Конфигурация и безопасность
│   │   ├── db/             # Модели базы данных
│   │   ├── services/       # Бизнес-логика
│   │   ├── workers/        # Фоновые задачи
│   │   └── main.py         # Точка входа
│   ├── requirements.txt
│   └── .env.example
├── frontend/               # Веб-интерфейс на Vue.js
│   ├── src/
│   │   ├── components/     # Vue компоненты
│   │   ├── views/          # Страницы
│   │   ├── stores/         # Pinia хранилища
│   │   └── App.vue
│   ├── package.json
│   └── .env.example
├── docker-compose.yml      # Docker конфигурация
└── README.md
```

## API Документация

После запуска бэкенда документация API доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Безопасность

- Все пароли хранятся в хешированном виде
- JWT токены для аутентификации
- HTTPS обязателен для продакшена
- Регулярно обновляйте зависимости
- Ограничьте доступ к базе данных

## Мониторинг и логи

Логи приложения сохраняются в:
- Бэкенд: `backend/logs/app.log`
- Уровень логирования настраивается в `.env` (LOG_LEVEL)

Для просмотра логов в реальном времени:

```bash
tail -f backend/logs/app.log
```

## Troubleshooting

### Ошибка подключения к Active Directory
- Проверьте корректность параметров в `.env`
- Убедитесь, что сервисный аккаунт имеет нужные права
- Проверьте сетевую доступность AD сервера

### Бот не получает сообщения
- Проверьте правильность настройки webhook в панели MAX
- Убедитесь, что сервер доступен из интернета
- Проверьте логи бэкенда на наличие ошибок

### Веб-интерфейс не подключается к API
- Проверьте `VITE_API_URL` в frontend/.env
- Убедитесь, что бэкенд запущен
- Проверьте CORS настройки в бэкенде

## Разработка

### Запуск тестов

```bash
cd backend
pytest
```

### Линтинг кода

```bash
cd backend
flake8 app
black app --check
```

## Лицензия

Проект распространяется под лицензией MIT.

## Поддержка

По вопросам обращайтесь: [ваш-email@example.com](mailto:ваш-email@example.com)
