"""
从 The PureTime (orderonlinehub / ooh order 系统) 抓取指定服务的空闲预约时段。
"""
import os
import requests

BOOKING_URL = "https://www.orderonlinehub.com/index.php/service/booknostaff/time"
SLUG = "thepuretime_bn4w78g5v97rwg634bhe456jhq43hq4"

# 从环境变量读取 authorization 头(不要写死在代码里,存在 GitHub Secrets 里)
AUTH_HEADER = os.environ.get("BOOKING_AUTH_HEADER", "")

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "authorization": AUTH_HEADER,
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.orderonlinehub.com",
    "referer": f"https://www.orderonlinehub.com/servicesnostaff/{SLUG}",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
}


def fetch_today_slots(service_id: str = "200"):
    """
    返回今天(数据里第一个日期)所有 spots > 0 的时段。
    返回: (show_date: str, weekday: str, slots: list[dict{"show_time","spots"}])
    """
    params = {"slug": SLUG}
    resp = requests.post(
        BOOKING_URL,
        params=params,
        headers=HEADERS,
        data={"service_id": service_id},
        timeout=20,
    )
    resp.raise_for_status()
    payload = resp.json()

    if payload.get("code") != "0":
        raise RuntimeError(f"API 返回异常: {payload}")

    reservation_times = payload["data"]["reservation_times"]
    if not reservation_times:
        return None, None, []

    today = reservation_times[0]
    show_date = today["show_date"]        # e.g. "Aug 30"
    weekday = today["show_weekday"]       # e.g. "Sunday"

    slots = [
        {"show_time": dt["show_time"], "spots": dt["spots"]}
        for dt in today["date_times"]
        if dt["spots"] > 0
    ]
    return show_date, weekday, slots


if __name__ == "__main__":
    show_date, weekday, slots = fetch_today_slots()
    print(show_date, weekday, slots)
