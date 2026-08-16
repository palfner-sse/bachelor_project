# Bachelor Project — BESSER B-UML Java Code Generator & AI Migration Tool

A toolchain for generating Java source code from BESSER B-UML models and automatically migrating an existing Java codebase in response to model changes using a multi-agent AI system.

---

## What this project does

### Java Generator
Generates Java source files from a B-UML domain model:
- **Enumerations** — one `public enum` file per enumeration with all its literals
- **Classes** — one class file per class (sorted by inheritance) with:
  - Private fields for attributes and navigable association ends
  - Constructors, getters, setters, and add-methods
  - Method stubs for all methods defined in the model
  - Correct `extends` declaration for inherited classes

### AI Generator
When a B-UML model changes, the AI generator computes the diff between the before and after model and runs a multi-agent system (MAS) to automatically migrate the existing Java codebase to match the new model. The MAS pipeline consists of:
1. **Orchestrator** — splits the diff into chunks and delegates tasks
2. **ModelDiffChangeAnalyzer** — analyses each chunk and proposes codebase changes
3. **ModelDiffChangeAnalysisValidator** — validates the proposed changes
4. **CodeChangePlaner** — annotates source files with `[[PLAN:...]]` comments
5. **CodeChangePlanValidator** — validates the annotations
6. **CodeChanger** — implements the annotated changes as real code
7. **CodeChangeValidator** — verifies the implemented changes

---

## Installation

Requires Python 3.12+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/palfner-sse/bachelor_project.git
cd bachelor_project
uv pip install -e .
```

---

## Usage

Run from the project root:

### Java Generator
Generate Java source files from a B-UML model:
```bash
python src/python/main.py -b <model.py> -c <output_dir> -j
```

### AI Generator
Migrate an existing codebase based on a model change, wich works best with -c ./:
```bash
python src/python/main.py -b <before_model.py> -a <after_model.py> -c <codebase_dir>
```

### BUML Model Analyzer
Count all changeable elements in a B-UML model (classes, attributes, associations, methods, enums, etc.):
```bash
python src/python/main.py -b <model.py> --count
```

### Arguments

| Argument | Description |
|---|---|
| `-b` / `--before` | Path to the B-UML model file. Used as the sole input for the Java generator, or as the before-state model for the AI generator. |
| `-a` / `--after` | Path to the B-UML model file after the change. Required for the AI generator. |
| `-c` / `--codebase` | Output directory for the Java generator, or the codebase directory the AI generator reads and modifies. |
| `-j` / `--java` | Flag to use the Java generator. Omit to use the AI generator. |
| `--count` | Count changeable elements in the model (classes, attributes, methods, etc.). Outputs JSON with element counts. |

### Example

```bash
# Generate Java files from a model
python src/python/main.py -b input/before/model.py -c input/before/code_base/src -j

# Migrate codebase after a model change
python src/python/main.py -b input/before/model.py -a input/after/model.py -c input/before/code_base/src

# Count changeable elements in a model
python src/python/main.py -b input/model.py --count
```
