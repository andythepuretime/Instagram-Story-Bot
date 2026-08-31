"""
把当天的空闲时段渲染成 1080x1920 的 Instagram Story 图片。
"""
import base64
import datetime
import os
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright
from PIL import Image

STORE_TZ = ZoneInfo("America/Detroit")

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "template.html")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "output", "story.png")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
BG_PHOTO_PATH = os.path.join(os.path.dirname(__file__), "assets", "bg_photo.png")


def build_slots_html(slots: list[dict]) -> str:
    if not slots:
        return '<div class="empty-msg">Fully booked today —<br>check back tomorrow!</div>'

    rows = []
    for slot in slots:
        spots = slot["spots"]
        label = "1 SPOT LEFT" if spots == 1 else f"{spots} SPOTS LEFT"
        time_str = slot["show_time"]
        # 把 "11:30 AM" 拆成主时间 + 小号 AM/PM
        if " " in time_str:
            main, ampm = time_str.rsplit(" ", 1)
        else:
            main, ampm = time_str, ""
        rows.append(
            f'<div class="slot"><div class="t">{main}<span class="ampm">{ampm}</span></div>'
            f'<div class="s">{label}</div></div>'
        )
    return "\n".join(rows)


def relative_day_label(show_date_str: str) -> str:
    """固定显示 Today —— 每天早上8点跑的任务，抓到的就是当天数据。"""
    return "Today"


def generate(show_date: str, weekday: str, slots: list[dict], output_path: str = OUTPUT_PATH):
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    rel_day = relative_day_label(show_date)
    full_date = f"{weekday}, {show_date}"

    html = html.replace("{{REL_DAY}}", rel_day)
    html = html.replace("{{FULL_DATE}}", full_date)
    html = html.replace("{{SLOTS_HTML}}", build_slots_html(slots))
    with open(LOGO_PATH, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("ascii")
    html = html.replace("{{LOGO_PATH}}", f"data:image/png;base64,{logo_b64}")

    with open(BG_PHOTO_PATH, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode("ascii")
    html = html.replace("{{BG_PHOTO_PATH}}", f"data:image/png;base64,{bg_b64}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 用 2 倍分辨率超采样渲染，再精细缩小到目标尺寸，让文字和logo边缘更清晰锐利
    SCALE = 2
    TARGET_W, TARGET_H = 1080, 1920
    raw_path = output_path + ".raw.png"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": TARGET_W, "height": TARGET_H},
            device_scale_factor=SCALE,
        )
        page.set_content(html)
        page.wait_for_timeout(200)
        page.screenshot(path=raw_path)
        browser.close()

    # 高质量下采样(LANCZOS)，比直接1倍渲染清晰很多
    with Image.open(raw_path) as im:
        im = im.convert("RGB")
        im = im.resize((TARGET_W, TARGET_H), Image.LANCZOS)
        im.save(output_path, quality=95)
    os.remove(raw_path)

    return output_path


if __name__ == "__main__":
    # 用真实抓到的示例数据测试(Aug 31 / Monday)
    sample_slots = [
        {"show_time": "11:30 AM", "spots": 1},
        {"show_time": "1:00 PM", "spots": 2},
        {"show_time": "2:30 PM", "spots": 2},
        {"show_time": "4:00 PM", "spots": 2},
        {"show_time": "5:30 PM", "spots": 2},
    ]
    path = generate("Aug 31", "Monday", sample_slots)
    print("saved to", path)
