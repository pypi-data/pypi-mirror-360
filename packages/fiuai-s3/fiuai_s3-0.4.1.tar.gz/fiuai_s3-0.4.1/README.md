# FiuAI S3

一个支持阿里云OSS和MinIO的对象存储抽象包，提供了统一的接口来操作不同的对象存储服务。

## 特性

- 支持阿里云OSS和MinIO存储服务
- 统一的接口设计
- 工厂模式实现，易于扩展
- 完整的类型提示
- 详细的日志记录
- 异常处理机制

## 安装

```bash
pip install fiuai-s3
```

## 快速开始

### 初始化存储

```python
# file: utils/s3.py
from fiuai_s3 import ObjectStorageFactory
from config.app_config import get_settings

ObjectStorageFactory.initialize(
        # 初始化对象存储
        provider=get_settings().object_storage_config.provider,
        bucket_name=get_settings().object_storage_config.bucket_name,
        endpoint=get_settings().object_storage_config.endpoint,
        access_key=get_settings().object_storage_config.access_key,
        secret_key=get_settings().object_storage_config.secret_key,
        temp_dir=get_settings().object_storage_config.s3_temp_dir,
        use_https=get_settings().object_storage_config.s3_use_https
    
)
S3_Client = ObjectStorageFactory.get_instance()

```


### 使用存储实例

```python
# file: app.py
from utils.s3 import S3_Client

# 上传文件
S3_Client.upload_file("test.txt", b"Hello World")

# 下载文件
data = S3_Client.download_file("test.txt")

# 删除文件
S3_Client.delete_file("test.txt")

# 列出文件
files = S3_Client.list_files(prefix="test/")
```

### 单据文件管理（推荐业务用法）

支持业务身份（auth_tenant_id, auth_company_id, doc_id）在实例初始化时注入（可为空），各操作方法参数可选，若不传则使用实例属性，若传则覆盖。

#### 初始化带业务身份
```python
from fiuai_s3 import ObjectStorageFactory
from fiuai_s3.object_storage import StorageConfig

config = StorageConfig(
    provider="minio",
    bucket_name="dev",
    endpoint="http://127.0.0.1:19000",
    access_key="devdevdev",
    secret_key="devdevdev"
)
# 业务身份可选
S3_Client = ObjectStorageFactory.create_storage(
    config,
    auth_tenant_id="t1",
    auth_company_id="c1",
    doc_id="d1"
)
```

#### 上传单据文件
```python
# 方法参数可选，优先级高于实例属性
S3_Client.upload_doc_file(
    filename="发票.pdf",
    data=b"...文件内容...",
    tags={"业务类型": "发票", "年份": "2024"}
    # auth_tenant_id、auth_company_id、doc_id 可不传，使用实例属性
)
```

为了规范文件, 文档类型的文件上传请按规范进行打标  
```python
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
    ARCHIVE = "archive"
    OTHER = "other"
```
```python
class DocSourceFrom(Enum):
    """
    文档来源, 避免某些场景同类文件混淆,比如有2个xml文件,一个用户上传,一个ai生成
    """
    USER = "user"
    AI = "ai"
    INTEGRATION = "integration"
    ETAX = "etax"
    BANK = "bank"
    OTHER = "other"
```

上传时标注  
```python
c = ObjectStorageFactory.get_instance()
    c.upload_doc_file(
        filename="test.txt",
        data=b"test",
        doc_source_from=DocSourceFrom.USER,
        doc_file_type=DocFileType.XML,
        tags={"name": "hilton", "age": "10"},
        auth_tenant_id="t1",
        auth_company_id="c1",
        doc_id="id111",
    )

```

#### 下载单据文件
```python
data = S3_Client.download_doc_file(
    filename="发票.pdf"
    # auth_tenant_id、auth_company_id、doc_id 可不传，使用实例属性
)
```

#### 列出单据下所有文件
```python
files = S3_Client.list_doc_files()
```

- 存储路径自动为：`bucketname/auth_tenant_id/auth_company_id/doc_id/filename`
- tags会自动打到对象存储（Alicloud用OSS Tagging，Minio用metadata）
- 支持实例初始化时设置默认auth_tenant_id、auth_company_id、doc_id，调用时可覆盖
- 缺失必要参数会抛出异常

## 配置参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| provider | str | 是 | - | 存储提供商，支持 "alicloud" 或 "minio" |
| bucket_name | str | 是 | - | 存储桶名称 |
| endpoint | str | 是 | - | 存储服务端点 |
| access_key | str | 是 | - | 访问密钥 |
| secret_key | str | 是 | - | 密钥 |
| temp_dir | str | 否 | "temp/" | 临时目录 |
| use_https | bool | 否 | False | 是否使用HTTPS |

## 开发

### 安装开发依赖

```bash
uv pip install .
```

### 运行测试

```bash
python -m pytest tests/
```

## 许可证

MIT License

## 作者

- liming (lmlala@aliyun.com)

## 贡献

欢迎提交 Issue 和 Pull Request！


# 发布
uv publish --username __token__ --password your-pypi-token-here