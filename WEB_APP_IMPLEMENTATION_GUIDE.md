# SkillEngine Web Application - Implementation Guide

## 🎯 Project Overview

This guide provides step-by-step instructions to implement the complete React + FastAPI web application for SkillEngine.

**Tech Stack:**
- **Backend:** FastAPI (Python) + MongoDB + Motor (async driver)
- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Database:** MongoDB
- **Real-time:** WebSocket for execution progress
- **Deployment:** Docker Compose

**Estimated Effort:** 34-47 hours (~1 week full-time)

---

## 📁 Project Structure (Already Created)

```
CreditMemoGenerationFramework/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── models/            # MongoDB models
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   └── schemas/           # Pydantic schemas
│   └── requirements.txt        # ✅ CREATED
├── frontend/                   # React frontend
│   └── src/
│       ├── api/               # API client
│       ├── components/        # React components
│       ├── pages/             # Page components
│       ├── hooks/             # Custom hooks
│       ├── types/             # TypeScript types
│       └── utils/             # Utilities
└── docker-compose.yml          # Docker configuration
```

---

## 🚀 Quick Start Commands

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Full Stack with Docker
```bash
docker-compose up --build
```

---

## 📝 Step-by-Step Implementation

### PHASE 1: FastAPI Backend (Day 1-2, 12-16 hours)

#### Step 1.1: Create `backend/app/config.py`

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "skillengine"

    # API
    api_v1_prefix: str = "/api"
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]

    # LLM
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Server
    port: int = 8000
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
```

#### Step 1.2: Create `backend/app/database.py`

```python
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


mongodb = MongoDB()


async def connect_to_mongo():
    """Connect to MongoDB on startup."""
    mongodb.client = AsyncIOMotorClient(settings.mongodb_uri)
    mongodb.db = mongodb.client[settings.database_name]
    print(f"Connected to MongoDB: {settings.database_name}")


async def close_mongo_connection():
    """Close MongoDB connection on shutdown."""
    mongodb.client.close()
    print("Closed MongoDB connection")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    return mongodb.db
```

#### Step 1.3: Create `backend/app/models/skill.py`

```python
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class SkillMetadata(BaseModel):
    total_steps: int
    has_verification: bool
    estimated_tokens: Optional[int] = None


class SkillModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    version: str = "1.0.0"
    author: str
    tags: List[str] = []
    markdown_content: str
    parsed_metadata: SkillMetadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
```

#### Step 1.4: Create `backend/app/models/execution.py`

```python
from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.skill import PyObjectId


class StepOutput(BaseModel):
    output: str
    completed_at: datetime
    verification_passed: Optional[bool] = None


class ExecutionMetadata(BaseModel):
    model_used: str
    total_tokens: Optional[int] = None
    duration_seconds: Optional[float] = None


class ExecutionModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    skill_id: str
    skill_name: str
    status: str = "pending"  # pending|running|completed|failed
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    input_variables: Dict = {}
    current_step: int = 0
    total_steps: int
    step_outputs: Dict[str, StepOutput] = {}
    final_output: Optional[str] = None
    error_message: Optional[str] = None
    execution_metadata: Optional[ExecutionMetadata] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
```

#### Step 1.5: Create `backend/app/routes/skills.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.database import get_database
from app.models.skill import SkillModel, SkillMetadata
from bson import ObjectId
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from skill_engine.parser.markdown_parser import SkillMarkdownParser

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("/", response_model=List[SkillModel])
async def list_skills(db = Depends(get_database)):
    """List all skills."""
    skills = await db.skills.find().to_list(100)
    return skills


