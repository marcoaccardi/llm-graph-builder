# Schema Loading Guide

This guide explains how to load and configure graph schemas in the LLM Graph Builder application.

## Overview

The application provides **three methods** to define graph schemas for entity extraction:

1. **Predefined Schemas** - Choose from 10 built-in domain schemas
2. **Load Existing Schema** - Extract schema from your connected Neo4j database
3. **Get Schema From Text** - Use AI to extract schema from text description
4. **Data Importer JSON** - Upload Neo4j Data Importer JSON files

---

## Method 1: Predefined Schemas

### What It Does
Provides ready-to-use schemas for common domains like movies, social networks, e-commerce, etc.

### How to Use
1. Click **"Graph Enhancement"** button
2. Go to **"Entity Extraction Settings"** tab
3. Click **"Add Schema from..."** dropdown
4. Select **"Predefined Schema"**
5. Choose from available domains:
   - **stackoverflow** - Questions, Answers, Users, Tags
   - **movies** - Actors, Directors, Movies, Genres
   - **network** - IT infrastructure (Servers, Networks, Applications)
   - **retail** - E-commerce (Customers, Orders, Products, Suppliers)
   - **social** - Social media (Users, Posts, Tags, Links)
   - **reviews** - Business reviews (Businesses, Users, Reviews, Photos)
   - **payments** - Financial transactions (Clients, Transactions, Banks)
   - **crime** - Law enforcement data (Persons, Crimes, Officers, Locations)
   - **flights** - Aviation (Airports, Cities, Countries, Routes)
   - **healthcare** - Pharmaceutical adverse events (Drugs, Reactions, Cases)

### Example Pattern
When you select "movies", you get patterns like:
- `Actor -[:ACTED_IN]-> Movie`
- `Director -[:DIRECTED]-> Movie`
- `Movie -[:IN_GENRE]-> Genre`
- `User -[:RATED]-> Movie`

---

## Method 2: Load Existing Schema

### What It Does
Queries your connected Neo4j database and extracts existing node labels and relationship types.

### Requirements
- Active connection to Neo4j database
- Database must contain data (nodes and relationships)

### How to Use
1. Click **"Graph Enhancement"** button
2. Go to **"Entity Extraction Settings"** tab
3. Click **"Add Schema from..."** dropdown
4. Select **"Load Existing Schema"**
5. Wait for the schema to load from your database
6. Review and remove any patterns you don't want
7. Click **"Apply"**

### Expected Format from Database
The backend API returns triplets in this format:
```
Person-KNOWS->Person
Company-LOCATED_IN->City
Employee-WORKS_FOR->Company
```

These are automatically converted to Neo4j Cypher pattern format:
```
Person -[:KNOWS]-> Person
Company -[:LOCATED_IN]-> City
Employee -[:WORKS_FOR]-> Company
```

---

## Method 3: Get Schema From Text

### What It Does
Uses an LLM to analyze text and extract graph patterns automatically.

### Requirements
- Backend LLM service must be running
- Model selected in application settings

### How to Use
1. Click **"Graph Enhancement"** button
2. Go to **"Entity Extraction Settings"** tab
3. Click **"Add Schema from..."** dropdown
4. Select **"Get Schema From Text"**
5. Enter your text in one of two ways:

#### Option A: Document Text
Paste actual document content. The AI will identify entities and relationships.

**Example:**
```
John works at Acme Corporation in San Francisco.
He knows Mary, who is a developer at TechCorp.
TechCorp is located in New York.
```

**Extracted Schema:**
- `Person -[:WORKS_AT]-> Company`
- `Person -[:KNOWS]-> Person`
- `Company -[:LOCATED_IN]-> City`

#### Option B: Schema Description (Recommended)
Check **"Text is schema description"** and describe your desired schema.

**Example:**
```
I need a schema for a university system.
Students enroll in courses.
Professors teach courses.
Courses belong to departments.
Students can be friends with other students.
```

**Extracted Schema:**
- `Student -[:ENROLLS_IN]-> Course`
- `Professor -[:TEACHES]-> Course`
- `Course -[:BELONGS_TO]-> Department`
- `Student -[:FRIENDS_WITH]-> Student`

6. Click **"Analyze"**
7. Review extracted patterns
8. Click **"Apply"**

---

## Method 4: Data Importer JSON ⭐ RECOMMENDED FOR CUSTOM SCHEMAS

### What It Does
Allows you to upload a JSON file in Neo4j Data Importer format with complete schema definition.

