# Schema JSON Examples

This directory contains example JSON files in Neo4j Data Importer format that you can use to load custom graph schemas into the LLM Graph Builder.

## Files in This Directory

### 1. `custom-schema-template.json`
**Use this file as a starting point for your own schemas.**

- Minimal template with one relationship
- Copy this file and modify the labels and relationships
- Best for creating your first custom schema

**Pattern Created:**
```
YourNodeLabel1 -[:YOUR_RELATIONSHIP_TYPE]-> YourNodeLabel2
```

### 2. `social-network-schema.json`
**A complete social media platform schema.**

- Demonstrates multiple node types and relationships
- Shows self-referencing relationships (User follows User)
- Good example of a real-world schema

**Patterns Created:**
```
User -[:FOLLOWS]-> User
User -[:POSTS]-> Post
Post -[:CONTAINS]-> Link
Post -[:TAGS]-> Tag
Post -[:MENTIONS]-> User
User -[:REPLY_TO]-> Post
User -[:REPOST]-> Post
```

### 3. `complete-example-schema.json`
**A comprehensive business/professional network schema.**

- Demonstrates complex relationships
- Shows hierarchical patterns (City -> Country)
- Multiple relationship types between different entities
- Best example for understanding advanced schema design

**Patterns Created:**
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

## How to Use These Files

### Option 1: Use As-Is

1. Open the LLM Graph Builder application
2. Click **"Graph Enhancement"**
3. Go to **"Entity Extraction Settings"** tab
4. Click **"Add Schema from..."** dropdown
5. Select **"Data Importer JSON"**
6. Drag and drop one of these JSON files
7. Click **"Apply"**

### Option 2: Modify for Your Needs

1. Copy `custom-schema-template.json` to a new file
2. Edit the file to add your node labels and relationships:
   - Update `nodeLabels` with your entity types
   - Update `relationshipTypes` with your relationship types
   - Update `nodeObjectTypes` to reference your node labels
   - Update `relationshipObjectTypes` to connect your nodes
3. Follow the steps in Option 1 to upload your modified file

## Quick Start Tutorial

Let's create a simple library schema from scratch:

### Step 1: Copy the Template
```bash
cp custom-schema-template.json library-schema.json
```

### Step 2: Define Your Entities

We want to model:
- Books
- Authors
- Publishers
- Readers

### Step 3: Edit `library-schema.json`

```json
{
  "dataModel": {
    "graphSchemaRepresentation": {
      "graphSchema": {
        "nodeLabels": [
          { "$id": "nl1", "token": "Book" },
          { "$id": "nl2", "token": "Author" },
          { "$id": "nl3", "token": "Publisher" },
          { "$id": "nl4", "token": "Reader" }
        ],
        "relationshipTypes": [
          { "$id": "rt1", "token": "WROTE" },
          { "$id": "rt2", "token": "PUBLISHED" },
          { "$id": "rt3", "token": "READ" }
        ],
        "nodeObjectTypes": [
          { "$id": "node1", "labels": [{ "$ref": "#nl1" }] },
          { "$id": "node2", "labels": [{ "$ref": "#nl2" }] },
          { "$id": "node3", "labels": [{ "$ref": "#nl3" }] },
          { "$id": "node4", "labels": [{ "$ref": "#nl4" }] }
        ],
        "relationshipObjectTypes": [
          {
            "$id": "rel1",
            "from": { "$ref": "#node2" },
            "to": { "$ref": "#node1" },
            "type": { "$ref": "#rt1" }
          },
          {
            "$id": "rel2",
            "from": { "$ref": "#node3" },
            "to": { "$ref": "#node1" },
            "type": { "$ref": "#rt2" }
          },
          {
            "$id": "rel3",
            "from": { "$ref": "#node4" },
            "to": { "$ref": "#node1" },
            "type": { "$ref": "#rt3" }
          }
        ]
      }
    }
  }
}
```

### Step 4: Upload to Application

This creates the graph patterns:
```
Author -[:WROTE]-> Book
Publisher -[:PUBLISHED]-> Book
Reader -[:READ]-> Book
```

## Tips for Creating Your Own Schemas

### 1. Start Simple
Begin with 2-3 node types and 1-2 relationships. You can always add more later.

### 2. Think About Your Domain
Ask yourself:
- What are the main entities? (Nodes)
- How do they relate to each other? (Relationships)
- Are there hierarchies? (e.g., City -> Country -> Continent)

### 3. Use Clear Naming
- **Nodes**: Singular nouns in PascalCase (Person, not People)
- **Relationships**: Verbs in UPPER_SNAKE_CASE (WORKS_AT, not works_at)

### 4. Validate Your JSON
Before uploading, validate at https://jsonlint.com to catch syntax errors.

### 5. Test with Sample Data
Upload a small document first to verify the schema extracts entities correctly.

## Common Patterns

### Pattern: Self-Reference
When an entity relates to itself (e.g., Person knows Person):
- Create one node object
- Reference it in both `from` and `to` of the relationship

### Pattern: Many-to-Many
When entities can have multiple relationships:
- Create separate relationship objects for each type
- Use the same node objects but different relationship types

### Pattern: Hierarchy
When entities form a tree/hierarchy:
- Create relationship objects that connect each level
- Example: Person -> City -> Country -> Continent

## Troubleshooting

### Upload Fails
- **Check JSON syntax** at https://jsonlint.com
- **Verify all $ref values** point to existing $id values
- **Ensure $ref uses # prefix**: `"$ref": "#nl1"` not `"$ref": "nl1"`

### No Patterns Extracted
- **Check structure** matches Neo4j Data Importer format exactly
- **Verify all required arrays** are present (nodeLabels, relationshipTypes, etc.)

### Wrong Patterns Created
- **Review nodeObjectTypes** - ensure labels reference correct node types
- **Check relationshipObjectTypes** - verify from/to/type references are correct

## Need More Help?

- **Quick Reference**: `../SCHEMA_JSON_FORMAT.md`
- **Complete Guide**: `../SCHEMA_LOADING_GUIDE.md`
- **Neo4j Data Importer**: https://console-preview.neo4j.io/tools/import/models

## Contributing Examples

Have a great schema example? Consider adding it to this directory:

1. Create a descriptive filename (e.g., `healthcare-schema.json`)
2. Add clear comments in this README explaining what it models
3. Include the patterns it creates
4. Submit a pull request!
