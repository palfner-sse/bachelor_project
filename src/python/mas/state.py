import operator
from typing import TypedDict, Annotated, List

from python.mas.types import GlobalMessage, Task, ProposedEnvironmentalChange, Issue


class State(TypedDict):
    global_messages: Annotated[List[GlobalMessage], operator.add]
    task_list: list[Task]
    model_before: None
    model_after: None
    model_diff: str
    ProposedEnvironmentalChanges: list[ProposedEnvironmentalChange]
    issues: list[Issue]
    code_change_plan_validator_history: Annotated[List[str], operator.add]
    code_change_planer_history: Annotated[List[str], operator.add]
    code_change_validator_history: Annotated[List[str], operator.add]
    code_changer_history: Annotated[List[str], operator.add]
    model_diff_change_analysis_validator_history: Annotated[List[str], operator.add]
    model_diff_change_analyzer_history: Annotated[List[str], operator.add]
    orchestrator_history: Annotated[List[Issue], operator.add]
