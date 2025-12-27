# Studio TZ - Complete Project Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [How It Works](#how-it-works)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Core Features](#core-features)
6. [AI Agents & Their Roles](#ai-agents--their-roles)
7. [API Endpoints](#api-endpoints)
8. [Frontend Components](#frontend-components)
9. [User Journey](#user-journey)
10. [File Structure](#file-structure)
11. [Database & Storage](#database--storage)
12. [Authentication](#authentication)

---

## 🎯 Project Overview

**Studio TZ** (also known as **NCD INAI**) is an AI-powered website builder that transforms natural language descriptions into production-ready websites. Users simply describe what kind of website they want in plain English, and the AI generates complete HTML, CSS, and JavaScript code.

### What Makes It Special?
- **Zero Coding Required**: Users describe their needs in natural language
- **Intelligent Understanding**: AI identifies business domain and asks relevant questions
- **Visual Blueprint**: Preview website structure before generation
- **Live Editing**: Chat-based modifications with surgical precision
- **Production Ready**: Generates clean, downloadable code
- **Cloud Storage**: Files stored securely in Cloudflare R2
- **User Accounts**: Clerk authentication with user data isolation
- **Persistent Data**: PostgreSQL database for session management

---

## 🔄 How It Works

### Step-by-Step Process:

```mermaid
graph TD
    A[User Signs In with Clerk] --> B[User Describes Website]
    B --> C[AI Identifies Domain]
    C --> D[AI Asks Relevant Questions]
    D --> E[User Answers Questions]
    E --> F[AI Creates Blueprint]
    F --> G[User Reviews Blueprint]
    G --> H[AI Generates Website]
    H --> I[Files Saved to R2 Storage]
    I --> J[Metadata Saved to Database]
    J --> K[User Edits via Chat]
    K --> L[Download Complete Website]
```

### Detailed Flow:

1. **User Authentication**
   - User signs in with Clerk (Google, GitHub, Email)
   - User record created in PostgreSQL database
   - Secure session with JWT tokens

2. **Session Creation**
   - User starts by creating a new session
   - System generates unique session UUID
   - Session linked to user_id in database
   - Session tracks entire website building process

3. **Intent Processing**
   - User describes website (e.g., "I want a restaurant website")
   - Domain Identifier Agent analyzes the description
   - Classifies business type (restaurant, portfolio, e-commerce, etc.)
   - Saves intent to database

4. **Smart Questioning**
   - Question Generator Agent creates domain-specific questions
   - For restaurant: "What's your restaurant name?", "What cuisine?", "Do you offer delivery?"
   - For portfolio: "What's your profession?", "What services do you offer?"
   - User provides answers
   - Answers saved to session in database

5. **Blueprint Creation**
   - Blueprint Architect Agent designs website structure
   - Creates page layouts, sections, and components
   - Blueprint saved as JSONB in database
   - User can review and approve the plan

6. **Code Generation**
   - Code Generator Agent produces actual HTML, CSS, and JavaScript
   - Uses Groq AI (Kimi K2 model) for high-quality code
   - Generates multi-page websites with proper structure
   - **Files uploaded to Cloudflare R2 storage**
   - **File metadata (URLs, sizes) saved to database**

7. **Live Editing**
   - User can chat to make changes: "Make the button red"
   - Editor Agent understands and applies changes
   - Surgical Edit System ensures precise modifications
   - Chat history saved to database
   - Version control tracks all changes

8. **Download & Deploy**
   - User downloads complete website as ZIP file
   - Files retrieved from R2 storage
   - All files ready for deployment
   - Can be hosted on any web server

---

## 🛠️ Technology Stack

### Backend (Python)
- **FastAPI**: High-performance web framework
- **LangChain + LangGraph**: AI agent orchestration
- **Groq API**: LLM provider (Kimi K2 model for generation, Llama 3.3 for questions)
- **SQLAlchemy**: Async ORM for database operations
- **asyncpg**: PostgreSQL async driver
- **BeautifulSoup**: HTML parsing and manipulation
- **Pydantic**: Data validation
- **boto3**: AWS S3-compatible client for R2
- **Python 3.12+**: Core language

### Frontend (TypeScript/React)
- **Next.js 14**: React framework with App Router
- **React 19**: UI library
- **TypeScript**: Type-safe JavaScript
- **Clerk**: Authentication and user management
- **Monaco Editor**: Code viewing/editing
- **CSS Modules**: Component-scoped styles

### Database & Storage
- **Neon PostgreSQL**: Serverless PostgreSQL database
  - User management
  - Session tracking
  - File metadata
  - Chat history
- **Cloudflare R2**: Object storage for generated files
  - HTML, CSS, JavaScript files
  - User uploaded assets
  - Public URL generation
  - S3-compatible API

### AI Models
- **Primary Model**: `moonshotai/kimi-k2-instruct-0905` (code generation, blueprints)
- **Question Model**: `llama-3.3-70b-versatile` (faster for simple tasks)

---

## 🏗️ System Architecture

### Backend Structure

```
backend/
├── app/
│   ├── agents/              # AI Agents
│   │   ├── domain_identifier.py    # Identifies business domain
│   │   ├── question_generator.py   # Generates domain-specific questions
│   │   ├── blueprint_architect.py  # Creates website structure
│   │   ├── code_generator.py       # Generates HTML/CSS/JS
│   │   ├── editor.py               # Plans edits
│   │   └── validator.py            # Validates generated code
│   │
│   ├── database/            # Database Layer (NEW)
│   │   ├── connection.py    # Async database connection & engine
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   └── crud.py          # Database CRUD operations
│   │
│   ├── storage/             # Storage Layer (NEW)
│   │   └── r2_client.py     # Cloudflare R2 client
│   │
│   ├── routers/             # API Endpoints
│   │   ├── session.py       # Session management (updated for DB)
│   │   ├── intent.py        # Intent processing
│   │   ├── questions.py     # Question handling
│   │   ├── blueprint.py     # Blueprint creation
│   │   ├── generate.py      # Website generation
│   │   ├── edit.py          # Editing system
│   │   ├── theme.py         # Theme customization
│   │   ├── assets.py        # Asset management
│   │   └── deploy.py        # Deployment
│   │
│   ├── services/            # Business Logic
│   │   ├── session_manager.py      # Session state management
│   │   ├── storage_service.py      # R2 + DB integration (NEW)
│   │   ├── file_manager.py         # File operations
│   │   ├── component_registry.py   # Component tracking
│   │   ├── edit_history.py         # Version control
│   │   └── safe_edit_engine.py     # Surgical edits
│   │
│   ├── models/              # Pydantic Data Models
│   │   ├── session.py       # Session models
│   │   ├── website.py       # Website models
│   │   └── ...
│   │
│   ├── migrations/          # Database Migrations (NEW)
│   │   └── schema.sql       # PostgreSQL schema
│   │
│   ├── config.py            # Configuration
│   └── main.py              # Application entry point
│
└── projects/                # Local storage fallback (deprecated)
```

### Frontend Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── builder/[sessionId]/    # Website builder pages
│   │   │   ├── page.tsx            # Main builder interface
│   │   │   ├── questions/          # Questions step
│   │   │   ├── blueprint/          # Blueprint review
│   │   │   ├── preview/            # Website preview
│   │   │   └── edit/               # Editing interface
│   │   ├── layout.tsx              # Root layout with Clerk
│   │   └── page.tsx                # Home page with auth
│   │
│   ├── components/
│   │   ├── features/               # Feature components
│   │   │   ├── MonacoCodeViewer.tsx    # Code viewer
│   │   │   ├── ThemePanel.tsx          # Theme customization
│   │   │   ├── AssetManager.tsx        # Asset upload
│   │   │   └── PageManager.tsx         # Multi-page management
│   │   └── ...
│   │
│   ├── lib/                        # Utilities
│   │   └── api.ts                  # API client
│   │
│   └── middleware.ts               # Clerk middleware
│
└── public/                         # Static assets
```

---

## ✨ Core Features

### 1. **User Authentication (NEW)**
- Clerk integration for secure authentication
- Google, GitHub, Email sign-in
- User profile management
- Session linked to user accounts
- Data isolation per user

### 2. **Natural Language Interface**
- Users describe websites in plain English
- No technical knowledge required
- AI understands context and intent

### 3. **Domain Detection**
- Automatically identifies business type
- Supports 20+ domains:
  - Restaurant, Flower Shop, Portfolio, Agency
  - E-commerce, SaaS, Blog, Nonprofit
  - Medical, Legal, Real Estate, Education
  - Fitness, Beauty, Photography, Construction
  - Automotive, Travel, Event Planning, Tech Startup

### 4. **Smart Questioning System**
- Domain-specific questions
- Gathers essential information
- Customizes website based on answers
- Answers stored in database

### 5. **Visual Blueprint**
- Preview website structure before generation
- See pages, sections, and components
- Approve or request changes
- Blueprint saved in database as JSONB

### 6. **Multi-Page Website Generation**
- Generates complete websites with multiple pages
- Proper navigation between pages
- Consistent styling across all pages
- **Files stored in Cloudflare R2**
- **Metadata tracked in PostgreSQL**

### 7. **Theme Customization**
- Change color schemes
- Modify fonts
- Adjust layouts
- Real-time preview
- Theme settings saved to database

### 8. **Asset Management**
- Upload images to R2 storage
- Manage files with database tracking
- Replace placeholders with real content
- Public URLs for all assets

### 9. **Surgical Edit System**
- Chat-based editing: "Change the heading to Welcome"
- Precise modifications using NCD IDs
- Version control with rollback capability
- Edit history tracking in database
- Chat messages persisted

### 10. **Code Viewing**
- Monaco Editor integration
- Syntax highlighting
- View HTML, CSS, and JavaScript
- Files loaded from R2 storage

### 11. **One-Click Download**
- Export complete website as ZIP
- Files retrieved from R2
- All files organized properly
- Ready for deployment

### 12. **Cloud Storage (NEW)**
- Cloudflare R2 for file storage
- Fast global CDN
- Public URLs for all files
- Automatic cleanup on session delete

### 13. **Persistent Data (NEW)**
- PostgreSQL database
- Sessions never lost
- User data persisted
- Query history and analytics
- Scalable architecture

---

## 🤖 AI Agents & Their Roles

[Previous agent descriptions remain the same...]

---

## 🔌 API Endpoints

### Session Management

#### `POST /api/session/create`
Creates a new website building session (updated for database)
```json
Request: {
  "intent": "I want a restaurant website"
}

Headers: {
  "Authorization": "Bearer clerk_user_id"
}

Response: {
  "session_id": "uuid-here",
  "status": "created",
  "message": "Session created successfully"
}
```

#### `GET /api/session/{session_id}/status`
Gets session status from database
```json
Response: {
  "session_id": "uuid",
  "status": "website_generated",
  "created_at": "2025-12-24T12:00:00Z",
  "user_id": "uuid",
  "blueprint_confirmed": true,
  "files_count": 3
}
```

#### `DELETE /api/session/{session_id}`
Deletes session and all files from R2 and database

[Other endpoints remain similar but now use database...]

---

## 📁 File Structure

### Database Storage (NEW)

**Sessions Table:**
- User ID (foreign key to users)
- Intent, status, domain
- Questions and answers (JSONB)
- Blueprint (JSONB)
- Timestamps

**Generated Files Table:**
- Session ID (foreign key)
- File name, path, type
- R2 key and public URL
- Size and MIME type
- Creation timestamp

**Chat Messages Table:**
- Session ID (foreign key)
- Role (user/ai/system)
- Content
- Metadata
- Timestamp

**Users Table:**
- Clerk user ID
- Email, name, avatar
- Created/updated timestamps

### R2 Storage Structure
```
r2://ncd-inai-files/
└── sessions/
    └── {session-uuid}/
        ├── index.html
        ├── about.html
        ├── styles.css
        ├── script.js
        └── assets/
            └── uploaded-images/
```

---

## 💾 Database & Storage

### Neon PostgreSQL Database

**Tables:**
1. **users** - Clerk user integration
2. **sessions** - Website building sessions
3. **generated_files** - File metadata with R2 URLs
4. **chat_messages** - AI chat history
5. **themes** - Theme customizations
6. **assets** - User uploaded files
7. **activity_logs** - Analytics and tracking

**Features:**
- Async operations with SQLAlchemy
- Connection pooling
- JSONB for flexible data (blueprints, answers)
- Foreign key relationships
- Indexes for performance
- Automatic timestamps

**Example Session Record:**
```sql
{
  "id": "uuid",
  "user_id": "uuid",
  "intent": "restaurant website",
  "status": "website_generated",
  "domain": {"domain": "restaurant", "confidence": 0.95},
  "questions": [...],
  "answers": {"restaurant_name": "Bella Italia"},
  "blueprint": {"pages": [...]},
  "created_at": "2025-12-24T12:00:00Z"
}
```

### Cloudflare R2 Storage

**Features:**
- S3-compatible API
- Global CDN
- Public URLs
- Automatic caching
- Cost-effective

**Operations:**
- Upload files (HTML, CSS, JS)
- Generate public URLs
- Delete files
- Batch operations

**Integration with Database:**
```python
# Upload to R2 and save metadata
await storage_service.save_generated_file(
    db=db,
    session_id=session_uuid,
    file_content="<html>...</html>",
    file_name="index.html",
    file_type="html"
)
# This automatically:
# 1. Uploads to R2: sessions/{id}/index.html
# 2. Saves metadata to database
# 3. Returns public URL
```

---

## 🔐 Authentication

### Clerk Integration

**Setup:**
- Clerk Provider wraps entire app
- Sign in/Sign up modals
- User button component
- Session management

**Frontend:**
```tsx
<ClerkProvider>
  <SignedIn>
    <UserButton />
  </SignedIn>
  <SignedOut>
    <SignInButton />
    <SignUpButton />
  </SignedOut>
</ClerkProvider>
```

**Backend API:**
```python
async def get_user_from_clerk_header(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    # Extract clerk_user_id from JWT
    # Get or create user in database
    return user
```

**User Data Flow:**
1. User signs in with Clerk
2. Frontend gets Clerk user ID
3. Sends to backend in Authorization header
4. Backend creates/retrieves user from database
5. Session linked to user_id
6. All data isolated by user

---

## 🎯 Key Innovations

### 1. **Cloud-Native Architecture**
- Serverless PostgreSQL (Neon)
- Object storage (Cloudflare R2)
- Scalable infrastructure
- No local file storage

### 2. **User Data Isolation**
- Sessions linked to user accounts
- Query only user's data
- Secure multi-tenancy
- Analytics per user

### 3. **Integrated Storage Service**
- Coordinates R2 uploads with database
- Atomic operations
- Automatic cleanup
- Metadata tracking

### 4. **Persistent Sessions**
- No data loss on restart
- Resume from any device
- Full history tracking
- Audit trail

### 5. **Surgical Edit System**
- NCD (Natural Component Descriptor) IDs
- Version control with rollback
- Non-destructive editing
- Change tracking in database

### 6. **Multi-Agent Architecture**
- Specialized agents for different tasks
- LangGraph orchestration
- Efficient task distribution
- Scalable design

---

## 📊 Environment Configuration

### Backend `.env`

```env
# LLM Configuration
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key

# Models
LLM_MODEL=moonshotai/kimi-k2-instruct-0905
QUESTION_MODEL=llama-3.3-70b-versatile

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Database (Neon PostgreSQL)
USE_DATABASE=true
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Cloudflare R2 Storage
USE_R2_STORAGE=true
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=ncd-inai-files
R2_ENDPOINT=https://account.r2.cloudflarestorage.com
R2_PUBLIC_URL=https://pub-xxx.r2.dev

# Local Storage (Fallback)
PROJECTS_DIR=./projects
```

### Frontend `.env.local`

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## 🚀 Running the Application

### Prerequisites
- Python 3.12+
- Node.js 18+
- Neon PostgreSQL account
- Cloudflare R2 account
- Clerk account
- Groq API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"

# Run server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Access
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## 📈 Benefits of New Architecture

### Scalability
- ✅ Handle unlimited users
- ✅ No server storage limits
- ✅ Auto-scaling database
- ✅ Global CDN for files

### Reliability
- ✅ No data loss (persistent storage)
- ✅ Session recovery
- ✅ Automatic backups
- ✅ High availability

### Performance
- ✅ Fast database queries
- ✅ Cached file delivery
- ✅ Async operations
- ✅ Connection pooling

### Security
- ✅ User data isolation
- ✅ Clerk authentication
- ✅ Secure file storage
- ✅ Audit logging

### Maintainability
- ✅ Centralized data
- ✅ Easy debugging
- ✅ Analytics ready
- ✅ Clean architecture

---

## 🎓 Development Roadmap

### Phase 1: Core Platform ✅
- Natural language website generation
- Multi-domain support
- Blueprint system
- Code generation

### Phase 2: Enhanced Features ✅
- Multi-page websites
- Theme customization
- Asset management
- Edit system

### Phase 3: Cloud Infrastructure ✅ (CURRENT)
- **Database integration (Neon PostgreSQL)**
- **R2 object storage**
- **User authentication (Clerk)**
- **Session persistence**

### Phase 4: Advanced Features (UPCOMING)
- Real-time collaboration
- Team workspaces
- Template marketplace
- Version control UI
- Custom code editing

### Phase 5: Enterprise (PLANNED)
- White-label solution
- API access
- Webhooks
- Advanced analytics
- Custom integrations

---

## 📝 Notes

- All generated websites are production-ready
- Code follows modern web standards
- Responsive design included
- SEO-friendly markup
- Accessibility features included
- Cross-browser compatible
- Files stored securely in cloud
- User data protected and isolated
- Scalable architecture for growth

---

**Last Updated**: December 24, 2025
**Version**: 2.0 (Cloud-Native Architecture)
