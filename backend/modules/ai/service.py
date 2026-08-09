import os
import anthropic
from anthropic.types import ToolParam

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

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

def ask(prompt: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=TOOLS,
        system=(
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
    ),
        messages=[{"role": "user", "content": prompt}]
    )
    return next(block.text for block in response.content if hasattr(block, "text"))