@router.get("/{skill_id}", response_model=SkillModel)
async def get_skill(skill_id: str, db = Depends(get_database)):
    """Get skill by ID."""
    skill = await db.skills.find_one({"_id": ObjectId(skill_id)})
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.post("/", response_model=SkillModel)
async def create_skill(skill: SkillModel, db = Depends(get_database)):
    """Create new skill."""
    # Parse markdown to validate and extract metadata
    parser = SkillMarkdownParser()
    try:
        parsed_skill = parser.parse_markdown(skill.markdown_content)
        skill.parsed_metadata = SkillMetadata(
            total_steps=parsed_skill.get_total_steps(),
            has_verification=any(step.verification for step in parsed_skill.steps),
            estimated_tokens=parsed_skill.metadata.estimated_tokens
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid skill format: {str(e)}")

    skill_dict = skill.dict(by_alias=True, exclude={"id"})
    result = await db.skills.insert_one(skill_dict)
    skill.id = result.inserted_id
    return skill


@router.put("/{skill_id}", response_model=SkillModel)
async def update_skill(skill_id: str, skill: SkillModel, db = Depends(get_database)):
    """Update skill."""
    skill.updated_at = datetime.now()
    skill_dict = skill.dict(by_alias=True, exclude={"id"})
    result = await db.skills.update_one(
        {"_id": ObjectId(skill_id)},
        {"$set": skill_dict}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Skill not found")
    return await get_skill(skill_id, db)


@router.delete("/{skill_id}")
async def delete_skill(skill_id: str, db = Depends(get_database)):
    """Delete skill."""
    result = await db.skills.delete_one({"_id": ObjectId(skill_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Skill not found")
    return {"message": "Skill deleted"}
```

#### Step 1.6: Create `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import skills  # We'll create this


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title="SkillEngine API",
    description="API for managing and executing LLM skills",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(skills.router)


@app.get("/")
async def root():
    return {"message": "SkillEngine API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
```

---

### PHASE 2: React Frontend (Day 3-4, 10-14 hours)

#### Step 2.1: Initialize React with Vite

```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install react-router-dom axios @tanstack/react-query lucide-react
```

#### Step 2.2: Configure Tailwind (`frontend/tailwind.config.js`)

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

#### Step 2.3: Create `frontend/src/api/client.ts`

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);
```

#### Step 2.4: Create `frontend/src/api/skillsApi.ts`

```typescript
import { apiClient } from './client';

export interface Skill {
  _id?: string;
  name: string;
  description: string;
  version: string;
  author: string;
  tags: string[];
  markdown_content: string;
  parsed_metadata: {
    total_steps: number;
    has_verification: boolean;
    estimated_tokens?: number;
  };
  created_at?: string;
  updated_at?: string;
  is_active: boolean;
}

export const skillsApi = {
  // List all skills
  list: async (): Promise<Skill[]> => {
    const response = await apiClient.get('/api/skills');
    return response.data;
  },

  // Get skill by ID
  get: async (id: string): Promise<Skill> => {
    const response = await apiClient.get(`/api/skills/${id}`);
    return response.data;
  },

  // Create new skill
  create: async (skill: Skill): Promise<Skill> => {
    const response = await apiClient.post('/api/skills', skill);
    return response.data;
  },

  // Update skill
  update: async (id: string, skill: Skill): Promise<Skill> => {
    const response = await apiClient.put(`/api/skills/${id}`, skill);
    return response.data;
  },

  // Delete skill
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/skills/${id}`);
  },
};
```

#### Step 2.5: Create `frontend/src/App.tsx`

```typescript
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import SkillsManagement from './pages/admin/SkillsManagement';
import BrowseSkills from './pages/user/BrowseSkills';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                SkillEngine
              </h1>
              <nav className="flex gap-4">
                <Link to="/" className="text-gray-600 hover:text-gray-900">
                  Home
                </Link>
                <Link to="/admin" className="text-gray-600 hover:text-gray-900">
                  Admin
                </Link>
                <Link to="/skills" className="text-gray-600 hover:text-gray-900">
                  Skills
                </Link>
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/admin" element={<SkillsManagement />} />
            <Route path="/skills" element={<BrowseSkills />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
```

---

### PHASE 3: Docker Compose (Day 5, 4-6 hours)

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: skillengine-mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    networks:
      - skillengine-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: skillengine-backend
    ports:
      - "8000:8000"
    depends_on:
      - mongodb
    environment:
      MONGODB_URI: mongodb://admin:password@mongodb:27017/skillengine?authSource=admin
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    volumes:
      - ./skills:/app/skills
      - ./backend:/app
    networks:
      - skillengine-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: skillengine-frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
    environment:
      VITE_API_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - skillengine-network

networks:
  skillengine-network:
    driver: bridge

volumes:
  mongodb_data:
```

---

## 📋 Complete File Checklist

### Backend (Priority Order)
- [x] `backend/requirements.txt` - Dependencies
- [ ] `backend/app/config.py` - Configuration
- [ ] `backend/app/database.py` - MongoDB connection
- [ ] `backend/app/models/skill.py` - Skill model
- [ ] `backend/app/models/execution.py` - Execution model
- [ ] `backend/app/routes/skills.py` - Skills CRUD
- [ ] `backend/app/routes/executions.py` - Executions API
- [ ] `backend/app/routes/websocket.py` - WebSocket streaming
- [ ] `backend/app/services/llm_service.py` - SkillProcessor wrapper
- [ ] `backend/app/main.py` - FastAPI app
- [ ] `backend/Dockerfile` - Docker build
- [ ] `backend/.env.example` - Environment template

### Frontend (Priority Order)
- [ ] `frontend/package.json` - Dependencies
- [ ] `frontend/vite.config.ts` - Vite config
- [ ] `frontend/tailwind.config.js` - Tailwind config
- [ ] `frontend/src/api/client.ts` - Axios setup
- [ ] `frontend/src/api/skillsApi.ts` - Skills API
- [ ] `frontend/src/App.tsx` - Main app
- [ ] `frontend/src/main.tsx` - Entry point
- [ ] `frontend/src/pages/Home.tsx` - Home page
- [ ] `frontend/src/pages/admin/SkillsManagement.tsx` - Admin panel
- [ ] `frontend/src/pages/user/BrowseSkills.tsx` - Skill catalog
- [ ] `frontend/src/hooks/useWebSocket.ts` - WebSocket hook
- [ ] `frontend/Dockerfile` - Docker build
- [ ] `frontend/.env.example` - Environment template

### Root
- [ ] `docker-compose.yml` - Docker orchestration
- [ ] `README.md` - Main documentation
- [ ] `.env.example` - Global environment template

---

## 🧪 Testing Your Implementation

### Test Backend API
```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/api/skills
```

### Test Frontend
```bash
# Start frontend
cd frontend
npm run dev

# Visit http://localhost:5173
```

### Test Full Stack
```bash
# Start everything
docker-compose up --build

# Visit:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# MongoDB: mongodb://localhost:27017
```

---

## 🚧 Implementation Order (Recommended)

### Week 1 - MVP
1. ✅ Backend foundation (config, database, models)
2. ✅ Skills CRUD API
3. ✅ Frontend foundation (React, routing, API client)
4. ✅ Admin: Skills list and create skill pages
5. ✅ User: Browse skills page
6. ✅ Docker Compose setup

### Week 2 - Core Features
7. Skill Editor with Markdown preview
8. Execution API + WebSocket
9. Execute Skill page with progress
10. Results Viewer

### Week 3 - Polish
11. File upload management
12. Execution history
13. Export functionality
14. Error handling & loading states
15. Mobile responsive design

---

## 📚 Additional Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Motor (Async MongoDB):** https://motor.readthedocs.io/
- **React Router:** https://reactrouter.com/
- **Tailwind CSS:** https://tailwindcss.com/
- **WebSocket with FastAPI:** https://fastapi.tiangolo.com/advanced/websockets/

---

## 💡 Next Steps

1. **Start with backend foundation** - Create the files listed in Phase 1
2. **Test each endpoint** using Swagger UI at `http://localhost:8000/docs`
3. **Build frontend incrementally** - Start with pages, then add components
4. **Integrate as you go** - Connect frontend to backend endpoints one by one
5. **Deploy with Docker** when basic features work

**Good luck building your SkillEngine web app! 🚀**

For questions or issues, refer to the detailed plan at: `C:\Users\atulv\.claude\plans\peppy-stirring-firefly.md`
