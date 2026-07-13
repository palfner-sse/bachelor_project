import operator
from typing import TypedDict, Annotated, List

from besser.BUML.metamodel.structural import DomainModel

from python.ai_generator.mas.types import GlobalMessage, Task, ProposedEnvironmentalChange, Issue


class State(TypedDict):
    global_messages: Annotated[List[GlobalMessage], operator.add]
    task_list: list[Task]
    model_before: DomainModel
    model_after: DomainModel
    model_diff: str
    proposed_environmental_changes: list[ProposedEnvironmentalChange]
    issues: list[Issue]
    code_change_plan_validator_history: Annotated[List[str], operator.add]
    code_change_planer_history: Annotated[List[str], operator.add]
    code_change_validator_history: Annotated[List[str], operator.add]
    code_changer_history: Annotated[List[str], operator.add]
    model_diff_change_analysis_validator_history: Annotated[List[str], operator.add]
    model_diff_change_analyzer_history: Annotated[List[str], operator.add]
    orchestrator_history: Annotated[List[str], operator.add]
