from django import forms
from django.utils.safestring import mark_safe


class TOSUploadWidget(forms.Widget):
    template_name = "tos_uploader/widget.html"

    def __init__(
        self,
        file_types=None,
        upload_path=None,
        readonly=False,
        get_sts_token_url=None,
        attrs=None,
    ):
        super().__init__(attrs)
        self.file_types = file_types or []
        self.upload_path = upload_path or "user-uploads"
        self.readonly = readonly
        self.get_sts_token_url = (
            get_sts_token_url or "/get-sts-token/"
        )  # 默认URL，用户可自定义

        # 生成accept属性
        if self.file_types:
            accept_map = {
                "image": "image/*",
                "video": "video/*",
                "audio": "audio/*",
                "pdf": ".pdf",
                "doc": ".doc,.docx",
                "txt": ".txt",
            }
            accepts = [accept_map.get(ft, f".{ft}") for ft in self.file_types]
            self.accept = ",".join(accepts)
        else:
            self.accept = None

    def render(self, name, value, attrs=None, renderer=None):
        # 确保value不为None
        if value is None:
            value = ""

        context = {
            "widget": {
                "name": name,
                "value": value,
                "attrs": attrs or {},
                "accept": self.accept,
                "upload_path": self.upload_path,
                "readonly": self.readonly,
            },
            "get_sts_token_url": self.get_sts_token_url,
        }

        return mark_safe(self.render_template(context))

    def render_template(self, context):
        from django.template.loader import render_to_string

        return render_to_string(self.template_name, context)

    class Media:
        css = {"all": ("tos_uploader/css/uploader.css",)}
        js = (
            "https://unpkg.com/axios/dist/axios.min.js",
            "https://tos-public.volccdn.com/obj/volc-tos-public/@volcengine/tos-sdk@latest/browser/tos.umd.production.min.js",
            "tos_uploader/js/uploader.js",
        )
