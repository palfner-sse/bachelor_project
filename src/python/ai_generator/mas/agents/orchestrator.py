"""
Orchestrator Agent as described in 6.2.2.1.
"""

import json

from langgraph.graph import END

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from config import AGENT_MODEL, ROUTING_MODEL, AGENT_CWD
from ai_generator.mas.agents.system_prompts import ORCHESTRATOR_PROMPT, ORCHESTRATOR_PATH_PROMPT, BUML_DOKUMENTATION
from ai_generator.mas.util import add_global_messages, add_agent_history, add_task_list, add_model_diff, strip_json_markdown, run_with_retry
from ai_generator.mas.state import State

"""
Orchestrator Agents runnable node function

Args:
    state : State - Multiagent System State

Return:
    global_messages         : Agents Global Message update
    task_list               : Updated task list with assignments for subsequent agents
    orchestrator_history    : Agents internal Dialog between invocations
"""

async def orchestrator(state: State):
    # Adds the required information from the state to the system and user prompts.
    system_parts = [ORCHESTRATOR_PROMPT, BUML_DOKUMENTATION]
    prompt_parts = []

    add_agent_history(state=state, input_list=system_parts, agent_name="orchestrator")

    add_task_list(state=state, input_list=prompt_parts)
    add_global_messages(state=state, input_list=prompt_parts)
    add_model_diff(state=state, input_list=prompt_parts)

    system = "\n\n".join(system_parts)
    prompt = "\n\n".join(prompt_parts)

    # Asynchronous agent call function.
    async def run():
        result = None
        async for message in query(
                prompt=prompt,
                options=ClaudeAgentOptions(
                    model=AGENT_MODEL,
                    system_prompt=system,
                    permission_mode="bypassPermissions",
                    tools=["WebFetch"],
                    cwd=AGENT_CWD,
                ),
        ):
            # Prints all SDK messages (assistant text, tool calls, tool results, final result)
            # print("SDK MESSAGE [orchestrator]:", type(message).__name__, repr(message))
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    # Agent call with appropriate prompts and repetition in the event of failure.
    json_result = await run_with_retry(run, "orchestrator")
    if not json_result:
        raise RuntimeError("Orchestrator returned no result")

    print("RESULT [orchestrator]:", repr(json_result))
    print("\n\n")

    history = json_result.get("orchestrator_history", [])
    if isinstance(history, str):
        history = [history]

    return {"global_messages": [{"node": "orchestrator", "message": json_result["message"]}],
            "task_list": [{"task": t["task"], "reasoning": t["reasoning"], "agent": t["agent"]} for t in
                          json_result["task_list"]],
            "orchestrator_history": history}


"""
Routing function of the Orchestrator Agent, which determines which agent to route to next
based on the current task list and global messages.

Args:
    state : State - Multiagent System State

Return:
    str : Next node name to route to
"""
async def orchestrator_path(state: State):
    # Adds the required information from the state to the system and user prompts.
    system_parts = [ORCHESTRATOR_PATH_PROMPT]
    prompt_parts = []

    add_task_list(state=state, input_list=prompt_parts)
    add_global_messages(state=state, input_list=prompt_parts)

    system = "\n\n".join(system_parts)
    prompt = "\n\n".join(prompt_parts)

    # Asynchronous agent call function.
    async def run():
        result = None
        async for message in query(
                prompt=prompt,
                options=ClaudeAgentOptions(
                    model=ROUTING_MODEL,
                    system_prompt=system,
                    permission_mode="bypassPermissions",
                    tools=["WebFetch"],
                    cwd=AGENT_CWD,
                ),
        ):
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    # Agent call with appropriate prompts and repetition in the event of failure.
    json_result = await run_with_retry(run, "orchestrator_path")
    if not json_result:
        raise RuntimeError("Orchestrator_path returned no result")

    return json_result.get("next_agent", "").strip()

#Agent paths map used to determine the graph structure for conditional edges.
orchestrator_path_map = {"model_diff_change_analyzer": "model_diff_change_analyzer",
                         "code_change_planer": "code_change_planer", "code_changer": "code_changer", "finish": END}
