from typing import TypedDict, Literal


class GlobalMessage(TypedDict):
    node: str
    message: str


class ProposedEnvironmentalChange(TypedDict):
    proposed_change: str
    source: str
    reasoning: str


class Issue(TypedDict):
    issue: str
    source: str
    reasoning: str


class Task(TypedDict):
    task: str
    reasoning: str
