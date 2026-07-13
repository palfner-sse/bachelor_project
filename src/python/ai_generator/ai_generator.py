import asyncio
import subprocess

import config
from input.after.model import domain_model as model_after
from input.before.model import domain_model as model_before

from python.ai_generator.mas.graph import graph

diff = subprocess.run(
    ["git", "diff", "--no-index", "input/before/model.py.save", "input/after/model.py.save"],
    capture_output=True,
    text=True,
    cwd="/home/klausmp/dev/work/bachelor_project"
)

result = asyncio.run(graph.ainvoke({
    "model_before": model_before,
    "model_after": model_after,
    "model_diff": diff.stdout,
    "global_messages": [],
    "task_list": [],
    "proposed_environmental_changes": [],
    "issues": [],
}))

print(result)

