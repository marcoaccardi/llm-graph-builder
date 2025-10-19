# Data Importer JSON Schema Format - Quick Reference

## Overview

This document provides a quick reference for creating Neo4j Data Importer JSON files to load custom graph schemas.

## File Structure

```
{
  dataModel
    └── graphSchemaRepresentation
          └── graphSchema
                ├── nodeLabels[]          // Define node types
                ├── relationshipTypes[]   // Define relationship types
                ├── nodeObjectTypes[]     // Create node instances
                └── relationshipObjectTypes[]  // Connect nodes
}
```

## Complete Minimal Example

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
          { "$id": "rt1", "token": "WORKS_AT" }
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

This creates the pattern: **`Person -[:WORKS_AT]-> Company`**

---

## Step-by-Step Guide

### Step 1: Define Node Labels

List all node types your graph will use:

```json
"nodeLabels": [
  { "$id": "nl1", "token": "Person" },
  { "$id": "nl2", "token": "Company" },
  { "$id": "nl3", "token": "City" }
]
```

**Rules:**
- Each entry needs a unique `$id` (e.g., "nl1", "nl2", "nl3")
- `token` is the actual node label name
- Use PascalCase for node labels (e.g., Person, PhoneNumber, CompanyAddress)

### Step 2: Define Relationship Types

List all relationship types:

```json
"relationshipTypes": [
  { "$id": "rt1", "token": "WORKS_AT" },
  { "$id": "rt2", "token": "LOCATED_IN" },
  { "$id": "rt3", "token": "KNOWS" }
]
```

**Rules:**
- Each entry needs a unique `$id` (e.g., "rt1", "rt2", "rt3")
- `token` is the actual relationship type name
- Use UPPER_SNAKE_CASE for relationships (e.g., WORKS_AT, KNOWS, LOCATED_IN)

### Step 3: Create Node Object Types

Create instances of each node label:

```json
"nodeObjectTypes": [
  {
    "$id": "node1",
    "labels": [{ "$ref": "#nl1" }]
  },
  {
    "$id": "node2",
    "labels": [{ "$ref": "#nl2" }]
  }
]
```

**Rules:**
- Each node object needs a unique `$id` (e.g., "node1", "node2")
- `$ref` must point to an existing node label ID using `#` prefix
- One node object per unique node label

### Step 4: Create Relationship Object Types

Connect node objects with relationships:

```json
"relationshipObjectTypes": [
  {
    "$id": "rel1",
    "from": { "$ref": "#node1" },
    "to": { "$ref": "#node2" },
    "type": { "$ref": "#rt1" }
  }
]
```

**Rules:**
- Each relationship needs a unique `$id`
- `from.$ref` points to source node object
- `to.$ref` points to target node object
- `type.$ref` points to relationship type
- All `$ref` values must use `#` prefix

---

## Common Patterns

### Self-Referencing Relationship

**Pattern:** `Person -[:KNOWS]-> Person`

```json
{
  "nodeLabels": [
    { "$id": "nl1", "token": "Person" }
  ],
  "relationshipTypes": [
    { "$id": "rt1", "token": "KNOWS" }
  ],
  "nodeObjectTypes": [
    { "$id": "node1", "labels": [{ "$ref": "#nl1" }] }
  ],
  "relationshipObjectTypes": [
    {
      "$id": "rel1",
      "from": { "$ref": "#node1" },
      "to": { "$ref": "#node1" },
      "type": { "$ref": "#rt1" }
    }
  ]
}
```

### Multiple Relationships Between Same Nodes

**Patterns:**
- `Person -[:WORKS_AT]-> Company`
- `Person -[:OWNS]-> Company`

```json
{
  "relationshipTypes": [
    { "$id": "rt1", "token": "WORKS_AT" },
    { "$id": "rt2", "token": "OWNS" }
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
      "to": { "$ref": "#node2" },
      "type": { "$ref": "#rt2" }
    }
  ]
}
```

### Chain of Relationships

**Patterns:**
- `Person -[:LIVES_IN]-> City`
- `City -[:IN_COUNTRY]-> Country`
- `Country -[:ON_CONTINENT]-> Continent`

```json
{
  "nodeLabels": [
    { "$id": "nl1", "token": "Person" },
    { "$id": "nl2", "token": "City" },
    { "$id": "nl3", "token": "Country" },
    { "$id": "nl4", "token": "Continent" }
  ],
  "relationshipTypes": [
    { "$id": "rt1", "token": "LIVES_IN" },
    { "$id": "rt2", "token": "IN_COUNTRY" },
    { "$id": "rt3", "token": "ON_CONTINENT" }
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
      "from": { "$ref": "#node1" },
      "to": { "$ref": "#node2" },
      "type": { "$ref": "#rt1" }
    },
    {
      "$id": "rel2",
      "from": { "$ref": "#node2" },
      "to": { "$ref": "#node3" },
      "type": { "$ref": "#rt2" }
    },
    {
      "$id": "rel3",
      "from": { "$ref": "#node3" },
      "to": { "$ref": "#node4" },
      "type": { "$ref": "#rt3" }
    }
  ]
}
```

