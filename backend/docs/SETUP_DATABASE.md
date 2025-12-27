# Neon + R2 Integration Setup Instructions

## Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Setup Neon Database

1. Create account: https://neon.tech
2. Create new project + database
3. Copy connection string from dashboard
4. Format: `postgresql+asyncpg://user:password@host/database`

## Step 3: Run Database Migrations

```bash
cd backend

# Connect to your Neon database and run schema
psql "postgresql://user:password@host/database" -f migrations/schema.sql
```

## Step 4: Setup Cloudflare R2

1. Login to Cloudflare Dashboard
2. Go to R2 Object Storage
3. Create new bucket: `ncd-inai-files`
4. Generate R2 API tokens:
   - Account ID: From R2 dashboard
   - Access Key ID & Secret: From "Manage R2 API Tokens"

## Step 5: Update .env File

Copy `.env.example` to `.env` and fill in values:

```env
# Database
DATABASE_URL=postgresql+asyncpg://your_user:your_pass@ep-xxx.aws.neon.tech/your_db
USE_DATABASE=true

# R2 Storage
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=ncd-inai-files
R2_PUBLIC_URL=https://pub-xxx.r2.dev
USE_R2_STORAGE=true
```

## Step 6: Test Connection

```bash
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

## What's Been Added:

✅ **Database Schema** (`migrations/schema.sql`)
- Users, Sessions, Files, Chat, Themes, Assets tables
- Indexes for performance
- Relationships and constraints

✅ **SQLAlchemy Models** (`app/database/models.py`)
- User, Session, GeneratedFile, ChatMessage, Theme, Asset
- Full relationships and typing

✅ **Database Connection** (`app/database/connection.py`)
- Async engine with connection pooling
- Session management
- Transaction support

✅ **R2 Client** (`app/storage/r2_client.py`)
- Upload/download files
- Delete operations
- Public URL generation

✅ **Updated Config** (`app/config.py`)
- Database settings
- R2 credentials
- Feature flags (USE_DATABASE, USE_R2_STORAGE)

## Next Steps (After User Review):

1. Update routers to use database
2. Create CRUD operations
3. Migrate existing data (optional)
4. Test end-to-end
