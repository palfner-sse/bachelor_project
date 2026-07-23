"""
Code Change Plan Validator Agent as described in section 6.2.2.5.
"""

import json

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from python.config import AGENT_MODEL, ROUTING_MODEL, AGENT_CWD
from python.ai_generator.mas.agents.system_prompts import CODE_CHANGE_PLAN_VALIDATOR_PROMPT, CODE_CHANGE_PLAN_VALIDATOR_PATH_PROMPT, BUML_DOKUMENTATION
from python.ai_generator.mas.util import add_agent_history, add_global_messages, add_task_list, add_model_diff, \
    add_proposed_environmental_changes, add_issues, strip_json_markdown, run_with_retry
from python.ai_generator.mas.state import State

"""
Code Change Plan Validator Agents runnable node function 

Args:
    state : State - Multiagent System State
    
Return:
    global_messages                         : Agents Global Message update
    issues                                  : Agents proposed issues in the work propsed by the Code Change Planing Agent
    code_change_plan_validator_history      : Agents internal Dialog between invocations  
"""

async def code_change_plan_validator(state: State):
    # Adds the required information from the state to the system and user prompts.
    system_parts = [CODE_CHANGE_PLAN_VALIDATOR_PROMPT, BUML_DOKUMENTATION]
    prompt_parts = []

    add_agent_history(state=state, input_list=system_parts, agent_name="code_change_plan_validator")

    add_task_list(state=state, input_list=prompt_parts)
    add_global_messages(state=state, input_list=prompt_parts)
    add_proposed_environmental_changes(state=state, input_list=prompt_parts)
    add_model_diff(state=state, input_list=prompt_parts)
    add_issues(state=state, input_list=prompt_parts)

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
                    tools=["Read", "Edit", "Write", "Glob", "Grep", "WebFetch"],
                    cwd=AGENT_CWD,
                ),
        ):
            # Prints all SDK messages (assistant text, tool calls, tool results, final result)
            print("SDK MESSAGE [code_change_plan_validator]:", type(message).__name__, repr(message))
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    # Agent call with appropriate prompts and repetition in the event of failure.
    result = await run_with_retry(run, "code_change_plan_validator")
    if not result:
        raise RuntimeError("code_change_plan_validator returned no result")

    print("RAW RESULT [code_change_plan_validator]:", repr(result))

    # JSON extraction from the agent response.
    json_result = json.loads(strip_json_markdown(result))

    return {"global_messages": [{"node": "code_change_plan_validator", "message": json_result["message"]}],
            "issues": [{"issue": i["issue"], "source": i["source"], "reasoning": i["reasoning"]}
                       for i in json_result.get("issues", [])] if isinstance(json_result.get("issues"), list) else [],
            "code_change_plan_validator_history": json_result["code_change_plan_validator_history"]}


"""
Routing function of the Code Change Plan Validator Agent, which determines whether the previous agent must 
revise its work or whether routing can return to the orchestrator because the previous work has been validated.

Args:
    state : State - Multiagent System State

Return:
    global_messages                         : Agents Global Message update
    issues                                  : Agents proposed issues in the work propsed by the Code Change Planing Agent
    code_change_plan_validator_history      : Agents internal Dialog between invocations  
"""
async def code_change_plan_validator_routing(state: State):
    # Adds the required information from the state to the system and user prompts.
    system_parts = [CODE_CHANGE_PLAN_VALIDATOR_PATH_PROMPT]
    prompt_parts = []

    add_global_messages(state=state, input_list=prompt_parts)
    add_issues(state=state, input_list=prompt_parts)

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
                ),
        ):
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    # Agent call with appropriate prompts and repetition in the event of failure.
    result = await run_with_retry(run, "code_change_plan_validator_routing")
    if not result:
        raise RuntimeError("code_change_plan_validator_routing returned no result")

    return result.strip()

#Agent paths map used to determine the graph structure for conditional edges.
code_change_plan_validator_path_map = {"orchestrator" : "orchestrator", "code_change_planer" : "code_change_planer"}
