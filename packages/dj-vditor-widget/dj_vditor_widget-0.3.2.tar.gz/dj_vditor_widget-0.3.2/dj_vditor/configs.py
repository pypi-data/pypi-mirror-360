from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import copy


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
        "url": "/upload/",  # 上传接口地址
        "max": 5 * 1024 * 1024,  # 5MB
        "accept": "image/png,image/jpeg,image/gif,image/webp",  # 允许类型
        "fieldName": "file[]",
        "multiple": True,
    },
}


def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            d[k] = deep_update(d[k], v)
        else:
            d[k] = v
    return d


class VditorConfig(dict):
    def __init__(self, config_name="default"):
        # 总是从深度复制的默认配置开始
        config = copy.deepcopy(DEFAULT_CONFIG)

        # 获取 settings.py 中的 VDITOR_CONFIGS
        custom_configs = getattr(settings, "VDITOR_CONFIGS", None)

        if custom_configs:
            if not isinstance(custom_configs, dict):
                raise ImproperlyConfigured(
                    "VDITOR_CONFIGS setting must be a dictionary type."
                )

            if config_name == "default":
                # 如果是默认配置，直接将 VDITOR_CONFIGS 视为覆盖项
                config = deep_update(config, custom_configs)
            elif config_name in custom_configs:
                # 如果是具名配置，从 custom_configs 中查找
                named_config = custom_configs[config_name]
                if not isinstance(named_config, dict):
                    raise ImproperlyConfigured(
                        'VDITOR_CONFIGS["%s"] setting must be a dictionary type.'
                        % config_name
                    )
                config = deep_update(config, named_config)
            # 如果具名配置在 custom_configs 中不存在，则静默使用默认配置

        self.update(config)
