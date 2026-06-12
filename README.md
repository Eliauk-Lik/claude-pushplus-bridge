# Claude Code → PushPlus → 手环通知

Claude Code 在需要你操作或任务完成时，通过 PushPlus 推送到你的手腕。

> 荣耀手环 / 华为手环 / 小米手环 / Apple Watch 均可，Android / iOS 均支持。

## 原理

```
Claude Code hook 事件
    ↓
notify.py (零依赖, 纯 Python 3 stdlib)
    ↓
PushPlus API (pushplus.plus)
    ↓
微信服务号推送
    ↓
手机通知 → 运动健康App → 手环震动
```

## 快速开始

### 1. 获取 PushPlus Token

打开 [pushplus.plus](http://www.pushplus.plus)，微信扫码关注服务号，复制 Token。

### 2. 保存 Token

```bash
echo "你的token" > ~/.claude/pushplus_token
```

### 3. 安装脚本

```bash
mkdir -p ~/.claude/scripts
cp notify.py ~/.claude/scripts/pushplus-notify.py
```

### 4. 配置 Claude Code Hooks

在 `~/.claude/settings.json` 的 `hooks` 段添加：

```json
"PermissionRequest": [
  {
    "matcher": "*",
    "hooks": [
      {
        "type": "command",
        "command": "python3 /home/Eliauk/.claude/scripts/pushplus-notify.py PermissionRequest"
      }
    ]
  }
],
"Stop": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 /home/Eliauk/.claude/scripts/pushplus-notify.py Stop"
      }
    ]
  }
]
```

### 5. 验证

```bash
echo '{"hook_type":"test"}' | python3 ~/.claude/scripts/pushplus-notify.py test
```

手机应当收到「🧪 PushPlus 链路测试」通知。

## 触发事件

| 事件 | 时机 | 推送内容 |
|------|------|---------|
| `PermissionRequest` | Claude 弹出权限确认框 | 🔔 需要你的操作 + 工具名 |
| `Stop` | Claude 完成任务 | ✅ 任务完成 |

## 手机侧检查清单

- [ ] 微信已关注 PushPlus 服务号
- [ ] 微信 → 设置 → 消息通知 → 接收服务号消息（开启）
- [ ] PushPlus 服务号未被设为免打扰
- [ ] 运动健康 App → 通知管理 → 微信通知同步到手环（开启）

## 项目结构

```
notify.py        # 核心脚本（零依赖）
settings-hook-sample.json  # Hook 配置示例
```

## License

MIT
