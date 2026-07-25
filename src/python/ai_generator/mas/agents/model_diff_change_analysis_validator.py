"""
Model Diff Change Analysis Validator Agent as described in 6.2.2.3.
"""

import json

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from python.config import AGENT_MODEL, ROUTING_MODEL, AGENT_CWD
from python.ai_generator.mas.agents.system_prompts import MODEL_DIFF_CHANGE_ANALYSIS_VALIDATOR_PROMPT, \
    MODEL_DIFF_CHANGE_ANALYSIS_VALIDATOR_PATH_PROMPT, BUML_DOKUMENTATION
from python.ai_generator.mas.util import add_agent_history, add_proposed_environmental_changes, add_model_diff, \
    add_global_messages, add_task_list, add_models, add_issues, strip_json_markdown, run_with_retry
from python.ai_generator.mas.state import State

"""
Model Diff Change Analysis Validator Agents runnable node function

Args:
    state : State - Multiagent System State

Return:
    global_messages                                 : Agents Global Message update
    issues                                          : Agents proposed issues in the work proposed by the Model Diff Change Analyzer Agent
    model_diff_change_analysis_validator_history    : Agents internal Dialog between invocations
"""

async def model_diff_change_analysis_validator(state: State):
    # Adds the required information from the state to the system and user prompts.
    system_parts = [MODEL_DIFF_CHANGE_ANALYSIS_VALIDATOR_PROMPT, BUML_DOKUMENTATION]
    prompt_parts = []

    add_agent_history(state=state, input_list=system_parts, agent_name="model_diff_change_analysis_validator")

    add_task_list(state=state, input_list=prompt_parts)
    add_global_messages(state=state, input_list=prompt_parts)
    add_proposed_environmental_changes(state=state, input_list=prompt_parts)
    add_model_diff(state=state, input_list=prompt_parts)
    add_models(state=state, input_list=prompt_parts)

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
            print("SDK MESSAGE [model_diff_change_analysis_validator]:", type(message).__name__, repr(message))
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    # Agent call with appropriate prompts and repetition in the event of failure.
    json_result = await run_with_retry(run, "model_diff_change_analysis_validator")
    if not json_result:
        raise RuntimeError("model_diff_change_analysis_validator returned no result")

    print("RESULT [model_diff_change_analysis_validator]:", repr(json_result))

    return {"global_messages": [{"node": "model_diff_change_analysis_validator", "message": json_result["message"]}],
            "issues": [{"issue": i["issue"], "source": i["source"], "reasoning": i["reasoning"]}
                       for i in json_result.get("issues", [])] if isinstance(json_result.get("issues"), list) else [],
            "model_diff_change_analysis_validator_history": json_result["model_diff_change_analysis_validator_history"]}


"""
Routing function of the Model Diff Change Analysis Validator Agent, which determines whether the previous agent must
revise its work or whether routing can return to the orchestrator because the previous work has been validated.

Args:
    state : State - Multiagent System State

Return:
    str : Next node name to route to
"""
async def model_diff_change_analysis_validator_router(state: State):
    # Adds the required information from the state to the system and user prompts.
    system_parts = [MODEL_DIFF_CHANGE_ANALYSIS_VALIDATOR_PATH_PROMPT]
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
                    tools=["WebFetch"],
                    cwd=AGENT_CWD,
                ),
        ):
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    # Agent call with appropriate prompts and repetition in the event of failure.
    json_result = await run_with_retry(run, "model_diff_change_analysis_validator_router")
    if not json_result:
        raise RuntimeError("model_diff_change_analysis_validator_router returned no result")

    return json_result.get("next_agent", "").strip()

#Agent paths map used to determine the graph structure for conditional edges.
model_diff_change_analysis_validator_path_map = {"orchestrator": "orchestrator",
                                                 "model_diff_change_analyzer": "model_diff_change_analyzer"}
