import os
import json
import anthropic
import redis
from anthropic.types import ToolParam
from datetime import datetime, timezone

from backend.modules.tasks.models import Task
from backend.modules.tasks import repo as task_repo
from backend.modules.tasks.service import _normalize as task_normalize

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    timeout=30.0
)
redis_client = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))
current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

CONVERSATION_TTL = 1800  # 30 minutes
CONVERSATION_MAX_MESSAGES = 20

def _get_history(user_id: int) -> list:
    data = redis_client.get(f"conv:{user_id}")
    return json.loads(data) if data else []

def _serialize_messages(messages: list) -> list:
    result = []
    for msg in messages:
        content = msg["content"]
        if isinstance(content, list) and content and hasattr(content[0], "model_dump"):
            content = [block.model_dump() for block in content]
        result.append({"role": msg["role"], "content": content})
    return result

def _save_history(user_id: int, messages: list):
    trimmed = messages[-CONVERSATION_MAX_MESSAGES:]
    redis_client.setex(f"conv:{user_id}", CONVERSATION_TTL, json.dumps(_serialize_messages(trimmed)))

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
        "description": "When user asks for task suggestions, which task should be done first, or the recommended sequence to complete tasks, call this tool.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "list_tasks",
        "description": "When user wants to see their tasks, asks what tasks they have, or asks about their task list, call this tool.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "create_tasks",
        "description": "When user wants to create one or more tasks, or break down a complex task into subtasks, call this tool.",
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
                            "task_due": {"type": "string", "description": "Format: YYYY-MM-DD HH:MM, or null if not mentioned. Use 23:59 instead of 24:00. 12am means 00:00, 12pm means 12:00."},
                            "task_level": {"type": "integer", "description": "Priority 1-4. 1=important and urgent, 2=important but not urgent, 3=not important but urgent, 4=not important and not urgent. Infer from context if not specified."}
                        },
                        "required": ["task_title", "task_level"]
                    }
                }
            },
            "required": ["tasks"]
        }
    },
    {
        "name": "complete_task",
        "description": "When user says they finished, completed, or done with a task, call this tool. If you don't know the exact task title, call list_tasks first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_title": {"type": "string", "description": "The title or partial title of the task to mark as complete"}
            },
            "required": ["task_title"]
        }
    },
    {
        "name": "delete_task",
        "description": "When user wants to delete or remove a task, call this tool. If you don't know the exact task title, call list_tasks first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_title": {"type": "string", "description": "The title or partial title of the task to delete"}
            },
            "required": ["task_title"]
        }
    },
    {
        "name": "update_task",
        "description": "When user wants to modify, edit, or update an existing task's title, description, due date, or priority, call this tool. If you don't know the exact task title, call list_tasks first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_title": {"type": "string", "description": "The title or partial title of the task to update"},
                "new_title": {"type": "string", "description": "New title if user wants to rename the task"},
                "new_description": {"type": "string", "description": "New description if user wants to update it"},
                "new_due": {"type": "string", "description": "New due date in format YYYY-MM-DD HH:MM, or null to clear it"},
                "new_level": {"type": "integer", "description": "New priority level 1-4"}
            },
            "required": ["task_title"]
        }
    }
]

def _find_task_by_title(session, user_id: int, title: str):
    tasks = task_repo.list_tasks(session, user_id=user_id, include_deleted=False)
    title_lower = title.lower()
    return next((t for t in tasks if title_lower in t.task_title.lower()), None)

def _handle_task_suggestion(session, user_id):
    unfinished_tasks = task_repo.list_unfinished_tasks(session, user_id)
    if not unfinished_tasks:
        return "The user has no unfinished tasks."

    lines = []
    for t in unfinished_tasks:
        lines.append(f"- task_title: {t.task_title} | due: {t.task_due or "none"} | description: {t.task_description or "none"} | level: {t.task_level} | is_pinned: {t.is_pinned}")

    return "\n".join(lines)

