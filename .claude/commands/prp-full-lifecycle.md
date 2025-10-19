---
description: Full PRP lifecycle automation - Create → Validate → Execute → Analyze → Learn
argument-hint: [feature-description]
---

# PRP Full Lifecycle - Automated Workflow

## Feature: $ARGUMENTS

**Purpose:** End-to-end PRP workflow automation - Create → Validate → Execute → Analyze → Learn

**Timeline:** Reduces manual orchestration from ~60 minutes to ~5 minutes

---

## 🎯 Workflow Overview

```
CREATE → VALIDATE → EXECUTE → ANALYZE → UPDATE KNOWLEDGE BASE
  ↓          ↓          ↓          ↓              ↓
 PRP      Pre-flight   Implement   Metrics    Self-improving
        checks pass   with gates   captured      system
```

---

## Phase 1: PRP Creation

**Executing:** `/prp-base-create "$ARGUMENTS"`

```markdown
## Step 1: Generate PRP with Parallel Research

Spawning research agents:
- codebase-analyst: Search Hygent stack patterns
- library-researcher: Fetch Graphiti/LlamaIndex/LangGraph docs
- knowledge-base-query: Check failure_patterns.yaml, success_metrics.yaml
- validation-strategist: Design test scenarios

Research scope:
- Hygent stack: Graphiti, LlamaIndex, LangGraph, Sigma.js, Neo4j, Qdrant
- Project docs: MASTER-PLAN.md, NOTES.md, IMPLEMENTATION-STRATEGY.MD
- Existing patterns in backend/app/ and frontend/src/

**Output:** PRPs/{feature-name}.md
```

---

## Phase 2: Pre-Flight Validation

**Executing:** `/prp-validate PRPs/{feature-name}.md`

```markdown
## Step 2: Validate PRP Before Execution

Quality Gates:
✓ All referenced files exist
✓ URLs accessible
✓ Hygent stack dependencies available (Graphiti, Neo4j, Qdrant)
✓ Environment variables configured (.env validation)
✓ Docker services running (docker compose ps)

Hygent-Specific Checks:
✓ Neo4j GDS library available (CALL gds.version())
✓ Ollama models present (ollama list)
✓ Qdrant collection exists or can be created
✓ Frontend Next.js server can start
✓ Backend FastAPI imports work

**Decision Point:**
- ✅ PASS: All checks passed → Proceed to execution
- ⚠️ ISSUES: Fix and re-validate
- 🛑 BLOCKED: Manual intervention required

**Output:** Validation report with pass/fail per check
```

---

## Phase 3: Implementation with Progressive Validation

**Executing:** `/prp-base-execute PRPs/{feature-name}.md`

```markdown
## Step 3: Execute PRP with 4-Level Validation

Implementation Mode: Progressive validation with early exit

Level 1: Syntax & Style (Immediate feedback)
  Commands:
    - ruff check backend/ --fix
    - mypy backend/
    - npm run lint (frontend)

  Early exit: If errors, auto-fix attempt → retry → if still failing, STOP

Level 2: Unit Tests (Component validation)
  Commands:
    - pytest backend/tests/ -v
    - npm test (frontend)

  Early exit: If failures, analyze → fix → retry → if still failing, STOP

Level 3: Integration (System validation)
  Commands:
    - docker compose up -d
    - curl http://localhost:8000/health
    - curl http://localhost:3000/api/graph

  Early exit: If services fail, troubleshoot → retry → if still failing, STOP

Level 4: Hygent-Specific Validation
  Commands:
    - Neo4j connection test (MATCH (n) RETURN count(n) LIMIT 1)
    - Qdrant collection test (GET /collections)
    - Graphiti extraction test (1 sample document)
    - Sigma.js render test (50 nodes)

  Success criteria: All Hygent components respond correctly

**Context-Aware Error Recovery:**
- Capture error messages, stack traces, failed validation commands
- Query knowledge_base/failure_patterns.yaml for similar issues
- Apply known fixes automatically
- Document new patterns if novel error

**Output:** Working implementation with all validation levels passed
```

---

## Phase 4: Post-Execution Analysis

**Executing:** `/prp-analyze-run PRPs/{feature-name}.md`

