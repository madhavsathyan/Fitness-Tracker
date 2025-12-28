# 🏥 Health & Fitness Monitor Dashboard

**Your Personal Health Intelligence Platform**

A full-stack health and fitness tracking application with an interactive real-time dashboard.

> 📚 **CA-2 Assignment** | CSR210 - Advanced Programming and Database Systems

---

## 📋 Table of Contents

- [About This Project](#-about-this-project)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Endpoints](#-api-endpoints)
- [Test Accounts](#-test-accounts)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 🎯 About This Project

This is a **proof of concept** project built for my college CA-2 examination. It demonstrates a full-stack health monitoring application with:

- ✅ A REST API backend with authentication
- ✅ A modern React frontend with real-time updates
- ✅ Interactive data visualizations
- ✅ Complete CRUD operations
- ✅ JWT-based security

> ⚠️ **Note:** This is a prototype for educational purposes, not intended for production use.

---

## ✨ Features

### Health Tracking Modules

| Module | What You Can Track |
|--------|-------------------|
| 🏋️ **Workouts** | Cardio, Strength, Flexibility, Sports |
| 🍽️ **Nutrition** | Calories, Protein, Carbs, Fat |
| 😴 **Sleep** | Duration and Quality |
| 💧 **Hydration** | Daily water intake |
| ⚖️ **Weight** | Progress and BMI trends |

### Dashboard Charts (6 Types)

| Chart Type | What It Shows |
|------------|---------------|
| 📉 Line Chart | Weight progress over time |
| 📊 Bar Chart | Weekly workout summary |
| 🍩 Donut Chart | Macronutrient breakdown |
| 📈 Area Chart | Daily calorie intake by meal |
| ⏱️ Gauge Chart | Water intake progress |
| 🔵 Scatter Plot | Sleep trends with quality markers |

### Real-Time Updates

- 🔄 Dashboard auto-refreshes every 2 seconds
- 🔔 Toast notifications for new data
- ⚡ No page reload required

---

## 🛠️ Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| FastAPI | Python REST API framework |
| SQLite | File-based database |
| SQLAlchemy | ORM for database operations |
| Pydantic | Data validation |
| Uvicorn | ASGI server |
| python-jose | JWT authentication |
| passlib | Password hashing |

### Frontend

| Technology | Purpose |
|------------|---------|
| React 19 | UI framework |
| TypeScript | Type-safe JavaScript |
| Vite | Build tool |
| TailwindCSS 4 | CSS framework |
| Plotly.js | Interactive charts |
| Recharts | React charting |
| Framer Motion | Animations |
| Zustand | State management |

---

## 📁 Project Structure

```
health_fitness_monitor/
│
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── database.py       # Database config
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── routers/          # API routes
│   │   ├── services/         # Business logic
│   │   └── utils/            # Helper functions
│   ├── data/
│   │   └── health_fitness.db # SQLite database
│   └── requirements.txt      # Python dependencies
│
├── frontend-react/
│   ├── src/
│   │   ├── main.tsx          # React entry point
│   │   ├── App.tsx           # Main component
│   │   ├── pages/            # Page components
│   │   ├── components/       # UI components
│   │   ├── services/         # API client
│   │   ├── stores/           # State management
│   │   └── index.css         # Styles
│   ├── package.json          # Node dependencies
│   └── vite.config.ts        # Vite config
│
├── run.py                    # Start both servers
└── README.md                 # You are here!
```

---

## 🚀 Getting Started

### Prerequisites

Make sure you have installed:

- Python 3.9 or higher
- Node.js 18 or higher
- npm (comes with Node.js)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/madhavsathyan/Fitness-Tracker.git
cd health_fitness_monitor
```

### Step 2: Set Up the Backend

Open a terminal and run:

```bash
# Go to backend folder
cd backend

# Install Python packages
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 3: Set Up the Frontend

Open a **new terminal** and run:

```bash
# Go to frontend folder
cd frontend-react

# Install Node packages
npm install

# Start the dev server
npm run dev
```

You should see:

```
VITE v5.x.x  ready

➜  Local:   http://localhost:5173/
```

### Step 4: Open the App

| What | URL |
|------|-----|
| Dashboard | http://localhost:5173 |
| API Docs | http://localhost:8000/docs |

**🎉 You're all set!**

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login (get JWT) |
| GET | `/api/auth/me` | Get current user |

### Workouts

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/workouts/` | Create workout |
| GET | `/api/workouts/` | List workouts |
| GET | `/api/workouts/{id}` | Get one workout |
| PUT | `/api/workouts/{id}` | Update workout |
| DELETE | `/api/workouts/{id}` | Delete workout |

### Nutrition

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/nutrition/` | Log meal |
| GET | `/api/nutrition/` | List meals |
| GET | `/api/nutrition/daily/{date}` | Daily summary |
| PUT | `/api/nutrition/{id}` | Update meal |
| DELETE | `/api/nutrition/{id}` | Delete meal |

### Other Endpoints

| Resource | Base URL | Extra Endpoints |
|----------|----------|-----------------|
| Sleep | `/api/sleep/` | `/average` |
| Water | `/api/water/` | `/daily/{date}` |
| Weight | `/api/weight/` | `/trend` |
| Analytics | `/api/analytics/` | Dashboard data |

---

## 🔑 Test Accounts

Use these to log in:

| Username | Password | Role |
|----------|----------|------|
| admin | password123 | Admin |
| demo_user | password123 | User |

---

## 🔧 Troubleshooting

### Backend won't start

```bash
# Kill any process using port 8000
lsof -ti:8000 | xargs kill -9

# Try again
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend won't start

```bash
# Delete and reinstall packages
cd frontend-react
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Database errors

```bash
# Delete the database (it will recreate automatically)
cd backend/data
rm health_fitness.db

# Restart the backend
```

### Permission errors with pip

```bash
pip install -r requirements.txt --user
```

---

## ⚡ Quick Commands

```bash
# Start Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Start Frontend
cd frontend-react && npm run dev

# Stop either server
Ctrl + C
```

---

## 🎓 Project Context

This project was built as part of **CA-2 (Continuous Assessment)** for:

- **Course:** CSR210 - Advanced Programming and Database Systems
- **Type:** Proof of Concept / Prototype
- **Purpose:** Demonstrate full-stack development skills

---

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ for learning**
