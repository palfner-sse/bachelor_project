import json

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from python.config import AGENT_MODEL, ROUTING_MODEL, AGENT_CWD
from python.ai_generator.mas.agents.system_prompts import BUML_DOKUMENTATION, CODE_CHANGE_VALIDATOR_PROMPT, \
    CODE_CHANGE_VALIDATOR_PATH_PROMPT
from python.ai_generator.mas.agents.util import add_agent_history, add_task_list, add_global_messages, add_model_diff, add_models, \
    add_issues, strip_json_markdown, run_with_retry
from python.ai_generator.mas.state import State


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
                    model=AGENT_MODEL,
                    system_prompt=system,
                    permission_mode="bypassPermissions",
                    tools=["Read", "Edit", "Glob", "Grep", "Bash", "WebFetch"],
                    cwd=AGENT_CWD,
                ),
        ):
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    result = await run_with_retry(run, "code_change_validator")
    if not result:
        raise RuntimeError("code_changer returned no result")

    print("RAW RESULT [code_change_validator]:", repr(result))
    json_result = json.loads(strip_json_markdown(result))

    return {"global_messages": [{"node": "code_changer", "message": json_result["message"]}],
            "issues": [{"issue": i["issue"], "source": i["source"], "reasoning": i["reasoning"]}
                       for i in json_result.get("issues", [])] if isinstance(json_result.get("issues"), list) else [],
            "code_change_validator_history": json_result["code_change_validator_history"]}


async def code_change_validator_routing(state: State):
    system_parts = [CODE_CHANGE_VALIDATOR_PATH_PROMPT]
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
                    model=ROUTING_MODEL,
                    system_prompt=system,
                    permission_mode="bypassPermissions",
                ),
        ):
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    result = await run_with_retry(run, "code_change_validator_routing")
    if not result:
        raise RuntimeError("code_change_validator_routing returned no result")

    return result.strip()

code_change_validator_path_map = {"orchestrator": "orchestrator", "code_changer": "code_changer"}
