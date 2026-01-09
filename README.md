Here’s a **clean, professional README** you can drop straight into your repo.
It’s written like a real-world project (not AI-ish, not fluffy).

You can copy-paste this into `README.md`.

---

# 🧭 Choose Your Own Adventure – AI Story Generator

A full-stack **Choose Your Own Adventure** application that generates interactive stories using AI.
Users select a theme, receive a dynamically generated story, and make choices that shape the narrative as it unfolds.

---

## ✨ Features

* 🎭 AI-generated interactive stories
* 🧩 Branching story paths based on user choices
* ⚡ Background job processing for story generation
* 🧠 Persistent story nodes stored in a database
* 🌐 REST API built with FastAPI
* 💻 Modern frontend (React)
* 🔐 Secure environment variable handling

---

## 🏗️ Tech Stack

### Backend

* **Python**
* **FastAPI**
* **SQLAlchemy**
* **Pydantic**
* **PostgreSQL / SQLite**
* **BackgroundTasks**
* **OpenAI API**

### Frontend

* **React**
* **Axios**
* **Vite**
* **React Router**

---

## 📂 Project Structure

```
choose-your-own-adventure/
├── backend/
│   ├── app/
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── core/
│   ├── main.py
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   └── package.json
│
└── README.md
```

---

## 🔐 Environment Variables

### ⚠️ IMPORTANT

The real `.env` file is **NOT** committed to GitHub.

Use `.env.example` as a template.

### `.env.example`

```env
DATABASE_URL=
SECRET_KEY=
OPENAI_API_KEY=
JWT_SECRET=
```

Create your own `.env` locally and fill in the values.

---

## 🚀 Getting Started

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/choose-your-own-adventure.git
cd choose-your-own-adventure
```

---

### 2️⃣ Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

Create `.env` (DO NOT commit it):

```bash
cp .env.example .env
```

Run the backend:

```bash
uvicorn main:app --reload
```

API docs will be available at:

```
http://localhost:8000/docs
```

---

### 3️⃣ Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

## 🔄 Story Generation Flow

1. User selects a story theme
2. Frontend sends request to `/stories/create`
3. Backend creates a background job
4. AI generates the story nodes
5. User receives choices and continues the story

---

## 🛡️ Security Notes

* `.env` is ignored via `.gitignore`
* Secrets are never committed
* GitHub push protection is enabled
* Production uses platform environment variables (Render, etc.)

---

## 🧪 API Example

### Create a story

```http
POST /stories/create
Content-Type: application/json

{
  "theme": "Dark fantasy medieval world"
}
```

---

## 📌 Future Improvements

* User authentication
* Save & resume stories
* Multiple difficulty levels
* Story sharing
* Image generation per story node

---

## 👤 Author

**Tavan Mohammed**
Full-stack developer & software engineering student

