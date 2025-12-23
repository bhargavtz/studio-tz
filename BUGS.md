# Bug Report & Code Analysis

## Critical Issues

### 1. Missing Backend Endpoint for General File Editing
**Severity:** Critical
**Location:** `backend/app/routers/edit.py` vs `frontend/src/lib/api.ts`
**Description:**
The frontend API library (`api.ts`) defines an `editWebsite` function that sends a POST request to `${API_BASE}/edit/${sessionId}` with a payload containing `edit_type`, `file_path`, etc.
 However, the backend router `edit.py` **does not define this endpoint**. It only supports:
- `/edit/{session_id}/structured` (requires `ncd_id`)
- `/edit/{session_id}/chat` (natural language)
- `/edit/{session_id}/rollback`

**Consequence:**
Any client-side feature attempting to save manual code edits (e.g., from a code editor) or apply non-structured updates will fail with a `404 Not Found` or `405 Method Not Allowed`.

### 2. Inconsistent Internal File Hiding
**Severity:** Medium
**Location:** `backend/app/routers/questions.py` vs `backend/app/services/file_manager.py`
**Description:**
- `file_manager.py` is configured to hide internal files, including `questions.json`.
- `questions.py` saves generated questions as `domain_questions.json`.
**Consequence:**
Since `domain_questions.json` is not in the exclude list of `file_manager.py`, it will be visible to the user in the file tree or asset list, exposing internal logic/prompts.

### 3. Hardcoded API URL
**Severity:** Medium
**Location:** `frontend/src/lib/config.ts`
**Description:**
The `apiUrl` is hardcoded to `http://localhost:8000` as a default.
```typescript
export const config = {
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
} as const;
```
**Consequence:**
If deployed to a remote server without explicit environment variables, the frontend will still try to contact localhost, causing connection failures.

### 4. Code Viewer is Read-Only
**Severity:** Low (Feature Check)
**Location:** `frontend/src/components/features/MonacoCodeViewer.tsx`
**Description:**
The Monaco Editor is explicitly set to `readOnly: true`.
```typescript
options={{
    readOnly: true,
    // ...
}}
```
**Consequence:**
Users cannot manually edit the code even if they want to, restricting the "Code" tab to viewing only. This might be intended, but contradicts the existence of `api.editWebsite`.

## Resolved Issues (Already Fixed)

### 1. Download Link 404
**Fixed in:** `frontend/src/app/builder/[sessionId]/page.tsx`
**Description:**
The download button was constructing a manual URL (`/deploy/.../download`) which often failed.
**Fix:**
Updated to use the `api.downloadProject()` method which handles the file blob response correctly.

### 2. Strict Answer Validation Blocking Generation
**Fixed in:** `backend/app/routers/blueprint.py`
**Description:**
The backend was raising a `400 Bad Request` if `session.answers` was empty.
**Fix:**
Relaxed the check to allow generating a blueprint even if the user skips all questions.

### 3. AI Asset Hallucination
**Fixed in:** `backend/app/agents/code_generator.py`
**Description:**
The AI was generating fake local paths for images (e.g., `assets/hero.jpg`) which resulted in 404 errors.
**Fix:**
Updated the system prompt to STRICTLY mandate the use of external placeholder services (Placehold.co, Unsplash) or verified assets only.

## Recommended Actions

1.  **Implement General Edit Endpoint:** Add a `POST /edit/{session_id}` endpoint in `edit.py` that accepts `file_path` and `content` to allow manual code saving.
2.  **Update File Hiding match:** Add `domain_questions.json` to the excluded list in `file_manager.py`.
3.  **Unlock Editor:** If manual editing is desired, set `readOnly: false` in `MonacoCodeViewer.tsx` and implement the save handler.
