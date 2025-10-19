# Schema Loading Quick Start Guide

## What Was Fixed

✅ **Bug Fixed**: The "Add Schema from..." dropdown menu items are now clickable

### The Problem
The dropdown menu items were wrapped in `TooltipWrapper` components with `hasButtonWrapper={true}`, which created nested interactive elements that blocked click events.

### The Solution
Removed the `TooltipWrapper` components and used simple string titles for the menu items in:
- `frontend/src/components/Popups/GraphEnhancementDialog/EnitityExtraction/NewEntityExtractionSetting.tsx`

---

## Quick Start: Load Your First Schema

### Method 1: Use a Predefined Schema (Easiest)

1. Click **"Graph Enhancement"** button in the app
2. Go to **"Entity Extraction Settings"** tab
3. Click **"Add Schema from..."** dropdown ⬅️ **NOW WORKING!**
4. Select **"Predefined Schema"**
5. Choose a domain (e.g., "social", "movies", "retail")
6. Click **"Apply"**

### Method 2: Upload a Custom JSON Schema (Recommended)

1. Choose an example file from `backend/docs/examples/`:
   - `social-network-schema.json` - Social media platform
   - `complete-example-schema.json` - Business network
   - `custom-schema-template.json` - Template to modify

2. In the app:
   - Click **"Graph Enhancement"**
   - Go to **"Entity Extraction Settings"** tab
   - Click **"Add Schema from..."**
   - Select **"Data Importer JSON"**
   - Drag and drop your JSON file
   - Click **"Apply"**

### Method 3: Type Manually

1. In the **"Graph Pattern"** section, click the dropdowns and type:
   - **Source**: Type "Person" and press Enter
   - **Type**: Type "KNOWS" and press Enter
   - **Target**: Type "Person" and press Enter
2. Click **"+ Add"**
3. Your pattern appears: `Person -[:KNOWS]-> Person`
4. Click **"Apply"**

---

## Available Documentation

### For Users

📖 **[Schema Loading Guide](backend/docs/SCHEMA_LOADING_GUIDE.md)**
- Complete guide to all three loading methods
- When to use each method
- Best practices and troubleshooting

📋 **[JSON Format Reference](backend/docs/SCHEMA_JSON_FORMAT.md)**
- Quick reference for JSON structure
- Common patterns and examples
- Validation checklist

📁 **[Example Files](backend/docs/examples/)**
- Ready-to-use JSON schema files
- Templates for creating custom schemas
- Tutorial on creating your own

---

## Example JSON Schemas Provided

### 1. Social Network
**File:** `backend/docs/examples/social-network-schema.json`

**Patterns:**
```
User -[:FOLLOWS]-> User
User -[:POSTS]-> Post
Post -[:CONTAINS]-> Link
Post -[:TAGS]-> Tag
Post -[:MENTIONS]-> User
User -[:REPLY_TO]-> Post
User -[:REPOST]-> Post
```

### 2. Business/Professional Network
**File:** `backend/docs/examples/complete-example-schema.json`

**Patterns:**
```
Person -[:WORKS_AT]-> Company
Person -[:LIVES_IN]-> City
Company -[:LOCATED_IN]-> City
City -[:IN_COUNTRY]-> Country
Person -[:HAS_SKILL]-> Skill
Person -[:KNOWS]-> Person
Person -[:MANAGES]-> Person
Person -[:WORKED_ON]-> Project
Project -[:REQUIRES_SKILL]-> Skill
```

### 3. Custom Template
**File:** `backend/docs/examples/custom-schema-template.json`

A minimal template you can copy and modify for your own schemas.

---

## Creating Your Own JSON Schema

### Step 1: Copy the Template
```bash
cp backend/docs/examples/custom-schema-template.json my-schema.json
```

### Step 2: Edit the File

Replace the placeholder values:

```json
{
  "dataModel": {
    "graphSchemaRepresentation": {
      "graphSchema": {
        "nodeLabels": [
          { "$id": "nl1", "token": "YourEntity1" },
          { "$id": "nl2", "token": "YourEntity2" }
        ],
        "relationshipTypes": [
          { "$id": "rt1", "token": "YOUR_RELATIONSHIP" }
        ],
        "nodeObjectTypes": [
          { "$id": "node1", "labels": [{ "$ref": "#nl1" }] },
          { "$id": "node2", "labels": [{ "$ref": "#nl2" }] }
        ],
        "relationshipObjectTypes": [
          {
            "$id": "rel1",
            "from": { "$ref": "#node1" },
            "to": { "$ref": "#node2" },
            "type": { "$ref": "#rt1" }
          }
        ]
      }
    }
  }
}
```

### Step 3: Validate
Visit https://jsonlint.com and paste your JSON to check for errors.

### Step 4: Upload
Follow "Method 2" above to upload your custom schema.

---

## Testing Your Schema

After applying a schema:

1. Upload a test document
2. Click **"Generate Graph"**
3. Verify entities are extracted correctly
4. Check the graph visualization
5. Adjust schema if needed

---

## Troubleshooting

### Menu Still Not Clickable
- Clear browser cache and refresh
- Check browser console for errors

### "No data found" when loading from database
- Verify Neo4j connection is active
- Ensure database contains data

### JSON upload fails
- Validate JSON syntax at https://jsonlint.com
- Ensure it follows the Neo4j Data Importer format
- Check all `$ref` values use `#` prefix

### Schema not extracting correctly
- Verify node labels use PascalCase
- Verify relationships use UPPER_SNAKE_CASE
- Check that `$ref` values point to existing `$id` values

---

## Next Steps

1. **Test the fix**: Try clicking the dropdown menu items
2. **Explore examples**: Check out the JSON files in `backend/docs/examples/`
3. **Create your schema**: Use the template to build your own
4. **Read the guides**: Full documentation in `backend/docs/`

---

## File Locations

```
llm-graph-builder/
├── frontend/src/components/Popups/GraphEnhancementDialog/
│   └── EnitityExtraction/
│       └── NewEntityExtractionSetting.tsx  ⬅️ Bug fix applied here
│
└── backend/docs/
    ├── SCHEMA_LOADING_GUIDE.md              ⬅️ Complete user guide
    ├── SCHEMA_JSON_FORMAT.md                ⬅️ JSON format reference
    └── examples/
        ├── README.md                         ⬅️ Examples documentation
        ├── social-network-schema.json        ⬅️ Example 1
        ├── complete-example-schema.json      ⬅️ Example 2
        └── custom-schema-template.json       ⬅️ Template
```

---

## Summary of Changes

### Code Changes
- **File Modified**: `frontend/src/components/Popups/GraphEnhancementDialog/EnitityExtraction/NewEntityExtractionSetting.tsx`
  - Removed `TooltipWrapper` from menu items (lines 377-408)
  - Removed unused import (line 19)
  - Changed `title` prop from JSX component to simple string

### Documentation Created
1. `backend/docs/SCHEMA_LOADING_GUIDE.md` - Complete user guide (9KB)
2. `backend/docs/SCHEMA_JSON_FORMAT.md` - JSON format reference (10KB)
3. `backend/docs/examples/README.md` - Examples documentation (6KB)

### Example Files Created
1. `backend/docs/examples/social-network-schema.json` - Social media schema
2. `backend/docs/examples/complete-example-schema.json` - Business network schema
3. `backend/docs/examples/custom-schema-template.json` - Starter template

---

## Support

For questions or issues:
- Check the documentation in `backend/docs/`
- Review example files in `backend/docs/examples/`
- Open an issue on GitHub with details about your use case

Happy graph building! 🎉
