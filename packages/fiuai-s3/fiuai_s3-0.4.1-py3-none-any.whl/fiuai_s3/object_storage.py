# -- coding: utf-8 --
# Project: fiuai-s3
# Created Date: 2025-05-01
# Author: liming
# Email: lmlala@aliyun.com
# Copyright (c) 2025 FiuAI

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import logging
from uuid import uuid4
from .type import DocFileObject, DocSourceFrom, DocFileType

logger = logging.getLogger(__name__)

class StorageConfig(BaseModel):
    """存储配置类"""
    provider: str = Field(..., description="存储提供商，支持 alicloud 或 minio")
    bucket_name: str = Field(..., description="存储桶名称")
    endpoint: str = Field(..., description="存储服务端点")
    access_key: str = Field(..., description="访问密钥")
    secret_key: str = Field(..., description="密钥")
    temp_dir: str = Field("temp/", description="临时目录")
    use_https: bool = Field(False, description="是否使用HTTPS")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class ObjectStorage(ABC):
    """对象存储抽象基类
    
    支持业务身份（auth_tenant_id, auth_company_id, doc_id）在实例初始化时注入（可为空），
    各操作方法参数可选，若不传则使用实例属性，若传则覆盖。
    """
    
    def __init__(self, config: StorageConfig, auth_tenant_id: Optional[str] = None, auth_company_id: Optional[str] = None, doc_id: Optional[str] = None):
        """
        Args:
            config: 存储配置对象
            auth_tenant_id: 业务租户ID（可为空，后续操作可覆盖）
            auth_company_id: 业务公司ID（可为空，后续操作可覆盖）
            doc_id: 单据ID（可为空，后续操作可覆盖）
        """
        self.config = config
        self._id = str(uuid4())
        self.auth_tenant_id = auth_tenant_id
        self.auth_company_id = auth_company_id
        self.doc_id = doc_id
    
    @abstractmethod
    def upload_temp_file(self, object_key: str, data: bytes, tmppath: str = None) -> bool:
        """上传临时文件
        
        Args:
            object_key: 对象存储中的key
            tmppath: 临时文件路径, 如果为空，则使用默认临时目录
        """
        pass

    @abstractmethod
    def download_temp_file(self, object_key: str, tmppath: str = None) -> bool:
        """下载临时文件
        
        Args:
            object_key: 对象存储中的key
            tmppath: 临时文件路径, 如果为空，则使用默认临时目录
        """
        pass

    @abstractmethod
    def upload_file(self, object_key: str, data: bytes) -> bool:
        """上传文件到对象存储
        
        Args:
            object_key: 对象存储中的key
            data: 文件数据
            
        Returns:
            bool: 是否上传成功
        """
        pass
    
    @abstractmethod
    def download_file(self, object_key: str) -> bytes:
        """从对象存储下载文件
        
        Args:
            object_key: 对象存储中的key
            
        Returns:
            bytes: 文件数据
        """
        pass
    
    @abstractmethod
    def delete_file(self, object_key: str) -> bool:
        """删除对象存储中的文件
        
        Args:
            object_key: 对象存储中的key
            
        Returns:
            bool: 是否删除成功
        """
        pass
    
    @abstractmethod
    def list_files(self, prefix: Optional[str] = None) -> List[str]:
        """列出对象存储中的文件
        
        Args:
            prefix: 文件前缀过滤
            
        Returns:
            List[str]: 文件key列表
        """
        pass

    @abstractmethod
    def upload_doc_file(self, 
                        filename: str, 
                        data: bytes, 
                        tags: Optional[Dict[str, str]] = None,
                        auth_tenant_id: Optional[str] = None, auth_company_id: Optional[str] = None, doc_id: Optional[str] = None) -> bool:
        """
        上传单据文件，自动拼接存储路径并打tag
        Args:
            filename: 文件名
            data: 文件内容
            tags: 标签字典
            auth_tenant_id: 租户ID（可选，若不传则用实例属性）
            auth_company_id: 公司ID（可选，若不传则用实例属性）
            doc_id: 单据ID（可选，若不传则用实例属性）
        Returns:
            bool: 是否上传成功
        """
        pass

    @abstractmethod
    def download_doc_file(self, filename: str, auth_tenant_id: Optional[str] = None, auth_company_id: Optional[str] = None, doc_id: Optional[str] = None) -> bytes:
        """
        下载单据文件，自动拼接存储路径
        Args:
            filename: 文件名
            auth_tenant_id: 租户ID（可选，若不传则用实例属性）
            auth_company_id: 公司ID（可选，若不传则用实例属性）
            doc_id: 单据ID（可选，若不传则用实例属性）
        Returns:
            bytes: 文件内容
        """
        pass

    @abstractmethod
    def list_doc_files(self, auth_tenant_id: Optional[str] = None, auth_company_id: Optional[str] = None, doc_id: Optional[str] = None) -> List[DocFileObject]:
        """
        列出单据下所有文件
        Args:
            auth_tenant_id: 租户ID（可选，若不传则用实例属性）
            auth_company_id: 公司ID（可选，若不传则用实例属性）
            doc_id: 单据ID（可选，若不传则用实例属性）
        Returns:
            List[str]: 文件名列表
        """
        pass

