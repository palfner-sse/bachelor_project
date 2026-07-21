import operator
from typing import TypedDict, Annotated, List

from besser.BUML.metamodel.structural import DomainModel

from python.ai_generator.mas.types import GlobalMessage, Task, ProposedEnvironmentalChange, Issue

"""
Shared state passed between all agents in the multi-agent system.
Annotated fields use operator.add so LangGraph appends new entries instead of overwriting.

Fields:
    global_messages                                 : Broadcast messages from all agents visible to every node in the graph.
    task_list                                       : Current list of tasks assigned by the orchestrator to downstream agents.
    model_before                                    : The full BUML domain model before the change was applied.
    model_after                                     : The full BUML domain model after the change was applied.
    model_diff                                      : Raw string diff between model_before and model_after.
    proposed_environmental_changes                  : Structured list of codebase changes proposed by the ModelDiffChangeAnalyzer.
    issues                                          : Validation issues raised by a validator agent for the previous agent to fix.
    code_change_plan_validator_history              : Per-invocation log entries from the CodeChangePlanValidator.
    code_change_planer_history                      : Per-invocation log entries from the CodeChangePlaner.
    code_change_validator_history                   : Per-invocation log entries from the CodeChangeValidator.
    code_changer_history                            : Per-invocation log entries from the CodeChanger.
    model_diff_change_analysis_validator_history    : Per-invocation log entries from the ModelDiffChangeAnalysisValidator.
    model_diff_change_analyzer_history              : Per-invocation log entries from the ModelDiffChangeAnalyzer.
    orchestrator_history                            : Per-invocation log entries from the Orchestrator.
"""
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
