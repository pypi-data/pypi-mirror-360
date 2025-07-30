# -- coding: utf-8 --
# Project: fiuai-s3
# Created Date: 2025-05-01
# Author: liming
# Email: lmlala@aliyun.com
# Copyright (c) 2025 FiuAI

from .object_storage import ObjectStorage, ObjectStorageFactory, StorageConfig
from .type import DocFileObject, DocSourceFrom, DocFileType

__version__ = "0.3.9"
__all__ = ["ObjectStorage", "ObjectStorageFactory", "StorageConfig", "DocFileObject", "DocSourceFrom", "DocFileType"] 