class ObjectStorageFactory:
    """对象存储工厂类"""
    
    _instance: Optional[ObjectStorage] = None
    _config: Optional[StorageConfig] = None
    
    @classmethod
    def initialize(cls, 
                  provider: str = "minio",
                  bucket_name: str = "dev",
                  endpoint: str = "http://127.0.0.1:19000",
                  access_key: str = "devdevdev",
                  secret_key: str = "devdevdev",
                  temp_dir: str = "temp/",
                  use_https: bool = False) -> None:
        """初始化对象存储配置
        
        Args:
            provider: 存储提供商，支持 alicloud 或 minio
            bucket_name: 存储桶名称
            endpoint: 存储服务端点
            access_key: 访问密钥
            secret_key: 密钥
            temp_dir: 临时目录
            use_https: 是否使用HTTPS
        """
        cls._config = StorageConfig(
            provider=provider,
            bucket_name=bucket_name,
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            temp_dir=temp_dir.rstrip("/").lstrip("/"),
            use_https=use_https
        )
        cls._instance = None
    
    @classmethod
    def get_instance(cls) -> ObjectStorage:
        """获取对象存储单例实例
        
        Returns:
            ObjectStorage: 对象存储实例
            
        Raises:
            ValueError: 未初始化配置或不支持的存储提供商
        """
        if cls._config is None:
            raise ValueError("请先调用 initialize() 方法初始化配置")
            
        if cls._instance is None:
            provider = cls._config.provider.lower()
            
            if provider == "alicloud":
                from .alicloud.alicloud_storage import AliCloudStorage
                cls._instance = AliCloudStorage(cls._config)
                logger.info(f"已初始化阿里云对象存储实例")
            elif provider == "minio":
                from .minio.minio_storage import MinioStorage
                cls._instance = MinioStorage(cls._config)
                logger.info(f"已初始化MinIO对象存储实例")
            else:
                raise ValueError(f"不支持的存储提供商: {provider}")
                
        return cls._instance
    
    @classmethod
    def create_storage(cls, config: StorageConfig, auth_tenant_id: Optional[str] = None, auth_company_id: Optional[str] = None, doc_id: Optional[str] = None) -> ObjectStorage:
        """创建新的对象存储实例
        
        Args:
            config: 存储配置对象
            auth_tenant_id: 业务租户ID（可为空，后续操作可覆盖）
            auth_company_id: 业务公司ID（可为空，后续操作可覆盖）
            doc_id: 单据ID（可为空，后续操作可覆盖）
        Returns:
            ObjectStorage: 对象存储实例
        Raises:
            ValueError: 不支持的存储提供商
        """
        provider = config.provider.lower()
        
        if provider == "alicloud":
            from .alicloud.alicloud_storage import AliCloudStorage
            return AliCloudStorage(config, auth_tenant_id, auth_company_id, doc_id)
        elif provider == "minio":
            from .minio.minio_storage import MinioStorage
            return MinioStorage(config, auth_tenant_id, auth_company_id, doc_id)
        else:
            raise ValueError(f"不支持的存储提供商: {provider}")

# 导出工厂类
__all__ = ['ObjectStorage', 'ObjectStorageFactory', 'StorageConfig']




