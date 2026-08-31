"""
每日自动化主流程:
1. 抓取预约数据
2. 生成 Story 图片
3. 把图片提交(commit)到 GitHub 仓库，得到一个公网可访问的 raw URL
   (Instagram API 要求传一个公网图片地址，不能直接上传文件)
4. 调用 Instagram Graph API 发布 Story
"""
import os
import subprocess
import time

from fetch_availability import fetch_today_slots
from generate_story import generate, OUTPUT_PATH
from post_to_ig import post_story

SERVICE_ID = os.environ.get("BOOKING_SERVICE_ID", "200")

# 形如 "your-username/your-repo"
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "")
GITHUB_REF_NAME = os.environ.get("GITHUB_REF_NAME", "main")


def commit_and_push_image():
    """把生成的图片提交并推送到当前仓库，返回可公开访问的 raw URL。"""
    subprocess.run(["git", "config", "user.name", "story-bot"], check=True)
    subprocess.run(["git", "config", "user.email", "story-bot@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", "output/story.png"], check=True)

    diff = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if diff.returncode == 0:
        print("图片内容没有变化，跳过提交。")
    else:
        subprocess.run(["git", "commit", "-m", "chore: update daily story image"], check=True)
        subprocess.run(["git", "push"], check=True)

    # 加时间戳参数破缓存，确保 Instagram 抓到的是最新图片
    cache_buster = int(time.time())
    return (
        f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/{GITHUB_REF_NAME}/"
        f"output/story.png?t={cache_buster}"
    )


def main():
    show_date, weekday, slots = fetch_today_slots(service_id=SERVICE_ID)
    if show_date is None:
        print("没有抓到任何预约数据，终止。")
        return

    print(f"{show_date} ({weekday}) 空闲时段: {slots}")
    generate(show_date, weekday, slots)

    image_url = commit_and_push_image()
    print("图片公网地址:", image_url)

    # 给 GitHub raw CDN 一点缓存生效时间
    time.sleep(15)

    result = post_story(image_url)
    print("Instagram 发布结果:", result)


if __name__ == "__main__":
    main()
