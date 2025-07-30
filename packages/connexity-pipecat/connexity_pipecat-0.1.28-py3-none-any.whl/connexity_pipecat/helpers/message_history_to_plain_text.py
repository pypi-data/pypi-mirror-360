import json
from typing import List, Dict

def message_history_to_plaintext(history: List[Dict]) -> str:
    """
    Map an OpenAI / Pipecat chat-history list to a plain transcript.

    Output format:
        System: ...
        Assistant: ...
        User: ...
        Assistant: ...
        …

    Notes
    -----
    • 'tool' frames are skipped.
    • If an assistant turn contains only `tool_calls`, the function prints the
      call name and arguments (feel free to drop or tweak that branch).
    """
    role_map = {"system": "System", "assistant": "Assistant", "user": "User"}
    lines = []

    for msg in history:
        role = msg.get("role")

        # ── skip or keep tool frames ─────────────────────────────────────────
        if role == "tool":
            # lines.append(f"Tool: {msg.get('content', '').strip()}")
            continue

        # ── regular text content ────────────────────────────────────────────
        content = msg.get("content", "")
        if content:
            lines.append(f"{role_map.get(role, role.title())}: {content.strip()}")
            continue

        # ── assistant tool-call with no direct content ───────────────────────
        if role == "assistant" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                fn = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"])
                lines.append(
                    f"Assistant (tool_call → {fn}): {json.dumps(args, ensure_ascii=False)}"
                )

    return "\n".join(lines)