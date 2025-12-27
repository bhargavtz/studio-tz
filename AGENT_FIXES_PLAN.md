# Website Generation Fixes - Agent Prompts Enhancement

## Problem Analysis
1. **Single Page Generation**: code_generator only generates one `index.html`
2. **Duplicate Content**: multi_page_generator copies the same HTML to all pages
3. **No Unique Content**: Each page has identical content, just filtered sections
4. **Poor File Connectivity**: CSS/JS not properly linked across pages
5. **Navigation Issues**: Links not working between pages

## Solution: Enhanced Multi-Page Generation

### Approach 1: Generate Each Page Separately (RECOMMENDED)
Instead of generating one page and duplicating it, generate each page individually with unique content.

**Changes Required:**
1. **Update `code_generator.py`**:
   - Create a new method `generate_multipage()` 
   - Loop through each page in blueprint
   - Generate unique HTML for cada page
   - Share common CSS/JS files
   - Ensure navigation is consistent

2. **Enhanced Prompt**:
   - Specify EACH page should have unique content
   - Provide page-specific context (About, Contact, Services, etc.)
   - Ensure CSS/JS references are identical across pages
   - Add proper navigation structure

### Approach 2: Enhanced Multi-Page Generator
Keep current structure but make multi_page_generator smarter.

**Changes Required:**
1. **Update `multi_page_generator.py`**:
   - Generate unique content per page type
   - Use LLM to create page-specific sections
   - Maintain design consistency
   - Proper validation

## Recommended Implementation

I recommend **Approach 1** because:
- More control over quality
- Better uniqueness per page
- Easier to ensure file connectivity
- Better navigation handling

### New System Prompt Structure

```
For MULTI-PAGE websites, you must generate:
1. **index.html** - Home page with hero, features overview, CTA
2. **For each additional page in blueprint**:
   - Generate COMPLETELY UNIQUE content
   - Use the SAME theme/colors/fonts
   - Link the SAME CSS file (styles/main.css)
   - Link the SAME JS file (scripts/main.js)
   - Include IDENTICAL navigation structure
   
Example for "About" page:
- Hero section about company story
- Mission/Vision section
- Team profiles
- Company values
- Different from home page but same design

Example for "Services" page:
- Hero for services
- Individual service cards with details
- Pricing or packages
- CTA for contact
```

## File Connectivity Rules
1. ALL pages must reference: `styles/main.css`
2. ALL pages must reference: `scripts/main.js`
3. Navigation links must be .html files for multi-page
4. Anchor links (#section) only for single-page sites

## Next Steps
1. Update code_generator.py with new generate_multipage method
2. Enhance CODE_GENERATOR_PROMPT
3. Update generate.py router to use new method
4. Test with multi-page blueprint