```markdown
## Step 4: Capture Metrics and Learnings

Execution Metrics Collection:
- Git statistics (commits, files changed, lines added/deleted)
- Test results (passed/failed counts)
- Code quality (ruff issues, mypy errors)
- Implementation time (start to completion)
- Validation iterations (how many fix-retry cycles)

Quality Scoring (Hygent-specific):
- Context Richness (8-10): All Graphiti/LlamaIndex/LangGraph references included
- Implementation Clarity (8-10): Clear integration with ottomator-agents patterns
- Validation Completeness (8-10): All 4 levels + Hygent checks passed
- Success Probability (8-10): Would pass Week 1-3 checkpoint criteria

Hygent-Specific Metrics:
- Entity extraction quality (>80% accuracy target)
- Graph visualization performance (<2s render for 150 nodes)
- Framework integration success (Graphiti + LlamaIndex + LangGraph)
- Neo4j query latency (<1s for typical queries)

Pattern Discovery:
- Success patterns: What worked well (e.g., "Using Instructor for structured LLM outputs")
- Failure patterns: What broke (e.g., "Python 3.12 dependency conflicts")
- Performance patterns: Bottlenecks identified
- Integration patterns: Framework quirks discovered

**Output:** Analysis report with metrics, patterns, recommendations
```

---

## Phase 5: Knowledge Base Update

**Executing:** Automatic update to PRPs/knowledge_base/

```markdown
## Step 5: Feed Learnings Back to System

Update Files:
1. PRPs/knowledge_base/failure_patterns.yaml
   - Add new patterns discovered during implementation
   - Update frequency counts for recurring issues
   - Tag with Hygent stack components (Graphiti, Neo4j, etc.)

2. PRPs/knowledge_base/success_metrics.yaml
   - Update running averages for feature type
   - Track Hygent-specific metrics (extraction quality, render time)
   - Adjust confidence scores based on actual outcomes

3. PRPs/knowledge_base/hygent_stack_gotchas.yaml (NEW)
   - Framework-specific quirks (Graphiti entity resolution edge cases)
   - Integration patterns (how LlamaIndex + LangGraph coordinate)
   - Performance optimizations (WebWorker for Force-Atlas2)
   - Validation shortcuts (common test patterns)

4. PRPs/knowledge_base/library_gotchas.yaml
   - Graphiti: Known limitations and workarounds
   - LlamaIndex: Integration patterns
   - LangGraph: Agent orchestration tips
   - Sigma.js: Performance optimization techniques

Self-Improvement Loop:
- Next PRP creation will query these files automatically
- Confidence scores adjusted based on historical success rates
- Known issues auto-avoided (e.g., Python version conflicts)
- Proven patterns auto-injected (e.g., Docker-first approach)

**Output:** Updated knowledge base files, ready for next PRP
```

---

## Continuous Improvement Metrics

After 5-10 PRPs executed through this lifecycle:

**Expected Improvements:**
- 📈 First-pass success rate: 60% → 90%
- ⏱️ Time to working code: 4 hours → 1.5 hours
- 🐛 Validation failures: 8 per PRP → 2 per PRP
- 🎯 Confidence score accuracy: ±3 points → ±1 point
- 🔁 Fix-retry iterations: 4 cycles → 1 cycle

**Hygent-Specific Improvements:**
- Entity extraction quality improves as prompts refined
- Graph rendering performance optimizations accumulated
- Framework integration patterns become standardized
- Neo4j + Qdrant query patterns optimized
- Week 1-3 checkpoint criteria consistently met

---

## Usage Examples

### Example 1: New Ingestion Format
```bash
/prp-full-lifecycle "Add support for Jupyter notebooks (.ipynb) to ingestion pipeline"

# Workflow:
# 1. Creates PRP with Docling patterns, LangChain loaders research
# 2. Validates: LangChain NotebookLoader available, test .ipynb file present
# 3. Executes: Adds loader, tests with sample notebook, validates extraction
# 4. Analyzes: Tracks cell extraction quality, metadata preservation
# 5. Updates KB: Adds "jupyter_notebook_loader" success pattern
```

