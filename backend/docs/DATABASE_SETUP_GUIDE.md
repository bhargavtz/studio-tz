# Quick Database Setup Guide

## Current Status
❌ Database is not configured yet in your `.env` file.

## Option 1: Enable Database (Recommended for Production)

### Step 1: Create Neon Database (Free)
1. Visit: https://neon.tech
2. Sign up with GitHub/Google
3. Click "Create Project"
4. Copy the connection string (looks like):
   ```
   postgresql://user:pass@ep-xxx.neon.tech/neondb
   ```

### Step 2: Update `.env` File
Add these lines to `backend/.env`:
```env
# Enable database
USE_DATABASE=true
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech/neondb
```

### Step 3: Run Schema
```bash
# Install dependencies first
cd backend
pip install sqlalchemy asyncpg

# Then run schema (replace with your connection string)
psql "postgresql://user:pass@host/db" -f migrations/schema.sql
```

### Step 4: Test
```bash
python test_database.py
```

---

## Option 2: Keep File-Based Storage (Current Setup)

If you don't want to use database yet:
```env
# Keep using files
USE_DATABASE=false
USE_R2_STORAGE=false
```

Your app will continue working with `./projects` directory.

---

## Option 3: Use Database Later

You can also:
1. Leave `USE_DATABASE=false` for now
2. Set up Neon when ready
3. Migrate data using migration script (we can create this)

---

## Which option do you prefer?

Reply with:
- **"setup neon"** - I'll guide you through Neon setup
- **"keep files"** - Continue with file-based storage
- **"both"** - Set up database but keep files as backup
