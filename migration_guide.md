# Phase 4 Migration Guide - Quick Reference

## 🔄 Before vs After

### Old Architecture (નું)
```python
# Old way - Direct database + file system
from app.services.session_manager import session_manager
from app.services.file_manager import file_manager
from app.database import crud

# Get session
session = session_manager.get_session(session_id)  # In-memory + files

# Save file
file_manager.write_file(session_id, "index.html", content)  # Local files
```

### New Architecture (નવું) ✅
```python
# New way - Repository pattern + unified storage
from app.services.new_session_service import SessionService
from app.infrastructure.storage.file_store import UnifiedFileStore
from app.api.dependencies import get_session_service, get_file_store

# Get session (with dependency injection)
async def my_endpoint(session_service: SessionService = Depends(get_session_service)):
    session = await session_service.get_session(session_id)  # Database
    
    # Save file (R2 + Database)
    file_store = UnifiedFileStore(db)
    await file_store.save_file(session_id, "index.html", content)
```

---

## 📊 Comparison Table

| Feature | Old | New |
|---------|-----|-----|
| **Session Storage** | In-memory + JSON files | PostgreSQL Database |
| **File Storage** | Local file system | R2 + Database metadata |
| **Error Handling** | HTTPException | Custom exceptions |
| **Dependency Injection** | Global instances | FastAPI Depends() |
| **Testing** | Hard to mock | Easy to mock |
| **Logging** | print() statements | Structured logging |
| **Type Safety** | Weak | Strong (with exceptions) |

---

## 🚀 How to Migrate a Router

### Step 1: Update Imports

```python
# ❌ Remove these
from app.services.session_manager import session_manager
from app.services.file_manager import file_manager
from app.database import crud
from fastapi import HTTPException

# ✅ Add these
from app.services.new_session_service import SessionService
from app.infrastructure.storage.file_store import UnifiedFileStore
from app.api.dependencies import get_session_service, get_file_store
from app.core.exceptions import SessionNotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)
```

### Step 2: Update Endpoint Signature

```python
# ❌ Old
@router.get("/endpoint/{session_id}")
async def my_endpoint(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Not found")

# ✅ New
@router.get("/endpoint/{session_id}")
async def my_endpoint(
    session_id: str,
    session_service: SessionService = Depends(get_session_service)
):
    session_uuid = UUID(session_id)
    session = await session_service.get_session(session_uuid)
    # Raises SessionNotFoundError automatically
```

### Step 3: Replace Error Handling

```python
# ❌ Old
raise HTTPException(status_code=400, detail="Invalid input")

# ✅ New
raise ValidationError("field_name", "Invalid input")
```

### Step 4: Replace File Operations

```python
# ❌ Old
file_manager.write_file(session_id, "file.html", content)
content = file_manager.read_file(session_id, "file.html")

# ✅ New
file_store = UnifiedFileStore(db)
await file_store.save_file(session_id, "file.html", content)
content = await file_store.get_file(session_id, "file.html")
```

---

## 📝 Routers to Migrate

| Router | Status | Complexity | Notes |
|--------|--------|------------|-------|
| [blueprint.py](file:///e:/studio-tz/backend/app/routers/blueprint.py) | ✅ Done | Low | Example completed |
| [session_database.py](file:///e:/studio-tz/backend/app/routers/session_database.py) | ⏳ TODO | Low | Simple CRUD |
| [questions.py](file:///e:/studio-tz/backend/app/routers/questions.py) | ⏳ TODO | Low | Uses session_manager |
| [generate.py](file:///e:/studio-tz/backend/app/routers/generate.py) | ⏳ TODO | **HIGH** | Uses file_manager heavily |
| [edit.py](file:///e:/studio-tz/backend/app/routers/edit.py) | ⏳ TODO | High | Uses file_manager + session_manager |
| [chat.py](file:///e:/studio-tz/backend/app/routers/chat.py) | ⏳ TODO | Medium | AI editing |
| [theme.py](file:///e:/studio-tz/backend/app/routers/theme.py) | ⏳ TODO | Medium | File operations |
| [assets.py](file:///e:/studio-tz/backend/app/routers/assets.py) | ⏳ TODO | High | File uploads |
| [deploy.py](file:///e:/studio-tz/backend/app/routers/deploy.py) | ⏳ TODO | Medium | File packaging |
| [dashboard.py](file:///e:/studio-tz/backend/app/routers/dashboard.py) | ⏳ TODO | Low | Already uses database |

---

## ⚠️ Breaking Changes to Avoid

### 1. Don't Mix Old and New
```python
# ❌ BAD - Mixing approaches
session = session_manager.get_session(id)  # Old
await session_service.update_session(id)    # New
# This will NOT work!

# ✅ GOOD - Consistent approach
session = await session_service.get_session(id)
await session_service.update_session(id)
```

### 2. Don't Forget UUID Conversion
```python
# ❌ BAD
session = await session_service.get_session(session_id)  # str

# ✅ GOOD
session_uuid = UUID(session_id)
session = await session_service.get_session(session_uuid)
```

### 3. Don't Forget Async/Await
```python
# ❌ BAD
file_store.save_file(...)  # Forgot await

# ✅ GOOD
await file_store.save_file(...)
```

---

## 🎯 Next Steps

1. **Migrate generate.py** - સૌથી વધુ important (uses file_manager)
2. **Migrate edit.py** - File editing functionality
3. **Migrate remaining routers** - One by one
4. **Remove old services** - Delete file_manager.py and session_manager.py
5. **Update tests** - Add unit tests for new services

---

## 💡 Benefits You Get

✅ **Type Safety** - Catch errors at development time  
✅ **Testability** - Easy to mock and test  
✅ **Clean Code** - Clear separation of concerns  
✅ **Better Errors** - Meaningful exception messages  
✅ **Scalability** - Can scale to millions of users  
✅ **Maintainability** - Easy to understand and modify  

---

## 📞 Need Help?

જો કોઈ router migrate કરતી વખતે problem આવે તો:

1. Check blueprint.py for example
2. Follow the 4-step migration guide
3. Test with server startup
4. Check logs for errors
