#!/usr/bin/env python3
"""Claude Code → PushPlus → 智能手环 通知链路

让 Claude Code 的权限请求和任务完成通知推送到你的手腕。

依赖: 零（仅用 Python 3 标准库）
推送服务: PushPlus (pushplus.plus)
"""

import sys
import json
import os
import urllib.request

TOKEN_FILE = os.path.expanduser("~/.claude/pushplus_token")
PUSHPLUS_URL = "http://www.pushplus.plus/send"


def get_token() -> str:
    """读取 PushPlus token，优先文件，其次环境变量"""
    try:
        with open(TOKEN_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        return os.environ.get("PUSHPLUS_TOKEN", "")


def send(title: str, content: str) -> None:
    """通过 PushPlus API 发送通知"""
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
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            # 正常使用时取消下面注释以查看日志:
            # print(f"[pushplus] code={result.get('code')} title={title}", file=sys.stderr)
    except Exception:
        pass  # 网络静默失败，不阻塞 Claude Code


def main() -> None:
    # 读取 Claude Code hook 传来的 stdin（含 tool_name, tool_input 等）
    stdin_data: dict = {}
    try:
        raw = sys.stdin.read()
        if raw.strip():
            stdin_data = json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 从命令行参数获取事件类型
    hook_type = sys.argv[1] if len(sys.argv) > 1 else ""

    if hook_type == "PermissionRequest":
        tool_name = stdin_data.get("tool_name", "未知")
        tool_input = stdin_data.get("tool_input", "")
        if len(tool_input) > 200:
            tool_input = tool_input[:200] + "..."
        send(
            "🔔 Claude 需要你的操作",
            f"**{tool_name}** 请求执行：\n`{tool_input}`",
        )

    elif hook_type == "Stop":
        send("✅ Claude 任务完成", "回来看看吧。")

    # 输出决策 JSON（PermissionRequest 需要，Stop 兼容）
    print(json.dumps({"decision": "approve"}))


if __name__ == "__main__":
    main()
