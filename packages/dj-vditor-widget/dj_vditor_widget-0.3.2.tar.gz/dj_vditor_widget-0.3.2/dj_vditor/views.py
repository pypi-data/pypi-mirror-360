from django.http import JsonResponse
from .configs import VditorConfig
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .oss import upload_to_oss
import uuid
from django.views.decorators.csrf import csrf_exempt


VDITOR_CONFIGS = VditorConfig("default")


@login_required
@require_POST
@csrf_exempt
def vditor_images_upload_view(request):
    """处理图片上传请求"""
    file_list = request.FILES.getlist("file[]")

    # 验证文件存在
    if not file_list:
        return JsonResponse(
            {
                "code": 400,
                "msg": "未收到上传文件",
                "data": {"errFiles": [], "succMap": {}},
            },
            status=400,
        )

    succ_map = {}
    err_files = []

    allowed_types = VDITOR_CONFIGS["upload"]["accept"].split(",")
    max_size = VDITOR_CONFIGS["upload"]["max"]
    user_id = request.user.id

    # 初始化pathname变量
    if isinstance(user_id, uuid.UUID):
        pathname = f"user-{user_id}"
    else:
        # 将数字 ID 格式化为 8 位带前导零
        try:
            pathname = f"user-{int(user_id):08d}"
        except ValueError:
            # 如果既不是 UUID 也不是数字，保留原始值
            pathname = f"user-{str(user_id)}"

    for file_obj in file_list:

        # 文件类型验证
        if file_obj.content_type not in allowed_types:
            err_files.append(file_obj.name)
            continue

        # 文件大小验证
        if file_obj.size > max_size:
            err_files.append(file_obj.name)
            return JsonResponse(
                {
                    "code": 413,
                    "msg": f"文件大小超过{max_size//1024//1024}MB限制",
                    "data": {"errFiles": [file_obj.name], "succMap": {}},
                },
                status=413,
            )

        try:
            # 上传文件
            file_url = upload_to_oss(file_obj, pathname)
            succ_map[file_obj.name] = file_url
        except Exception as e:
            err_files.append(file_obj.name)
            logger.error(f"文件上传失败: {str(e)}")

    return JsonResponse(
        {
            "code": 0 if len(err_files) == 0 else 500,
            "msg": f"成功上传 {len(succ_map)} 个文件",
            "data": {
                "errFiles": [],
                "succMap": succ_map,
            },
        }
    )
