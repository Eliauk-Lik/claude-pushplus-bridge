#!/usr/bin/env python3
"""Claude Code → PushPlus → 智能手环 通知链路

由 Claude Code PermissionRequest hook 调用，在需要审批时推送通知。
内置 30 秒防抖，避免短时间多次审批触发 PushPlus 限流。

依赖: 零（仅 Python 3 标准库）
"""
import sys
import json
import os
import time
import urllib.request

TOKEN_FILE = os.path.expanduser("~/.claude/pushplus_token")
PUSHPLUS_URL = "http://www.pushplus.plus/send"
COOLDOWN_FILE = "/tmp/claude-push-cooldown"
MIN_INTERVAL = 30  # 两次推送最小间隔（秒）


def get_token() -> str:
    try:
        with open(TOKEN_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        return os.environ.get("PUSHPLUS_TOKEN", "")


def cooldown_ok() -> bool:
    """检查是否超过最小推送间隔"""
    try:
        with open(COOLDOWN_FILE) as f:
            last = float(f.read().strip())
        return (time.time() - last) >= MIN_INTERVAL
    except (FileNotFoundError, ValueError):
        return True


def mark_sent() -> None:
    try:
        with open(COOLDOWN_FILE, "w") as f:
            f.write(str(time.time()))
    except Exception:
        pass


def push(title: str, content: str) -> None:
    token = get_token()
    if not token:
        return

    payload = json.dumps({
        "token": token,
        "title": title,
        "content": content,
        "template": "markdown",
    }).encode("utf-8")

    req = urllib.request.Request(
        PUSHPLUS_URL,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


def main() -> None:
    hook_type = sys.argv[1] if len(sys.argv) > 1 else ""

    if hook_type == "PermissionRequest":
        if not cooldown_ok():
            print(json.dumps({"decision": "approve"}))
            return

        stdin_data: dict = {}
        try:
            raw = sys.stdin.read()
            if raw.strip():
                stdin_data = json.loads(raw)
        except json.JSONDecodeError:
            pass

        tool_name = stdin_data.get("tool_name", "未知")
        tool_input = stdin_data.get("tool_input", "")
        if len(tool_input) > 200:
            tool_input = tool_input[:200] + "..."

        push(
            "🔔 Claude 需要你的操作",
            f"**{tool_name}** 请求执行：\n`{tool_input}`",
        )
        mark_sent()

    # 输出决策 JSON，PermissionRequest 必须返回
    print(json.dumps({"decision": "approve"}))


if __name__ == "__main__":
    main()
