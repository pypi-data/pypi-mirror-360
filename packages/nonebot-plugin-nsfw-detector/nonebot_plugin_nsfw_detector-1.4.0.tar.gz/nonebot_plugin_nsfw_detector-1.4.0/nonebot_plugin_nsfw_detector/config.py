from pydantic import Field, BaseModel


class PluginConfig(BaseModel):
    """NSFW检测器配置"""
    
    # API配置
    api_url: str = "https://nsfwpy.cn/analyze" # API地址
    model: str = "mobilenet_v2" # 检测模型
    request_timeout: int = 30 # 请求超时时间
    
    # 默认群组配置
    default_enabled: bool = True # 是否启用检测
    default_threshold: float = 0.7 # 默认阈值
    default_ban_time: int = 60 # 禁言时间(分钟)
    default_warning_limit: int = 3 # 警告次数上限
    default_kick_enabled: bool = True # 是否踢出群聊
    
    # 消息撤回配置
    auto_recall_enabled: bool = True # 是否自动撤回插件消息
    recall_delay: int = 15  # 撤回延迟时间(秒)
    
    # 调试配置
    debug_mode: bool = False  # 是否启用调试模式
    
    # 数据存储配置
    data_dir: str = "data/nsfw_detector" # 数据存储目录


class Config(BaseModel):
    nsfw_detector: PluginConfig = Field(default_factory=PluginConfig) 