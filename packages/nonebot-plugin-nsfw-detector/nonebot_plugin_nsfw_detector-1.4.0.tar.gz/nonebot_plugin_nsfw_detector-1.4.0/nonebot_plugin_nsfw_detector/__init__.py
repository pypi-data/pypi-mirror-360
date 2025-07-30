import json
import asyncio
from pathlib import Path
from typing import Dict
from datetime import datetime

import httpx
from nonebot import get_plugin_config, get_driver, logger
from nonebot.adapters import Event, Bot
from nonebot.adapters.onebot.v11 import (
    Bot as OneBotV11Bot,
    GroupMessageEvent,
    MessageSegment,
)
from nonebot.plugin import PluginMetadata, on_message, on_command
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from nonebot.exception import MatcherException

from .config import Config

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="NSFW检测器",
    description="基于 nsfwpy.cn API 的 NoneBot2 NSFW 图片检测插件，自动检测群聊中的不当图片并进行相应处理",
    usage="""
自动功能：
- 检测群聊中的图片是否为NSFW内容
- 对违规用户进行警告、禁言、撤回消息
- 达到阈值后可踢出群聊
- 自动跳过管理员、群主和超级用户

用户命令：
/nsfw_check - 检测图片的NSFW内容（回复图片或附带图片发送）

管理员命令：
/nsfw_config - 查看默认配置
/nsfw_set <参数> <值> - 设置当前群配置
/nsfw_set <群号> <参数> <值> - 设置指定群配置
/nsfw_status - 查看当前群状态
/nsfw_status <群号> - 查看指定群状态
/nsfw_reset - 重置当前群所有警告
/nsfw_reset @用户 - 重置当前群指定用户
/nsfw_reset <群号> [用户QQ] - 重置指定群警告

配置参数：
threshold: NSFW阈值 (0.0-1.0)
ban_time: 禁言时间(分钟)
warning_limit: 警告次数上限
kick_enabled: 是否踢出群聊 (true/false)
enabled: 是否启用检测 (true/false)
auto_recall: 是否自动撤回插件消息 (true/false)
recall_delay: 消息撤回延迟时间(秒)

白名单：
- 超级用户（配置在.env中的SUPERUSERS）
- 群主（owner）
- 群管理员（admin）
    """,
    type="application",
    homepage="https://github.com/Msg-Lbo/nonebot-plugin-nsfw-detector",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

# 获取配置
plugin_config = get_plugin_config(Config).nsfw_detector
driver = get_driver()

# 数据存储路径
DATA_DIR = Path(plugin_config.data_dir)
DATA_DIR.mkdir(parents=True, exist_ok=True)
WARNING_FILE = DATA_DIR / "warnings.json"
CONFIG_FILE = DATA_DIR / "group_configs.json"

# 内存中的数据存储
user_warnings: Dict[str, Dict[str, Dict]] = (
    {}
)  # {group_id: {user_id: {count: int, last_time: datetime}}}
group_configs: Dict[str, Dict] = (
    {}
)  # {group_id: {threshold: float, ban_time: int, ...}}

# 默认配置
DEFAULT_GROUP_CONFIG: Dict[str, any] = {}


