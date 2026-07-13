import json

from langgraph.graph import END

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from python.config import AGENT_MODEL, ROUTING_MODEL, AGENT_CWD
from python.ai_generator.mas.agents.system_prompts import ORCHESTRATOR_PROMPT, ORCHESTRATOR_PATH_PROMPT, BUML_DOKUMENTATION
from python.ai_generator.mas.agents.util import add_global_messages, add_agent_history, add_task_list, add_model_diff, strip_json_markdown, run_with_retry
from python.ai_generator.mas.state import State


async def orchestrator(state: State):
    system_parts = [ORCHESTRATOR_PROMPT, BUML_DOKUMENTATION]
    prompt_parts = []

    add_agent_history(state=state, input_list=system_parts, agent_name="orchestrator")

    add_task_list(state=state, input_list=prompt_parts)
    add_global_messages(state=state, input_list=prompt_parts)
    add_model_diff(state=state, input_list=prompt_parts)

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
                    tools=["WebFetch"],
                    cwd=AGENT_CWD,
                ),
        ):
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    result = await run_with_retry(run, "orchestrator")
    if not result:
        raise RuntimeError("Orchestrator returned no result")

    print("RAW RESULT [orchestrator]:", repr(result))
    json_result = json.loads(strip_json_markdown(result))

    return {"global_messages": [{"node": "orchestrator", "message": json_result["message"]}],
            "task_list": [{"task": t["task"], "reasoning": t["reasoning"], "agent": t["agent"]} for t in
                          json_result["task_list"]],
            "orchestrator_history": json_result["orchestrator_history"]}


async def orchestrator_path(state: State):
    system_parts = [ORCHESTRATOR_PATH_PROMPT]
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
                    tools=["WebFetch"],
                    cwd=AGENT_CWD,
                ),
        ):
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    result = await run_with_retry(run, "orchestrator_path")
    if not result:
        raise RuntimeError("Orchestrator_path returned no result")

    return result.strip()


orchestrator_path_map = {"model_diff_change_analyzer": "model_diff_change_analyzer",
                         "code_change_planer": "code_change_planer", "code_changer": "code_changer", "finish": END}
