import json

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from python.config import MODEL_NAME
from python.mas.agents.system_prompts import MODEL_DIFF_CHANGE_ANALYSIS_VALIDATOR_PROMPT, \
    MODEL_DIFF_CHANGE_ANALYSIS_VALIDATOR_PATH_PROMPT, BUML_DOKUMENTATION
from python.mas.agents.util import add_agent_history, add_proposed_environmental_changes, add_model_diff, \
    add_global_messages, add_task_list, add_models, add_issues
from python.mas.state import State


async def model_diff_change_analysis_validator(state: State):
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

    async def run():
        result = None
        async for message in query(
                prompt=prompt,
                options=ClaudeAgentOptions(
                    model=MODEL_NAME,
                    system_prompt=system,
                    permission_mode="dontAsk",
                    tools=["WebFetch"],
                ),
        ):
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    result = await run()
    if not result:
        raise RuntimeError("model_diff_change_analysis_validator returned no result")

    json_result = json.loads(result)

    return {"global_messages": [{"node": "model_diff_change_analysis_validator", "message": json_result["message"]}],
            "issues": [{"issue": i["issue"], "source": i["source"], "reasoning": i["reasoning"]}
                       for i in json_result.get("issues", [])] if isinstance(json_result.get("issues"), list) else [],
            "model_diff_change_analysis_validator_history": json_result["model_diff_change_analysis_validator_history"]}


async def model_diff_change_analysis_validator_router(state: State):
    system_parts = [MODEL_DIFF_CHANGE_ANALYSIS_VALIDATOR_PATH_PROMPT]
    prompt_parts = []

    add_global_messages(state=state, input_list=prompt_parts)
    add_issues(state=state, input_list=prompt_parts)

    system = "\n\n".join(system_parts)
    prompt = "\n\n".join(prompt_parts)

    async def run():
        result = None
        async for message in query(
                prompt=prompt,
                options=ClaudeAgentOptions(
                    model=MODEL_NAME,
                    system_prompt=system,
                    permission_mode="dontAsk",
                ),
        ):
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    result = await run()
    if not result:
        raise RuntimeError("Orchestrator_path returned no result")

    return result.strip()


model_diff_change_analysis_validator_path_map = {"orchestrator": "orchestrator",
                                                 "model_diff_change_analyzer": "model_diff_change_analyzer"}
