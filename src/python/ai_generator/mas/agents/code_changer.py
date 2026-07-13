import json

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from python.config import AGENT_MODEL, AGENT_CWD
from python.ai_generator.mas.agents.system_prompts import CODE_CHANGER_PROMPT
from python.ai_generator.mas.agents.util import add_agent_history, add_task_list, add_global_messages, add_issues, strip_json_markdown, run_with_retry
from python.ai_generator.mas.state import State


async def code_changer(state: State):
    system_parts = [CODE_CHANGER_PROMPT]
    prompt_parts = []

    add_agent_history(state=state, input_list=system_parts, agent_name="code_changer")

    add_global_messages(state=state, input_list=prompt_parts)
    add_task_list(state=state, input_list=prompt_parts)
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

    result = await run_with_retry(run, "code_changer")
    if not result:
        raise RuntimeError("code_changer returned no result")

    print("RAW RESULT [code_changer]:", repr(result))
    json_result = json.loads(strip_json_markdown(result))

    return {"global_messages": [{"node": "code_changer", "message": json_result["message"]}],
            "code_changer_history": json_result["code_changer_history"]}
