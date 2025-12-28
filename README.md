# Health & Fitness Monitor Dashboard

A full-stack health and fitness tracking application with interactive real-time dashboard.

**CA-2 Assignment | CSR210 | Advanced Programming and Database Systems**

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | Modern Python REST API framework |
| **SQLite** | Lightweight file-based database |
| **SQLAlchemy** | ORM for database operations |
| **Pydantic** | Data validation and schemas |
| **Uvicorn** | ASGI server |
| **python-jose** | JWT authentication |
| **passlib[bcrypt]** | Password hashing |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 19** | Modern UI framework |
| **TypeScript** | Type-safe JavaScript |
| **Vite** | Lightning-fast build tool |
| **TailwindCSS 4** | Utility-first CSS framework |
| **Plotly.js** | Interactive charts and graphs |
| **Recharts** | React charting library |
| **Framer Motion** | Animation library |
| **Zustand** | State management |
| **React Router** | Client-side routing |
| **Axios** | HTTP client |

---

## 📊 Features

### Health Tracking
- 💪 **Workouts** - Log cardio, strength, flexibility, and sports activities
- 🍽️ **Nutrition** - Track meals with macronutrients (calories, protein, carbs, fat)
- 😴 **Sleep** - Record sleep duration and quality
- 💧 **Water Intake** - Monitor daily hydration
- ⚖️ **Weight** - Track weight and BMI progress

### Dashboard Visualizations (6 Chart Types)
1. **Line Chart** - Weight progress over time
2. **Bar Chart** - Weekly workout summary by type
3. **Pie/Donut Chart** - Macronutrient distribution
4. **Area Chart** - Daily calorie intake by meal
5. **Gauge Chart** - Water intake progress
6. **Scatter with Markers** - Sleep trends with quality indicators

### Real-Time Updates
- Dashboard auto-refreshes every 2 seconds
- Toast notifications for new data
- No page reload required

### API Features
- Full CRUD operations on all resources
- JWT-based authentication
- Role-based access (User/Admin)
- Swagger/OpenAPI documentation

---

## 📁 Project Structure

```
health_fitness_monitor/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── database.py          # SQLAlchemy configuration
│   │   ├── models/              # ORM models (6 tables)
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API endpoints (11+ routers)
│   │   ├── services/            # Business logic
│   │   └── utils/               # Helpers
│   ├── data/
│   │   └── health_fitness.db    # SQLite database
│   └── requirements.txt         # Python dependencies
│
├── frontend-react/              # React + Vite frontend
│   ├── src/
│   │   ├── main.tsx            # React entry point
│   │   ├── App.tsx             # Main app component
│   │   ├── pages/              # Page components
│   │   ├── components/         # Reusable UI components
│   │   ├── services/           # API client
│   │   ├── stores/             # Zustand state management
│   │   └── index.css           # Global styles
│   ├── public/                 # Static assets
│   ├── package.json            # Node dependencies
│   └── vite.config.ts          # Vite configuration
│
├── frontend/                    # Legacy Dash frontend (optional)
│   ├── app.py                  # Main Dash application
│   ├── layouts/                # Page layouts
│   ├── callbacks/              # Interactivity handlers
│   └── services/               # API client
│
├── run.py                      # Start both servers
├── demo_script.md              # 5-minute demo guide
├── video_script.md             # Explainer video script
└── README.md                   # This file
```

---

## 🚀 First Time Setup (For New Users)

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <your-repo-url>

# Navigate into the project
cd health_fitness_monitor
```

### Step 2: Open in VSCode

```bash
# Open the project in VSCode
code .
```

Or manually: **File → Open Folder** → Select `health_fitness_monitor`

### Step 3: Open Integrated Terminal

In VSCode, open the integrated terminal:
- **Mac**: `⌃` + `` ` `` (Control + Backtick)
- **Windows**: `Ctrl` + `` ` ``
- Or: **View → Terminal**

### Step 4: Install Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# If you get permission errors, use:
pip install -r requirements.txt --user
```

### Step 5: Install Frontend Dependencies

