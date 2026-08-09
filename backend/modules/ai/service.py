import os
import anthropic
from anthropic.types import ToolParam

from backend.modules.tasks import repo as task_repo

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = (
        "You are a smart task management assistant for a todo application. "
        "You help users manage their tasks more effectively.\n\n"
        "You can only assist with task-related requests using the provided tools. "
        "If the user asks something unrelated to task management, politely decline "
        "and remind them of what you can help with.\n\n"
        "Rules:\n"
        "- Always use the provided tools to respond. Do not answer freely without calling a tool.\n"
        "- If no tool matches the user's intent, do not make up an answer. Return nothing and let the system handle it.\n"
        "- Reply in English by default. Switch to the user's language if they write in another language.\n"
        "- Be concise and actionable in your responses."
    )

TOOLS: list[ToolParam] = [
    {
        "name": "task_suggestion",
        "description": "When user ask for task suggestions, which task should be done first or the recommended sequence to complete tasks, call this tool.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

def _handle_task_suggestion(session, user_id):
    unfinished_tasks = task_repo.list_unfinished_tasks(session, user_id)
    if not unfinished_tasks:
        return "The user has no unfinished tasks."

    lines = []
    for t in unfinished_tasks:
        lines.append(f"- task_title: {t.task_title} | due: {t.task_due or "none"} | description: {t.task_description or "none"} | level: {t.task_level} | is_pinned: {t.is_pinned}")

    return "\n".join(lines)

def ask(prompt: str, session, user_id: int) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=TOOLS,
        system= SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    if response.stop_reason != "tool_use":
        return next(block.text for block in response.content if hasattr(block, "text"))

    tool_call = next(b for b in response.content if b.type == "tool_use")
    if tool_call.name == "task_suggestion":
        tool_result = _handle_task_suggestion(session, user_id)
    else:
        return "Unkown tool"

    second_response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=TOOLS,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt},
            {"role":"assistant", "content": response.content},
            {
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": tool_result
                }]
            }
        ]
    )
    return next(b.text for b in second_response.content if hasattr(b, "text"))