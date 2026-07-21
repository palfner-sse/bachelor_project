from typing import TypedDict, Literal


class GlobalMessage(TypedDict):
    """
    A broadcast message posted by an agent visible to all nodes in the graph.

    Fields:
        node    : Name of the agent that produced the message.
        message : The message content, typically a summary of the agent's decision or outcome.
    """
    node: str
    message: str


class ProposedEnvironmentalChange(TypedDict):
    """
    A single codebase change proposed by the ModelDiffChangeAnalyzer.

    Fields:
        proposed_change : Concrete description of what must change in the codebase.
        source          : The specific model element or diff section this change originates from.
        reasoning       : Why this change is necessary given the model diff.
    """
    proposed_change: str
    source: str
    reasoning: str


class Issue(TypedDict):
    """
    A validation issue raised by a validator agent when rejecting a previous agent's output.

    Fields:
        issue     : Clear description of what is wrong.
        source    : The specific change, file, or plan comment this issue refers to.
        reasoning : Why this is considered an issue.
    """
    issue: str
    source: str
    reasoning: str


class Task(TypedDict):
    """
    A task created by the Orchestrator and assigned to a downstream agent.

    Fields:
        task      : Short instruction for the receiving agent describing what to do.
        reasoning : One sentence explaining why this task is needed.
        agent     : Name of the agent this task is assigned to.
    """
    task: str
    reasoning: str
    agent: str