### Example 2: Graph Visualization Feature
```bash
/prp-full-lifecycle "Add pathfinding between nodes (shortest path visualization)"

# Workflow:
# 1. Creates PRP with Neo4j path algorithms, Sigma.js path rendering
# 2. Validates: Neo4j GDS available, Sigma.js path plugin installed
# 3. Executes: Implements Neo4j shortest path query, frontend path highlight
# 4. Analyzes: Measures path computation latency, render performance
# 5. Updates KB: Documents Neo4j pathfinding patterns for future use
```

### Example 3: Week 1-3 Checkpoint Feature
```bash
/prp-full-lifecycle "Build Graphiti extraction quality validator (80% accuracy check)"

# Workflow:
# 1. Creates PRP referencing IMPLEMENTATION-STRATEGY.MD Week 3 criteria
# 2. Validates: Test corpus available (3 PDFs from NOTES.md)
# 3. Executes: Builds validator, tests with known-good papers
# 4. Analyzes: Tracks false positive/negative rates
# 5. Updates KB: Establishes baseline extraction quality metrics
```

---

## Integration with Existing Hygent Docs

**Automatically References:**
- `/Users/marco/Documents/PROJECTS_2025/Hygent/docs/MASTER-PLAN.md` → Architecture patterns
- `/Users/marco/Documents/PROJECTS_2025/Hygent/docs/NOTES.md` → Risk Radar, Week 1-3 checkpoints
- `/Users/marco/Documents/PROJECTS_2025/Hygent/docs/IMPLEMENTATION-STRATEGY.MD` → Detailed week plans
- `/Users/marco/Documents/PROJECTS_2025/Hygent/CLAUDE.md` → Project principles (KISS, YAGNI)

**Respects Hygent Constraints:**
- ✅ Use `rg` (ripgrep) instead of `grep` (from CLAUDE.md)
- ✅ Never assume context - ask questions if uncertain
- ✅ Never hallucinate libraries - only use verified stack
- ✅ Follow existing code patterns from backend/app/ and frontend/src/

---

## Success Criteria

**This lifecycle is successful if:**
✅ PRP quality scores average 8+ across all dimensions
✅ 90% of PRPs execute without manual intervention
✅ Knowledge base grows with every execution
✅ Time from idea to working code reduces by 60%
✅ Hygent Week 1-3 checkpoint criteria consistently met
✅ Framework integration patterns become standardized

**This lifecycle needs improvement if:**
❌ Validation failures increase over time
❌ Same issues recurring (pattern not captured)
❌ Manual intervention needed >20% of time
❌ Confidence scores don't improve accuracy
❌ Execution time not reducing

---

## Emergency Backup Plans

**If Phase 2 (Validation) Fails:**
- Option 1: Skip to execution, fail fast at Level 1
- Option 2: Manual fix guided by validation report
- Option 3: Simplify scope (reduce feature complexity)

**If Phase 3 (Execution) Blocks:**
- Option 1: Activate backup plans from NOTES.md Risk Radar
- Option 2: Create minimal viable implementation
- Option 3: Defer to Phase 2 (Enhanced Features)

**If Phase 5 (Knowledge Update) Fails:**
- Option 1: Continue without KB update (manual learning)
- Option 2: Batch update multiple PRPs later
- Option 3: Simplify KB structure (YAML → JSON)

---

## Expected Timeline

**Manual workflow (before this command):**
- PRP creation: 30-40 minutes
- Validation: 5-10 minutes (if remembered)
- Execution: 2-4 hours
- Analysis: 15-30 minutes (if remembered)
- KB update: Never (manual notes only)
- **Total:** ~3-5 hours with gaps

**Automated workflow (with this command):**
- PRP creation: 2-5 minutes (parallel research)
- Validation: 1-2 minutes (automatic)
- Execution: 1.5-3 hours (with auto-recovery)
- Analysis: 2-3 minutes (automatic)
- KB update: 1 minute (automatic)
- **Total:** ~2-3.5 hours, no gaps

**Time saved:** 1-2 hours per PRP
**Quality improvement:** Consistent validation + learning loop
**Knowledge retention:** 100% vs 0% (manual notes often forgotten)

---

**END OF LIFECYCLE COMMAND**
