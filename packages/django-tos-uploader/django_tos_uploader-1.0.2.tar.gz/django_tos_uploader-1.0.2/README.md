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
VOLCENGINE_STS_ROLE_NAME = 'your-sts-role-name'
```

### 3. 实现 STS Token 视图

```python
# views.py
from django.conf import settings
from volcengine.sts.StsService import StsService

from rest_framework import serializers


class StsTokenSerializer(serializers.Serializer):
    access_key = serializers.CharField(help_text="临时访问密钥ID")
    secret_key = serializers.CharField(help_text="临时访问密钥")
    security_token = serializers.CharField(help_text="安全令牌")
    expiration = serializers.DateTimeField(help_text="凭证过期时间")
    endpoint = serializers.CharField(help_text="Endpoint")
    bucket = serializers.CharField(help_text="Bucket")
    region = serializers.CharField(help_text="Region")

class GetStsTokenAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["服务"],
        summary="获取火山引擎STS临时访问凭证",
        responses={
            status.HTTP_200_OK: StsTokenSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiTypes.OBJECT,
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            # 初始化 STS 服务
            sts_service = StsService()
            sts_service.set_ak(settings.VOLCENGINE_ACCESS_KEY)
            sts_service.set_sk(settings.VOLCENGINE_SECRET_KEY)

            # 获取 STS 临时凭证
            params = {
                "DurationSeconds": 3600,  # 1小时有效期
                "RoleTrn": f"trn:iam::{settings.VOLCENGINE_ACCOUNT_ID}:role/{settings.VOLCENGINE_STS_ROLE_NAME}",
                "RoleSessionName": f"renlib_user_{request.user.id}",
            }
            resp = sts_service.assume_role(params)
            credentials = resp["Result"]["Credentials"]

            data = {
                "access_key": credentials["AccessKeyId"],
                "secret_key": credentials["SecretAccessKey"],
                "security_token": credentials["SessionToken"],
                "expiration": credentials["ExpiredTime"],
                "endpoint": settings.VOLCENGINE_ENDPOINT,
                "bucket": settings.VOLCENGINE_BUCKET,
                "region": settings.VOLCENGINE_REGION,
            }
            serializer = StsTokenSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