def _handle_list_tasks(session, user_id: int) -> str:
    tasks = task_repo.list_tasks(session, user_id=user_id, include_deleted=False)
    if not tasks:
        return "The user has no tasks."
    lines = []
    for t in tasks:
        status = "done" if t.is_finished else "pending"
        lines.append(f"- [id:{t.id}] {t.task_title} | due: {t.task_due or 'none'} | level: {t.task_level} | status: {status}")
    return "\n".join(lines)

def _handle_complete_task(session, user_id: int, tool_input: dict) -> str:
    task = _find_task_by_title(session, user_id, tool_input["task_title"])
    if not task:
        return f"Task '{tool_input['task_title']}' not found."
    task.is_finished = 1
    task_repo.update_task(session, task)
    return f"Task '{task.task_title}' marked as complete."

def _handle_delete_task(session, user_id: int, tool_input: dict) -> str:
    task = _find_task_by_title(session, user_id, tool_input["task_title"])
    if not task:
        return f"Task '{tool_input['task_title']}' not found."
    task_repo.soft_delete_task(session, task.id)
    return f"Task '{task.task_title}' deleted."

def _handle_update_task(session, user_id: int, tool_input: dict) -> str:
    task = _find_task_by_title(session, user_id, tool_input["task_title"])
    if not task:
        return f"Task '{tool_input['task_title']}' not found."
    if "new_title" in tool_input:
        task.task_title = tool_input["new_title"]
    if "new_description" in tool_input:
        task.task_description = tool_input["new_description"]
    if "new_level" in tool_input:
        task.task_level = tool_input["new_level"]
    if "new_due" in tool_input:
        try:
            from backend.modules.tasks.service import _parse_due_time
            task.task_due = _parse_due_time(tool_input["new_due"])
        except ValueError:
            pass
    task_repo.update_task(session, task)
    return f"Task '{task.task_title}' updated."

def _handle_create_tasks(session, user_id, tool_input: dict) -> str:
    tasks_from_agent = tool_input["tasks"]

    tasks = []
    for data in tasks_from_agent:
        try:
            normalized = task_normalize(data)
            normalized["user_id"] = user_id
            tasks.append(Task(**normalized))
        except ValueError:
            # due date always cause ValueError
            data.pop("task_due", None)
            normalized = task_normalize(data)
            normalized["user_id"] = user_id
            tasks.append(Task(**normalized))

    created = task_repo.bulk_create_tasks(session, tasks)
    prompt_lines_return = [f"Successfully created {len(created)} tasks:"]
    for t in created:
        prompt_lines_return.append(f"- [id:{t.id}] {t.task_title} | due: {t.task_due or 'none'} | level: {t.task_level}")
    return "\n".join(prompt_lines_return)

def _dispatch(tool_name: str, tool_input: dict, session, user_id) -> str:
    if tool_name == "task_suggestion":
        return _handle_task_suggestion(session, user_id)
    elif tool_name == "list_tasks":
        return _handle_list_tasks(session, user_id)
    elif tool_name == "create_tasks":
        return _handle_create_tasks(session, user_id, tool_input=tool_input)
    elif tool_name == "complete_task":
        return _handle_complete_task(session, user_id, tool_input=tool_input)
    elif tool_name == "delete_task":
        return _handle_delete_task(session, user_id, tool_input=tool_input)
    elif tool_name == "update_task":
        return _handle_update_task(session, user_id, tool_input=tool_input)
    else:
        return "Unknown tool"

MAX_STEPS = 10

def ask(prompt: str, session, user_id: int) -> str:
    messages = _get_history(user_id)
    messages.append({"role": "user", "content": prompt})

    steps = 0
    while steps < MAX_STEPS:
        steps += 1
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                tools=TOOLS,
                system=SYSTEM_PROMPT,
                messages=messages
            )
        except anthropic.APITimeoutError:
            _save_history(user_id, messages)
            return "Request timed out. Please try again."
        except anthropic.APIStatusError as e:
            _save_history(user_id, messages)
            return f"API error: {e.message}"

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            reply = next(b.text for b in response.content if hasattr(b, "text"))
            _save_history(user_id, messages)
            return reply
        elif response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = _dispatch(block.name, block.input, session, user_id)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    _save_history(user_id, messages)
    return "I was unable to complete the request. Please try again."