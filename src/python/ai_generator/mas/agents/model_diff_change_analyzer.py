"""
Model Diff Change Analyzer Agent as described in 6.2.2.2.
"""

import json

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from config import AGENT_MODEL, AGENT_CWD
from ai_generator.mas.agents.system_prompts import MODEL_DIFF_CHANGE_ANALYZER_PROMPT, BUML_DOKUMENTATION
from ai_generator.mas.util import add_agent_history, add_model_diff, add_task_list, add_models, add_global_messages, \
    add_proposed_environmental_changes, add_issues, strip_json_markdown, run_with_retry
from ai_generator.mas.state import State

"""
Model Diff Change Analyzer Agents runnable node function

Args:
    state : State - Multiagent System State

Return:
    global_messages                      : Agents Global Message update
    proposed_environmental_changes       : Agents proposed changes to the environment based on the model diff
    model_diff_change_analyzer_history   : Agents internal Dialog between invocations
"""

async def model_diff_change_analyzer(state: State):
    # Adds the required information from the state to the system and user prompts.
    system_parts = [MODEL_DIFF_CHANGE_ANALYZER_PROMPT, BUML_DOKUMENTATION]
    prompt_parts = []

    add_agent_history(state=state, input_list=system_parts, agent_name="model_diff_change_analyzer")

    add_task_list(state=state, input_list=prompt_parts)
    add_global_messages(state=state, input_list=prompt_parts)
    add_model_diff(state=state, input_list=prompt_parts)
    add_models(state=state, input_list=prompt_parts)
    add_proposed_environmental_changes(state=state, input_list=prompt_parts)
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
                    tools=["WebFetch"],
                    cwd=AGENT_CWD,
                ),
        ):
            # Prints all SDK messages (assistant text, tool calls, tool results, final result)
            # print("SDK MESSAGE [model_diff_change_analyzer]:", type(message).__name__, repr(message))
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    # Agent call with appropriate prompts and repetition in the event of failure.
    json_result = await run_with_retry(run, "model_diff_change_analyzer")
    if not json_result:
        raise RuntimeError("model_diff_change_analyzer returned no result")

    print("RESULT [model_diff_change_analyzer]:", repr(json_result))

    history = json_result.get("model_diff_change_analyzer_history", [])
    if isinstance(history, str):
        history = [history]

    return {"global_messages": [{"node": "model_diff_change_analyzer", "message": json_result["message"]}],
            "proposed_environmental_changes": [{"proposed_change": c["proposed_change"], "source": c["source"],
                                                "reasoning": c["reasoning"]}
                                               for c in json_result["proposed_environmental_changes"]],
            "model_diff_change_analyzer_history": history}
