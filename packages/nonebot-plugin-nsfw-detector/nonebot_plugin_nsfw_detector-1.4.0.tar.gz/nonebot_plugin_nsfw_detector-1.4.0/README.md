<h1 align="center">NoneBot Plugin NSFW Detector</h1>

<p align="center">
  <a href="https://github.com/Msg-Lbo/nonebot-plugin-nsfw-detector/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/Msg-Lbo/nonebot-plugin-nsfw-detector?style=flat-square" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-nsfw-detector">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-nsfw-detector?style=flat-square" alt="pypi">
  </a>
  <img src="https://img.shields.io/pypi/dm/nonebot-plugin-nsfw-detector?style=flat-square" alt="pypi download">
</p>

基于 [nsfwpy.cn](https://nsfwpy.cn) API 的 NoneBot2 NSFW 图片检测插件，可自动检测群聊中的不当图片并进行相应处理。

## ✨ 功能特性

- 🔍 **自动检测**：实时检测群聊中的图片内容。
- ⚠️ **智能警告**：对违规用户进行警告和记录。
- 🔇 **自动禁言**：违规后自动禁言指定时间。
- 🗑️ **消息撤回**：自动撤回违规图片及插件消息。
- 👢 **踢出群聊**：达到警告上限后可自动踢出。
- ⚙️ **灵活配置**：支持每个群组独立配置，并提供全局默认配置。
- 🛡️ **智能白名单**：自动跳过对管理员、群主和超级用户的检测。
- 🧪 **测试命令**：提供命令以测试插件功能是否正常。

## 🔧 安装与配置

### 1. 安装插件

使用 `nb-cli` 或 `pip` 安装本插件：

<details>
<summary>使用 nb-cli</summary>

```bash
nb plugin install nonebot-plugin-nsfw-detector
```

</details>

<details>
<summary>使用 pip</summary>

```bash
pip install nonebot-plugin-nsfw-detector
```

</details>

### 2. 环境配置

插件配置项遵循 `scoped config` 规范，请在您的 `.env` 文件中进行如下配置。请注意，配置项使用**双下划线 `__`** 作为分隔符。

```dotenv
# .env.prod

# 设置超级用户
SUPERUSERS=["你的QQ号"]

# NSFW检测器插件配置(可选)
NSFW_DETECTOR__API_URL="https://nsfwpy.cn/analyze"
NSFW_DETECTOR__MODEL="mobilenet_v2"
NSFW_DETECTOR__REQUEST_TIMEOUT=30

# 默认群组配置(可选)
NSFW_DETECTOR__DEFAULT_ENABLED=true
NSFW_DETECTOR__DEFAULT_THRESHOLD=0.7
NSFW_DETECTOR__DEFAULT_BAN_TIME=60
NSFW_DETECTOR__DEFAULT_WARNING_LIMIT=3
NSFW_DETECTOR__DEFAULT_KICK_ENABLED=true

# 消息撤回配置(可选)
NSFW_DETECTOR__AUTO_RECALL_ENABLED=true
NSFW_DETECTOR__RECALL_DELAY=5

# 调试与数据存储(可选)
NSFW_DETECTOR__DEBUG_MODE=false
NSFW_DETECTOR__DATA_DIR="data/nsfw_detector"
```

### 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NSFW_DETECTOR__API_URL` | `str` | `"https://nsfwpy.cn/analyze"` | NSFW检测API的URL |
| `NSFW_DETECTOR__MODEL` | `str` | `"mobilenet_v2"` | 使用的检测模型 |
| `NSFW_DETECTOR__REQUEST_TIMEOUT`| `int` | `30` | API请求超时时间（秒） |
| `NSFW_DETECTOR__DEFAULT_ENABLED`| `bool` | `True` | 默认是否在群聊中启用检测 |
| `NSFW_DETECTOR__DEFAULT_THRESHOLD`| `float` | `0.7` | 默认NSFW阈值，越低越严格 |
| `NSFW_DETECTOR__DEFAULT_BAN_TIME` | `int` | `60` | 默认禁言时间（分钟） |
| `NSFW_DETECTOR__DEFAULT_WARNING_LIMIT`| `int` | `3` | 默认警告次数上限 |
| `NSFW_DETECTOR__DEFAULT_KICK_ENABLED`| `bool` | `True` | 达到警告上限后是否踢出 |
| `NSFW_DETECTOR__AUTO_RECALL_ENABLED` | `bool` | `True` | 是否自动撤回插件发送的消息 |
| `NSFW_DETECTOR__RECALL_DELAY` | `int` | `5` | 撤回延迟时间（秒） |
| `NSFW_DETECTOR__DEBUG_MODE` | `bool` | `False`| 是否启用调试模式，输出详细日志 |
| `NSFW_DETECTOR__DATA_DIR` | `str` | `"data/nsfw_detector"` | 插件数据存储目录 |

## 📖 使用说明

### 用户命令

> **注意**：用户命令所有人都可以使用，**不会**触发处罚操作。

- `/nsfw_check`：回复包含图片的消息或在命令后附带图片，以检测图片的NSFW内容。

### 管理员命令

> **注意**：所有管理命令仅限**超级用户**使用。

- `/nsfw_config`：查看插件的默认配置。
- `/nsfw_set <参数> <值>`：在群聊中设置当前群的配置。
- `/nsfw_set <群号> <参数> <值>`：设置指定群的配置。
- `/nsfw_status`：查看当前群的状态和配置。
- `/nsfw_status <群号>`：查看指定群的状态和配置。
- `/nsfw_reset`：重置当前群所有用户的警告记录。
- `/nsfw_reset @用户` 或 `/nsfw_reset 用户QQ`：重置当前群指定用户的警告。
- `/nsfw_reset <群号> [用户QQ]`：重置指定群的警告记录。
- `/nsfw_test_recall`：在当前群聊中测试消息自动撤回功能。

### 可设置参数

| 参数 | 说明 | 示例值 |
|---|---|---|
| `threshold` | NSFW检测阈值 (0.0-1.0) | `0.5` |
| `ban_time` | 禁言时间（分钟） | `30` |
| `warning_limit` | 警告次数上限 | `2` |
| `kick_enabled` | 是否启用踢出 (`true`/`false`) | `false` |
| `enabled` | 是否启用NSFW检测 (`true`/`false`) | `false` |
| `auto_recall` | 是否自动撤回插件消息 (`true`/`false`) | `true` |
| `recall_delay` | 消息撤回延迟（秒） | `10` |

## 💡 注意事项

1. **API 依赖**：插件功能依赖于第三方API，请注意其服务状态和调用频率。
2. **机器人权限**：机器人需要**群管理员权限**才能执行禁言和踢出操作。
3. **网络问题**：请确保您的服务器与检测API之间的网络连接通畅。
4. **隐私安全**：图片仅用于实时检测，插件不会存储任何用户图片。

## 📄 更新日志

### v1.4.0
- ⚙️ 重构插件配置以使用 `scoped config`，避免与其他插件的配置项冲突。
- 🐛 修复了调用 NSFW 检测 API 时因请求参数错误导致的 `422` 错误。
- 📝 全面更新 `README.md`，提供了更清晰的安装、配置和使用说明。

### v1.3.0
- 🗑️ 新增消息自动撤回功能
- ⚙️ 新增 `auto_recall` 和 `recall_delay` 配置参数
- 🧪 新增 `/nsfw_test_recall` 测试命令
- 📝 优化日志记录和错误处理

### v1.2.0
- 🆕 新增 `/nsfw_check` 用户命令
- 📊 支持手动检测图片NSFW内容
- 🔍 显示详细检测结果和风险评级
- ⏱️ 显示检测耗时信息
- ✅ 纯检测功能，不触发处罚操作
- 📱 支持回复消息和附带图片两种使用方式

### v1.1.0
- 新增智能白名单功能
- 自动跳过管理员、群主和超级用户检测
- 优化权限检查逻辑
- 增强日志记录功能

### v1.0.0
- 基础NSFW检测功能
- 群组配置管理
- 警告记录系统
- 管理员命令支持
- 数据持久化存储

## 📄 开源许可

本插件使用 [MIT License](LICENSE) 开源。 