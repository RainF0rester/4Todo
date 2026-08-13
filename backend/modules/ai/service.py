import os
import anthropic
from anthropic.types import ToolParam
from datetime import datetime, timezone

from backend.modules.tasks.models import Task
from backend.modules.tasks import repo as task_repo
from backend.modules.tasks.service import _normalize as task_normalize

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

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
        f"Current datetime: {current_time}"
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
    },
    {
        "name": "create_tasks",
        "description": "When user wants to create on or more tasks, call this tool to extract task information from the user's message.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "task_title": {"type": "string"},
                            "task_description": {"type": "string"},
                            "task_due": {"type": "string", "description": "Format: YYYY-MM-DD HH:MM, or null if not mentioned. 12am means 23:59 and using 00:00 instead of 24:00, 12pm means 12:00."},
                            "task_level": {"type": "integer", "description": "Priority 1-4, infer from context if not specified. 1 means important and urgent, 2 means important but not urgent, 3 means not important but urgent, 4 means not important and not urgent."}
                        },
                        "required": ["task_title", "task_level"]
                    }
                }
            },
            "required": ["tasks"]
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

def _handle_create_tasks(session, user_id, tool_input: dict) -> str:
    tasks_from_agent = tool_input["tasks"]

    tasks = []
    for data in tasks_from_agent:
        try:
            normalized = task_normalize(data)
            normalized["user_id"] = user_id
            tasks.append(Task(**normalized))
        except ValueError:
            data.pop("task_due", None)
            normalized = task_normalize(data)
            normalized["user_id"] = user_id
            tasks.append(Task(**normalized))

    created = task_repo.bulk_create_tasks(session, tasks)
    prompt_lines_return = ["Successfully created {len(created)} tasks:"]
    for t in created:
        prompt_lines_return.append(f"- [id:{t.id}] {t.task_title} | due: {t.task_due or 'none'} | level: {t.task_level}")
    return "\n".join(prompt_lines_return)

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
    elif tool_call.name == "create_tasks":
        tool_result = _handle_create_tasks(session, user_id, tool_input=tool_call.input)
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