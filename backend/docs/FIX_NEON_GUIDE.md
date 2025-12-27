# Fix Neon Database Connection - Step by Step

## 🔧 Step 1: Check Neon Dashboard

1. Open browser and go to: **https://console.neon.tech**
2. Login to your Neon account
3. Find your project: **"ncd"** or **"ncd-inai"**

## 🔍 Step 2: Check Database Status

Look for these indicators:
- ⚠️ **"Suspended"** badge - Database is sleeping (free tier)
- ✅ **"Active"** badge - Database is running
- 🔴 **"Error"** - Database has issues

**If Suspended:**
- Click on the project
- Click **"Resume"** button
- Wait 10-20 seconds for activation

## 📝 Step 3: Get Fresh Connection String

In your Neon project:
1. Click on **"Connection Details"** or **"Connect"**
2. Select **"Pooled connection"** (recommended)
3. Select **"Parameters only"** or **"Connection string"**
4. Copy the full connection string

It should look like:
```
postgresql://username:password@ep-xxxxx.region.aws.neon.tech/dbname
```

## ⚙️ Step 4: Update .env File

Replace in `backend/.env`:

**Old:**
```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_OFTG4k6BdXxQ@ep-fancy-king-a11apt3i-pooler.ap-southeast-1.aws.neon.tech/ncd?sslmode=require
```

**New:** (paste YOUR connection string from dashboard)
```env
DATABASE_URL=postgresql+asyncpg://YOUR_USERNAME:YOUR_PASSWORD@YOUR_ENDPOINT.neon.tech/YOUR_DATABASE?sslmode=require
```

⚠️ **Important:** Add `postgresql+asyncpg://` prefix (not just `postgresql://`)

## 🧪 Step 5: Test Connection

Run this test:
```bash
cd backend
python test_neon_connection.py
```

If it shows ✅ SUCCESS, you're good!

## 🚀 Step 6: Enable Database

In `backend/.env`, change:
```env
USE_DATABASE=true
```

Then restart backend server.

---

## 🆘 Troubleshooting

### Error: "Database suspended"
- Go to Neon dashboard
- Click "Resume" on your project
- Wait and try again

### Error: "Authentication failed"
- Double-check username and password
- Make sure no extra spaces in .env
- Try copying connection string again

### Error: "Connection timeout"
- Check your internet connection
- Try different network (wifi vs mobile hotspot)
- Check if firewall blocking port 5432

### Error: "SSL required"
- Make sure URL ends with `?sslmode=require`

---

## ✅ When It Works

You should see:
```
✅ Database connected!
✅ Tables initialized
✅ Backend running with database support
```

Then all user data will save to Neon! 🎉

---

**Ready? Go to Neon dashboard and get fresh credentials!**
Tell me when you have the new connection string.
