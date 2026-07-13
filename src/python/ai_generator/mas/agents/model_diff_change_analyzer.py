import json

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from python.config import AGENT_MODEL, AGENT_CWD
from python.ai_generator.mas.agents.system_prompts import MODEL_DIFF_CHANGE_ANALYZER_PROMPT, BUML_DOKUMENTATION
from python.ai_generator.mas.agents.util import add_agent_history, add_model_diff, add_task_list, add_models, add_global_messages, \
    add_proposed_environmental_changes, add_issues, strip_json_markdown, run_with_retry
from python.ai_generator.mas.state import State


async def model_diff_change_analyzer(state: State):
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

    result = await run_with_retry(run, "model_diff_change_analyzer")
    if not result:
        raise RuntimeError("model_diff_change_analyzer returned no result")

    print("RAW RESULT [model_diff_change_analyzer]:", repr(result))
    json_result = json.loads(strip_json_markdown(result))

    return {"global_messages": [{"node": "model_diff_change_analyzer", "message": json_result["message"]}],
            "proposed_environmental_changes": [{"proposed_change": c["proposed_change"], "source": c["source"],
                                                "reasoning": c["reasoning"]}
                                               for c in json_result["proposed_environmental_changes"]],
            "model_diff_change_analyzer_history": json_result["model_diff_change_analyzer_history"]}
