# AI Chat Panel - Model & Update Configuration

## 🤖 **Connected AI Model**

**Model**: `moonshotai/kimi-k2-instruct-0905`  
**Provider**: Groq API  
**Temperature**: 0.2 (Lower for precise code edits)  
**Max Tokens**: 6000

### Configuration Location

- **Config File**: `backend/app/config.py`
- **Line 28**: `self.llm_model = os.getenv("LLM_MODEL", "moonshotai/kimi-k2-instruct-0905")`
- **Editor File**: `backend/app/services/advanced_groq_editor.py`
- **Line 21**: Uses `settings.llm_model` (Kimi model)

---

## 🎯 **Targeted Update System**

The chat panel now performs **SURGICAL/TARGETED updates** instead of full code rewrites.

### How It Works

1. **Planning Phase**: AI analyzes the user request and classifies it:
   - `ADD_SECTION` - Adding new sections (hero, features, gallery, etc.)
   - `MODIFY_SECTION` - Changing an existing section
   - `UPDATE_CONTENT` - Text, image, or link changes
   - `STYLE_CHANGE` - CSS/styling modifications
   - `COMPLEX` - Multiple changes (fallback to full update)

2. **Execution Phase**: Based on classification:
   - **ADD_SECTION**: Generates only the new `<section>` and inserts it
   - **MODIFY_SECTION**: Updates only the targeted section
   - **UPDATE_CONTENT**: Changes specific text/elements
   - **STYLE_CHANGE**: Modifies CSS without touching HTML
   - **COMPLEX**: Full HTML update (last resort)

### Benefits

✅ **Preserves Existing Code**: Only modifies what's requested  
✅ **Faster Updates**: Less code generation needed  
✅ **Fewer Errors**: No risk of breaking unrelated sections  
✅ **Better Context**: Keeps user's existing design intact  
✅ **More Predictable**: User knows exactly what will change

---

## 📍 **Code Locations**

### Chat Endpoint

**File**: `backend/app/routers/edit.py`  
**Endpoint**: `POST /edit/{session_id}/chat`  
**Lines**: 293-369

### Editor Service

**File**: `backend/app/services/advanced_groq_editor.py`  
**Methods**:

- `modify_website()` - Main entry point (line 25)
- `_plan_modification()` - Analyzes request (line 103)
- `_add_section()` - Adds new sections (line 142)
- `_modify_section()` - Modifies existing sections (line 174)
- `_update_content()` - Updates content (line 219)
- `_full_update()` - Fallback full update (line 253)

---

## 🛠️ **Environment Variables**

Make sure your `.env` file has:

```env
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=moonshotai/kimi-k2-instruct-0905
```

---

## 🎨 **Example Usage**

### User Request - Add a hero section

**Classification**: `ADD_SECTION`  
**Action**: Generates only `<section class="hero">...</section>`  
**Result**: New section added before footer, existing code unchanged

### User Request - Change the heading to Welcome

**Classification**: `UPDATE_CONTENT`  
**Action**: Finds `<h1>` and updates text only  
**Result**: Only `<h1>` text changes, rest stays same

### User Request - Make it look modern with gradients

**Classification**: `STYLE_CHANGE`  
**Action**: Updates CSS styles only  
**Result**: Styles modified, HTML structure intact

---

## ✨ **Summary**

Your agentic chat panel is now powered by:

- **Kimi K2 Instruct Model** (via Groq) for intelligent code understanding
- **Targeted/Surgical Update System** for precise modifications
- **Smart Classification** to determine the minimum necessary changes
- **Preservation of Existing Code** - only touches what needs to change

This ensures efficient, predictable, and safe website modifications through natural language! 🚀
