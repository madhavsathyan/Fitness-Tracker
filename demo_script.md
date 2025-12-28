# Demo Script - Health & Fitness Monitor Dashboard
## CA-2 Assignment | 5-Minute Demonstration

---

## 🎬 Before You Start

### Ensure Both Servers Are Running:
```bash
# Option 1: Using run script
python run.py

# Option 2: Manual startup
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
python app.py
```

### URLs to Keep Open:
- **Dashboard**: http://localhost:8050
- **API Docs (Swagger)**: http://localhost:8000/docs

---

## 📋 Demo Script (5 Minutes)

### Step 1: Repository Overview (1 minute)

**What to Say:**
> "Let me start by showing you the project structure. This Health & Fitness Monitor is built with a clean separation of concerns..."

**What to Show:**
1. Open GitHub/project folder
2. Point out key directories:
   - `backend/` - FastAPI REST API
   - `frontend/` - Dash dashboard
   - `backend/app/models/` - SQLAlchemy ORM models
   - `backend/app/routers/` - API endpoints

**Key Points:**
- "Backend uses FastAPI with SQLite database"
- "Frontend uses Plotly Dash for interactive visualizations"
- "Real-time updates every 2 seconds"

---

### Step 2: System Architecture (30 seconds)

**What to Say:**
> "Here's how the components communicate..."

**Architecture Flow:**
```
User → Dash Frontend (8050) → REST API (8000) → SQLite Database
                ↑                    ↓
                └──── JSON Data ─────┘
```

**Key Points:**
- "RESTful API with full CRUD operations"
- "Dash uses interval component for auto-refresh"
- "All data persisted in SQLite"

---

### Step 3: Live Dashboard Demo (2 minutes)

**What to Say:**
> "Now let me show you the live dashboard..."

**Actions:**
1. **Show Dashboard** (http://localhost:8050/dashboard)
   - Point out the 4 summary cards (Calories, Workouts, Sleep, Water)
   - Show the 6 different charts

2. **Highlight Chart Types** (meets 3+ requirement):
   - "Line chart for weight trends"
   - "Bar chart for weekly workouts"
   - "Pie/Donut chart for macronutrients"
   - "Area chart for daily calories"
   - "Gauge for water intake"
   - "Line with markers for sleep trends"

3. **Show Database Record Count:**
   > "The database contains over 9,000 sample records across all tables"

---

### Step 4: API CRUD Demonstration (1 minute)

**What to Say:**
> "Let me demonstrate the API in action with a CREATE operation..."

**Actions:**

1. **Open API Docs** (http://localhost:8000/docs)

2. **POST a New Workout:**
   - Click on `POST /api/workouts/`
   - Click "Try it out"
   - Enter this JSON:
   ```json
   {
     "user_id": 1,
     "workout_type": "cardio",
     "workout_name": "Live Demo Run",
     "duration_minutes": 25,
     "calories_burned": 300,
     "workout_date": "2025-12-26"
   }
   ```
   - Click "Execute"
   - Show the 201 Created response

3. **Show Real-Time Update:**
   > "Now watch the dashboard update automatically..."
   - Switch to dashboard
   - Point to the workout bar chart updating
   - Show toast notification appearing

4. **Quick DELETE demo** (optional):
   - Delete the workout just created
   - Show dashboard updates again

---

### Step 5: Wrap-Up (30 seconds)

**What to Say:**
> "To summarize, this application demonstrates:
> 1. A fully functional RESTful API with CRUD operations
> 2. Six different interactive visualizations
> 3. Real-time dashboard updates without page refresh
> 4. Clean code organization with proper separation of concerns
> 
> The code is available on GitHub. Thank you!"

---

## 🎯 Key Points to Emphasize

| Requirement | How We Meet It |
|-------------|----------------|
| 50+ sample records | ✅ 9,000+ records |
| 3+ chart types | ✅ 6 chart types |
| Real-time updates | ✅ 2-second interval refresh |
| CRUD operations | ✅ Full CRUD on all resources |
| Clean code | ✅ Separated models/schemas/routers |

---

## ⚠️ Troubleshooting

**If dashboard is blank:**
- Ensure backend is running on port 8000
- Check browser console for errors
- Try hard refresh (Cmd+Shift+R)

**If API returns errors:**
- Verify database exists at `backend/data/health_fitness.db`
- Run `python -m app.utils.seed_data` to reseed

**If servers won't start:**
- Check if ports 8000/8050 are in use
- Kill existing processes: `pkill -f uvicorn; pkill -f "python app.py"`
