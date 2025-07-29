from django.db import models
from django import forms
from django.core import validators
from .widgets import TOSUploadWidget
import re


class TOSFileField(models.TextField):
    def __init__(
        self,
        file_types=None,
        upload_path=None,
        readonly=False,
        get_sts_token_url=None,
        *args,
        **kwargs
    ):
        self.file_types = file_types or []  # 允许的文件类型列表
        self.upload_path = upload_path or "user-uploads"  # 自定义上传路径
        self.readonly = readonly  # 只读模式
        self.get_sts_token_url = get_sts_token_url  # 自定义STS token获取URL
        kwargs.setdefault("max_length", 2000)  # TOS URL can be long
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_form_class():
        return TOSFileFormField

    def formfield(self, **kwargs):
        defaults = {
            "form_class": TOSFileFormField,
            "widget": TOSUploadWidget(
                file_types=self.file_types,
                upload_path=self.upload_path,
                readonly=self.readonly,
                get_sts_token_url=self.get_sts_token_url,
            ),
            "file_types": self.file_types,
            "upload_path": self.upload_path,
            "readonly": self.readonly,
            "get_sts_token_url": self.get_sts_token_url,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.file_types:
            kwargs["file_types"] = self.file_types
        if self.upload_path != "user-uploads":
            kwargs["upload_path"] = self.upload_path
        if self.readonly:
            kwargs["readonly"] = self.readonly
        if self.get_sts_token_url:
            kwargs["get_sts_token_url"] = self.get_sts_token_url
        return name, path, args, kwargs


class TOSURLValidator(validators.URLValidator):
    """自定义URL验证器，支持中文字符"""

    def __call__(self, value):
        # 如果URL包含中文字符，先进行URL编码
        try:
            # 简单检查是否是有效的URL格式
            if value and (value.startswith("http://") or value.startswith("https://")):
                return value
            else:
                raise validators.ValidationError(
                    self.message,
                    code=self.code,
                    params={"value": value},
                )
        except Exception:
            # 如果有任何问题，使用父类的验证
            super().__call__(value)


class TOSFileFormField(forms.CharField):
    def __init__(
        self,
        file_types=None,
        upload_path=None,
        readonly=False,
        get_sts_token_url=None,
        **kwargs
    ):
        self.file_types = file_types or []
        self.upload_path = upload_path or "user-uploads"
        self.readonly = readonly
        self.get_sts_token_url = get_sts_token_url

        # 如果是只读模式，不需要验证器
        if not readonly:
            kwargs.setdefault("validators", [TOSURLValidator()])

        kwargs.update(
            {
                "widget": TOSUploadWidget(
                    file_types=self.file_types,
                    upload_path=self.upload_path,
                    readonly=self.readonly,
                    get_sts_token_url=self.get_sts_token_url,
                )
            }
        )
        super().__init__(**kwargs)

    def clean(self, value):
        # 如果是只读模式，跳过验证
        if self.readonly:
            return value

        value = super().clean(value)
        if value:
            # 基本的URL格式检查
            if not (value.startswith("http://") or value.startswith("https://")):
                raise forms.ValidationError("请输入有效的URL")
        return value
