"""
ScholarAI - 用户设置数据模型

定义用户设置数据结构和相关操作。
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import uuid
import base64
import json
from cryptography.fernet import Fernet
import os


class Theme(str, Enum):
    """主题枚举"""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class Language(str, Enum):
    """语言枚举"""
    ZH_CN = "zh-CN"
    EN_US = "en-US"


class ApiConfig:
    """API配置"""
    def __init__(
        self,
        provider: str = "zhipu",
        api_key: Optional[str] = None,
        model: str = "glm-4-flash",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def to_dict(self, include_key: bool = False) -> Dict[str, Any]:
        """转换为字典"""
        data = {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        if include_key and self.api_key:
            # 只返回部分密钥用于显示
            data["api_key_preview"] = self.api_key[:8] + "..." if len(self.api_key) > 8 else "***"
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ApiConfig':
        """从字典创建实例"""
        return ApiConfig(
            provider=data.get("provider", "zhipu"),
            api_key=data.get("api_key"),
            model=data.get("model", "glm-4-flash"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 2000)
        )


class UserSettings:
    """
    用户设置数据模型

    属性:
        user_id: 用户唯一标识符
        theme: 主题设置
        language: 语言设置
        api_config: AI API配置
        notification_enabled: 是否启用通知
        email_subscription: 是否订阅邮件
        created_at: 创建时间
        updated_at: 更新时间
    """

    # 加密密钥（在生产环境中应该从环境变量获取）
    _encryption_key = None
    _cipher = None

    @classmethod
    def _get_cipher(cls) -> Fernet:
        """获取加密器"""
        if cls._cipher is None:
            # 从环境变量获取密钥，如果没有则使用默认密钥（仅用于开发）
            key = os.environ.get("ENCRYPTION_KEY")
            if not key:
                # 生成一个默认密钥（仅用于开发环境）
                key = Fernet.generate_key()
                print("⚠️  Warning: Using auto-generated encryption key. Set ENCRYPTION_KEY in production!")
            else:
                # 确保密钥是32字节的base64编码格式
                if isinstance(key, str):
                    key = key.encode()
                if len(key) != 44:  # Fernet需要32字节，base64编码后44字符
                    # 如果密钥长度不对，使用PBKDF2派生
                    from hashlib import sha256
                    key = base64.urlsafe_b64encode(sha256(key).digest())
            cls._cipher = Fernet(key)
        return cls._cipher

    @classmethod
    def encrypt_api_key(cls, api_key: str) -> str:
        """加密API密钥"""
        if not api_key:
            return ""
        cipher = cls._get_cipher()
        encrypted = cipher.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    @classmethod
    def decrypt_api_key(cls, encrypted_key: str) -> str:
        """解密API密钥"""
        if not encrypted_key:
            return ""
        try:
            cipher = cls._get_cipher()
            encrypted = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            print(f"Error decrypting API key: {e}")
            return ""

    def __init__(
        self,
        user_id: str,
        theme: str = Theme.SYSTEM,
        language: str = Language.ZH_CN,
        api_config: Optional[ApiConfig] = None,
        notification_enabled: bool = True,
        email_subscription: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        初始化用户设置实例

        参数:
            user_id: 用户ID
            theme: 主题设置（默认为system）
            language: 语言设置（默认为zh-CN）
            api_config: API配置（可选）
            notification_enabled: 是否启用通知（默认为True）
            email_subscription: 是否订阅邮件（默认为False）
            created_at: 创建时间（可选）
            updated_at: 更新时间（可选）
        """
        self.user_id = user_id
        self.theme = theme
        self.language = language
        self.api_config = api_config or ApiConfig()
        self.notification_enabled = notification_enabled
        self.email_subscription = email_subscription
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update_theme(self, theme: str) -> None:
        """
        更新主题设置

        参数:
            theme: 主题（light, dark, system）
        """
        if theme in [Theme.LIGHT, Theme.DARK, Theme.SYSTEM]:
            self.theme = theme
            self.updated_at = datetime.utcnow()

    def update_language(self, language: str) -> None:
        """
        更新语言设置

        参数:
            language: 语言（zh-CN, en-US）
        """
        if language in [Language.ZH_CN, Language.EN_US]:
            self.language = language
            self.updated_at = datetime.utcnow()

    def update_api_config(self, api_config: ApiConfig) -> None:
        """
        更新API配置

        参数:
            api_config: API配置对象
        """
        self.api_config = api_config
        self.updated_at = datetime.utcnow()

    def to_dict(self, include_api_key: bool = False) -> Dict[str, Any]:
        """
        转换为字典格式

        参数:
            include_api_key: 是否包含API密钥（仅用于返回给前端，不存储）

        返回:
            Dict: 设置信息字典
        """
        return {
            "user_id": self.user_id,
            "theme": self.theme,
            "language": self.language,
            "api_config": self.api_config.to_dict(include_key=include_api_key),
            "notification_enabled": self.notification_enabled,
            "email_subscription": self.email_subscription,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def to_db_dict(self) -> Dict[str, Any]:
        """
        转换为数据库存储格式（加密敏感信息）

        返回:
            Dict: 适合存储在数据库的字典
        """
        data = self.to_dict()
        # 加密API密钥
        if self.api_config.api_key:
            data["api_config"]["encrypted_api_key"] = self.encrypt_api_key(self.api_config.api_key)
            # 删除明文密钥
            if "api_key" in data["api_config"]:
                del data["api_config"]["api_key"]
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UserSettings':
        """
        从字典创建用户设置实例

        参数:
            data: 设置数据字典

        返回:
            UserSettings: 用户设置实例
        """
        api_config_data = data.get("api_config", {})

        # 处理加密的API密钥
        if "encrypted_api_key" in api_config_data:
            decrypted_key = UserSettings.decrypt_api_key(api_config_data["encrypted_api_key"])
            api_config_data["api_key"] = decrypted_key
            # 删除加密字段
            del api_config_data["encrypted_api_key"]

        api_config = ApiConfig.from_dict(api_config_data) if api_config_data else ApiConfig()

        return UserSettings(
            user_id=data["user_id"],
            theme=data.get("theme", Theme.SYSTEM),
            language=data.get("language", Language.ZH_CN),
            api_config=api_config,
            notification_enabled=data.get("notification_enabled", True),
            email_subscription=data.get("email_subscription", False),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<UserSettings user_id={self.user_id} theme={self.theme} language={self.language}>"