---

## Validation Checklist

Before uploading your JSON file, verify:

- [ ] Valid JSON syntax (use https://jsonlint.com)
- [ ] All required top-level keys exist: `dataModel.graphSchemaRepresentation.graphSchema`
- [ ] All four arrays present: `nodeLabels`, `relationshipTypes`, `nodeObjectTypes`, `relationshipObjectTypes`
- [ ] Every element has a unique `$id`
- [ ] All `$ref` values:
  - Start with `#` prefix
  - Reference an existing `$id`
  - Point to correct type (node references node, relationship references relationship)
- [ ] No circular references in `$ref` chains
- [ ] At least one relationship defined

---

## Common Errors

### Error: "Invalid graphSchema format"

**Cause:** Missing required fields in JSON structure

**Fix:** Ensure your JSON has this exact structure:
```json
{
  "dataModel": {
    "graphSchemaRepresentation": {
      "graphSchema": {
        "nodeLabels": [...],
        "relationshipTypes": [...],
        "nodeObjectTypes": [...],
        "relationshipObjectTypes": [...]
      }
    }
  }
}
```

### Error: "Failed to parse JSON file"

**Cause:** Invalid JSON syntax

**Fix:**
- Remove trailing commas
- Use double quotes, not single quotes
- Validate at https://jsonlint.com

### References Not Working

**Cause:** `$ref` doesn't match any `$id`

**Fix:**
- Ensure `$ref` uses `#` prefix: `"$ref": "#nl1"`
- Check that the referenced `$id` exists
- Verify spelling matches exactly

---

## ID Naming Conventions

While you can use any string for IDs, we recommend:

| Type | Prefix | Example |
|------|--------|---------|
| Node Labels | `nl` | `nl1`, `nl2`, `nlPerson` |
| Relationship Types | `rt` | `rt1`, `rt2`, `rtWorksAt` |
| Node Objects | `node` | `node1`, `node2`, `nodePerson` |
| Relationship Objects | `rel` | `rel1`, `rel2`, `relWorksAt` |

---

## Quick Template

Copy this template and fill in your own values:

```json
{
  "dataModel": {
    "graphSchemaRepresentation": {
      "graphSchema": {
        "nodeLabels": [
          { "$id": "nl1", "token": "NODE_LABEL_1" },
          { "$id": "nl2", "token": "NODE_LABEL_2" }
        ],
        "relationshipTypes": [
          { "$id": "rt1", "token": "RELATIONSHIP_TYPE_1" }
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

Replace:
- `NODE_LABEL_1`, `NODE_LABEL_2` with your node labels
- `RELATIONSHIP_TYPE_1` with your relationship type

---

## Visual Diagram

```
┌─────────────────────────────────────────┐
│ nodeLabels                              │
│  ┌────────────────────┐                 │
│  │ $id: "nl1"         │◄────┐           │
│  │ token: "Person"    │     │           │
│  └────────────────────┘     │           │
└─────────────────────────────┼───────────┘
                              │
                              │ references via $ref
                              │
┌─────────────────────────────┼───────────┐
│ nodeObjectTypes             │           │
│  ┌────────────────────┐     │           │
│  │ $id: "node1"       │     │           │
│  │ labels:            │     │           │
│  │   $ref: "#nl1" ────┼─────┘           │
│  └────────────────────┘                 │
│         │                               │
│         │ used in relationships         │
│         ▼                               │
└─────────┼───────────────────────────────┘
          │
          │
┌─────────┼───────────────────────────────┐
│ relationshipObjectTypes                 │
│  ┌────────────────────┐                 │
│  │ $id: "rel1"        │                 │
│  │ from:              │                 │
│  │   $ref: "#node1" ──┼─────────────────┤
│  │ to:                │                 │
│  │   $ref: "#node2"   │                 │
│  │ type:              │                 │
│  │   $ref: "#rt1"     │                 │
│  └────────────────────┘                 │
└─────────────────────────────────────────┘
```

---

## Additional Resources

- Full Examples: `backend/docs/examples/`
- Complete Guide: `backend/docs/SCHEMA_LOADING_GUIDE.md`
- Neo4j Data Importer: https://console-preview.neo4j.io/tools/import/models
