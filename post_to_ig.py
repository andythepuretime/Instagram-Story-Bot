"""
调用 Instagram Graph API，把一张公网可访问的图片发布为 Instagram Story。

需要的环境变量:
- IG_USER_ID          你的 Instagram Business Account ID
- IG_ACCESS_TOKEN     长期有效的 access token(需要 instagram_content_publish 权限)
"""
import os
import time
import requests

GRAPH_API_VERSION = "v21.0"
# 用 Instagram Login 方式生成的 token，要调用 graph.instagram.com，
# 不是 graph.facebook.com（那是 Facebook Login 方式专用的）。
GRAPH_BASE = f"https://graph.instagram.com/{GRAPH_API_VERSION}"


def post_story(image_url: str, ig_user_id: str = None, access_token: str = None):
    ig_user_id = ig_user_id or os.environ["IG_USER_ID"]
    access_token = access_token or os.environ["IG_ACCESS_TOKEN"]

    # 第一步: 创建 media container
    create_resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media",
        data={
            "image_url": image_url,
            "media_type": "STORIES",
            "access_token": access_token,
        },
        timeout=30,
    )
    create_resp.raise_for_status()
    creation_id = create_resp.json()["id"]

    # Instagram 需要几秒钟处理图片，轮询状态直到 FINISHED
    status = "IN_PROGRESS"
    for _ in range(15):
        status_resp = requests.get(
            f"{GRAPH_BASE}/{creation_id}",
            params={"fields": "status_code", "access_token": access_token},
            timeout=20,
        )
        status_resp.raise_for_status()
        status = status_resp.json().get("status_code", "IN_PROGRESS")
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise RuntimeError(f"Instagram 处理图片失败: {status_resp.json()}")
        time.sleep(2)
    else:
        raise TimeoutError("等待 Instagram 处理图片超时")

    # 第二步: 正式发布
    publish_resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media_publish",
        data={
            "creation_id": creation_id,
            "access_token": access_token,
        },
        timeout=30,
    )
    publish_resp.raise_for_status()
    return publish_resp.json()


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else None
    if not url:
        print("用法: python3 post_to_ig.py <公网图片URL>")
        sys.exit(1)
    result = post_story(url)
    print("发布成功:", result)
