import json

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from python.config import MODEL_NAME
from python.mas.agents.system_prompts import BUML_DOKUMENTATION, CODE_CHANGE_VALIDATOR_PROMPT
from python.mas.agents.util import add_agent_history, add_task_list, add_global_messages, add_model_diff, add_models, \
    add_issues
from python.mas.state import State


async def code_change_validator(state: State):
    system_parts = [CODE_CHANGE_VALIDATOR_PROMPT, BUML_DOKUMENTATION]
    prompt_parts = []

    add_agent_history(state=state, input_list=system_parts, agent_name="code_change_validator")

    add_task_list(state=state, input_list=prompt_parts)
    add_global_messages(state=state, input_list=prompt_parts)
    add_model_diff(state=state, input_list=prompt_parts)
    add_models(state=state, input_list=prompt_parts)
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
                    tools=["Read", "Edit", "Glob", "Grep", "Bash", "WebFetch"]
                ),
        ):
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    result = await run()
    if not result:
        raise RuntimeError("code_changer returned no result")

    json_result = json.loads(result)

    return {"global_messages": [{"node": "code_changer", "message": json_result["message"]}],
            "issues": [{"issue": i["issue"], "source": i["source"], "reasoning": i["reasoning"]}
                       for i in json_result.get("issues", [])] if isinstance(json_result.get("issues"), list) else [],
            "code_change_validator_history": json_result["code_change_validator_history"]}


async def code_change_validator_routing(state: State):
    system_parts = []
    prompt_parts = []

    add_task_list(state=state, input_list=prompt_parts)
    add_global_messages(state=state, input_list=prompt_parts)

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
        raise RuntimeError("code_change_validator_routing returned no result")

    return result.strip()

code_change_validator_path_map = {"orchestrator": "orchestrator", "code_changer": "code_changer"}
