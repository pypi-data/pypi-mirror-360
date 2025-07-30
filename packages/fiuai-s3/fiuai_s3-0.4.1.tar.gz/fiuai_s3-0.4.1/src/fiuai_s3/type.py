        # -- coding: utf-8 --
# Project: fiuai-s3
# Created Date: 1700-01-01
# Author: liming
# Email: lmlala@aliyun.com
# Copyright (c) 2025 FiuAI

from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict

class DocFileType(Enum):
    """
    文档文件类型, 避免某些场景不规范的文件名
    """
    PDF = "pdf"
    OFD = "ofd"
    XML = "xml"
    DOCTYPE = "doctype"
    TABLE = "table"
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    ARCHIVE = "archive"
    OTHER = "other"

class DocSourceFrom(Enum):
    """
    文档来源, 避免某些场景同类文件混淆,比如有2个xml文件,一个用户上传,一个ai生成
    """
    USER = "user"
    AI = "ai"
    IDP = "idp"
    INTEGRATION = "integration"
    ETAX = "etax"
    BANK = "bank"
    OTHER = "other"

class DocFileObject(BaseModel):
    """
    文档文件对象
    """
    file_name: str
    tags: Optional[Dict[str, str]] = None
