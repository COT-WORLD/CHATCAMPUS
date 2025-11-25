# CHATCAMPUS 🚀

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/COT-WORLD/CHATCAMPUS)  
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

### Real-Time Chat Application (React + TypeScript + Django REST Framework)

CHATCAMPUS is a **full-stack real-time chat application** where users can create or join chat rooms, send messages, and communicate instantly.  
It features **Google SSO**, **WebSocket messaging**, **media uploads**, and **activity tracking** for enhanced collaboration.

---

## 📺 Demo / Website

Access the live application: [CHATCAMPUS](https://chatcampus.vercel.app/)

> For demo purposes, use:
>
> - **Email**: `jasmine@gmail.com`
> - **Password**: `securepass123`

---

## 📋 Table of Contents

- [Features](#✨-features)
- [Tech Stack](#🛠-tech-stack)
- [Getting Started](#⚙️-getting-started)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Configuration](#🔧-configuration)
- [Testing](#🧪-testing)
- [Deployment](#🚀-deployment)
- [Contributing](#🤝-contributing)
- [License](#📝-license)
- [Author](#👨‍💻-author)

---

## ✨ Features

**Frontend:**

- 🔥 Real-time group chat with WebSockets
- 🧑‍💻 User authentication (Email + Google SSO)
- 🏫 Create or join chat rooms
- 🎨 Responsive modern UI with React + Tailwind
- 📝 Form validation with React Hook Form + Zod

**Backend:**

- 🌐 Django REST Framework APIs (Topics, Rooms, Messages, Users)
- ⚙️ Modular architecture with Django Apps
- 🔒 JWT authentication + OAuth2 (Google SSO)
- 🛡 Security tests (CSRF, SQL Injection, headers)
- 📈 Optimized queries using Django Debug Toolbar
- ☁️ Media storage with Cloudinary
- 🔄 Async tasks with Celery + Redis

---

## 🛠 Tech Stack

**Frontend:**

- React
- TypeScript
- React Query (TanStack)
- Axios
- React Hook Form + Zod
- React Router v6
- OAuth2 Google SSO
- WebSocket / Socket.io
- Tailwind CSS
- Vite

**Backend:**

- Python 3.x
- Django
- Django REST Framework
- Django Channels (WebSockets)
- PostgreSQL
- Redis (caching + channels)
- Celery (async tasks)
- Cloudinary (media storage)
- JWT authentication
- Django Allauth (Google OAuth2)
- Django Debug Toolbar

---

## ⚙️ Getting Started

### Backend Setup

**Prerequisites:**

- Python 3.x
- PostgreSQL
- Redis
- pip

**Steps:**

1. Clone the repository:

```bash
git clone https://github.com/COT-WORLD/CHATCAMPUS.git
cd backend
```

2. Create and activate virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate # Windows: venvScriptsactivate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file (use `.env.example` as reference):

```env
EXTERNAL_DATABASE_URL=postgres://<username>:<password>@<host>:<port>/<database>
DJANGO_SECRET_KEY="YOUR_SECRET_KEY"
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
GOOGLE_OAUTH2_CLIENT_ID=<YOUR_GOOGLE_CLIENT_ID>
GOOGLE_OAUTH2_SECRET=<YOUR_GOOGLE_CLIENT_SECRET>
DJANGO_SUPER_USER_USERNAME=admin
DJANGO_SUPER_USER_EMAIL=admin@example.com
DJANGO_SUPER_USER_PASSWORD=securepassword123
JWT_TOKEN_SECRET_KEY=JWT_SECRET_KEY
CLOUDINARY_NAME=<YOUR_CLOUDINARY_NAME>
CLOUDINARY_API_KEY=<YOUR_CLOUDINARY_API_KEY>
CLOUDINARY_API_SECRET=<YOUR_CLOUDINARY_API_SECRET>
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:4173
CSRF_WEBSOCKET_ORIGIN=http://localhost:8000
```

5. Apply migrations and collect static files:

```bash
python manage.py migrate
python manage.py collectstatic
```

6. Run the server:

```bash
python manage.py runserver
```

---

### Frontend Setup

**Prerequisites:**

- Node.js v18+

**Steps:**

1. Navigate to frontend:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Create `.env` file:

```env
VITE_GOOGLE_CLIENT_ID=<YOUR_GOOGLE_CLIENT_ID>
VITE_API_URL=http://localhost:8000/api/
VITE_WEBSOCKET_URL=ws://localhost:8000
```

4. Start development server:

```bash
npm run dev
```

---

## 🔧 Configuration

- Redis server must be running.
- `.env.example` provides all required environment variables.
- First run after migrations automatically creates:
  - `Site` instance
  - Google `SocialApp`
  - Django superuser

---

## 🧪 Testing

**Backend Tests:**

```bash
python manage.py test
```

**Security Tests:**

- SQL Injection prevention
- CSRF protection
- Security headers validation

---

## 🚀 Deployment

- **Backend**: Gunicorn + Nginx + WhiteNoise (Gzip/Brotli compression)
- **Frontend**: Vite build served via CDN / Vercel
- **Media**: Cloudinary for fast global delivery
- **Async tasks**: Celery + Redis
- Supports auto-creation of superuser & Google Social App on first deploy

> ⚠️ On free hosting (Render), first request may take ~50s after inactivity. This is infrastructure-related, not code.

---

## 📝 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file.

---

## 👨‍💻 Author

COT_WORLD – Passionate software developer building scalable full-stack applications.  
Connect on [LinkedIn](https://www.linkedin.com/in/hardik-chaudhary/)
