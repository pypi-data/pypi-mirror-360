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
    文档文件类型
    """
    PDF = "pdf"
    OFD = "ofd"
    XML = "xml"
    DOCTYPE = "doctype"
    TABLE = "table"
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    ARCHIVE = "archive"

class DocFileObject(BaseModel):
    """
    文档文件对象
    """
    file_name: str
    tags: Optional[Dict[str, str]] = None
