# dj_vditor

**Django-vditor** 是基于 [vditor v3.8.0](https://github.com/Vanessa219/vditor) 的一个 [django](djangoproject.com) Markdown 文本编辑插件应用。

**Django-mdeditor** 的灵感参考自伟大的项目 [django-ckeditor](https://github.com/django-ckeditor/django-ckeditor).

## Installation

```bash
### 默认安装只需Django
pip install dj-vditor-widget

### 安装oss上传插件
pip install dj-vditor-widget[oss]

### 安装tos上传插件
pip install dj-vditor-widget[tos]

### 安装所有插件
pip install dj-vditor-widget[all]

```

## Quick Start

1. Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'dj_vditor',
]
```

2. Add URL route in `urls.py`:

```python
# 当然你也可以自定义url和view, 只要跟配置中的upload.url一致即可
from dj_vditor.views import vditor_images_upload_view

urlpatterns = [
   ...
    path('upload/', vditor_images_upload_view, name='vditor_upload'),
]
```

3. Use in Model:

```python
from dj_vditor.models import VditorTextField

class Article(models.Model):
    content = VditorTextField()
```

4. Configure settings:

```python
# settings.py
# 如果你需要使用阿里云的OSS上传, 请设置以下配置
# DJ_IMAGE_UPLOADER_OSS_CONFIG = {
#     "ACCESS_KEY": getenv("ALIYUN_ACCESS_KEY_ID"),
#     "SECRET_KEY": getenv("ALIYUN_ACCESS_KEY_SECRET"),
#     "ENDPOINT": getenv("OSS_ENDPOINT"),
#     "BUCKET_NAME": getenv("OSS_BUCKET_NAME"),
# }

# 如果要使用火山引擎的TOS上传, 请设置以下配置
DJ_IMAGE_UPLOADER_TOS_CONFIG = {
    "ACCESS_KEY": getenv("VOLCENGINE_ACCESS_KEY"),
    "SECRET_KEY": getenv("VOLCENGINE_SECRET_KEY"),
    "ENDPOINT": getenv("VOLCENGINE_ENDPOINT"),
    "BUCKET_NAME": getenv("VOLCENGINE_BUCKET_NAME"),
    "REGION": getenv("VOLCENGINE_REGION"),
}
# 这是默认配置, 如果不需要修改的话, 可以不设置, 直接使用默认配置
DEFAULT_CONFIG = {
    "width": "100%",
    "height": 720,
    "cache": {"enable": False},
    "mode": "sv",
    "debugger": "false",
    "icon": "ant",
    "outline": "",
    "counter": {
        "enable": True,
    },
    "lang": "zh_CN",
    "toolbar": [
        "emoji",
        "headings",
        "bold",
        "italic",
        "strike",
        "link",
        "|",
        "list",
        "ordered-list",
        "check",
        "outdent",
        "indent",
        "|",
        "quote",
        "line",
        "code",
        "inline-code",
        "insert-after",
        "table",
        "|",
        "upload",
        "fullscreen",
        "export",
        "|",
        "outline",
    ],
    "upload": {
        "storage": "local",
        "local_path": "admin",
        "url": "/upload/",  # 上传接口地址
        "max": 5 * 1024 * 1024,  # 5MB
        "accept": "image/png,image/jpeg,image/gif,image/webp",  # 允许类型
        "fieldName": "file[]",
        "multiple": True,
    },
}

# 如果要覆盖的话, 可以在settings.py中设置VDITOR_CONFIGS, 这样就不会使用默认配置了
VDITOR_CONFIGS = {
    "upload": {"local_path": "my_custom_path", "storage": "tos"},
    "height": 500,
}

```
