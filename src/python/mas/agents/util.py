from python.mas.state import State


def add_global_messages(state: State, input_list: list):
    if state["global_messages"]:
        global_messages = "\n".join(f"[{m['node']}]: {m['message']}" for m in state["global_messages"])
        input_list.append(f"Global messages:\n{global_messages}")
    else:
        input_list.append("No global messages")


def add_agent_history(state: State, input_list: list, agent_name: str):
    state_name = f"{agent_name}_history"

    if state[state_name]:
        agent_history = "\n".join(m for m in state[state_name])
        input_list.append(f"Your history:\n{agent_history}")
    else:
        input_list.append("No agent history")


def add_task_list(state: State, input_list: list):
    if state["task_list"]:
        task_list = "\n".join(
            f"Task Description: {t["task"]} with this reasoning {t["reasoning"]} which should be done by this agent {t["agent"]}"
            for t in state["task_list"])
        input_list.append(f"Task list:\n{task_list}")
    else:
        input_list.append("No task list")


def add_model_diff(state: State, input_list: list):
    if state["model_diff"]:
        input_list.append(f"Model Diff:\n{state['model_diff']}")
    else:
        input_list.append("No model diff")


def add_models(state: State, input_list: list):
    if state["model_before"]:
        input_list.append(f"Model Before:\n{state['model_before']}")
    else:
        input_list.append("No model before")

    if state["model_after"]:
        input_list.append(f"Model After:\n{state['model_after']}")
    else:
        input_list.append("No model after")


def add_proposed_environmental_changes(state: State, input_list: list):
    if state["proposed_environmental_changes"]:
        input_list.append(f"Proposed Environmental Changes:\n{state['proposed_environmental_changes']}")
    else:
        input_list.append("No proposed environmental changes")


def add_issues(state: State, input_list: list):
    if state["issues"]:
        input_list.append("Issues:\n" + "\n".join(state["issues"]))
    else:
        input_list.append("No issues")