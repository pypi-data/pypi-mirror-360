# Django TOS Uploader

一个用于 Django 的火山引擎 TOS（Tinder Object Storage）文件上传组件。

## 功能特性

- 🚀 支持大文件分片上传
- 🔒 使用 STS 临时凭证，安全可靠
- 🎨 现代化 UI 设计，支持响应式布局
- 📱 支持拖拽上传和点击选择
- 🔍 实时预览（图片、视频等）
- 📊 上传进度显示
- 🛡️ 支持只读模式
- 🎯 动态上传路径配置
- ⚡ 懒加载预览，节省资源

## 安装

```bash
pip install django-tos-uploader
```

## 快速开始

### 依赖

```bash
pip install volcengine
```

### 1. 添加到 INSTALLED_APPS

```python
INSTALLED_APPS = [
    # ... 其他应用
    'tos_uploader',
]
```

### 2. 配置设置

```python
# settings.py

# 火山引擎配置
VOLCENGINE_ACCESS_KEY = 'your-access-key'
VOLCENGINE_SECRET_KEY = 'your-secret-key'
VOLCENGINE_REGION = 'cn-beijing'  # 或其他区域
VOLCENGINE_ENDPOINT = 'tos-cn-beijing.volces.com'
VOLCENGINE_BUCKET = 'your-bucket-name'
VOLCENGINE_ACCOUNT_ID = 'your-account-id'
VOLCENGINE_ROLE_NAME = 'your-role-name'
```

### 3. 实现 STS Token 视图

```python
# views.py
from django.conf import settings
from django.http import JsonResponse
from volcengine.sts.StsService import StsService

def get_sts_token(request):
    try:
        # 初始化 STS 服务
        sts_service = StsService()
        sts_service.set_ak(settings.VOLCENGINE_ACCESS_KEY)
        sts_service.set_sk(settings.VOLCENGINE_SECRET_KEY)

        # 获取 STS 临时凭证
        params = {
            "DurationSeconds": 3600,  # 1小时有效期
            "RoleTrn": f"trn:iam::{settings.VOLCENGINE_ACCOUNT_ID}:role/{settings.VOLCENGINE_ROLE_NAME}",
            "RoleSessionName": "django-tos-uploader",
        }
        resp = sts_service.assume_role(params)
        credentials = resp["Result"]["Credentials"]

        return JsonResponse(
            {
                "AccessKeyId": credentials["AccessKeyId"],
                "SecretAccessKey": credentials["SecretAccessKey"],
                "SessionToken": credentials["SessionToken"],
                "ExpiredTime": credentials["ExpiredTime"],
                "Endpoint": settings.VOLCENGINE_ENDPOINT,
                "Bucket": settings.VOLCENGINE_BUCKET,
                "region": settings.VOLCENGINE_REGION,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

```

### 4. 配置 URL 路由

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('get-sts-token/', views.get_sts_token, name='get_sts_token'),
    # ... 其他URL
]

```

### 5. 在模型中使用

```python
from tos_uploader.fields import TOSFileField
from django.db import models

class MyModel(models.Model):
    # 其他字段...
    tos_file = TOSFileField(
        upload_path="my-uploads/",
        get_sts_token_url=reverse_lazy('get_sts_token'),  # 替换为你的视图名
        file_types=["image/*", "video/*"],  # 可选，文件类型限制
        readonly=False,  # 可选，是否只读
    )
```
