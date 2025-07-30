from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage
from .configs import VditorConfig


def upload_to_storage(file_obj, pathname=None):
    upload_config = VditorConfig("default").get("upload", {})

    storage_type = upload_config.get("storage", "local")
    if storage_type == "oss":
        import oss2

        return upload_to_oss(file_obj, pathname, oss2)
    elif storage_type == "tos":
        import tos

        return upload_to_tos(file_obj, pathname, tos)
    elif storage_type == "local":
        return upload_to_local(file_obj, pathname)
    else:
        raise ImproperlyConfigured(f"不支持: {storage_type}")


def _get_remote_filename(file_name, pathname):
    local_path = VditorConfig("default").get("upload", {}).get("local_path", "")
    parts = [part for part in [local_path, pathname, file_name] if part]  # 过滤掉空值
    return "/".join(parts)


def upload_to_local(file_obj, pathname=None):
    filename_with_path = _get_remote_filename(file_obj.name, pathname)

    # 使用 Django 默认的 FileSystemStorage，它会自动使用 settings.MEDIA_ROOT
    fs = FileSystemStorage()

    # 保存文件，fs.save 会处理重名并返回实际保存的（可能重命名后的）路径
    actual_filename = fs.save(filename_with_path, file_obj)

    # 使用 fs.url 来获取正确的、包含所有路径的 URL
    return fs.url(actual_filename)


def upload_to_oss(file_obj, pathname, oss2):
    oss_config = settings.DJ_IMAGE_UPLOADER_OSS_CONFIG
    filename = _get_remote_filename(pathname, file_obj.name)
    try:
        auth = oss2.Auth(oss_config["ACCESS_KEY_ID"], oss_config["ACCESS_KEY_SECRET"])
        bucket = oss2.Bucket(auth, oss_config["ENDPOINT"], oss_config["BUCKET_NAME"])
        bucket.put_object(filename, file_obj)
        return (
            f"https://{oss_config['BUCKET_NAME']}.{oss_config['ENDPOINT']}/{filename}"
        )
    except KeyError as e:
        raise ImproperlyConfigured(f"缺少OSS配置: {e}")


def upload_to_tos(file_obj, pathname, tos):
    tos_config = settings.DJ_IMAGE_UPLOADER_TOS_CONFIG
    filename = _get_remote_filename(pathname, file_obj.name)
    try:
        client = tos.TosClientV2(
            region=tos_config["REGION"],
            ak=tos_config["ACCESS_KEY"],
            sk=tos_config["SECRET_KEY"],
            endpoint=tos_config["ENDPOINT"],
        )
        client.put_object(tos_config["BUCKET_NAME"], filename, content=file_obj)
        return (
            f"https://{tos_config['BUCKET_NAME']}.{tos_config['ENDPOINT']}/{filename}"
        )
    except KeyError as e:
        raise ImproperlyConfigured(f"缺少TOS配置: {e}")
