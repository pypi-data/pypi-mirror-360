import requests


# 获取外网IP
def get_public_ip():
    try:
        return requests.get("https://api.ipify.org/", timeout=30).text.strip()
    except:
        pass

    try:
        return requests.get("https://myip4.ipip.net/s", timeout=30).text.strip()
    except:
        pass

    return None


# 获取 IP 归属地
def get_ip_location(ip: str, source="baidu"):
    if not ip:
        return None
    if source == "baidu":
        try:
            result = requests.get(f"https://opendata.baidu.com/api.php?query={ip}&resource_id=6006", timeout=10).json()
            if result["status"] == "0":
                return result["data"][0]["location"]
        except Exception:
            return None
    elif source == "ip-api":
        try:
            result = requests.get(f"http://ip-api.com/json/{ip}?lang=zh-CN", timeout=10).json()
            if result["status"] == "success":
                return result["regionName"] + result["city"]
        except Exception:
            return None

    return None