### How to Use
1. Create a JSON file (see format below)
2. Click **"Graph Enhancement"** button
3. Go to **"Entity Extraction Settings"** tab
4. Click **"Add Schema from..."** dropdown
5. Select **"Data Importer JSON"**
6. Drag and drop your JSON file or click to browse
7. Review extracted patterns
8. Click **"Apply"**

### JSON File Format

The application expects the **Neo4j Data Importer format**. Here's the structure:

```json
{
  "dataModel": {
    "graphSchemaRepresentation": {
      "graphSchema": {
        "nodeLabels": [
          { "$id": "nl1", "token": "Person" },
          { "$id": "nl2", "token": "Company" }
        ],
        "relationshipTypes": [
          { "$id": "rt1", "token": "WORKS_AT" },
          { "$id": "rt2", "token": "KNOWS" }
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
          },
          {
            "$id": "rel2",
            "from": { "$ref": "#node1" },
            "to": { "$ref": "#node1" },
            "type": { "$ref": "#rt2" }
          }
        ]
      }
    }
  }
}
```

### Field Explanations

| Field | Description |
|-------|-------------|
| `nodeLabels` | Array of node types with unique IDs |
| `relationshipTypes` | Array of relationship types with unique IDs |
| `nodeObjectTypes` | Node instances that reference node labels |
| `relationshipObjectTypes` | Relationship instances connecting node objects |
| `$id` | Unique identifier for referencing |
| `$ref` | Reference to another element by ID (using `#` prefix) |
| `token` | The actual label/type name |

### See Example Files
Check `backend/docs/examples/` for complete examples:
- `social-network-schema.json` - Simple social network
- `custom-schema-template.json` - Template to copy
- `complete-example-schema.json` - Full featured example

---

## Creating Schemas Manually

You can also create patterns manually by typing directly into the dropdowns:

1. In the **"Graph Pattern"** section, you'll see three dropdowns:
   - **Source** - Starting node label
   - **Type** - Relationship type
   - **Target** - Ending node label

2. Click any dropdown and **start typing** to create new values:
   - Example: Type "Person" in Source
   - Type "KNOWS" in Type
   - Type "Person" in Target

3. Click **"+ Add"** button

4. Your pattern appears as: `Person -[:KNOWS]-> Person`

5. Repeat to add more patterns

6. Click **"Apply"** when done

---

## Best Practices

### 1. Start Simple
Begin with a few core patterns and expand as needed.

### 2. Use Consistent Naming
- **Node labels**: PascalCase (e.g., `Person`, `Company`, `PhoneNumber`)
- **Relationships**: UPPER_SNAKE_CASE (e.g., `WORKS_AT`, `KNOWS`, `LOCATED_IN`)

### 3. Define Bidirectional Relationships Carefully
If `Person -[:KNOWS]-> Person` is symmetric, you only need one pattern.
If different, use two:
- `Person -[:FOLLOWS]-> Person`
- `Person -[:FOLLOWED_BY]-> Person`

### 4. Test with Small Datasets
Apply your schema to a small document first to verify it extracts correctly.

### 5. Combine Multiple Sources
You can load schemas from multiple sources (Predefined + Custom + Database) - they will be combined.

---

## Troubleshooting

### "No data found" when loading from database
- Ensure your Neo4j database has data
- Check your connection in the connection modal
- Verify database credentials

### Menu items not clickable
- This was a bug that has been fixed
- Refresh your browser if you still experience issues

### Schema not extracting correctly from text
- Try using "Text is schema description" mode
- Be explicit about relationships (use verbs like "works at", "knows", "belongs to")
- Ensure the LLM model is selected in settings

### JSON upload fails
- Verify JSON is valid (use a JSON validator)
- Ensure it follows the Neo4j Data Importer format exactly
- Check that all `$ref` values reference existing `$id` values

---

## API Endpoints

For developers integrating with the backend:

### Get Database Schema
```
GET /api/schema/from-database
```
Returns existing node labels and relationship types from connected Neo4j database.

### Extract Schema from Text
```
POST /api/schema/from-text
Body: {
  "text": "your text here",
  "is_schema_description": true/false,
  "model": "model-name"
}
```
Returns extracted graph patterns from text using LLM.

---

## Additional Resources

- **Neo4j Data Importer**: https://console-preview.neo4j.io/tools/import/models
- **Example Schemas**: See `backend/docs/examples/`
- **Frontend Code**: `frontend/src/components/Popups/GraphEnhancementDialog/`