def load_data():
    """加载数据"""
    global user_warnings, group_configs

    # 加载警告数据
    if WARNING_FILE.exists():
        try:
            with open(WARNING_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 转换时间字符串回datetime对象
                for group_id, users in data.items():
                    user_warnings[group_id] = {}
                    for user_id, user_data in users.items():
                        user_warnings[group_id][user_id] = {
                            "count": user_data["count"],
                            "last_time": datetime.fromisoformat(user_data["last_time"]),
                        }
        except Exception as e:
            logger.error(f"加载警告数据失败: {e}")
            user_warnings = {}

    # 加载群组配置
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                group_configs = json.load(f)
        except Exception as e:
            logger.error(f"加载群组配置失败: {e}")
            group_configs = {}


def save_data():
    """保存数据"""
    try:
        # 保存警告数据
        data_to_save = {}
        for group_id, users in user_warnings.items():
            data_to_save[group_id] = {}
            for user_id, user_data in users.items():
                data_to_save[group_id][user_id] = {
                    "count": user_data["count"],
                    "last_time": user_data["last_time"].isoformat(),
                }

        with open(WARNING_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)

        # 保存群组配置
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(group_configs, f, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"保存数据失败: {e}")


def get_group_config(group_id: str) -> Dict:
    """获取群组配置"""
    if group_id not in group_configs:
        group_configs[group_id] = DEFAULT_GROUP_CONFIG.copy()
        save_data()
    return group_configs[group_id]


async def send_with_auto_recall(
    bot: OneBotV11Bot, 
    group_id: int, 
    message: str, 
    group_config: Dict = None
) -> None:
    """发送群消息并根据配置自动撤回"""
    try:
        # 发送消息
        message_info = await bot.send_group_msg(group_id=group_id, message=message)
        
        # 调试: 打印消息信息结构
        logger.info(f"发送消息返回信息: {message_info}, 类型: {type(message_info)}")
        
        # 检查是否需要自动撤回
        if group_config is None:
            group_config = get_group_config(str(group_id))
        
        auto_recall = group_config.get("auto_recall", plugin_config.auto_recall_enabled)
        recall_delay = group_config.get("recall_delay", plugin_config.recall_delay)
        
        logger.info(f"撤回配置 - 群:{group_id}, 自动撤回:{auto_recall}, 延迟:{recall_delay}秒")
        
        if auto_recall and recall_delay > 0:
            # 尝试多种方式获取消息ID
            message_id = None
            
            # 方式1: 直接从返回值获取
            if isinstance(message_info, dict):
                message_id = message_info.get("message_id") or message_info.get("msg_id")
            
            # 方式2: 如果返回的是数字，直接使用
            elif isinstance(message_info, (int, str)):
                message_id = int(message_info) if str(message_info).isdigit() else None
            
            # 方式3: 检查是否有其他可能的字段
            if not message_id and hasattr(message_info, '__dict__'):
                for attr in ['message_id', 'msg_id', 'id']:
                    if hasattr(message_info, attr):
                        message_id = getattr(message_info, attr)
                        break
            
            logger.info(f"获取到的消息ID: {message_id}, 类型: {type(message_id)}")
            
            if message_id:
                # 延迟撤回
                async def recall_message():
                    try:
                        logger.info(f"开始等待 {recall_delay} 秒后撤回消息 - 群:{group_id}, 消息ID:{message_id}")
                        await asyncio.sleep(recall_delay)
                        await bot.delete_msg(message_id=message_id)
                        logger.info(f"✅ 已自动撤回消息 - 群:{group_id}, 消息ID:{message_id}")
                    except Exception as e:
                        logger.warning(f"❌ 自动撤回消息失败 - 群:{group_id}, 消息ID:{message_id}, 错误:{e}")
                
                # 创建后台任务
                task = asyncio.create_task(recall_message())
                logger.info(f"已创建撤回任务 - 群:{group_id}, 任务ID:{id(task)}")
            else:
                logger.warning(f"❌ 无法获取消息ID，跳过自动撤回 - 群:{group_id}")
        else:
            logger.info(f"自动撤回未启用或延迟为0 - 群:{group_id}")
    
    except Exception as e:
        logger.error(f"发送消息失败 - 群:{group_id}, 错误:{e}")
        raise


async def smart_send_with_recall(bot: Bot, event: Event, message: str) -> None:
    """智能发送消息，支持群聊自动撤回"""
    try:
        if hasattr(event, 'group_id') and event.group_id:
            # 群聊消息 - 使用自动撤回功能
            group_id = int(event.group_id)
            group_config = get_group_config(str(group_id))
            
            # 确保bot是OneBotV11Bot类型
            if isinstance(bot, OneBotV11Bot):
                await send_with_auto_recall(bot, group_id, message, group_config)
            else:
                # 如果不是OneBot v11，直接发送
                await bot.send(event, message)
        else:
            # 私聊消息 - 直接发送，不撤回
            await bot.send(event, message)
    except Exception as e:
        logger.error(f"智能发送消息失败: {e}")
        # 回退到普通发送
        await bot.send(event, message)


async def smart_finish_with_recall(matcher, bot: Bot, event: Event, message: str) -> None:
    """智能结束命令并发送消息，支持群聊自动撤回"""
    try:
        await smart_send_with_recall(bot, event, message)
    except MatcherException:
        raise
    except Exception as e:
        logger.error(f"智能结束命令失败: {e}")
        # 回退到普通finish
        await matcher.finish(message)


async def detect_nsfw(image_data: bytes) -> Dict:
    """使用nsfwpy.cn API检测NSFW内容"""
    if not image_data:
        return {"error": "没有提供图片数据"}

    try:
        async with httpx.AsyncClient() as client:
            files = {"file": ("image.jpg", image_data, "image/jpeg")}
            data = {"model": plugin_config.model}
            response = await client.post(
                url=plugin_config.api_url,
                files=files,
                data=data,
                timeout=plugin_config.request_timeout,
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.error("请求NSFW API超时")
        return {"error": "请求API超时"}
    except httpx.HTTPStatusError as e:
        logger.error(f"请求NSFW API失败: {e.response.status_code}, {e.response.text}")
        return {"error": f"API请求失败: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"检测过程中发生未知错误: {e}")
        return {"error": f"未知错误: {e}"}


async def download_image(image_url: str) -> bytes:
    """下载图片"""
    # 设置请求头，模拟QQ客户端
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://web.qun.qq.com/',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # 尝试多次下载
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(image_url, headers=headers)
                response.raise_for_status()
                
                # 检查响应内容类型
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    logger.warning(f"响应内容类型不是图片: {content_type}")
                
                # 检查内容长度
                content = response.content
                if len(content) < 100:  # 太小的文件可能不是有效图片
                    raise ValueError(f"下载的文件太小: {len(content)} bytes")
                
                logger.info(f"成功下载图片，大小: {len(content)} bytes")
                return content
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP错误 (尝试 {attempt + 1}/{max_retries}): {e.response.status_code} - {e}")
            if e.response.status_code == 403:
                logger.error("图片访问被拒绝，可能是权限问题")
            elif e.response.status_code == 404:
                logger.error("图片不存在或已过期")
            
            if attempt == max_retries - 1:
                raise ValueError(f"图片下载失败: HTTP {e.response.status_code}")
                
        except httpx.TimeoutException:
            logger.error(f"下载超时 (尝试 {attempt + 1}/{max_retries})")
            if attempt == max_retries - 1:
                raise ValueError("图片下载超时")
                
        except Exception as e:
            logger.error(f"下载失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise ValueError(f"图片下载失败: {str(e)}")
        
        # 等待一段时间后重试
        if attempt < max_retries - 1:
            await asyncio.sleep(1)
    
    raise ValueError("图片下载失败: 超过最大重试次数")


def add_warning(group_id: str, user_id: str) -> int:
    """添加警告记录，返回当前警告次数"""
    if group_id not in user_warnings:
        user_warnings[group_id] = {}

    if user_id not in user_warnings[group_id]:
        user_warnings[group_id][user_id] = {"count": 0, "last_time": datetime.now()}

    user_warnings[group_id][user_id]["count"] += 1
    user_warnings[group_id][user_id]["last_time"] = datetime.now()

    save_data()
    return user_warnings[group_id][user_id]["count"]


def get_warning_count(group_id: str, user_id: str) -> int:
    """获取用户警告次数"""
    if group_id in user_warnings and user_id in user_warnings[group_id]:
        return user_warnings[group_id][user_id]["count"]
    return 0


def reset_warnings(group_id: str, user_id: str = None):
    """重置警告记录"""
    if group_id in user_warnings:
        if user_id:
            if user_id in user_warnings[group_id]:
                del user_warnings[group_id][user_id]
        else:
            user_warnings[group_id] = {}
    save_data()


# 启动时加载数据
@driver.on_startup
async def startup():
    """启动时加载数据并应用配置"""
    global DEFAULT_GROUP_CONFIG
    logger.info("NSFW检测插件正在启动...")

    # 从主配置更新默认群组配置
    DEFAULT_GROUP_CONFIG = {
        "enabled": plugin_config.default_enabled,
        "threshold": plugin_config.default_threshold,
        "ban_time": plugin_config.default_ban_time,
        "warning_limit": plugin_config.default_warning_limit,
        "kick_enabled": plugin_config.default_kick_enabled,
        "auto_recall": plugin_config.auto_recall_enabled,
        "recall_delay": plugin_config.recall_delay,
    }

    load_data()
    logger.info("NSFW插件数据加载完成")


async def is_user_privileged(bot: OneBotV11Bot, group_id: int, user_id: int) -> bool:
    """检查用户是否有特权（管理员、群主或超级用户）"""
    try:
        # 检查是否为超级用户
        from nonebot import get_driver
        driver = get_driver()
        superusers = driver.config.superusers
        if str(user_id) in superusers:
            logger.info(f"用户 {user_id} 是超级用户，跳过检测")
            return True
        
        # 获取群成员信息
        member_info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
        role = member_info.get("role", "member")
        
        # 检查是否为管理员或群主
        if role in ["admin", "owner"]:
            logger.info(f"用户 {user_id} 是群 {group_id} 的{role}，跳过检测")
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"检查用户权限失败 - 群:{group_id}, 用户:{user_id}, 错误:{e}")
        return False


# 消息处理器
message_handler = on_message(priority=5, block=False)


@message_handler.handle()
async def handle_message(bot: OneBotV11Bot, event: GroupMessageEvent, state: T_State):
    """处理群消息，检测NSFW图片"""
    group_id = str(event.group_id)
    user_id = str(event.user_id)
    group_config = get_group_config(group_id)

    # 调试模式下打印配置
    if plugin_config.debug_mode:
        logger.info(f"调试模式 - 群组({group_id})配置: {group_config}")
        logger.info(f"调试模式 - 用户({user_id})警告: {user_warnings.get(group_id, {}).get(user_id)}")

    # 检查插件是否在该群启用
    if not group_config.get("enabled", plugin_config.default_enabled):
        return

    # 检查用户是否是白名单成员
    if await is_user_privileged(bot, event.group_id, event.user_id):
        return

    # 检查消息中是否有图片
    images = []
    for segment in event.message:
        if segment.type == "image":
            images.append(segment.data["url"])

    if not images:
        return

    # 处理每张图片
    for image_url in images:
        try:
            # 下载图片
            try:
                image_data = await download_image(image_url)
            except ValueError as e:
                logger.warning(f"图片下载失败，跳过检测 - 群:{group_id}, 用户:{user_id}, 错误:{e}")
                continue
            except Exception as e:
                logger.error(f"图片下载异常，跳过检测 - 群:{group_id}, 用户:{user_id}, 错误:{e}")
                continue

            # 检测NSFW
            try:
                result = await detect_nsfw(image_data)
            except Exception as e:
                logger.error(f"NSFW检测失败，跳过检测 - 群:{group_id}, 用户:{user_id}, 错误:{e}")
                continue

            # 分析结果
            hentai_prob = 0.0
            for prediction in result.get("predictions", []):
                if prediction["className"] == "Hentai":
                    hentai_prob = prediction["probability"]
                    break

            logger.info(
                f"图片NSFW检测结果 - 群:{group_id}, 用户:{user_id}, Hentai概率:{hentai_prob}"
            )

            # 判断是否违规
            threshold = group_config.get("threshold", plugin_config.default_threshold)
            if hentai_prob >= threshold:
                await handle_violation(bot, event, group_config, hentai_prob)
                break  # 只要有一张图片违规就处理

        except Exception as e:
            logger.error(f"处理图片时发生未知错误: {e}")
            continue


async def handle_violation(
    bot: OneBotV11Bot, event: GroupMessageEvent, group_config: Dict, hentai_prob: float
):
    """处理违规行为"""
    group_id = str(event.group_id)
    user_id = str(event.user_id)

    try:
        # 撤回消息
        await bot.delete_msg(message_id=event.message_id)
        logger.info(f"已撤回违规消息 - 群:{group_id}, 用户:{user_id}")
    except Exception as e:
        logger.error(f"撤回消息失败: {e}")

    # 添加警告
    warning_count = add_warning(group_id, user_id)
    warning_limit = group_config.get("warning_limit", plugin_config.default_warning_limit)

    # 禁言用户
    ban_time = group_config.get("ban_time", plugin_config.default_ban_time)
    try:
        await bot.set_group_ban(
            group_id=int(group_id),
            user_id=int(user_id),
            duration=ban_time * 60,  # 转换为秒
        )
        logger.info(
            f"已禁言违规用户 - 群:{group_id}, 用户:{user_id}, 时长:{ban_time}分钟"
        )
    except Exception as e:
        logger.error(f"禁言失败: {e}")

    # 发送警告消息
    at_user = MessageSegment.at(user_id)
    warning_msg = (
        f"{at_user} 您发送的图片包含不当内容！\n"
        f"🚫 违规概率: {hentai_prob:.2%}\n"
        f"⚠️ 当前警告次数: {warning_count}/{warning_limit}\n"
        f"🔇 禁言时间: {ban_time}分钟\n"
    )

    if warning_count >= warning_limit:
        # 达到阈值
        if group_config.get("kick_enabled", plugin_config.default_kick_enabled):
            try:
                await bot.set_group_kick(group_id=int(group_id), user_id=int(user_id))
                warning_msg += "❌ 警告次数已达上限，您已被移出群聊！"
                logger.info(f"已踢出违规用户 - 群:{group_id}, 用户:{user_id}")
            except Exception as e:
                logger.error(f"踢出用户失败: {e}")
                warning_msg += "❌ 警告次数已达上限！"
        else:
            warning_msg += "❌ 警告次数已达上限！请注意您的行为！"
    else:
        remaining = warning_limit - warning_count
        warning_msg += f"💡 还有 {remaining} 次警告机会，请注意您的行为！"

    try:
        await send_with_auto_recall(bot, int(group_id), warning_msg, group_config)
    except Exception as e:
        logger.error(f"发送警告消息失败: {e}")


# 用户命令
check_cmd = on_command("nsfw_check", priority=1, block=True)

# 管理员命令
config_cmd = on_command("nsfw_config", permission=SUPERUSER, priority=1, block=True)
set_cmd = on_command("nsfw_set", permission=SUPERUSER, priority=1, block=True)
status_cmd = on_command("nsfw_status", permission=SUPERUSER, priority=1, block=True)
reset_cmd = on_command("nsfw_reset", permission=SUPERUSER, priority=1, block=True)

# 测试命令（调试用）
test_recall_cmd = on_command("nsfw_test_recall", permission=SUPERUSER, priority=1, block=True)


@check_cmd.handle()
async def handle_check(bot: OneBotV11Bot, event: Event):
    """检测图片的NSFW内容"""
    images = []
    
    # 检查消息中是否有图片
    for segment in event.message:
        if segment.type == "image":
            images.append(segment.data["url"])
    
    # 如果命令消息本身没有图片，检查是否回复了包含图片的消息
    if not images and hasattr(event, 'reply') and event.reply:
        for segment in event.reply.message:
            if segment.type == "image":
                images.append(segment.data["url"])
    
    if not images:
        await smart_finish_with_recall(check_cmd, bot, event, "❌ 请发送图片或回复包含图片的消息来使用此命令！")
    
    # 只检测第一张图片
    image_url = images[0]
    
    try:
        await smart_send_with_recall(bot, event, "🔍 正在检测图片，请稍候...")
        
        # 下载图片
        try:
            image_data = await download_image(image_url)
        except ValueError as e:
            await smart_finish_with_recall(check_cmd, bot, event, f"❌ 图片下载失败: {str(e)}")
        except Exception as e:
            logger.error(f"图片下载异常: {e}")
            await smart_finish_with_recall(check_cmd, bot, event, "❌ 图片下载失败，请稍后重试")
        
        # 检测NSFW
        try:
            result = await detect_nsfw(image_data)
        except Exception as e:
            logger.error(f"NSFW检测异常: {e}")
            await smart_finish_with_recall(check_cmd, bot, event, "❌ 图片检测失败，请稍后重试")
        
        # 构建回复消息
        msg = "📊 NSFW检测结果:\n\n"
        
        # 显示各类别概率
        msg += "🎯 检测结果:\n"
        predictions = result.get("predictions", [])
        for prediction in predictions:
            class_name = prediction["className"]
            probability = prediction["probability"]
            
            # 添加相应的emoji
            emoji_map = {
                "Drawing": "🎨",
                "Hentai": "🔞",
                "Neutral": "😊", 
                "Porn": "🚫",
                "Sexy": "💋"
            }
            emoji = emoji_map.get(class_name, "📋")
            
            msg += f"  {emoji} {class_name}: {probability:.2%}\n"
        
        # 显示处理时间
        processing_time = result.get("processing_time", {})
        if processing_time:
            total_time = processing_time.get("total", "未知")
            api_time = processing_time.get("api", "未知")
            msg += f"\n⏱️ 处理时间:\n"
            msg += f"  总耗时: {total_time}\n"
            msg += f"  API耗时: {api_time}\n"
        
        # 显示模型信息
        model = result.get("model", "未知")
        msg += f"\n🤖 检测模型: {model}"
        
        # 添加风险评级
        hentai_prob = 0.0
        porn_prob = 0.0
        sexy_prob = 0.0
        
        for prediction in predictions:
            if prediction["className"] == "Hentai":
                hentai_prob = prediction["probability"]
            elif prediction["className"] == "Porn":
                porn_prob = prediction["probability"]
            elif prediction["className"] == "Sexy":
                sexy_prob = prediction["probability"]
        
        risk_score = max(hentai_prob, porn_prob) + sexy_prob * 0.5
        
        if risk_score >= 0.8:
            risk_level = "🚨 高风险"
        elif risk_score >= 0.5:
            risk_level = "⚠️ 中风险"
        elif risk_score >= 0.2:
            risk_level = "🟡 低风险"
        else:
            risk_level = "✅ 安全"
            
        msg += f"\n\n📈 综合风险评级: {risk_level}"
        msg += f"\n📏 风险得分: {risk_score:.2%}"
        
        await smart_finish_with_recall(check_cmd, bot, event, msg)
    except MatcherException:
        raise
    except Exception as e:
        logger.error(f"检测图片时发生错误: {e}")
        await smart_finish_with_recall(check_cmd, bot, event, f"❌ 检测失败: {str(e)}")


@config_cmd.handle()
async def handle_config(bot: Bot, event: Event):
    """处理 /nsfw_config 命令"""
    msg = "NSFW插件默认配置：\n"
    msg += f" - 阈值: {plugin_config.default_threshold}\n"
    msg += f" - 禁言时间: {plugin_config.default_ban_time} 分钟\n"
    msg += f" - 警告上限: {plugin_config.default_warning_limit}\n"
    msg += f" - 踢出功能: {'开启' if plugin_config.default_kick_enabled else '关闭'}\n"
    msg += f" - 启用检测: {'是' if plugin_config.default_enabled else '否'}\n"
    msg += f" - 自动撤回: {'开启' if plugin_config.auto_recall_enabled else '关闭'}\n"
    msg += f" - 撤回延迟: {plugin_config.recall_delay} 秒"
    
    await smart_send_with_recall(bot, event, msg)


@set_cmd.handle()
async def handle_set(bot: Bot, event: Event):
    """设置配置"""
    # 获取命令参数，排除命令本身
    message_text = str(event.get_message()).strip()
    if message_text.startswith("/nsfw_set"):
        message_text = message_text[9:].strip()  # 移除 "/nsfw_set"
    args = message_text.split()

    # 检查是否在群聊中
    if hasattr(event, "group_id") and event.group_id:
        current_group_id = str(event.group_id)
    else:
        current_group_id = None

    # 支持两种用法：
    # 1. 在群聊中: /nsfw_set <参数> <值> (修改当前群)
    # 2. 私聊或指定群: /nsfw_set <群号> <参数> <值>
    if len(args) == 2 and current_group_id:
        # 在群聊中，2个参数：参数 值
        group_id = current_group_id
        param = args[0]
        value = args[1]
    elif len(args) == 3:
        # 3个参数：群号 参数 值
        group_id = args[0]
        param = args[1]
        value = args[2]
    else:
        usage_msg = "❌ 用法:\n"
        usage_msg += "• 在群聊中: /nsfw_set <参数> <值>\n"
        usage_msg += "• 指定群聊: /nsfw_set <群号> <参数> <值>\n"
        usage_msg += "参数: threshold, ban_time, warning_limit, kick_enabled, enabled, auto_recall, recall_delay"
        await smart_finish_with_recall(set_cmd, bot, event, usage_msg)

    try:

        # 获取群组配置
        group_config = get_group_config(group_id)

        # 设置参数
        if param == "threshold":
            group_config["threshold"] = float(value)
        elif param == "ban_time":
            group_config["ban_time"] = int(value)
        elif param == "warning_limit":
            group_config["warning_limit"] = int(value)
        elif param == "kick_enabled":
            group_config["kick_enabled"] = value.lower() in ["true", "1", "yes"]
        elif param == "enabled":
            group_config["enabled"] = value.lower() in ["true", "1", "yes"]
        elif param == "auto_recall":
            group_config["auto_recall"] = value.lower() in ["true", "1", "yes"]
        elif param == "recall_delay":
            group_config["recall_delay"] = int(value)
        else:
            await smart_finish_with_recall(set_cmd, bot, event, f"❌ 未知参数: {param}")

        save_data()
        await smart_finish_with_recall(set_cmd, bot, event, f"✅ 已设置群 {group_id} 的 {param} = {value}")

    except MatcherException:
        raise
    except Exception as e:
        await smart_finish_with_recall(set_cmd, bot, event, f"❌ 设置失败: {e}")


@status_cmd.handle()
async def handle_status(bot: Bot, event: Event):
    """查看状态"""
    # 获取命令参数，排除命令本身
    message_text = str(event.get_message()).strip()
    if message_text.startswith("/nsfw_status"):
        message_text = message_text[12:].strip()  # 移除 "/nsfw_status"
    args = message_text.split()

    # 检查是否在群聊中
    if hasattr(event, "group_id") and event.group_id:
        current_group_id = str(event.group_id)
    else:
        current_group_id = None

    # 支持两种用法：
    # 1. 在群聊中: /nsfw_status (查看当前群)
    # 2. 私聊或指定群: /nsfw_status <群号>
    if len(args) == 0 and current_group_id:
        # 在群聊中，无参数：查看当前群
        group_id = current_group_id
    elif len(args) == 1:
        # 1个参数：群号
        group_id = args[0]
    else:
        usage_msg = "❌ 用法:\n"
        usage_msg += "• 在群聊中: /nsfw_status\n"
        usage_msg += "• 指定群聊: /nsfw_status <群号>"
        await smart_finish_with_recall(status_cmd, bot, event, usage_msg)
    group_config = get_group_config(group_id)

    msg = f"📊 群 {group_id} 的NSFW检测状态:\n\n"
    msg += "⚙️ 配置:\n"
    for key, value in group_config.items():
        msg += f"  {key}: {value}\n"

    if group_id in user_warnings:
        msg += "\n⚠️ 用户警告记录:\n"
        for user_id, data in user_warnings[group_id].items():
            msg += f"  {user_id}: {data['count']}次 (最后: {data['last_time'].strftime('%Y-%m-%d %H:%M:%S')})\n"

    await smart_finish_with_recall(status_cmd, bot, event, msg)


@reset_cmd.handle()
async def handle_reset(bot: Bot, event: Event):
    """重置警告"""
    # 解析消息内容和参数
    message = event.get_message()
    message_text = str(message).strip()
    if message_text.startswith("/nsfw_reset"):
        message_text = message_text[11:].strip()  # 移除 "/nsfw_reset"
    args = message_text.split()

    # 检查是否为群聊消息
    if hasattr(event, "group_id") and event.group_id:
        current_group_id = str(event.group_id)
    else:
        current_group_id = None

    # 检查是否有@消息段
    at_user_id = None
    for segment in message:
        if segment.type == "at":
            at_user_id = segment.data["qq"]
            break

    # 解析参数
    group_id = None
    user_id = None

    logger.info(
        f"Reset命令解析 - 参数数量:{len(args)}, 参数:{args}, 当前群:{current_group_id}, @用户:{at_user_id}"
    )

    if len(args) == 0:
        # 没有参数，默认当前群，重置所有用户
        if not current_group_id:
            await smart_finish_with_recall(reset_cmd, bot, event, "❌ 请在群聊中使用此命令，或指定群号")
        group_id = current_group_id
        user_id = None

    elif len(args) == 1:
        # 一个参数的情况
        arg = args[0]
        if not arg.isdigit():
            # 不是纯数字，无效参数
            await smart_finish_with_recall(reset_cmd, bot, event, "❌ 参数必须是数字（群号或用户QQ）")
        elif current_group_id:
            # 在群聊中，优先判断为用户QQ（通常QQ号比群号长）
            if len(arg) >= 8:  # QQ号通常8位以上
                group_id = current_group_id
                user_id = arg
            else:
                # 短数字，可能是群号（但在群聊中不太可能）
                group_id = arg
                user_id = None
        else:
            # 不在群聊中，视为群号
            group_id = arg
            user_id = None

    elif len(args) == 2:
        # 两个参数：群号 用户QQ
        group_id = args[0]
        user_id = args[1]

    else:
        await smart_finish_with_recall(reset_cmd, bot, event, 
            "❌ 参数过多！用法:\n• /nsfw_reset - 重置当前群所有记录\n• /nsfw_reset 用户QQ - 重置当前群指定用户\n• /nsfw_reset 群号 - 重置指定群所有记录\n• /nsfw_reset 群号 用户QQ - 重置指定群指定用户\n• /nsfw_reset @用户 - 重置当前群@的用户"
        )

    # 如果有@用户，优先使用@的用户ID
    if at_user_id:
        if not current_group_id:
            await smart_finish_with_recall(reset_cmd, bot, event, "❌ @用户功能只能在群聊中使用")
        group_id = current_group_id
        user_id = at_user_id

    # 验证群号格式
    if not group_id or not group_id.isdigit():
        await smart_finish_with_recall(reset_cmd, bot, event, "❌ 群号必须是数字")

    # 验证用户QQ格式
    if user_id is not None and not str(user_id).isdigit():
        await smart_finish_with_recall(reset_cmd, bot, event, "❌ 用户QQ必须是数字")

    logger.info(f"Reset命令执行 - 群:{group_id}, 用户:{user_id}")

    try:
        # 执行重置操作
        reset_warnings(group_id, user_id)

        # 返回成功消息
        if user_id:
            await smart_finish_with_recall(reset_cmd, bot, event,
                f"✅ 已重置群 {group_id} 中用户 {user_id} 的警告记录"
            )
        else:
            await smart_finish_with_recall(reset_cmd, bot, event, f"✅ 已重置群 {group_id} 的所有警告记录")

    except MatcherException:
        raise
    except Exception as e:
        logger.error(f"重置警告记录失败: {e}")
        await smart_finish_with_recall(reset_cmd, bot, event, f"❌ 重置失败: {str(e)}")


@test_recall_cmd.handle()
async def handle_test_recall(bot: OneBotV11Bot, event: Event):
    """测试自动撤回功能"""
    if not hasattr(event, 'group_id') or not event.group_id:
        await smart_finish_with_recall(test_recall_cmd, bot, event, "❌ 此命令只能在群聊中使用")
    
    group_id = int(event.group_id)
    group_config = get_group_config(str(group_id))
    
    try:
        test_message = f"🧪 这是一条测试消息，将在 {group_config.get('recall_delay', 5)} 秒后自动撤回"
        await send_with_auto_recall(bot, group_id, test_message, group_config)
        logger.info(f"已发送测试撤回消息 - 群:{group_id}")
    except Exception as e:
        logger.error(f"测试撤回功能失败: {e}")
        await smart_finish_with_recall(test_recall_cmd, bot, event, f"❌ 测试失败: {e}")
