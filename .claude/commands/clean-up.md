---
description: Refactor code for better organization, readability, and documentation
argument-hint: <file-or-directory-path>
allowed-tools: Read, Edit, Grep, Glob, Bash(pytest:*), Bash(rg:*), Task
---

# Code Refactoring and Cleanup

## Target Path

Refactor the code at: **$ARGUMENTS**

## The Boy Scout Rule

**"Leave the code cleaner than you found it."**
- Always improve code—even slightly—whenever you touch it
- Apply Clean Code principles from Robert C. Martin's Clean Code
- Focus on readability, maintainability, and professional craftsmanship

## Clean Code Principles

### 1. Meaningful Naming
- **Use intention-revealing names**: `customerList` → `payingCustomers`
- **Avoid disinformation**: Don't call something `list` if it's a set
- **Make meaningful distinctions**: `getActiveAccount()` vs `getActiveAccountInfo()`
- **Use pronounceable and searchable names**
- **Avoid noise words**: Manager, Processor, Data (unless they add value)
- **Replace magic numbers with named constants**
- **Avoid encodings**: Hungarian notation or type prefixes

### 2. Functions Should Be Small and Focused
- **Do one thing only—and do it well** (Single Responsibility at function level)
- **Keep functions short** (ideally < 20 lines)
- **One level of abstraction per function**
- **Use descriptive names** (long names are acceptable if they clarify intent)
- **Minimize arguments**: Zero args (niladic) > one (monadic) > two (dyadic) >> three+ (avoid)
- **Avoid flag arguments** (split into separate functions)
- **No side effects** (a function shouldn't do hidden work)
- **Don't repeat yourself (DRY)**

### 3. Comments: Use Sparingly and Wisely
- **Prefer self-explanatory code over comments**
- **Never comment out code—delete it instead**
- **Avoid redundant, misleading, or noisy comments**
- **Good comments explain**:
  - Intent ("Why is this needed?")
  - Consequences ("This breaks if X changes")
  - Clarifications of complex logic
- **Don't use closing-brace comments** (// end if)

### 4. Formatting for Readability
- **Vertical openness**: Use blank lines to separate concepts
- **Vertical density**: Keep related code together
- **Vertical order**: Higher-level functions appear before lower-level ones
- **Keep lines short** (≤ 100–120 characters)
- **Declare variables close to their usage**
- **Use consistent indentation and whitespace**

### 5. Error Handling
- **Use exceptions, not error codes**
- **Write try/catch blocks first** (to define failure behavior early)
- **Provide context with exceptions** (include relevant data)
- **Don't return null—use special case objects or Optional**
- **Don't pass null as arguments**—defensive checks clutter code

### 6. Classes
- **Small and focused** (measured by number of responsibilities, not lines)
- **High cohesion**: Methods should operate on same set of instance variables
- **Single Responsibility Principle (SRP)**: A class should have only one reason to change
- **Base classes should know nothing about derivatives** (dependency inversion)

### 7. Professionalism & Craftsmanship
- **Code is a craft—write it with pride and care**
- **You are responsible for the long-term health of the codebase**
- **Clean code looks like it was written by someone who cares**

## Step-by-Step Instructions

### 1. Analysis Phase
- Read the target file(s) carefully using the Read tool
- If directory provided, use Glob to find all Python files: `rg --files -g "*.py"`
- Identify areas for improvement:
  - **Rigidity**: Hard to change
  - **Fragility**: Breaks in unexpected places
  - **Immobility**: Hard to reuse
  - **Viscosity**: Easy to do the wrong thing, hard to do the right thing
  - **Needless repetition** (violates DRY)
  - Redundant code
  - Unclear logic
  - Missing or poor documentation
  - Poor organization
  - Overly complex functions

### 2. Refactoring Phase

Follow KISS (Keep It Simple, Stupid) and YAGNI (You Aren't Gonna Need It) principles from @CLAUDE.md

**Add clear docstrings to:**
- All functions/methods (describe purpose, parameters, returns, raises)
- Complex code blocks (explain the "why" not just the "what")
- Classes (describe responsibility and usage)

**Code improvements:**
- Improve variable/function names for clarity
- Extract complex logic into well-named helper functions
- Remove dead code and unnecessary comments
- Ensure consistent code style matching repository patterns
- **CRITICAL**: Preserve all existing functionality - only refactor, don't change behavior

**Apply Object-Oriented Principles:**
- **Encapsulation**: Hide internal data (don't expose data structures directly)
- **Law of Demeter**: "Only talk to your immediate friends." Avoid chains like `a.getB().getC().doSomething()`
- **Polymorphism over if/else**: Prefer polymorphic behavior to conditional logic

**Simplicity & Refactoring:**
- **Successive refinement**: Write to make it work, then refactor to make it clean
- **Emergent design**: Follow simple design rules in order:
  1. Passes all tests
  2. Contains no duplication
  3. Expresses programmer intent
  4. Minimizes classes and methods

### 3. Docstring Format

Use this standard format for all Python docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief one-line description of what this function does.

    More detailed explanation if needed, describing the approach or algorithm.
    This section explains the "why" behind the implementation choices.

    Args:
        param1: Description of first parameter and its purpose
        param2: Description of second parameter and its purpose

    Returns:
        Description of return value and its structure

    Raises:
        ExceptionType: When and why this exception occurs
    """
    pass
```

### 4. Testing Phase

After refactoring:
- use the rules in `clean-up.md` to make sure the test are complete and follow the best practices
- Run existing tests to ensure functionality is preserved: `pytest $ARGUMENTS -v`
- If tests fail, fix the refactoring (not the tests) to maintain behavior
- **FIRST Principles for tests** (Fast, Independent, Repeatable, Self-validating, Timely)
- **One assert per test** (or one concept per test)
- Tests must be as clean as production code

## Final Report

Provide a comprehensive summary including:

1. **Files Modified**: List of all files changed
2. **Key Improvements**:
   - Organization improvements (e.g., "Extracted X helper functions")
   - Readability improvements (e.g., "Renamed Y unclear variables")
   - Documentation improvements (e.g., "Added Z docstrings")
   - Code smell reductions (e.g., "Eliminated N magic numbers")
3. **Lines of Code**: Before and after comparison
4. **Test Results**: Confirm all tests pass
5. **Next Steps**: Any remaining technical debt or suggestions

## Important Reminders

- **Do NOT change behavior** - only improve structure and documentation
- **Do NOT remove tests** - preserve all test coverage
- **Do follow existing patterns** - match the repository's code style
- **Do ask questions** - if unclear about intent, ask before refactoring
- **Always use Task tool** for complex multi-step refactoring tasks
- **Apply Boy Scout Rule** - leave the codebase cleaner than you found it