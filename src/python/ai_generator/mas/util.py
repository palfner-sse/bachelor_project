import asyncio
import re

from python.ai_generator.mas.state import State

"""
Function to run async function with a retry if the passed function returns an exception mostly connection problems.

Args:
    run_fn : function   - function to run
    agent_name : string - name of the agent which is needed for a possible error message
    max_retries : int   - amount of times to rerun run_fn
    base_delay : float  - amount of for the first retry which is multiplied with the amount of retry
"""
async def run_with_retry(run_fn, agent_name: str, max_retries: int = 3, base_delay: float = 10.0):
    for attempt in range(max_retries + 1):
        try:
            return await run_fn()
        except Exception as e:
            error_msg = str(e)
            is_api_error = "Claude Code returned an error result" in error_msg
            if attempt < max_retries and is_api_error:
                delay = base_delay * (2 ** attempt)
                print(f"[{agent_name}] API error (attempt {attempt + 1}/{max_retries + 1}): {error_msg}. Retrying in {delay:.0f}s...")
                await asyncio.sleep(delay)
            else:
                raise


"""
Extracts a JSON Object string from a string that can be read by json.loads(). 
This is necessary because large language models not always return only JSON, even if tooled to do so.  

Args:
    text : str  - string to extract JSON Object strings from 
    
Return:
    str - cleand json Object string
"""
def strip_json_markdown(text: str) -> str:
    text = text.strip()
    # Extract from ```json ... ``` block if present
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if match:
        text = match.group(1)
    else:
        # Strip leading/trailing fences
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.DOTALL)
        # If there's prose before the JSON object, extract from first { to last }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
    return _escape_control_chars_in_strings(text)


"""
Converts wrongly escaped characters in JSON Object strings from /<char> to //<char> because the first on is not readable by json.loads()

Args:
    json_text : str  - string to escape chars in 

Return:
    str - converted json Object string
"""
def _escape_control_chars_in_strings(json_text: str) -> str:
    result = []
    inside_string = False
    index = 0

    while index < len(json_text):
        current_char = json_text[index]

        # When we hit a backslash inside a string, the next character is escaped —
        # copy both as-is so we don't accidentally re-escape something like \"
        if current_char == '\\' and inside_string:
            result.append(current_char)
            index += 1
            if index < len(json_text):
                result.append(json_text[index])
            index += 1
            continue

        # A quote toggles whether we are inside a JSON string value or not
        if current_char == '"':
            inside_string = not inside_string
            result.append(current_char)

        # Control characters (0x00–0x1F) inside a string are invalid JSON —
        # replace them with their proper escape sequences
        elif inside_string and ord(current_char) < 0x20:
            if current_char == '\n':
                result.append('\\n')
            elif current_char == '\r':
                result.append('\\r')
            elif current_char == '\t':
                result.append('\\t')
            else:
                result.append(f'\\u{ord(current_char):04x}')

        # Outside a string or a normal character — copy unchanged
        else:
            result.append(current_char)

        index += 1

    return ''.join(result)


"""
Adds global messages to a list of strings. 

Args:
    state : State       - Multiagent System State
    input_list : List   - List of string the global message state needs to be added to

"""
def add_global_messages(state: State, input_list: list):
    if state["global_messages"]:
        global_messages = "\n".join(f"[{m['node']}]: {m['message']}" for m in state["global_messages"])
        input_list.append(f"Global messages:\n{global_messages}")
    else:
        input_list.append("No global messages")


"""
Adds the agent's invocation history to a list of strings.

Args:
    state : State       - Multiagent System State
    input_list : List   - List of strings the agent history needs to be added to
    agent_name : str    - Name of the agent whose history should be retrieved from state
"""
def add_agent_history(state: State, input_list: list, agent_name: str):
    state_name = f"{agent_name}_history"

    if state[state_name]:
        agent_history = "\n".join(m for m in state[state_name])
        input_list.append(f"Your history:\n{agent_history}")
    else:
        input_list.append("No agent history")


"""
Adds the current task list to a list of strings.

Args:
    state : State       - Multiagent System State
    input_list : List   - List of strings the task list needs to be added to
"""
def add_task_list(state: State, input_list: list):
    if state["task_list"]:
        task_list = "\n".join(
            f"Task Description: {t["task"]} with this reasoning {t["reasoning"]} which should be done by this agent {t["agent"]}"
            for t in state["task_list"])
        input_list.append(f"Task list:\n{task_list}")
    else:
        input_list.append("No task list")


"""
Adds the raw model diff string to a list of strings.

Args:
    state : State       - Multiagent System State
    input_list : List   - List of strings the model diff needs to be added to
"""
def add_model_diff(state: State, input_list: list):
    if state["model_diff"]:
        input_list.append(f"Model Diff:\n{state['model_diff']}")
    else:
        input_list.append("No model diff")


"""
Adds both the model before and model after to a list of strings.

Args:
    state : State       - Multiagent System State
    input_list : List   - List of strings the models need to be added to
"""
def add_models(state: State, input_list: list):
    if state["model_before"]:
        input_list.append(f"Model Before:\n{state['model_before']}")
    else:
        input_list.append("No model before")

    if state["model_after"]:
        input_list.append(f"Model After:\n{state['model_after']}")
    else:
        input_list.append("No model after")


"""
Adds the proposed environmental changes to a list of strings.

Args:
    state : State       - Multiagent System State
    input_list : List   - List of strings the proposed changes need to be added to
"""
def add_proposed_environmental_changes(state: State, input_list: list):
    if state["proposed_environmental_changes"]:
        input_list.append(f"Proposed Environmental Changes:\n{state['proposed_environmental_changes']}")
    else:
        input_list.append("No proposed environmental changes")


"""
Adds the list of validation issues raised by a validator agent to a list of strings.

Args:
    state : State       - Multiagent System State
    input_list : List   - List of strings the issues need to be added to
"""
def add_issues(state: State, input_list: list):
    if state["issues"]:
        lines = [f"- Issue: {i['issue']}\n  Source: {i['source']}\n  Reasoning: {i['reasoning']}" for i in state["issues"]]
        input_list.append("Issues:\n" + "\n".join(lines))
    else:
        input_list.append("No issues")
