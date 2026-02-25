# ✦ NexusAI — ChatGPT Clone (Django)

A full-featured ChatGPT-like web app built with Django + OpenAI API.

## Features
- 🔐 User authentication (register, login, logout)
- 💬 Multiple conversations with persistent history (SQLite)
- 🤖 Supports GPT-4o, GPT-4o Mini, GPT-4 Turbo, GPT-3.5 Turbo
- ✏️ Rename & delete conversations
- 💡 Suggestion cards on the welcome screen
- 📱 Clean, dark-mode UI (NexusAI theme)
- 🟡 Demo mode works WITHOUT an API key

---

## Quick Start

### 1. Create & activate virtual environment
```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your OpenAI API key
```bash
# macOS/Linux
export OPENAI_API_KEY="sk-your-key-here"

# Windows
set OPENAI_API_KEY=sk-your-key-here
```
> Without a key, the app runs in **Demo Mode** (echoes your message back).

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create a superuser (optional, for admin panel)
```bash
python manage.py createsuperuser
```

### 6. Start the development server
```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## Project Structure
```
chatgpt_clone/
├── chatgpt_clone/       # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── chat/                # Main app
│   ├── models.py        # Conversation + Message models
│   ├── views.py         # All view logic + OpenAI calls
│   ├── urls.py          # URL routing
│   ├── admin.py
│   └── templates/chat/
│       ├── index.html   # Main chat UI
│       ├── login.html
│       └── register.html
├── manage.py
├── requirements.txt
└── README.md
```

## API Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/send/` | Send a message |
| POST | `/api/conversations/new/` | Create new conversation |
| GET  | `/api/conversations/<id>/messages/` | Get messages |
| DELETE | `/api/conversations/<id>/delete/` | Delete conversation |
| PATCH | `/api/conversations/<id>/rename/` | Rename conversation |

## Production Deployment
1. Set `DEBUG = False` in settings.py
2. Set a strong `SECRET_KEY` via environment variable
3. Add your domain to `ALLOWED_HOSTS`
4. Use `gunicorn` + nginx for serving
5. Run `python manage.py collectstatic`