```bash
# Open a NEW terminal (keep the first one open)
# In VSCode: Click the '+' icon in terminal panel

# Navigate to frontend-react directory
cd frontend-react

# Install Node.js dependencies (this may take a few minutes)
npm install
```

### Step 6: Run Both Servers

**In Terminal 1 (Backend):**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

**In Terminal 2 (Frontend):**
```bash
cd frontend-react
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 7: Access the Application

Open your browser and visit:
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

### 🎉 You're all set!

---

## 🚀 Quick Start (For Returning Users)

### Prerequisites
- **Python 3.9+** (for backend)
- **Node.js 18+** and **npm** (for frontend)
- **pip** (Python package manager)

### Installation

#### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt
```

#### 2. Frontend Setup

```bash
# Navigate to frontend-react directory
cd frontend-react

# Install Node.js dependencies
npm install
```

### Run the Application

**Option 1: Manual startup (Recommended for Development)**

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend-react
npm run dev
```

**Option 2: Using run script:**
```bash
python3 run.py
```

### Access Points
| Service | URL | Description |
|---------|-----|-------------|
| **React Dashboard** | http://localhost:5173 | Main frontend application (Vite dev server) |
| **API Documentation** | http://localhost:8000/docs | Interactive Swagger UI |
| **API Documentation (ReDoc)** | http://localhost:8000/redoc | Alternative API docs |
| **Backend API** | http://localhost:8000 | REST API endpoints |

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create new user |
| POST | `/api/auth/login` | Login, get JWT token |
| GET | `/api/auth/me` | Get current user |

### Workouts
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/workouts/` | Create workout |
| GET | `/api/workouts/` | List all workouts |
| GET | `/api/workouts/{id}` | Get workout by ID |
| PUT | `/api/workouts/{id}` | Update workout |
| DELETE | `/api/workouts/{id}` | Delete workout |

### Nutrition
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/nutrition/` | Log meal |
| GET | `/api/nutrition/` | List all meals |
| GET | `/api/nutrition/daily/{date}` | Daily summary |
| PUT | `/api/nutrition/{id}` | Update meal |
| DELETE | `/api/nutrition/{id}` | Delete meal |

### Other Resources
- `/api/sleep/` - Sleep records (+ `/average` endpoint)
- `/api/water/` - Water intake (+ `/daily/{date}` endpoint)
- `/api/weight/` - Weight logs (+ `/trend` endpoint)
- `/api/analytics/` - Dashboard analytics

---

## 🔑 Test Accounts

| Username | Password | Role |
|----------|----------|------|
| `admin` | `password123` | Admin |
| `demo_user` | `password123` | User |

---

## 📈 Database Statistics

| Table | Records |
|-------|---------|
| Users | 53 |
| Workouts | 1,400+ |
| Meals | 9,000+ |
| Sleep Records | 4,000+ |
| Water Intakes | 3,500+ |
| Weight Logs | 650+ |

**Total: 18,000+ sample records**

---

## 🎬 Demo Resources

- **5-Minute Demo Script**: See `demo_script.md`
- **Explainer Video Script**: See `video_script.md`

---

## ️ Troubleshooting

### Backend won't start
```bash
# Make sure you're in the backend directory
cd backend

# Check if port 8000 is already in use
lsof -ti:8000 | xargs kill -9  # Kill any process on port 8000

# Try running again
uvicorn app.main:app --reload --port 8000
```

### Frontend won't start
```bash
# Make sure you're in the frontend-react directory
cd frontend-react

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Try running again
npm run dev
```

### Database errors
```bash
# The database will be created automatically
# If you have issues, delete and let it recreate
cd backend/data
rm health_fitness.db
# Then restart the backend server
```

### Python package installation issues
```bash
# Use --user flag
pip install -r requirements.txt --user

# Or upgrade pip first
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📋 Quick Reference (Cheat Sheet)

### Start Development Servers
```bash
# Backend (Terminal 1)
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend-react && npm run dev
```

### URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Stop Servers
- Press `Ctrl + C` in each terminal

### Test Login
- Username: `admin`
- Password: `password123`

---

## 👥 Contributors

Built as part of the CSR210 - Advanced Programming and Database Systems course assignment.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note**: This is an educational project created for academic purposes.
