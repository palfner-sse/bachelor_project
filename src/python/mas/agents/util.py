from rpds.rpds import List

from python.mas.state import State


def add_global_messages(state: State, input_list: list):
    if state["global_messages"]:
        global_messages = "\n".join(f"[{m['node']}]: {m['message']}" for m in state["global_messages"])
        input_list.append(f"Global messages:\n{global_messages}")
        return
    else:
        input_list.append("No global messages")
        return


def add_agent_history(state: State, input_list: list, agent_name: str):
    state_name = f"{agent_name}_history"

    if state[state_name]:
        agent_history = "\n".join(m for m in state[state_name])
        input_list.append(f"Your history:\n{agent_history}")
        return
    else:
        input_list.append("No agent history")
        return


def add_task_list(state: State, input_list: list):
    if state["task_list"]:
        task_list = "\n".join(
            f"Task Description: {t["task"]} with this reasoning {t["reasoning"]}" for t in state["task_list"])
        input_list.append(f"Task list:\n{task_list}")
        return
    else:
        input_list.append("No task list")
        return


def add_model_diff(state: State, input_list: list):
    if state["model_diff"]:
        input_list.append(f"Model Diff:\n{state['model_diff']}")
    else:
        input_list.append("No model diff")
        return
