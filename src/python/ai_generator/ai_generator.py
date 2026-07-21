import asyncio
import subprocess
import importlib.util

from python import config
from python.ai_generator.mas.graph import graph

"""
Dynamically loads and executes a B-UML model Python file and returns its domain_model variable.

Args:
    path : str  - Absolute or relative path to the model.py file

Return:
    DomainModel - The domain_model object defined in the loaded file
"""
def load_domain_model(path: str):
    spec = importlib.util.spec_from_file_location("model", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.domain_model


"""
Entry point for the AI generator. Computes the diff between two B-UML model files
and invokes the multi-agent system graph to migrate the codebase accordingly.

Args:
    model_before_path : str  - Path to the B-UML model file before the change
    model_after_path  : str  - Path to the B-UML model file after the change
    code_base_path    : str  - Path to the codebase directory the agents will read and modify
"""
def run(model_before_path: str, model_after_path: str, code_base_path: str):
    config.AGENT_CWD = code_base_path

    diff = subprocess.run(
        ["git", "diff", "--no-index", model_before_path, model_after_path],
        capture_output=True,
        text=True,
    )

    result = asyncio.run(graph.ainvoke({
        "model_before": load_domain_model(model_before_path),
        "model_after": load_domain_model(model_after_path),
        "model_diff": diff.stdout,
        "global_messages": [],
        "task_list": [],
        "proposed_environmental_changes": [],
        "issues": [],
    }))

    print(result)